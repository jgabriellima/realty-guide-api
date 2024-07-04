import time

from app.setup_logging import setup_logging
from app.worker import celery

logger = setup_logging(celery=True)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 2)
    logger.info(f"Task {task_type} completed")

    return True
