# PostgreSQL Database Schema & Migration Architecture

> **System Layer:** Storage & Relational Database  
> **RDBMS Engine:** PostgreSQL 15+  
> **ORM & Driver:** SQLAlchemy (AsyncIO) + asyncpg  
> **Migration Tool:** Alembic  

---

## 📐 Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    BUSINESSES ||--o{ AUDITS : "has audit history"
    BUSINESSES ||--o| OUTREACH_LEADS : "tracks outreach status"

    BUSINESSES {
        string id PK
        string place_id UK
        string name
        string category
        string city
        string country
        string phone
        string website
        float google_rating
        int review_count
        datetime created_at
    }

    AUDITS {
        string id PK
        string business_id FK
        boolean has_ssl
        boolean is_mobile_responsive
        boolean has_horizontal_overflow
        int pagespeed_score
        boolean has_meta_title
        boolean has_meta_description
        boolean has_h1_tag
        boolean has_schema_markup
        boolean has_online_booking
        boolean has_ai_chatbot
        int modernization_score
        string tier
        json score_breakdown
        datetime audited_at
    }

    OUTREACH_LEADS {
        string id PK
        string business_id FK
        string contact_name
        string contact_email
        string linkedin_url
        string preview_subdomain_url
        string outreach_status
        datetime last_contacted_at
        text notes
        datetime created_at
    }
```

---

## 🗄️ Tables Breakdown

### 1. `businesses`
Stores raw Google Places business directory information.
- `place_id` (Unique Index): Prevents duplicate scraping of the same local business.

### 2. `audits`
Stores detailed mobile UX, PageSpeed, SEO, schema, and modernization scoring results.
- `business_id` (Foreign Key -> `businesses.id`, `ON DELETE CASCADE`).

### 3. `outreach_leads`
Tracks outbound sales progress, contact information, generated website preview links, and notes.
- `outreach_status` Options: `NEW`, `LINKEDIN_SENT`, `EMAIL_SENT`, `WA_SENT`, `RESPONDED`, `CLOSED`.
