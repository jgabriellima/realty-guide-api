import time

from app.schemas.real_estate import Property
from app.services.property_tasks_service import PropertyLookup
from app.services.save_property import save_property
from app.setup_logging import setup_logging
from app.worker import celery

logger = setup_logging(celery=True)

from celery import Task as CeleryTask
from app.core.db.supabase_conn import SupabaseDB
from app.setup_logging import setup_logging

logger = setup_logging("BaseTaskWithUpdate")


class BaseTaskWithUpdate(CeleryTask):
    def apply_async(self, *args, **kwargs):
        # Update task status to running
        supabase = SupabaseDB().client
        task_id = kwargs['task_id']
        supabase.schema("real_estate").table("tasks").update({
            "status": "running",
            "updated_at": "now()"
        }).eq("task_id", task_id).execute()
        logger.info(f"Task {task_id} status updated to running")
        return super().apply_async(*args, **kwargs)

    def on_success(self, retval, task_id, args, kwargs):
        supabase = SupabaseDB().client
        supabase.schema("real_estate").table("tasks").update({
            "status": "completed",
            "updated_at": "now()"
        }).eq("task_id", task_id).execute()
        logger.info(f"Task {task_id} status updated to completed")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        supabase = SupabaseDB().client
        supabase.schema("real_estate").table("tasks").update({
            "status": "failed",
            "updated_at": "now()",
            "error": str(exc)
        }).eq("task_id", task_id).execute()
        logger.error(f"Task {task_id} status updated to failed: {exc}")


@celery.task(name="create_task")
def create_task(task_type):
    """
    Create a task in the database and send it to the celery worker
    """
    time.sleep(int(task_type) * 2)
    logger.info(f"Task {task_type} completed")

    return True


@celery.task(name="process_property_url", base=BaseTaskWithUpdate, bind=True)
def process_property_url(self, url: str):
    task_id = self.request.id
    logger.info(f"Started task {task_id} for URL: {url}")
    time.sleep(5)

    property: Property = PropertyLookup().process_url(url)
    logger.info(f"Property data: {property}")
    save_property(property)

    logger.info(f"Task {task_id} completed")

    return True
