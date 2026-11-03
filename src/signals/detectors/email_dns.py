import asyncio
import re
from typing import List, Optional
from urllib.parse import urlparse

from src.signals.base import Detector
from src.signals.dns_client import DNSLookupError, DoHResolver
from src.signals.models import Finding, Severity, SignalContext

FREE_MAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "hotmail.com", "hotmail.co.uk",
    "outlook.com", "live.com", "aol.com", "icloud.com", "me.com", "btinternet.com",
    "sky.com", "talktalk.net", "virginmedia.com", "protonmail.com",
}
# Common DKIM selectors across Google Workspace, Microsoft 365, Mailchimp and generic hosts.
_DKIM_SELECTORS = ["google", "selector1", "selector2", "default", "k1", "s1", "s2", "mail", "dkim"]


def registrable_host(url: str) -> Optional[str]:
    host = urlparse(url if "//" in url else "//" + url).hostname
    if not host:
        return None
    return host[4:] if host.startswith("www.") else host


class EmailDNSDetector(Detector):
    """SPF / DKIM / DMARC / MX checks over DNS, plus free-mail-address detection.
    The resolver is injectable for tests. Failed lookups produce no finding."""

    name = "email_dns"

    def __init__(self, resolver: Optional[DoHResolver] = None):
        self.resolver = resolver or DoHResolver()

    async def detect(self, ctx: SignalContext) -> List[Finding]:
        out: List[Finding] = []
        domain = registrable_host(ctx.website_url)

        free = sorted({e for e in ctx.contact_emails if e.split("@")[-1].lower() in FREE_MAIL_DOMAINS})
        if free:
            out.append(Finding(
                detector=self.name, signal_type="freemail_business_address", severity=Severity.LOW,
                title="Business publishes a free-mail address (Gmail/Yahoo/etc.)",
                detail="A branded address on their own domain looks more trustworthy and avoids spam filtering.",
                evidence={"addresses": free}, offers=["email_setup"],
            ))

        if not domain:
            return out
        try:
            mx, txt, dmarc = await asyncio.gather(
                self.resolver.query(domain, "MX"),
                self.resolver.query(domain, "TXT"),
                self.resolver.query(f"_dmarc.{domain}", "TXT"),
            )
        except DNSLookupError:
            return out

        if not mx:
            # Only a problem if the site advertises an address at this domain; plenty of
            # organisations (e.g. NHS trusts) host their website on a domain that doesn't
            # receive mail. Either way there is nothing to authenticate, so stop here.
            on_domain = sorted(e for e in ctx.contact_emails if e.lower().endswith("@" + domain))
            if on_domain:
                out.append(Finding(
                    detector=self.name, signal_type="no_mx_records", severity=Severity.HIGH,
                    title=f"{domain} publishes {on_domain[0]} but has no mail (MX) records",
                    detail="Email sent to the advertised address would bounce.",
                    evidence={"domain": domain, "addresses": on_domain}, offers=["email_setup"],
                ))
            return out

        spf = next((t for t in txt if t.lower().startswith("v=spf1")), None)
        dmarc_rec = next((t for t in dmarc if t.upper().startswith("V=DMARC1")), None)

        if spf is None:
            out.append(self._f("missing_spf", Severity.HIGH, f"{domain} has no SPF record",
                               "Anyone can forge email from this domain, and real mail is more likely to hit spam.",
                               domain))
        elif re.search(r"[+?]all\b", spf):
            out.append(self._f("weak_spf", Severity.MEDIUM, f"{domain} SPF policy allows any sender",
                               f"SPF ends in a permissive qualifier: {spf}", domain, {"spf": spf}))

        if dmarc_rec is None:
            out.append(self._f("missing_dmarc", Severity.HIGH, f"{domain} has no DMARC policy",
                               "Without DMARC, Gmail/Yahoo bulk-sender rules and spoofing protection are not met.",
                               domain))
        elif re.search(r"\bp=none\b", dmarc_rec, re.I):
            out.append(self._f("dmarc_monitor_only", Severity.LOW, f"{domain} DMARC is monitor-only (p=none)",
                               "DMARC exists but does not block spoofed mail.", domain, {"dmarc": dmarc_rec}))

        if await self._no_dkim(domain):
            out.append(self._f("dkim_not_detected", Severity.LOW,
                               f"No DKIM key found on common selectors for {domain}",
                               "DKIM selectors can be custom, so this is a prompt to verify, not proof.",
                               domain, {"selectors_checked": _DKIM_SELECTORS}))
        return out

    async def _no_dkim(self, domain: str) -> bool:
        try:
            results = await asyncio.gather(*(
                self.resolver.query(f"{s}._domainkey.{domain}", "TXT") for s in _DKIM_SELECTORS))
        except DNSLookupError:
            return False
        return not any(results)

    def _f(self, signal_type, severity, title, detail, domain, extra=None) -> Finding:
        return Finding(
            detector=self.name, signal_type=signal_type, severity=severity, title=title,
            detail=detail, evidence={"domain": domain, **(extra or {})}, offers=["email_setup"],
        )
