from celery import Celery
from config.settings import settings

celery_app = Celery("rebuildly")
celery_app.config_from_object("config.celery_config")

# Autodiscover tasks across src modules
celery_app.autodiscover_tasks([
    "src.tasks.discovery_tasks",
    "src.tasks.crawler_tasks",
    "src.tasks.pipeline_tasks"
])
