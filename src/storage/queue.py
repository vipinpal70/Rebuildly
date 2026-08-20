"""Redis Task Queue & Job State Manager.

Pushes background lead generation jobs, queue lists, job status hashes,
and audit logs directly into Redis so they are visible in Redis Commander,
BullMQ viewers, and RedisInsight dashboards."""
import json
import time
from typing import Dict, Any, List, Optional
import redis

from config.settings import settings
from src.utils.logger import logger

def get_sync_redis_client() -> Optional[redis.Redis]:
    try:
        return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}")
        return None

class RedisQueueManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisQueueManager, cls).__new__(cls)
            cls._instance.client = get_sync_redis_client()
        return cls._instance

    def enqueue_job(self, job_id: str, category: str, cities: List[str], max_per_city: int) -> Dict[str, Any]:
        """Push a new lead generation job into the Redis task queue."""
        job_data = {
            "job_id": job_id,
            "category": category,
            "cities": cities or ["Manchester", "Birmingham", "Leeds"],
            "max_per_city": max_per_city,
            "status": "queued",
            "progress": "0%",
            "message": f"Queued lead discovery for {category}",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        r = self.client or get_sync_redis_client()
        if r:
            try:
                # 1. Push to Redis queue list
                r.rpush("queue:lead_generation", json.dumps(job_data))
                # 2. Save Hash for instant job lookup in Redis
                r.hset(f"job:{job_id}", mapping={k: str(v) for k, v in job_data.items()})
                # 3. Add to set of all active job IDs
                r.sadd("jobs:active", job_id)
                logger.info(f"Pushed job {job_id} into Redis queue 'queue:lead_generation'")
            except Exception as e:
                logger.warning(f"Failed to push job {job_id} to Redis: {e}")

        return job_data

    def update_job_status(self, job_id: str, status: str, message: str, progress: str = "100%") -> None:
        """Update job status in Redis hash and queue state."""
        r = self.client or get_sync_redis_client()
        if not r:
            return
        try:
            updates = {
                "status": status,
                "message": message,
                "progress": progress,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            r.hset(f"job:{job_id}", mapping=updates)

            if status in ("completed", "failed"):
                r.srem("jobs:active", job_id)
                r.sadd(f"jobs:{status}", job_id)
        except Exception as e:
            logger.warning(f"Failed to update job status in Redis for {job_id}: {e}")

    def push_audit_log(self, log_entry: Dict[str, Any]) -> None:
        """Push an audit log event into Redis list 'audit:logs'."""
        r = self.client or get_sync_redis_client()
        if not r:
            return
        try:
            raw = json.dumps(log_entry)
            r.lpush("audit:logs:list", raw)
            r.ltrim("audit:logs:list", 0, 500) # Keep latest 500 logs
            r.set(f"audit:event:{log_entry['id']}", raw, ex=86400) # 24hr TTL
        except Exception as e:
            logger.warning(f"Failed to push audit log to Redis: {e}")

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch job data from Redis hash."""
        r = self.client or get_sync_redis_client()
        if not r:
            return None
        try:
            data = r.hgetall(f"job:{job_id}")
            return data if data else None
        except Exception:
            return None

redis_queue = RedisQueueManager()
