import re
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup

from config.settings import settings
from src.signals.base import Detector
from src.signals.models import Finding, Severity, SignalContext
from src.utils.logger import logger

_AXE_PATH = Path(__file__).resolve().parent.parent / "vendor" / "axe.min.js"


def static_accessibility_issues(html: str) -> dict:
    """Cheap WCAG checks that need no browser. Returns {issue_key: count_or_True}."""
    soup = BeautifulSoup(html, "html.parser")
    issues = {}

    html_tag = soup.find("html")
    if not (html_tag and html_tag.get("lang")):
        issues["missing_html_lang"] = True

    if not (soup.title and soup.title.get_text(strip=True)):
        issues["missing_page_title"] = True

    missing_alt = [i for i in soup.find_all("img") if i.get("alt") is None and i.get("role") != "presentation"]
    if missing_alt:
        issues["images_missing_alt"] = len(missing_alt)

    viewport = soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)})
    content = (viewport.get("content", "") if viewport else "").lower().replace(" ", "")
    max_scale = re.search(r"maximum-scale=([\d.]+)", content)
    if "user-scalable=no" in content or (max_scale and float(max_scale.group(1)) < 2):
        issues["zoom_disabled"] = True

    labelled_ids = {l.get("for") for l in soup.find_all("label") if l.get("for")}
    unlabelled = 0
    for inp in soup.find_all(["input", "select", "textarea"]):
        if inp.get("type") in ("hidden", "submit", "button", "image", "reset"):
            continue
        if inp.get("aria-label") or inp.get("aria-labelledby") or inp.get("title"):
            continue
        if inp.get("id") in labelled_ids or inp.find_parent("label"):
            continue
        unlabelled += 1
    if unlabelled:
        issues["form_fields_unlabelled"] = unlabelled

    empty_links = [
        a for a in soup.find_all("a", href=True)
        if not a.get_text(strip=True) and not a.get("aria-label") and not a.get("title")
        and not any(i.get("alt") for i in a.find_all("img"))
    ]
    if empty_links:
        issues["links_without_text"] = len(empty_links)
    return issues


async def run_axe(url: str) -> Optional[dict]:
    """Runs axe-core in headless Chromium. Returns {impact: violation_count, rules: [...]}
    or None if unavailable/failed."""
    if not _AXE_PATH.exists():
        return None
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                page.set_default_navigation_timeout(settings.ACCESSIBILITY_AXE_TIMEOUT_SECONDS * 1000)
                await page.goto(url, wait_until="load")
                await page.add_script_tag(path=str(_AXE_PATH))
                result = await page.evaluate(
                    "axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa']}})"
                )
            finally:
                await browser.close()
    except Exception as err:
        logger.warning(f"axe-core run failed for {url}: {err}")
        return None

    by_impact = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    rules = []
    for v in result.get("violations", []):
        impact = v.get("impact") or "minor"
        by_impact[impact] = by_impact.get(impact, 0) + 1
        rules.append({"id": v["id"], "impact": impact, "nodes": len(v.get("nodes", []))})
    return {"by_impact": by_impact, "rules": sorted(rules, key=lambda r: -r["nodes"])[:10]}


class AccessibilityDetector(Detector):
    """WCAG 2.1 AA signal: static HTML checks always, axe-core when enabled."""

    name = "accessibility"

    async def detect(self, ctx: SignalContext) -> List[Finding]:
        if not ctx.html:
            return []

        static = static_accessibility_issues(ctx.html)
        axe = await run_axe(ctx.website_url) if settings.ACCESSIBILITY_AXE_ENABLED else None

        serious = (axe["by_impact"]["critical"] + axe["by_impact"]["serious"]) if axe else 0
        total = sum(axe["by_impact"].values()) if axe else 0
        if not static and not total:
            return []

        if serious >= 3 or len(static) >= 4:
            severity = Severity.HIGH
        elif serious or len(static) >= 2:
            severity = Severity.MEDIUM
        else:
            severity = Severity.LOW

        parts = []
        if axe:
            parts.append(f"{serious} serious/critical WCAG violation type(s) found by axe-core")
        if static:
            parts.append(f"{len(static)} basic HTML accessibility issue(s)")
        return [Finding(
            detector=self.name, signal_type="accessibility_issues", severity=severity,
            title="Website has accessibility problems (WCAG 2.1 AA)",
            detail="; ".join(parts) + ". Accessibility is a legal requirement in the EU (EAA, June 2025) "
                   "and a litigation risk in the US.",
            evidence={"static": static, "axe": axe, "axe_ran": axe is not None},
            offers=["accessibility_remediation"],
        )]
