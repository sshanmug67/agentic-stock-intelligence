"""
Celery application configuration
"""
from celery import Celery
from .config.settings import settings

# Create Celery app
celery_app = Celery(
    "stock_intelligence",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,  # Take one task at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
)


# Auto-discover tasks from intents package
# This will find backend/graph/intents/tasks.py and import it
celery_app.autodiscover_tasks(['backend.graph.intents'])

# Optional: Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Example: cleanup old executions every hour
    # 'cleanup-executions': {
    #     'task': 'cleanup_old_executions',
    #     'schedule': 3600.0,
    # },
}

if __name__ == "__main__":
    celery_app.start()