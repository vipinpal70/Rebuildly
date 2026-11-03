import time
from datetime import date, timedelta

import pytest

from src.discovery.companies_house import CompaniesHouseClient, CompanyRecord
from src.discovery.models import PlaceLead, SearchQuery
from src.discovery.osm_client import OSMDiscoveryClient
from src.discovery.places_client import extract_gbp_details
from src.signals import Severity, SignalContext, SignalEngine, rank_offers
from src.signals.detectors import (
    AccessibilityDetector, CompanyDetector, EmailDNSDetector,
    GBPCompletenessDetector, ReviewDetector, TrackingDetector,
)
from src.signals.detectors.accessibility import static_accessibility_issues
from src.signals.dns_client import DNSLookupError


def make_lead(**kw) -> PlaceLead:
    base = dict(place_id="p1", name="Smile Dental Practice", category="Dentist", city="Manchester",
                country="UK", website="https://smile-dental.co.uk", phone="0161 000 0000",
                google_rating=4.8, review_count=120, address="1 High St, Manchester M1 1AA")
    return PlaceLead(**{**base, **kw})


def make_ctx(html="", lead=None, **kw) -> SignalContext:
    lead = lead or make_lead()
    return SignalContext(lead=lead, website_url=lead.website, html=html, **kw)


def types(findings):
    return {f.signal_type for f in findings}


# ---------------------------------------------------------------- tracking
@pytest.mark.asyncio
async def test_no_analytics_flagged():
    f = await TrackingDetector().detect(make_ctx("<html><body>hello</body></html>"))
    assert "no_analytics" in types(f)
    assert next(x for x in f if x.signal_type == "no_analytics").severity == Severity.HIGH


@pytest.mark.asyncio
async def test_legacy_ua_flagged_and_ga4_clean():
    ua = await TrackingDetector().detect(make_ctx("<script>ga('create','UA-1234567-1')</script>"))
    assert "legacy_universal_analytics" in types(ua)
    ga4 = await TrackingDetector().detect(make_ctx(
        '<script async src="https://www.googletagmanager.com/gtag/js?id=G-ABCDEFGH12"></script> cookiebot'))
    assert not types(ga4) & {"no_analytics", "legacy_universal_analytics", "tracking_without_consent"}


@pytest.mark.asyncio
async def test_gtm_never_reported_as_missing_analytics():
    f = await TrackingDetector().detect(make_ctx("<script src='https://www.googletagmanager.com/gtm.js?id=GTM-ABC123'></script>"))
    assert "no_analytics" not in types(f)
    assert "no_ad_pixels" not in types(f)
    assert "tracking_without_consent" in types(f)


@pytest.mark.asyncio
async def test_tracking_empty_html_returns_nothing():
    assert await TrackingDetector().detect(make_ctx("")) == []


# --------------------------------------------------------------------- gbp
@pytest.mark.asyncio
async def test_gbp_incomplete_scored():
    lead = make_lead(review_count=10, google_rating=3.5, phone=None,
                     gbp_details={"photo_count": 2, "has_hours": False, "has_summary": False, "reviews": []})
    [f] = await GBPCompletenessDetector().detect(make_ctx(lead=lead))
    assert f.severity == Severity.HIGH and f.evidence["completeness_score"] < 60
    assert "10+ photos" in f.evidence["missing"]


@pytest.mark.asyncio
async def test_gbp_complete_or_unfetched_is_silent():
    full = make_lead(gbp_details={"photo_count": 10, "has_hours": True, "has_summary": True, "reviews": []})
    assert await GBPCompletenessDetector().detect(make_ctx(lead=full)) == []
    assert await GBPCompletenessDetector().detect(make_ctx(lead=make_lead())) == []


def test_extract_gbp_details():
    d = extract_gbp_details({"photos": [{}] * 3, "opening_hours": {"x": 1},
                             "reviews": [{"rating": 5, "text": "great", "time": 1700000000}]})
    assert d["photo_count"] == 3 and d["has_hours"] and not d["has_summary"]
    assert d["reviews"][0]["published_epoch"] == 1700000000


# ----------------------------------------------------------------- reviews
def _rev(rating, days_ago=1, replied=None):
    return {"rating": rating, "text": f"{rating} stars", "published_epoch": int(time.time() - days_ago * 86400),
            "owner_replied": replied}


