from typing import Union

from fastapi import APIRouter

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import TaskStatusRequest, Task
from app.utils.parsers import parse_to_schema

api_task_router = APIRouter()


@api_task_router.post("/check_task_status", operation_id="check_task_status", response_model=Union[str, Task])
async def check_task_status(request: TaskStatusRequest) -> Union[str, Task]:
    supabase = SupabaseDB().client

    task: Task = parse_to_schema(Task, supabase.schema("real_estate").table("tasks")
                                 .select("*").eq("task_id", request.task_id).execute().data)

    if not task:
        return "Task not found"

    return task
