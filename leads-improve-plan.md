# Lead Quality & Conversion Improvement Plan

> **System:** Opportunity Finder
> **Goal:** Increase lead *quality* (right business, right pain, reachable decision-maker) and *conversion rate* (reply → call → closed deal), and expand coverage across more countries and business categories without diluting quality.
> **Builds on:** `Idea-plan.md` (core system) and `docs/04_scoring_matrix.md` (Modernization Need Score). This document does not replace those — it adds a lead-quality layer, a contact-enrichment layer, an expansion roadmap, and a conversion layer on top.

---

## 1. Why Leads Currently Underperform (Diagnosis)

The current pipeline (`Google Places → Crawler/Auditor → Modernization Score → Outreach`) is good at finding businesses with *bad websites*, but a bad website alone is not a good lead. Three gaps typically cause weak conversion:

1. **No buying-power / intent signal.** A 4.3★ business with 12 reviews and a 4.3★ business with 400 reviews get treated the same if both have outdated sites — but only the second one can comfortably afford a $1,500–$5,000 project.
2. **No decision-maker contact data.** `outreach_leads.contact_email` / `linkedin_url` are in the schema but nothing in the pipeline populates them — outreach likely falls back to generic `info@` addresses, which get filtered by gatekeepers or spam folders.
3. **No feedback loop from outreach results back into targeting.** Without tracking reply/close rate *by category and city*, the system can't learn which segments are actually worth scaling.

The fixes below target exactly these three gaps, then layer on country/category expansion.

---

## 2. Redefine "Good Lead": Composite Lead Quality Score

Keep the existing Modernization Need Score (0–100) exactly as-is — it's a solid technical-deficiency signal. Combine it with two new sub-scores into a **Composite Lead Quality Score**:

| Sub-score | What it measures | Signals to pull | Weight |
| :--- | :--- | :--- | :---: |
| **Modernization Need Score** (existing) | How broken/outdated the site is | Mobile UX, SSL, speed, SEO, schema, booking, chat, legacy stack | 40% |
| **Buying Power Score** (new) | Can they actually afford $1.5k–$5k? | Review count (proxy for volume), years in business (Places `business_status` + founding signals), price level (Places `price_level` field where available), number of locations, staff count via LinkedIn company page | 35% |
| **Contactability Score** (new) | Can we actually reach a real decision-maker? | Owner/founder name found, verified email found, LinkedIn profile found, direct phone (not call-center) found | 25% |

**Practical thresholds to add to `docs/04_scoring_matrix.md`:**
- Require **≥ 50 Google reviews** as a hard floor before a lead enters Tier 1/2 outreach — low review count usually means low revenue, regardless of site quality.
- Require **at least one enriched contact channel** (email or LinkedIn) before a lead leaves the "NEW" pipeline stage — sending outreach to `info@` inboxes should be the fallback, not the default.
- Add a `days_since_last_review` signal — a business with no new reviews in 12+ months may be inactive/closing, wasting outreach effort even if the score is high.

This turns the funnel from "find broken websites" into "find broken websites *belonging to businesses that can pay and that we can actually reach*" — the actual lever for conversion rate.

---

## 3. Multi-Source Discovery (Don't Rely on Google Places Alone)