@pytest.mark.asyncio
async def test_reviews_negative_and_stale():
    lead = make_lead(gbp_details={"reviews": [_rev(1, 200), _rev(2, 210), _rev(5, 300)]})
    f = await ReviewDetector().detect(make_ctx(lead=lead))
    assert {"recent_negative_reviews", "stale_reviews"} <= types(f)
    assert next(x for x in f if x.signal_type == "recent_negative_reviews").severity == Severity.HIGH


@pytest.mark.asyncio
async def test_reply_rate_only_when_data_known():
    unknown = make_lead(gbp_details={"reviews": [_rev(5), _rev(4), _rev(5)]})
    assert "low_review_response_rate" not in types(await ReviewDetector().detect(make_ctx(lead=unknown)))
    known = make_lead(gbp_details={"reviews": [_rev(2, replied=False), _rev(5, replied=False), _rev(5, replied=True)]})
    f = await ReviewDetector().detect(make_ctx(lead=known))
    assert "low_review_response_rate" in types(f)


# --------------------------------------------------------------- email dns
class FakeResolver:
    def __init__(self, records=None, fail=False):
        self.records, self.fail = records or {}, fail

    async def query(self, name, rtype):
        if self.fail:
            raise DNSLookupError("boom")
        return self.records.get((name, rtype), [])


@pytest.mark.asyncio
async def test_email_dns_missing_spf_dmarc():
    r = FakeResolver({("smile-dental.co.uk", "MX"): ["10 mx.google.com."],
                      ("smile-dental.co.uk", "TXT"): ["google-site-verification=abc"]})
    f = await EmailDNSDetector(r).detect(make_ctx())
    assert {"missing_spf", "missing_dmarc", "dkim_not_detected"} <= types(f)


@pytest.mark.asyncio
async def test_email_dns_healthy_domain_clean():
    d = "smile-dental.co.uk"
    r = FakeResolver({(d, "MX"): ["10 mx"], (d, "TXT"): ["v=spf1 include:_spf.google.com -all"],
                      (f"_dmarc.{d}", "TXT"): ["v=DMARC1; p=reject"], (f"google._domainkey.{d}", "TXT"): ["v=DKIM1"]})
    assert await EmailDNSDetector(r).detect(make_ctx()) == []


@pytest.mark.asyncio
async def test_email_dns_weak_policies_and_no_mx():
    d = "smile-dental.co.uk"
    r = FakeResolver({(d, "MX"): ["10 mx"], (d, "TXT"): ["v=spf1 +all"], (f"_dmarc.{d}", "TXT"): ["v=DMARC1; p=none"]})
    assert {"weak_spf", "dmarc_monitor_only"} <= types(await EmailDNSDetector(r).detect(make_ctx()))
    assert await EmailDNSDetector(FakeResolver()).detect(make_ctx()) == []
    nomx = await EmailDNSDetector(FakeResolver()).detect(make_ctx(contact_emails=["info@smile-dental.co.uk"]))
    assert types(nomx) == {"no_mx_records"}


@pytest.mark.asyncio
async def test_email_dns_lookup_failure_makes_no_claims_and_freemail_still_works():
    ctx = make_ctx(contact_emails=["drsmith@gmail.com"])
    f = await EmailDNSDetector(FakeResolver(fail=True)).detect(ctx)
    assert types(f) == {"freemail_business_address"}


# ----------------------------------------------------------- accessibility
BAD_HTML = """<html><head><meta name="viewport" content="width=device-width, user-scalable=no"></head>
<body><img src="a.png"><input type="text" name="q"><a href="/x"></a></body></html>"""


def test_static_accessibility_checks():
    issues = static_accessibility_issues(BAD_HTML)
    assert issues == {"missing_html_lang": True, "missing_page_title": True, "images_missing_alt": 1,
                      "zoom_disabled": True, "form_fields_unlabelled": 1, "links_without_text": 1}
    good = '<html lang="en"><head><title>x</title></head><body><img src=a alt=""><label for=q>Q</label><input id=q></body></html>'
    assert static_accessibility_issues(good) == {}


@pytest.mark.asyncio
async def test_accessibility_detector_static_only(monkeypatch):
    from config.settings import settings
    monkeypatch.setattr(settings, "ACCESSIBILITY_AXE_ENABLED", False)
    [f] = await AccessibilityDetector().detect(make_ctx(BAD_HTML))
    assert f.severity == Severity.HIGH and f.evidence["axe_ran"] is False


@pytest.mark.asyncio
async def test_axe_runs_in_real_browser(tmp_path):
    from src.signals.detectors.accessibility import run_axe
    page = tmp_path / "bad.html"
    page.write_text(BAD_HTML)
    result = await run_axe(page.as_uri())
    if result is None:
        pytest.skip("Chromium unavailable")
    assert sum(result["by_impact"].values()) > 0
    assert any(r["id"] == "image-alt" for r in result["rules"])


