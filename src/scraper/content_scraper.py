import re
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebContentScraper:
    """Scrapes raw web page text, services, images, and contact metadata from client existing websites."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }

    async def scrape_website(self, url: Optional[str], max_items: int = 15, deep_headings: bool = False) -> Dict[str, Any]:
        """Scrapes existing website content. Returns structured text payload.

        max_items caps how many headings/paragraphs are kept — bump it when reading a
        dedicated team/about page that may list many people. deep_headings extends
        heading capture from h1-h3 to h1-h6 — many WordPress page-builder themes
        (SiteOrigin, Elementor, Divi, etc.) render team member names as h4/h5/h6
        "sub-headline" widgets rather than real paragraphs, so a team-page scrape
        that only reads h1-h3 can come back with zero names despite the page
        visually listing a full team. Left off by default since broadening it
        everywhere risks pulling nav/widget clutter into homepage heading-derived
        heuristics (e.g. tagline picking) that were tuned against h1-h3 only."""
        if not url or not url.startswith("http"):
            return self._empty_result(url)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code != 200:
                    logger.warning(f"Scraper received status {response.status_code} for {url}")
                    return self._empty_result(url)

                html = response.text
                return self._parse_html(html, str(response.url), max_items, deep_headings)
        except Exception as e:
            logger.warning(f"Failed to scrape website {url}: {e}")
            return self._empty_result(url)

    async def scrape_rendered(self, url: Optional[str], max_items: int = 40, deep_headings: bool = False) -> Optional[Dict[str, Any]]:
        """Render a page in a headless browser and scroll it so lazy-loaded content
        (especially team headshots that only appear after JS runs) is materialised, then
        parse it with the same extractor as the static path. Returns None when a browser
        isn't available so callers can fall back to the plain HTTP fetch."""
        if not url or not url.startswith("http"):
            return None
        try:
            from playwright.async_api import async_playwright
        except Exception:
            return None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                try:
                    page = await browser.new_page(user_agent=self.headers["User-Agent"])
                    await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    await self._auto_scroll(page)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=6000)
                    except Exception:
                        pass
                    html = await page.content()
                    final_url = page.url
                    # Many team pages render headshots as CSS background-images (no <img>),
                    # so also harvest those, tagging each with its card's text (the name).
                    bg_images = await page.evaluate(
                        """() => {
                            const out = [];
                            document.querySelectorAll('*').forEach((el) => {
                                const bg = getComputedStyle(el).backgroundImage || '';
                                const m = bg.match(/url\\(["']?(.*?)["']?\\)/);
                                if (m && m[1] && !m[1].startsWith('data:')) {
                                    const box = el.closest('a,li,article,figure,div') || el;
                                    out.push({ src: m[1], alt: (box.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 80) });
                                }
                            });
                            return out.slice(0, 60);
                        }"""
                    )
                finally:
                    await browser.close()
            parsed = self._parse_html(html, final_url, max_items, deep_headings)
            for b in (bg_images or []):
                src = b.get("src")
                if src:
                    parsed["scraped_images"].append({"src": urljoin(final_url, src), "alt": b.get("alt", "")})
            return parsed
        except Exception as e:
            logger.warning(f"Playwright render failed for {url}: {e}")
            return None

    @staticmethod
    async def _auto_scroll(page) -> None:
        """Scroll to the bottom in steps to trigger lazy-loading, then settle."""
        try:
            await page.evaluate(
                """async () => {
                    await new Promise((resolve) => {
                        let total = 0; const step = 500;
                        const timer = setInterval(() => {
                            window.scrollBy(0, step); total += step;
                            if (total >= document.body.scrollHeight - window.innerHeight) {
                                clearInterval(timer); resolve();
                            }
                        }, 120);
                        setTimeout(() => { clearInterval(timer); resolve(); }, 6000);
                    });
                }"""
            )
            await page.wait_for_timeout(800)
        except Exception:
            pass

    async def discover_urls(self, url: Optional[str], limit: int = 250) -> List[str]:
        """Discover a site's FULL page inventory from robots.txt + sitemap(s).

        This is far more reliable than crawling homepage links: many important pages
        (team, fees, individual services) aren't linked from the homepage or sit behind
        JS menus, but they ARE in the sitemap. Handles sitemap index files (nested
        sitemaps) and returns same-host page URLs. Returns [] when no sitemap exists."""
        if not url or not url.startswith("http"):
            return []
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        host = parsed.netloc

        # 1. Seed candidate sitemaps from robots.txt + the conventional locations.
        queue: List[str] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                try:
                    robots = await client.get(urljoin(base + "/", "robots.txt"), headers=self.headers)
                    if robots.status_code == 200:
                        for line in robots.text.splitlines():
                            if line.strip().lower().startswith("sitemap:"):
                                queue.append(line.split(":", 1)[1].strip())
                except Exception:
                    pass
                for path in ("sitemap.xml", "sitemap_index.xml", "sitemap-index.xml",
                             "wp-sitemap.xml", "sitemap1.xml", "sitemap/sitemap.xml"):
                    queue.append(urljoin(base + "/", path))

                # 2. Walk sitemaps (following nested index files), collecting page URLs.
                seen_sm, pages, fetches = set(), [], 0
                queue = list(dict.fromkeys(queue))
                while queue and len(pages) < limit and fetches < 40:
                    sm = queue.pop(0)
                    if sm in seen_sm or sm.endswith(".gz"):
                        continue
                    seen_sm.add(sm)
                    fetches += 1
                    try:
                        r = await client.get(sm, headers=self.headers)
                    except Exception:
                        continue
                    if r.status_code != 200:
                        continue
                    text = r.text
                    if "<loc" not in text.lower():
                        continue
                    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text, re.I)
                    if "<sitemapindex" in text.lower():
                        queue.extend(l for l in locs if l not in seen_sm)  # nested sitemaps
                    else:
                        pages.extend(locs)

                # 3. Same-host, deduped, capped.
                out, seen = [], set()
                for u in pages:
                    pu = urlparse(u)
                    if pu.scheme not in ("http", "https") or (pu.netloc and pu.netloc != host):
                        continue
                    key = u.split("#")[0].rstrip("/")
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(u.split("#")[0])
                    if len(out) >= limit:
                        break
                return out
        except Exception as e:
            logger.warning(f"Sitemap discovery failed for {url}: {e}")
            return []

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Same-site links with their anchor text. Captured BEFORE nav/header/footer are
        stripped, because that chrome is exactly where 'Our Team' / 'About' links live."""
        base_host = urlparse(base_url).netloc
        out: List[Dict[str, str]] = []
        seen = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue
            full = urljoin(base_url, href).split("#")[0]
            parsed = urlparse(full)
            if parsed.scheme not in ("http", "https"):
                continue
            if parsed.netloc and parsed.netloc != base_host:
                continue  # internal links only
            if full in seen:
                continue
            seen.add(full)
            out.append({"text": a.get_text(" ", strip=True)[:80], "url": full})
        return out[:80]

    @staticmethod
    def _extract_contacts(soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Authoritative email/phone from mailto:/tel: hrefs — far cleaner than scraping
        them out of run-together page text (which produced junk like '6070info@...ukPatient')."""
        emails, phones = [], []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            low = href.lower()
            if low.startswith("mailto:"):
                addr = href[7:].split("?")[0].strip()
                if re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', addr) and addr not in emails:
                    emails.append(addr)
            elif low.startswith("tel:"):
                num = re.sub(r'[^\d+]', '', href[4:].split("?")[0])
                if 7 <= len(num.lstrip("+")) <= 15 and num not in phones:
                    phones.append(num)
        return {"emails": emails, "phones": phones}

    def _parse_html(self, html: str, url: str, max_items: int = 15, deep_headings: bool = False) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")

        # Capture internal links + contacts first — nav/header/footer (stripped next) hold them.
        links = self._extract_links(soup, url)
        contacts = self._extract_contacts(soup)

        # Strip scripts, styles, noscripts
        for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # og:image is usually the site's best hero-quality photo.
        og_image = ""
        og_tag = soup.find("meta", attrs={"property": "og:image"}) or soup.find("meta", attrs={"name": "og:image"})
        if og_tag and og_tag.get("content"):
            og_image = urljoin(url, og_tag["content"].strip())

        # Extract headings. h4-h6 are opt-in (deep_headings) — see scrape_website's
        # docstring for why: many page-builder themes put team member names there.
        heading_tags = ["h1", "h2", "h3", "h4", "h5", "h6"] if deep_headings else ["h1", "h2", "h3"]
        headings = []
        for h in soup.find_all(heading_tags):
            text = h.get_text().strip()
            if text and len(text) > 3:
                headings.append(text)

        # Extract body paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text and len(text) > 20:
                paragraphs.append(text)

        # Extract image URLs (including common lazy-load attributes).
        images = []
        for img in soup.find_all("img"):
            src = (img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                   or img.get("data-original") or img.get("data-lazy"))
            alt = img.get("alt", "")
            if src and not src.startswith("data:"):
                src = urljoin(url, src)
                images.append({"src": src, "alt": alt})

        # Contact info: prefer the clean mailto:/tel: values; only fall back to scraping
        # the visible text (with a strict, word-bounded regex) when the anchors are absent.
        full_text = soup.get_text(" ")
        phones = list(contacts["phones"])
        emails = list(contacts["emails"])
        if not emails:
            for m in re.findall(r'\b[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}\b', full_text):
                # Trim a trailing CamelCase word glued on by missing whitespace (…co.ukPatient).
                m = re.sub(r'([a-z]{2,})([A-Z][a-z]+)$', r'\1', m)
                if m not in emails:
                    emails.append(m)
        if not phones:
            phones = list(set(re.findall(r'\(?\+?[0-9]{1,4}\)?[-.\s]?\(?[0-9]{1,3}\)?[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}', full_text)))

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "headings": headings[:max_items],
            "paragraphs": paragraphs[:max_items],
            "raw_text_summary": f"Title: {title}\nMeta: {meta_desc}\nHeadings: {' | '.join(headings[:10])}\nBody: {' '.join(paragraphs[:8])}"[:2000],
            "phones": phones[:3],
            "emails": emails[:3],
            "og_image": og_image,
            "scraped_images": images[:max(12, max_items)],
            "links": links,
        }

    def _empty_result(self, url: Optional[str]) -> Dict[str, Any]:
        return {
            "url": url or "",
            "title": "",
            "meta_description": "",
            "headings": [],
            "paragraphs": [],
            "raw_text_summary": "",
            "phones": [],
            "emails": [],
            "og_image": "",
            "scraped_images": [],
            "links": [],
        }