Google Places API is a great starting point but has blind spots (rate limits/cost at scale, and it doesn't give you a contact name). Layer in enrichment sources after discovery, not instead of it:

| Stage | Tool / API | Purpose | Approx. Cost |
| :--- | :--- | :--- | :--- |
| 1. Discovery | Google Places API (existing) | Business name, category, city, rating, review count, phone, website | ~$0.017–$0.032/request |
| 2. Tech pre-filter | BuiltWith API or Wappalyzer API | Detect CMS/tech stack *before* running a full Playwright crawl — skip businesses already on modern stacks (Webflow, Shopify Plus, custom React) to save crawl budget | ~$0–$295/mo (has a free tier) |
| 3. Contact enrichment | Hunter.io or Apollo.io | Find verified owner/manager email by domain + name pattern | ~$49–$99/mo |
| 4. Decision-maker ID | LinkedIn (manual/Sales Navigator) | Confirm actual owner/practice manager, get LinkedIn profile URL for Step 1 outreach | ~$99/mo (Sales Navigator Core) |
| 5. Firmographic signal | Google Places `price_level`, review velocity, photo count | Rough proxy for business size/activity without paid tools | Free (already-available fields) |

**Action for the pipeline:** insert a `src/enrichment` module between the Discovery Module and the Crawler/Auditor Module so contact data and buying-power signals are attached to the `businesses` row *before* the audit runs — that way Tier-1 alerts arrive already outreach-ready instead of triggering a second manual lookup step.

**Schema addition to `docs/02_database_schema.md`:** add `owner_name`, `enriched_email`, `enriched_email_confidence`, `linkedin_company_url`, `review_velocity_90d` to the `businesses` or a new `enrichment` table, and add `source_channel`, `first_response_at`, `meeting_booked_at` to `outreach_leads` so conversion can actually be measured by stage (see Section 6).

---

## 4. Country Expansion Strategy

Keep the existing five countries (USA, UK, Australia, Germany, France) as the core, but treat them as **Tier 1**, and evaluate expansion candidates as **Tier 2** based on: English-language ease for outreach, cold-outreach legal risk, purchasing power, and competition density.

| Tier | Country | Why | Outreach Legal Note |
| :--- | :--- | :--- | :--- |
| **Tier 1 (current)** | USA | Largest market, huge tier-2 city pool, dollar pricing | CAN-SPAM: opt-out based, low friction for email. TCPA restricts unsolicited SMS/calls — get permission before texting. |
| **Tier 1** | UK | High English proficiency, strong SMB density | PECR/UK GDPR allows B2B email to a role-based address if relevant to their job ("soft opt-in"), needs clear opt-out. |
| **Tier 1** | Australia | Less saturated than US/UK, high avg. deal size | Spam Act 2003 is consent-based — lean on LinkedIn-first, use "existing relationship" carefully. |
| **Tier 1** | France | Large SMB base, good $/€ per project | CPCE Art. L34-5 explicitly *permits* B2B cold email if content relates to the recipient's professional function + opt-out included — favorable compared to Germany. |
| **Tier 1 — caution** | Germany | High-value clients, but riskiest for cold email | German UWG (unfair competition law) is interpreted strictly against unsolicited *any* email, even B2B, without a prior relationship. **Recommend LinkedIn + phone as primary channels here, de-prioritize cold email.** |
| **Tier 2 — add next** | Ireland | Native English, common-law GDPR interpretation similar to UK, far less freelancer competition than UK/US | Same PECR-style soft opt-in as UK. |
| **Tier 2 — add next** | Canada | High purchasing power, English/French bilingual market | CASL is the *strictest* anti-spam law in the list — requires implied or express consent. Treat as LinkedIn-first, or only email businesses with an existing/implied relationship (e.g., they engaged with content first). |
| **Tier 2 — test** | Netherlands | Very high English proficiency, strong SMB digital-spend culture | GDPR applies but B2B legitimate-interest email is commonly used; keep opt-out clear. |
| **Tier 2 — test, high LTV** | UAE (Dubai / Abu Dhabi) | English is the default business language, very high-ticket clinics/law firms/real estate, WhatsApp-first culture matches your existing WhatsApp channel step well | No GDPR-equivalent restriction on B2B cold outreach currently; WhatsApp Business outreach converts very well here. |
| **Tier 2 — small but easy** | New Zealand | Same playbook as Australia, minimal competition | Unsolicited Electronic Messages Act — consent-based, same caution as AU. |

**Recommendation:** don't spread thin across 10 countries at once. Run the current 5, but re-weight Germany toward LinkedIn/phone instead of cold email, and pilot **Ireland + UAE** next (Ireland = easiest legal/language fit, UAE = highest deal size and best channel fit for your existing WhatsApp step).

---

## 5. Business Category Expansion

Current niches (Medical, Legal/Financial, Home Services, Real Estate/Hospitality) are the right foundation. Rank expansion categories by **(a) customer LTV, (b) likelihood the owner is non-technical/older-generation (→ outdated site), (c) reliance on local search + booking for new customers, (d) Google review density (needed for the scoring pipeline to work at all).**

| Priority | Category | Why it fits the model |
| :---: | :--- | :--- |
| **High** | Chiropractors, Orthodontists, Med Spas / Cosmetic Dermatology | High per-visit and lifetime value, booking-dependent, frequently outdated WordPress sites |
| **High** | Family Law, Estate Planning, Bankruptcy Attorneys | Emotionally urgent searches → conversion hinges on trust signals your scoring already targets (reviews widget, fast mobile site, live chat) |
| **High** | Plumbers, Electricians, Garage Door, Pest Control | Extremely local-search-dependent, owner-operated, high review count, easy to audit at scale |
| **High** | Financial Advisors / Wealth Management, Mortgage Brokers | High-ticket relationships, strong trust-signal need, often legacy sites |
| **Medium** | Auto Body / Detailing / Tire Shops | High review density, good LTV, but slightly lower urgency than medical/legal |
| **Medium** | Boutique Gyms, Pilates/Yoga Studios | Recurring membership model rewards booking/CRM upgrades heavily — good fit for Package 2 (AI chatbot + scheduling) |
| **Medium** | Senior/Home Care Agencies, Assisted Living | High trust requirement, high LTV per client, but longer sales cycles (B2B2C, sometimes institutional buyers) |
| **Lower priority** | Restaurants, Retail | Lower per-project willingness to pay, high competition from cheap template vendors — deprioritize unless upmarket/fine-dining |

**Rollout order:** add 2–3 "High priority" categories per country per month rather than all at once, so the enrichment + scoring pipeline can be validated on real reply data before scaling further (see Section 6).

---

## 6. Conversion Rate: What Actually Moves Reply → Close

The existing multi-touch sequence (LinkedIn → Email → LinkedIn follow-up → WhatsApp/SMS) is sound. These additions target the *conversion* rate specifically, not just outreach volume:

1. **Speed-to-lead:** Get the diagnostic preview + first outreach touch out within 24–48 hours of a Tier-1 Telegram alert. Freshness matters — the review pattern or business activity you scored is a moving target.
2. **Hyper-local personalization:** Reference the business's actual city, a specific recent review, or a named local competitor that outranks them ("Dr. Smith's clinic two blocks away is getting 3x your online bookings because…"). Generic "I noticed your website is outdated" pitches convert far worse.
3. **Lead with a free diagnostic, not a sales pitch:** Frame first contact as "here's a free 2-minute scorecard of your site" (which you've already built via the Scoring Engine) rather than "I can build you a website." Lowers the reply barrier significantly.
4. **Category-specific social proof:** Once you close 1–2 clients in a niche, build a mini case study ("helped a dental practice in Nashville go from 15 to 40 booking-form leads/month") and use it in the *next* niche+city outreach — proof compounds per vertical.
5. **Risk reversal in pricing:** Consider a structure like "50% deposit only after mockup approval" or a PageSpeed 90+ guarantee — reduces the biggest objection (trust with an unknown freelancer) for non-technical owners.
6. **Local-hours availability for calls:** Even from India, block 2–3 overlapping-hours slots per target region (e.g., early morning IST = evening US Eastern) via Calendly so a "yes" doesn't stall waiting for a meeting slot.
7. **Instrument the funnel, not just the outcome.** Add stage timestamps (`contacted_at`, `first_response_at`, `meeting_booked_at`, `closed_at`) to `outreach_leads` so you can compute reply rate and close rate **per category, per city, per channel** — then kill the bottom-performing segments after ~50 leads and double down on winners. Right now the schema only has a single `outreach_status` field with no stage timing, so you can see *that* a lead responded but not *how fast* or *at what step the funnel is leaking*.

---

## 7. 30 / 60 / 90-Day Rollout

**Days 1–30 — Instrument & Tighten**
- Add enrichment module (owner name, email, LinkedIn) between Discovery and Crawler stages.
- Add Buying Power + Contactability sub-scores to the scoring engine; enforce the 50-review floor.
- Add funnel-stage timestamp columns to `outreach_leads`.
- Re-route Germany outreach to LinkedIn/phone-first sequencing.
- Launch 2–3 new "High priority" categories (start with Chiropractors/Med Spas + Family Law) in 2 existing tier-2 cities per country, ~50 leads/segment, to get real conversion data.

**Days 31–60 — Learn & Expand**
- Pull reply/meeting/close rates by category × city × channel. Kill the bottom ~30% of segments by reply rate.
- Double down on the top 2–3 performing segments with higher volume.
- Pilot Ireland (email-friendly) and UAE (WhatsApp-friendly) as Tier 2 country tests, 30–50 leads each.
- Produce first category-specific case study/proof asset from an early closed client.

**Days 61–90 — Scale What Works**
- Scale outreach volume in the proven winning segments (target 15–20 personalized touches/day as per existing plan, but concentrated on validated categories/cities).
- Formalize a referral ask from closed clients into adjacent categories in the same city.
- Revisit whether outsourcing initial outreach execution (VA) is viable now that segments/messaging are validated — keep scoring/audit/dev work in-house per the original plan's micro-agency roadmap.

---

## 8. Summary of Concrete Changes vs. Current Plan

- **Add** a Buying Power Score and Contactability Score alongside the existing Modernization Need Score → Composite Lead Quality Score.
- **Add** an enrichment stage (Hunter.io/Apollo.io + LinkedIn + BuiltWith/Wappalyzer) before outreach, so contact fields in `outreach_leads` are actually populated.
- **Add** hard floors: ≥50 reviews, at least one enriched contact channel, recent review activity.
- **Re-sequence** Germany toward LinkedIn/phone-first due to stricter cold-email law; keep France/UK/US/AU email-inclusive.
- **Expand** categories in priority order: Chiropractors/Med Spas, Family Law/Estate Planning, Plumbers/Electricians/Pest Control, Financial Advisors — before lower-LTV categories like restaurants/retail.
- **Pilot** Ireland and UAE as the next two country markets, based on outreach-channel fit.
- **Instrument** the outreach funnel with stage timestamps so conversion decisions are data-driven per segment, not assumption-driven.
