# Phase 1 Implementation Plan: Discovery & Audit Engine

> **Document Purpose:** Complete technical blueprint for Phase 1 execution, project directory setup, coding standards, and documentation architecture for the Opportunity Finder system.

---

## 1. Executive Summary & Scope

Phase 1 focuses on building the **automated core engine** that discovers high-ticket small business leads (UK, USA, Australia, Germany, France), crawls and audits their current websites across mobile UX, speed, technical SEO, and schema markup, calculates a Modernization Need Score (0–100), and sends real-time alerts for top-tier opportunities.

---

## 📁 2. Project Directory & Workspace Architecture

We follow a modular, production-ready Python project structure.

```text
Opportunity Finder/
├── config/                     # Application configuration & env settings
│   ├── __init__.py
│   └── settings.py             # Pydantic BaseSettings for env loading
├── docs/                       # Comprehensive System Documentation
│   ├── 01_architecture_overview.md
│   ├── 02_discovery_engine.md
│   ├── 03_crawler_and_auditor.md
│   ├── 04_scoring_matrix.md
│   ├── 05_database_and_queue.md
│   ├── 06_outreach_sequence.md
│   └── 07_coding_standards.md
├── src/                        # Core Application Source Code
│   ├── __init__.py
│   ├── discovery/              # Module 1: Lead Discovery (Google Places API / Maps)
│   │   ├── __init__.py
│   │   ├── places_client.py    # Official Places API Wrapper
│   │   ├── maps_scraper.py     # Fallback Directory Scraper
│   │   └── models.py           # Pydantic Lead & Place Data Schemas
│   ├── crawler/                # Module 2: Web Crawler & Site Auditor
│   │   ├── __init__.py
│   │   ├── mobile_auditor.py   # Playwright Mobile UX Inspector
│   │   ├── pagespeed_client.py # Google PageSpeed Insights API Client
│   │   ├── seo_parser.py       # BS4 SEO & Schema JSON-LD Extractor
│   │   └── site_crawler.py     # Main Crawler Orchestrator
│   ├── scorer/                 # Module 3: Lead Scoring Engine
│   │   ├── __init__.py
│   │   ├── scoring_matrix.py   # Score Matrix Calculation (0-100)
│   │   └── evaluator.py        # Lead Tier Classifier
│   ├── storage/                # Module 4: Database & Cache Layer
│   │   ├── __init__.py
│   │   ├── db_session.py       # Async SQLAlchemy Session Management
│   │   ├── models.py           # ORM Models (Businesses, Audits, Leads)
│   │   └── repository.py       # Data Access Layer (CRUD)
│   ├── notifications/          # Module 5: Real-time Alerting
│   │   ├── __init__.py
│   │   └── telegram_bot.py     # Instant Telegram Alert Bot
│   └── utils/                  # Shared Utility Helpers
│       ├── __init__.py
│       ├── logger.py           # Structured Loguru / Structlog logger
│       └── proxy_manager.py    # IP Rotation & Rate Limiter
├── tests/                      # Automated Unit & Integration Tests
│   ├── test_discovery.py
│   ├── test_crawler.py
│   └── test_scorer.py
├── scripts/                    # CLI Operations & Run Scripts
│   ├── run_discovery.py
│   └── run_audit_pipeline.py
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions
├── docker-compose.yml          # Local PostgreSQL & Redis services
├── Dockerfile                  # Containerization specification
├── Idea-plan.md                # Strategic Master Business Plan
├── roadmap.md                  # Project Engineering Roadmap
├── risk.md                     # Conversion & High-Yield Strategy Guide
├── phase-1-implementation-plan.md # This document
└── requirements.txt            # Python dependencies
```

---

## 🛠️ 3. Industry-Standard Coding & Engineering Principles

### 3.1 Python Standards (PEP 8 + Strict Typing)
- **Python Version:** 3.11+
- **Type Annotations:** 100% type coverage using Python `typing` module (`str`, `int`, `Optional`, `Dict`, `List`).
- **Data Validation:** Use **Pydantic V2** models for all API request/response parsing and internal data transfer objects (DTOs).
- **Asynchronous Execution:** Heavy use of `asyncio`, `aiohttp`, and `playwright.async_api` to ensure non-blocking concurrent crawls.

### 3.2 Error Handling & Logging
- **Custom Exception Hierarchy:** Define domain-specific exceptions (`DiscoveryAPIError`, `SiteUnreachableError`, `AuditTimeoutError`).
- **Structured Logging:** Use `loguru` or `structlog` outputting JSON in production, with contextual metadata (`business_name`, `place_id`, `audit_duration_ms`).
- **Graceful Retries:** Implement exponential backoff for network requests using `tenacity`.

### 3.3 Security & Environment Management
- No API keys, credentials, or DB URIs hardcoded in source files.
- Load configurations dynamically via `pydantic-settings` from `.env`.

---

## 📚 4. Documentation Architecture (`docs/` Folder Plan)

