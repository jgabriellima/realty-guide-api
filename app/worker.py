from celery import Celery
from celery.utils.log import get_logger

from app.core.settings import settings

logger = get_logger(__name__)

logger.info("Starting worker")

celery = Celery(__name__)
celery.conf.broker_url = settings.celery_broker_url
celery.conf.result_backend = settings.celery_result_backend
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_acks_late = True
celery.autodiscover_tasks(['app'])

celery.conf.update(
    result_expires=300,
)
