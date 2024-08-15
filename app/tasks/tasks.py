import time

import requests

from app.core.settings import settings
from app.core.setup_logging import setup_logging
from app.schemas.real_estate import Property, RealEstateAgent
from app.services.property.property_data import save_property, save_metadata
from app.services.property.property_tasks_service import PropertyLookup
from app.tasks.worker import celery
from app.utils.parsers import parse_to_schema

logger = setup_logging(celery=True)

from celery import Task as CeleryTask
from app.core.db.supabase_conn import SupabaseDB
from app.core.setup_logging import setup_logging

logger = setup_logging("BaseTaskWithUpdate")


def call_jambu_integrator_task_done(conversation_id, task_id):
    """
    Call the JambuAI service to notify that the task is done
    """
    logger.info(f"Calling JambuAI service for task {task_id} completed. Conversation ID: {conversation_id}")
    res = requests.post(
        f"{settings.jambu_integrator_url}/v1/whatsapp/task_done",
        json={"conversation_id": conversation_id,
              "task_id": task_id},
    )

    return res.text


class BaseTaskWithUpdate(CeleryTask):
    def apply_async(self, *args, **kwargs):
        try:
            # Update task status to running
            supabase = SupabaseDB().client
            task_id = kwargs['task_id']
            supabase.schema("real_estate").table("tasks").update({
                "status": "running",
                "updated_at": "now()"
            }).eq("task_id", task_id).execute()
            logger.info(f"Task {task_id} status updated to running")
            return super().apply_async(*args, **kwargs)
        except Exception as e:
            logger.info(f"Error updating task status:apply_async {e}")

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
            "error": f"{str(exc)}. Aks if the user wants to retry"
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


@celery.task(name="process_property_url", bind=True)
def process_property_url(self, url: str, conversation_id: str):
    """
    Process the property URL and save the property data
    """
    task_id = self.request.id
    logger.info(f"Started task {task_id} for URL: {url}")
    property: Property = PropertyLookup().process_url(url)
    logger.info(f"Property data: {property}")
    save_property(property)

    logger.info(f"Task {task_id} completed")

    try:
        call_jambu_integrator_task_done(conversation_id, task_id)
    except:
        logger.error(f"Error calling JambuAI service for task {task_id} completed. Conversation ID: {conversation_id}")

    return True


@celery.task(name="enrich_property_data", bind=True)
def enrich_property_data(self, property_id, request_details, conversation_id):
    """
    Enrich the property data with the request details
    """
    supabase = SupabaseDB().client
    res = supabase.schema('real_estate').rpc("get_property_with_metadata",
                                             params={"p_url": None,
                                                     "p_slug": None,
                                                     "p_id": property_id}).execute()

    # enrich property
    property: Property = parse_to_schema(Property, res.data)
    logger.info(f"Enriching property: {property}")
    result: Property = PropertyLookup().enrich_property_metadata(property, request_details)

    if not result:
        logger.info(f"Property not enriched: {property}")

    logger.info(f"Enriched property: {result}")
    save_metadata(property.id, result.property_metadata)

    try:
        call_jambu_integrator_task_done(conversation_id, "enrich_property_data")
    except:
        logger.error(f"Error calling JambuAI service for task enrich_property_data completed. Conversation ID: {conversation_id}")


    return True


@celery.task(name="trigger_scheduled_remainder", base=BaseTaskWithUpdate, bind=True)
def trigger_scheduled_remainder(self, real_estate_agent_id, remainder_description):
    """
    Trigger a scheduled remainder for a real estate agent
    """
    supabase = SupabaseDB().client
    agent_data = supabase.schema('real_estate').rpc("get_agent_with_metadata",
                                                    params={"p_whatsapp": None, "p_id": real_estate_agent_id}).execute()

    agent: RealEstateAgent = parse_to_schema(RealEstateAgent, agent_data.data)
    # call JambuAI Service passing the agent.whatsapp and the message
    message = f"This is a scheduled remainder: {remainder_description}"
    logger.info(f"Sending scheduled remainder to agent: {agent.whatsapp} - {message}")

    return True
