from celery import Celery
from celery.utils.log import get_logger

from app.core.settings import settings

logger = get_logger(__name__)

logger.info("Starting worker")

celery = Celery(__name__)
celery.conf.broker_url = settings.celery_broker_url
celery.conf.result_backend = settings.celery_result_backend
celery.worker_cancel_long_running_tasks_on_connection_loss = True
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_acks_late = True
celery.autodiscover_tasks(['app'])

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    worker_prefetch_multiplier=1,  # Prefetch only one task at a time
    worker_concurrency=10,  # Number of worker processes/threads
    broker_pool_limit=None,  # Unlimited connections
    broker_heartbeat=10,  # Heartbeat for RabbitMQ
    broker_connection_timeout=30,  # Connection timeout
    task_acks_late=True,  # Acknowledge tasks only after they have been executed
    task_reject_on_worker_lost=True,  # Reject tasks if worker process is lost
    worker_max_tasks_per_child=100,  # Restart workers after they have processed a certain number of tasks
)

celery.conf.update(
    result_expires=300,
)
