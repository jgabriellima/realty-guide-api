from typing import Union

from fastapi import APIRouter

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import TaskStatusRequest, Task, TaskStatus
from app.utils.parsers import parse_to_schema

api_task_router = APIRouter()


@api_task_router.post("/check_task_status", operation_id="check_task_status", response_model=Union[str, Task])
async def check_task_status(request: TaskStatusRequest) -> Union[str, Task]:
    """
    Check the status of a task

    :param request: TaskStatusRequest
    :return: Union[str, Task]
    """
    supabase = SupabaseDB().client

    task: Task = parse_to_schema(Task, supabase.schema("real_estate").table("tasks")
                                 .select("*").eq("task_id", request.task_id).execute().data)

    if not task:
        return "Task not found"

    if task.status == TaskStatus.COMPLETED:
        if task.function_name in ["process_property_url"]:
            return "Property processed successfully. Call the `property_lookup` tool again to the details"
        elif task.function_name in ["enrich_property_data"]:
            return "Query and Enrichment completed successfully. Call the `query_and_enrich_property_data` tool again to get the requested details"

    return task
