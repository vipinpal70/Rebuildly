# Lead Quality & Conversion Improvement Plan

> **System:** Rebuildly
> **Goal:** Increase lead *quality* (right business, right pain, reachable decision-maker) and *conversion rate* (reply → call → closed deal), and expand coverage across more countries/categories without diluting quality.
> **Method:** This version is grounded in the actual codebase (`src/`, `config/settings.py`, `src/storage/models.py`), not just the aspirational `Idea-plan.md` / `docs/`. Every recommendation below references the real file it touches, so this is directly actionable rather than conceptual.

## Implementation Status

| Section | Status |
| :--- | :--- |
| 1. Auto-populate decision-maker contact | ✅ Shipped — `src/outreach/contact_resolver.py`, wired into `enrich_lead` (`admin.py`) and both draft generators (`crm.py`) |
| 2. Composite Lead Quality Score | ✅ Shipped — `buying_power_score` (`scoring_matrix.py`), `contactability_score`/`composite_lead_score` (`contact_resolver.py`), `has_review_widget` scoring gap fixed, migration `002_lead_quality_scoring` applied |
| 3. Click-signal fast-follow | ✅ Shipped — `click_tracker.py` queues the WhatsApp draft + escalates to `HOT_ENGAGED` on repeat clicks; `telegram_bot.py` alert now embeds the ready-to-send message + wa.me link |
| 4. Deliverability hardening (real MX lookup, domain warmup) | ⬜ Not started — needs a new dependency (`dnspython`) and/or a paid sending-domain tool |
| 5. Category & country expansion | ⬜ Not started — operator-driven (run more discovery jobs); the `TRADES` imagery bucket in `business_researcher.py` is still unbuilt |
| 6. Multi-source enrichment fallback (Hunter.io/Apollo.io/LinkedIn) | ⬜ Not started — needs paid API credentials; only relevant for the remainder after Section 1's team-page resolution finds nothing |
| 7. Funnel instrumentation (REPLIED/MEETING_BOOKED) | ✅ Shipped — new outreach_status values recognized end-to-end (`crm.py`, `OutreachStudioModal.tsx` outcome buttons, `crm/page.tsx` badges/filters) |

Sections 1–3 and 7 are live in the codebase (backend + CRM frontend). Sections 4–6 remain as documented recommendations requiring new tooling/credentials or operator judgment calls the code can't make on its own.

---

## 0. Reality Check — What's Actually Built vs. What's Documented

`Idea-plan.md` and `docs/` describe the target system. The real code is further along in some ways and further behind in others. This matters because it changes what "improve leads" should mean in practice.

| Capability | Reality | Where |
| :--- | :--- | :--- |
| **Discovery** | Google Places text search only. Filters `google_rating < 4.2` or `review_count < 30` (config-driven), and **discards any business without an existing website** (the model needs a site to audit). No multi-source enrichment. | `src/discovery/places_client.py`, `config/settings.py` |
| **Discovery targeting** | Not a scheduled multi-country/multi-category matrix — it's a manual, one-shot admin job: pick one `category` + a list of `cities`, click run. Defaults are `category="Dentist"`, `cities=["Manchester"]`. | `src/api/admin.py:53-56, 399-426` |
| **Scoring** | Real 0–100 `ModernizationScoringEngine` matching the docs closely — **except** `has_review_widget` is detected by the crawler and stored on every audit row, but is never added to the score. It's dead weight in the data model right now. | `src/scorer/scoring_matrix.py`, `src/crawler/seo_parser.py:65` |
| **Buying-power / firmographic scoring** | Does not exist. The only quality filter is the blanket 4.2★/30-review floor at discovery time — a lead with exactly 30 reviews and one with 500 reviews score identically. | — |
| **Preview/content generation** | Genuinely strong. `BusinessResearcher` scrapes the prospect's real website (including following to a `/team` or `/about` page), grounds an LLM call strictly in that content, and has real anti-hallucination guards (never invents staff, prices, or reviews). This is the system's actual differentiator. | `src/scraper/business_researcher.py` |
| **Decision-maker contact** | **This is the biggest gap.** `OutreachLeadModel.contact_name` / `contact_email` / `linkedin_url` exist in the schema and have a working write path (`OutreachRepository.create_or_update_outreach_lead`), but **nothing in the pipeline ever populates them.** Every outreach draft defaults `contact = contact_name or f"Team at {name}"` — so every cold email currently opens with "Hi Team at Smith & Co Dental" instead of an owner's name. | `src/outreach/content_generator.py:31`, `src/outreach/repository.py` |
| **The near-miss** | `BusinessResearcher._build_team()` *already* extracts real people's names **and job titles** (Partner, Director, Founder, Practice Manager, etc.) from the client's own team page, for use in the generated preview site. That data just never gets fed back into the outreach draft as the decision-maker contact. This is a near-zero-cost fix (Section 2). | `src/scraper/business_researcher.py:350-433` |
| **Outreach copy** | Real 4-channel generator (LinkedIn / Email / WhatsApp / Call script), with an LLM path (Claude/OpenAI) and a template fallback. Good personalization on audit findings; weak personalization on the human being contacted (see above). | `src/outreach/content_generator.py`, `src/outreach/llm_sales_agent.py` |
| **Deliverability** | `EmailVerifier` checks email syntax, does a weak domain-resolves check (`socket.gethostbyname`, not a real MX lookup), and scans outgoing copy for spam trigger words. No sending-domain warmup, no bounce tracking, no reputation monitoring. | `src/outreach/email_verifier.py` |
| **Engagement signal** | `ClickTracker` correctly captures `preview_clicked`, `click_count`, `last_clicked_at` when a prospect opens their preview site, and pushes a Telegram alert. But the signal dead-ends there — no automated next action is triggered by a hot click. | `src/outreach/click_tracker.py` |
| **Funnel logging** | `OutreachLogModel` timestamps every channel action (`LINKEDIN_COPIED`, `MANUAL_EMAIL_SENT`, `WA_OPENED`, `CALLED`, `LINK_CLICKED`) — good raw data. But there's no "REPLIED" or "MEETING_BOOKED" action type, so inbound response can't currently be distinguished from outbound activity in the data. | `src/storage/models.py:117-129` |
| **Validated niche so far** | The live evidence (`generated_sites/`) is UK dental practices and solicitors, mostly Manchester — matching the admin defaults above. This is the proven foothold, not a hypothetical — expansion should branch from it deliberately, not replace it. | `generated_sites/*` |

