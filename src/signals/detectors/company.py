import re
from datetime import date
from typing import List

from src.discovery.companies_house import CompaniesHouseClient
from src.signals.base import Detector
from src.signals.models import Finding, Severity, SignalContext

_POSTCODE = re.compile(r"[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}", re.I)


class CompanyDetector(Detector):
    """UK-only enrichment from Companies House. Skipped without COMPANIES_HOUSE_API_KEY
    or for non-UK leads."""

    name = "company"

    def __init__(self, client: CompaniesHouseClient = None):
        self.client = client or CompaniesHouseClient()

    async def detect(self, ctx: SignalContext) -> List[Finding]:
        if not self.client.enabled or ctx.lead.country.strip().lower() not in ("uk", "united kingdom", "gb"):
            return []
        m = _POSTCODE.search(ctx.lead.address or "")
        company = await self.client.find_company(ctx.lead.name, m.group(0) if m else None)
        if not company:
            return []

        out: List[Finding] = []
        age_months = None
        if company.date_of_creation:
            today = date.today()
            age_months = (today.year - company.date_of_creation.year) * 12 + today.month - company.date_of_creation.month

        out.append(Finding(
            detector=self.name, signal_type="company_profile", severity=Severity.INFO,
            title=f"Registered company {company.name} ({company.company_number})",
            detail="Matched to Companies House by name"
                   + (" and postcode." if m else "; address had no postcode to confirm."),
            evidence={
                "company_number": company.company_number, "company_type": company.company_type,
                "incorporated": company.date_of_creation.isoformat() if company.date_of_creation else None,
                "directors": company.directors,
                # PECR: unsolicited B2B email is permitted to corporate subscribers
                # (ltd/llp/plc), but sole traders and partnerships count as individuals.
                "pecr_corporate_subscriber": company.company_type in ("ltd", "llp", "plc", "private-limited-guarant-nsc"),
            },
        ))
        if age_months is not None and age_months <= 24:
            out.append(Finding(
                detector=self.name, signal_type="new_company", severity=Severity.MEDIUM,
                title=f"Company incorporated {age_months} month(s) ago",
                detail="New businesses are still choosing their web, email and marketing providers.",
                evidence={"incorporated": company.date_of_creation.isoformat(), "age_months": age_months},
                offers=["launch_package", "website_rebuild"],
            ))
        return out
