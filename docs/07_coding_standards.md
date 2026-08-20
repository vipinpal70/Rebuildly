# 07. Engineering & Coding Standards

> **System:** Opportunity Finder  
> **Document:** Python 3.11+, Type Hinting, Logging, and Git Standards  
> **Author:** Vipin Pal

---

## 1. Python Code Quality Rules

1. **Strict Type Annotations:** Every function signature must contain explicit input parameters and return type annotations:
   ```python
   async def calculate_score(audit_data: Dict[str, Any]) -> int:
       ...
   ```
2. **Pydantic V2 Data Models:** All raw inputs/outputs must be parsed into Pydantic models. Avoid unvalidated bare dictionaries.
3. **Async First:** All IO-bound operations (HTTP requests, database access, Playwright headless browser rendering) MUST use `async`/`await`.
4. **Structured Logging:** Use `loguru` for structured logging. Never use `print()` statements in production code.
   ```python
   from loguru import logger
   
   logger.info("Auditing site", extra={"url": url, "place_id": place_id})
   ```

---

## 2. Error Handling & Retries

1. **Custom Exceptions:** Raise domain-specific exceptions inheriting from a base `OpportunityFinderException`.
2. **Exponential Backoff:** Use `@retry` from `tenacity` on transient API calls (e.g. Google Places API, PageSpeed API).

---

## 3. Git & Documentation Workflow

1. **Commit Messages:** Follow Conventional Commits format (`feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`).
2. **Documentation Maintenance:** Every new feature or architectural module must have a corresponding `.md` document in the `/docs` directory explaining its core logic and agent workflows.
