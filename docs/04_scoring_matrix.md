# 04. Modernization Scoring Matrix

> **System:** Rebuildly  
> **Document:** Mathematical Scoring Formula & Penalty Breakdown  
> **Author:** Vipin Pal

---

## 1. Overview

The **Modernization Need Score (0 – 100 points)** measures the degree to which a target business is losing potential customers due to an outdated, slow, or broken website.

* **Higher Score (80-100):** Greater opportunity! Business has strong customer demand (4.2+ ★ Google rating) but a terrible website.
* **Lower Score (<40):** Business already has a fast, modern site. Skip outreach.

---

## 2. Weighted Scoring Matrix

| Technical Category | Evaluation Condition | Points Added |
| :--- | :--- | :---: |
| **Mobile UX Failure** | Horizontal overflow, text < 14px, unclickable touch targets | **+15 pts** |
| **SSL / HTTPS Security** | Missing SSL or insecure protocol | **+15 pts** |
| **Page Speed (Mobile)** | Google PageSpeed Performance Score < 50 | **+10 pts** |
| **SEO Metadata** | Missing Meta Title, Description, or `<h1>` tag | **+10 pts** |
| **Schema Markup** | No `LocalBusiness` or `MedicalBusiness` JSON-LD schema | **+10 pts** |
| **Online Booking / Intake** | No interactive booking widget or contact form | **+10 pts** |
| **AI Receptionist / Chat** | No live chat or automated FAQ assistant | **+10 pts** |
| **Google Reviews Display** | No dynamic review social proof widget | **+5 pts** |
| **Legacy Tech Stack** | HTTP/1.1, ancient CMS (WordPress < 5.0), table layout | **+15 pts** |

---

## 3. Tier Classification Thresholds

```text
Score >= 80  ---> 🔥 Tier 1 Priority Lead (Instant Telegram Alert + Custom Preview Generation)
60 - 79      ---> 🟢 Tier 2 Standard Lead (Automated Email & LinkedIn Campaign Queue)
40 - 59      ---> 🟡 Tier 3 Low-Yield Prospect (Hold in Pipeline)
< 40         ---> 🔴 Skip (Modern Website Already Installed)
```
