"""Real-time audit log buffer and event memory store.

Tracks structured audit events across discovery, site crawling, modernization scoring,
LLM content synthesis, and website generation."""
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class AuditLogManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuditLogManager, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.max_logs = 1000
            cls._instance._seed_initial_logs()
        return cls._instance

    def _seed_initial_logs(self):
        """Seed initial realistic audit logs for demonstration if empty."""
        now = datetime.utcnow().isoformat() + "Z"
        sample_logs = [
            {
                "id": "log-001",
                "timestamp": now,
                "job_id": "system-init",
                "level": "SUCCESS",
                "stage": "SYSTEM",
                "business_name": "Rebuildly Engine",
                "message": "PostgreSQL & Redis Audit Engine initialized successfully.",
                "details": {"status": "healthy", "redis_port": 6379, "postgres_port": 5432}
            },
            {
                "id": "log-002",
                "timestamp": now,
                "job_id": "job-initial-audit",
                "level": "INFO",
                "stage": "DISCOVERY",
                "business_name": "Clarity Dental Clinic",
                "message": "Discovered business lead via UK Dental Directory (Manchester).",
                "details": {"rating": 4.8, "reviews": 124, "city": "Manchester"}
            },
            {
                "id": "log-003",
                "timestamp": now,
                "job_id": "job-initial-audit",
                "level": "WARNING",
                "stage": "AUDITOR",
                "business_name": "Clarity Dental Clinic",
                "message": "Technical Audit Completed: Missing Schema.org markup, PageSpeed: 45/100, SSL: Active.",
                "details": {"modernization_score": 78, "tier": "HIGH_PRIORITY_RENEWAL"}
            },
            {
                "id": "log-004",
                "timestamp": now,
                "job_id": "job-initial-audit",
                "level": "SUCCESS",
                "stage": "GENERATOR",
                "business_name": "Clarity Dental Clinic",
                "message": "Generated dedicated client route /sites/clarity-dental-clinic (CYBER_GLOW_TECH).",
                "details": {"preview_url": "http://localhost:3009/sites/clarity-dental-clinic"}
            }
        ]
        self.logs.extend(sample_logs)

    def log_event(
        self,
        level: str,
        stage: str,
        message: str,
        business_name: Optional[str] = None,
        job_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record an audit log entry."""
        entry = {
            "id": f"log-{int(time.time() * 1000)}-{len(self.logs)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "job_id": job_id or "system",
            "level": level.upper(),
            "stage": stage.upper(),
            "business_name": business_name or "Global System",
            "message": message,
            "details": details or {}
        }
        self.logs.insert(0, entry)
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[: self.max_logs]

        # Sync to Redis Task Queue & Logs Dashboard
        try:
            from src.storage.queue import redis_queue
            redis_queue.push_audit_log(entry)
        except Exception:
            pass

        return entry

    def get_logs(
        self,
        limit: int = 100,
        level: Optional[str] = None,
        stage: Optional[str] = None,
        job_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs matching filters."""
        result = self.logs
        if level and level != "ALL":
            result = [l for l in result if l["level"] == level.upper()]
        if stage and stage != "ALL":
            result = [l for l in result if l["stage"] == stage.upper()]
        if job_id:
            result = [l for l in result if l["job_id"] == job_id]
        if search:
            q = search.lower()
            result = [
                l for l in result
                if q in l["message"].lower() or q in l["business_name"].lower() or q in l["stage"].lower()
            ]
        return result[:limit]

audit_logger = AuditLogManager()