# ----------------------------------------------------------------- company
class FakeCH(CompaniesHouseClient):
    def __init__(self, record):
        super().__init__(api_key="k")
        self.record = record

    async def find_company(self, name, postcode=None):
        return self.record


@pytest.mark.asyncio
async def test_company_new_and_pecr():
    rec = CompanyRecord(company_number="123", name="SMILE DENTAL LTD", company_type="ltd",
                        date_of_creation=date.today() - timedelta(days=200), directors=["SMITH, Jane"])
    f = await CompanyDetector(FakeCH(rec)).detect(make_ctx())
    assert {"company_profile", "new_company"} == types(f)
    assert next(x for x in f if x.signal_type == "company_profile").evidence["pecr_corporate_subscriber"] is True


@pytest.mark.asyncio
async def test_company_skips_non_uk_and_no_key(monkeypatch):
    from config.settings import settings
    monkeypatch.setattr(settings, "COMPANIES_HOUSE_API_KEY", None)
    rec = CompanyRecord(company_number="1", name="x")
    assert await CompanyDetector(FakeCH(rec)).detect(make_ctx(lead=make_lead(country="US"))) == []
    assert await CompanyDetector(CompaniesHouseClient(api_key=None)).detect(make_ctx()) == []


@pytest.mark.asyncio
async def test_companies_house_matching(monkeypatch):
    client = CompaniesHouseClient(api_key="k")

    async def fake_get(session, path, params=None):
        if path == "/search/companies":
            return {"items": [
                {"title": "SMILE DENTAL PRACTICE LIMITED", "company_number": "1", "company_status": "active",
                 "company_type": "ltd", "date_of_creation": "2015-01-01", "address": {"postal_code": "M1 1AA"}},
                {"title": "UNRELATED BUILDERS LTD", "company_number": "2", "company_status": "active"},
            ]}
        return {"items": [{"name": "SMITH, Jane", "officer_role": "director"},
                          {"name": "OLD, Bob", "officer_role": "director", "resigned_on": "2020-01-01"}]}
    monkeypatch.setattr(client, "_get", fake_get)
    rec = await client.find_company("Smile Dental Practice", "M1 1AA")
    assert rec.company_number == "1" and rec.directors == ["SMITH, Jane"]
    assert await client.find_company("Totally Different Name") is None


# --------------------------------------------------------------------- osm
def test_osm_query_and_leads():
    ql = OSMDiscoveryClient._build_query("Dentist", ("area", "3600123"))
    assert '"amenity"="dentist"' in ql and "area:3600123" in ql and "'website'" in ql
    assert 'name"~"yoga studio"' in OSMDiscoveryClient._build_query("Yoga Studio", ("bbox", "1,2,3,4"))

    elements = [
        {"type": "node", "id": 1, "lat": 1, "lon": 2, "tags": {"name": "A Dental", "website": "a-dental.co.uk", "amenity": "dentist",
                                                                "addr:street": "High St", "addr:housenumber": "5"}},
        {"type": "way", "id": 2, "center": {"lat": 1, "lon": 2}, "tags": {"name": "B Dental", "contact:website": "https://b.com"}},
        {"type": "node", "id": 3, "tags": {"name": "No Site"}},
        {"type": "node", "id": 4, "tags": {"website": "https://noname.com"}},
        {"type": "node", "id": 5, "tags": {"name": "Known", "website": "https://k.com"}},
    ]
    leads = OSMDiscoveryClient._to_leads(elements, SearchQuery(category="Dentist", city="Leeds", country="UK"),
                                         {"osm:node/5"}, None)
    assert [l.place_id for l in leads] == ["osm:node/1", "osm:way/2"]
    assert leads[0].website == "http://a-dental.co.uk" and leads[0].address == "5 High St"
    assert leads[0].google_rating is None


# ------------------------------------------------------------ engine/offers
class Boom:
    name = "boom"
    async def detect(self, ctx):
        raise RuntimeError("x")


@pytest.mark.asyncio
async def test_engine_isolates_failures_and_ranks_offers():
    engine = SignalEngine([Boom(), TrackingDetector()])
    findings = await engine.run(make_ctx("<html></html>"))
    assert "no_analytics" in types(findings)
    ranked = rank_offers(findings)
    assert ranked[0].offer == "analytics_setup" and ranked[0].score == 50