**Bottom line:** the highest-leverage improvements are not "add enrichment tooling" (a lot of that scaffolding already exists) — they're **wire up the data that's already being collected**, then extend scoring and targeting on top.

---

## 1. Fix #1 (Do This First): Auto-Populate the Decision-Maker Contact

This is the single change most likely to move reply rate, because it's the difference between:
> "Hi Team at Smith & Co Dental, I noticed your website..."

and:

> "Hi Sarah, I noticed Smith & Co Dental's stellar 4.8★ rating..."

**What exists:** `BusinessResearcher._build_team()` already returns `[{name, role, credentials, ...}]` extracted and verified against the real team page.

**What's missing:** nothing selects the *right* person from that list and writes them into `OutreachLeadModel.contact_name` before drafts are generated.

**Concrete change:**
1. In `enrich_lead` (`src/api/admin.py:441`), after `research = await BusinessResearcher().research_business(b, audit)`, rank `research["team"]` by a role-priority list (`Owner`, `Founder`, `Managing Partner`, `Practice Manager`, `Director`, `Partner`, then anyone else) and take the top match.
2. Call `OutreachRepository.create_or_update_outreach_lead(OutreachLeadDTO(business_id=..., contact_name=<picked name>))` so it's persisted, not just used once.
3. Pass that `contact_name` through to `content_generator.generate_all_drafts_with_llm(..., contact_name=...)` when drafts are (re)generated.
4. When no named person is found (team page absent or anonymous), fall back to the current "Team at {name}" — don't block the pipeline on it.

This requires no new API keys, no new third-party tool, and reuses data the system already scrapes and vets for hallucination. It should ship before any Hunter.io/Apollo.io-style tool spend (Section 6) — those are for the *remaining* businesses where no team page exists at all.

---

## 2. Composite Lead Quality Score (extends `scoring_matrix.py`)

Keep `ModernizationScoringEngine`'s 0–100 technical score as-is, but stop treating "passed the 4.2★/30-review floor" as good enough to mean "good lead." Add two cheap sub-scores that use data the system *already has in the `businesses` row* — no new API calls required:

| Sub-score | Signal (already in `BusinessModel`) | Logic |
| :--- | :--- | :--- |
| **Buying Power** | `review_count`, `google_rating` | Bucket review_count (e.g. 30–99 / 100–299 / 300+) as a rough proxy for transaction volume/revenue — a 300+ review dental practice can absorb a $2–5k project far more comfortably than one at the 30-review floor. |
| **Contactability** | `outreach_leads.contact_name`, `contact_email`, `linkedin_url` (post Section 1 fix) | 0 if none found, partial if only a scraped generic email, full if a named decision-maker was matched. |