To maintain clean documentation, each sub-system has a dedicated `.md` file inside the `/docs` directory:

| Document File | Purpose & Core Content |
| :--- | :--- |
| **`docs/01_architecture_overview.md`** | High-level data flow, component interactions, and system topology. |
| **`docs/02_discovery_engine.md`** | Deep dive into Google Places API queries, city/category matrices, rate limits, and raw data extraction. |
| **`docs/03_crawler_and_auditor.md`** | Technical guide to Playwright mobile emulation, PageSpeed API metrics, BS4 parsing, and DOM checks. |
| **`docs/04_scoring_matrix.md`** | Exact mathematical weightage, point calculations (0-100), penalty definitions, and classification thresholds. |
| **`docs/05_database_and_queue.md`** | PostgreSQL ERD diagrams, SQLAlchemy models, migration workflows, and Redis/Celery queue setup. |
| **`docs/06_outreach_sequence.md`** | Detailed multi-channel outreach guidelines (LinkedIn, Cold Email, WhatsApp permission strategy). |
| **`docs/07_coding_standards.md`** | Detailed developer guidelines: linting (`ruff`), formatting (`black`), testing (`pytest`), and git commit rules. |

---

## 🚀 5. Phase 1 Implementation Workflow (Step-by-Step)

### Step 1: Environment & Virtualenv Setup
Initialize virtual environment and install core dependencies.

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Core dependencies setup
pip install fastapi uvicorn pydantic pydantic-settings asyncio aiohttp playwright beautifulsoup4 loguru sqlalchemy asyncpg redis celery tenacity python-dotenv
playwright install chromium
```

### Step 2: Configuration & Environment Setup (`config/settings.py`)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Opportunity Finder Engine"
    ENVIRONMENT: str = "development"
    
    # API Keys
    GOOGLE_PLACES_API_KEY: str
    PAGESPEED_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    
    # Database URIs
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/opportunity_finder"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Step 3: Discovery Module Implementation (`src/discovery/`)
- Implement `places_client.py` using `aiohttp` to fetch business listings based on parameters: `category`, `city`, `country`.
- Store raw API responses into Pydantic model `PlaceLead`.

### Step 4: Auditor Module Implementation (`src/crawler/`)
- Implement `mobile_auditor.py` using `playwright.async_api`:
  - Set viewport to iPhone 14 dimensions (`390 x 844`).
  - Capture screenshot of home page.
  - Test for horizontal overflow (`document.documentElement.scrollWidth > window.innerWidth`).
- Implement `pagespeed_client.py`: Query Google PageSpeed API for mobile performance score.
- Implement `seo_parser.py`: Parse site HTML using `BeautifulSoup4` for Title, Meta Description, H1, and JSON-LD Schema (`LocalBusiness`).

### Step 5: Scoring Engine (`src/scorer/`)
- Implement `scoring_matrix.py`: Compute score based on:
  - Mobile UX Failure: **+15 pts**
  - PageSpeed < 50: **+10 pts**
  - Missing SSL: **+15 pts**
  - Missing SEO Metadata: **+10 pts**
  - Missing Schema Markup: **+10 pts**
  - Missing Online Booking / Form: **+10 pts**
  - Outdated HTML Stack: **+15 pts**

### Step 6: Real-Time Telegram Notification (`src/notifications/`)
- When `modernization_score >= 80`, dispatch push alert to Vipin's Telegram containing:
  - Business Name, Location, Phone Number
  - Google Star Rating & Review Count
  - Calculated Score & Main 3 Technical Failures
  - Website URL

---

## 🤖 6. Agent Core Logic & Workflow Explanation

The system operates as an **Autonomous Technical Agent Pipeline**:

```text
[Discovery Agent] ➔ Extracts Place ID, Name, Phone, Website, Star Rating
                         │
                         ▼
[Auditor Agent]   ➔ Performs Headless Playwright Mobile Inspection + PageSpeed Fetch
                         │
                         ▼
[Scoring Agent]   ➔ Applies Weighted Penalty Matrix (0-100 Score)
                         │
                         ▼
[Alert Agent]     ➔ If Score > 80: Sends Structured Alert via Telegram & Enqueues for Preview Generation
```

1. **Discovery Agent:** Acts as the data gathering bot. It searches targeted geographic regions (e.g., Tier-2 cities in UK/US) and filters out low-trust businesses (only keeps 4.2+ ★ ratings).
2. **Auditor Agent:** Acts as an automated QA engineer. It renders the target website inside a headless browser, executes JavaScript DOM queries to test mobile layout bugs, calls PageSpeed APIs, and inspects SEO metadata.
3. **Scoring Agent:** Acts as a data analyst. It evaluates raw audit logs against a weighted scoring matrix to output a single numeric priority metric.
4. **Alert Agent:** Acts as a real-time notification trigger. When high-yielding leads are evaluated, it immediately formats and dispatches actionable alerts to the user's phone.

---
*Maintained by Vipin Pal | Phase 1 Implementation Specification*
