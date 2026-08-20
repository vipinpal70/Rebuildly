from config.settings import settings

broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Task rate limiting and concurrency limits
task_annotations = {
    'src.tasks.crawler_tasks.run_site_audit_task': {
        'rate_limit': '15/m'  # Max 15 web audits per minute to prevent IP blocks
    },
    'src.tasks.discovery_tasks.run_discovery_task': {
        'rate_limit': '10/m'
    }
}

# Worker retry & default timeout configurations
task_acks_late = True
worker_prefetch_multiplier = 1