**Two immediate, low-effort scoring fixes while touching this file:**
- Wire `audit.has_review_widget` into `ModernizationScoringEngine.evaluate_lead` (it's collected, stored, and displayed in the admin panel already — `src/api/admin.py:73` — just never scored). Matches the docs' `+5 pts` weight.
- Enforce a **hard floor before a lead is allowed into Tier 1/2 outreach**: at least a partial Contactability score. Right now a fully technical-only Tier-1 lead with zero contact data can enter the outreach queue and just... sit there, because there's no name to put in the draft.

---

## 3. Close the Loop on the Buying-Intent Signal You Already Capture

`ClickTracker.record_preview_click` (`src/outreach/click_tracker.py`) is genuinely good instrumentation — most cold-outreach systems don't track this at all. Right now it:
- Marks `preview_clicked = True`, increments `click_count`, sets `last_clicked_at`
- Flips `outreach_status` to `VIEWED`
- Sends a Telegram alert to Vipin

**What it should also do:** a prospect actively opening their personalized preview is the strongest buying-intent signal in the whole funnel — stronger than the Modernization Score itself. Right now the only next action is a manual "Vipin sees a Telegram ping and decides what to do." Add an automated fast-follow triggered directly in `record_preview_click`:
- On first click: auto-queue the WhatsApp/SMS draft that's already generated (per `content_generator.py`) to go out within minutes, not whenever Vipin next checks his phone — response-to-engagement speed is one of the highest-leverage conversion levers in cold outreach generally.
- On repeat clicks (`click_count >= 2`) or a click after `CALLED`/`EMAIL_SENT`: bump the lead to a distinct high-priority status (e.g. `HOT_ENGAGED`) so it visibly jumps the admin queue instead of blending into the general `VIEWED` bucket.

---

## 4. Deliverability Hardening (`email_verifier.py`)

The existing `EmailVerifier` (syntax regex + `socket.gethostbyname` + spam-word scan) is a reasonable first-pass smoke test, but two gaps matter as volume grows past a handful of manual sends per day:
- `socket.gethostbyname` checks that the *domain* resolves to an A record — it is not actually an MX lookup, so it can pass domains with no mail server and miss the point of the check. A proper MX lookup (e.g. via `dnspython`) is a small, contained fix in the same file.
- No sending-domain reputation management exists at all: no SPF/DKIM/DMARC verification, no bounce/complaint tracking, no warm-up schedule. This isn't a code gap so much as an infrastructure gap — as outreach volume increases, route sending through a dedicated warmed domain + a tool built for it (Instantly.ai or Smartlead, ~$37–97/mo) rather than scaling raw SMTP from the main domain, to protect deliverability on the outreach domain generally.

---

## 5. Category & Country Expansion

The proven foothold today is **UK dental + legal, Manchester-centric** (Section 0). Since discovery is a manual per-job trigger (`category` + `cities` list, one call at a time — `src/api/admin.py:53-56`), "expansion" concretely means running more of these jobs in a deliberate order, not flipping a config flag. A simple prioritized run-list beats scattershot triggering.

### Category priority (beyond current Dentist/Solicitor jobs)

Ranked by (a) customer lifetime value, (b) likelihood the owner is non-technical → outdated site, (c) reliance on local search + booking, (d) Google review density (needed for the 30-review discovery floor to even return leads):

| Priority | Category | Why |
| :---: | :--- | :--- |
| **High** | Chiropractors, Orthodontists, Med Spas / Cosmetic Dermatology | Same booking-dependent, trust-driven profile as the proven dental niche — reuses the same preview-generation strengths (`business_researcher.py` already has dental-adjacent imagery/niche detection built in). |
| **High** | Family Law, Estate Planning, Immigration, Accounting/CPA | Same profile as the proven solicitor niche; `business_researcher.py` already has a `LEGAL_SERVICES` niche and imagery path. |
| **High** | Plumbers, Electricians, Garage Door, Pest Control | Extremely local-search-dependent, owner-operated, high review density — easy to audit at scale, but needs a new imagery/niche bucket added to `business_researcher.py`'s `NICHE_GALLERY`/`HERO_IMAGES` (currently dental/legal/medspa/HVAC only — HVAC exists, trades generally don't). |
| **Medium** | Financial Advisors, Mortgage Brokers | High-ticket, trust-driven — good fit, no niche imagery yet. |
| **Medium** | Boutique Gyms, Pilates/Yoga Studios | Recurring-membership model rewards the booking/chat upsell (Package 2) heavily. |
| **Lower priority** | Restaurants, Retail | Lower willingness to pay, heavy competition from cheap template vendors — skip unless upmarket. |

Practical note: before running a "High" category job, check `business_researcher.py`'s `_industry_sector()` / `NICHE_GALLERY` mapping (lines ~440–476) — categories outside dental/legal/medspa/HVAC currently fall through to the generic `DEFAULT` imagery, which is fine but less polished than the dental/legal previews. Worth a small imagery-bucket addition before scaling a new category, since preview quality is the product's actual edge.

### Country expansion

Current jobs are UK-only. `docs/` and `Idea-plan.md` name USA/UK/Australia/Germany/France as the target set, but nothing in code differentiates outreach by country yet — the same 4-channel template runs regardless of jurisdiction. Before running discovery jobs in a new country, the operator (not the code) needs to apply different judgment per market:

| Tier | Country | Note |
| :--- | :--- | :--- |
| **Proven** | UK | Live evidence in `generated_sites/`. PECR/UK GDPR allows B2B email to a role-relevant address ("soft opt-in") with a clear opt-out. |
| **Next, low-risk** | Ireland | Same common-law-style soft opt-in as UK, English-native, far less freelancer competition than UK/US — the easiest next market with the current pipeline unchanged. |
| **Next** | USA | Large tier-2-city pool. CAN-SPAM is opt-out based (low friction); TCPA restricts unsolicited SMS/calls specifically — the WhatsApp/SMS draft channel should require explicit permission-first framing for US leads, which the current `content_generator.py` WhatsApp draft doesn't distinguish by country today. |
| **Next** | France | CPCE Art. L34-5 explicitly permits B2B cold email when content relates to the recipient's professional role + opt-out — favorable relative to Germany. |
| **Caution** | Germany | High-value clients, but German UWG is interpreted strictly against unsolicited email even B2B without a prior relationship. Until the outreach sequencing is country-aware in code, **manually route Germany leads to LinkedIn/phone channels only** and skip the auto-generated cold email draft for them. |
| **Test later** | Australia, UAE | AU: Spam Act 2003, consent-based — treat similarly to Germany (LinkedIn-first) until validated. UAE: no equivalent restriction, WhatsApp-first culture fits the existing WhatsApp draft channel unusually well, and deal sizes run high — worth a small pilot once Ireland/USA are validated. |

---

## 6. Multi-Source Enrichment — Only for the Remainder

After Section 1's fix, some businesses still won't have a discoverable team page (no `/team` or `/about` page, or an anonymous one). For *that* remainder only, add a fallback enrichment step rather than a blanket tool subscription:

| Tool | Purpose | Cost |
| :--- | :--- | :--- |
| Hunter.io or Apollo.io | Verified owner/manager email by domain + name-pattern guessing, when no team page exists | ~$49–99/mo |
| LinkedIn (manual or Sales Navigator) | Confirm the actual owner for the LinkedIn-DM channel (Step 1 of the existing multi-touch sequence in `Idea-plan.md`) | ~$99/mo optional |

Don't reach for BuiltWith/Wappalyzer tech-stack pre-filtering yet — at current volume (manual, one job at a time) the crawler/auditor cost isn't the bottleneck; contactability is.

---

## 7. Funnel Instrumentation — Distinguish Inbound from Outbound

`OutreachLogModel` already timestamps every action, which is more than most systems have. The gap is that all current `action` values (`LINKEDIN_COPIED`, `MANUAL_EMAIL_SENT`, `WA_OPENED`, `CALLED`, `LINK_CLICKED`) are things *you* did — there's no logged action for "they replied" or "meeting booked." Add two action types (`REPLIED`, `MEETING_BOOKED`) so a simple query grouped by category/city/channel can compute real reply and meeting rates — right now that can only be inferred indirectly from `outreach_status = CONVERTED`, which loses the funnel shape (where leads drop off) entirely.

---

## 8. 30 / 60 / 90-Day Rollout

**Days 1–30 — Wire up what's already collected**
- Ship Section 1 (decision-maker contact auto-population) — highest ROI, no new tooling.
- Fix `has_review_widget` scoring gap; add the Contactability hard floor to Tier 1/2 (Section 2).
- Ship the click-signal fast-follow + `HOT_ENGAGED` status (Section 3).
- Add `REPLIED`/`MEETING_BOOKED` action logging (Section 7).
- Run one new "High priority" category job (Chiropractors or Family Law) in Manchester + one more UK tier-2 city, using the now-improved contact/scoring pipeline, and compare reply rate against the historical dental/legal baseline.

**Days 31–60 — Validate Ireland, harden deliverability**
- Pilot Ireland with the same dental/legal categories (lowest-risk market expansion, code unchanged).
- Add the real MX lookup to `EmailVerifier` (Section 4); evaluate a dedicated warmed sending domain if email volume justifies it.
- Add a `TRADES` imagery bucket to `business_researcher.py` before running a plumbers/electricians job.
- Pull reply/meeting rates by category × city from the new logging; kill or scale based on real numbers.

**Days 61–90 — Scale proven segments, test USA**
- Scale the winning categories/cities from Days 31–60.
- Run first USA tier-2-city job (per `Idea-plan.md`'s target list), with the TCPA-aware permission-first WhatsApp/SMS framing applied manually until it's encoded in `content_generator.py`.
- Add Hunter.io/Apollo.io fallback enrichment (Section 6) only for the subset still missing contact data after the team-page fix.
- Revisit Germany: still LinkedIn/phone-only until outreach sequencing is country-aware in code.
