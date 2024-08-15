from datetime import datetime, timezone
from typing import Union, Dict, Any, TypeVar

from dateutil.parser import parse as parse_date

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import Task, TaskStatus
from app.core.setup_logging import setup_logging
from app.tasks.worker import celery

logger = setup_logging("GenericTaskService")

T = TypeVar('T')


class GenericTaskService:
    TASK_CANCEL_TIME_LIMIT = 180  # 3 minutes

    def handle_task(self, task: Task, function_name: str, input_data: Dict[str, Any], agent_id: int,
                    description: str) -> Union[str, Task]:
        if task:
            datetime_now = datetime.now(timezone.utc)
            if task.created_at.tzinfo is None:
                task.created_at = task.created_at.replace(tzinfo=timezone.utc)
            running_time = (datetime_now - task.created_at).seconds

            if running_time > self.TASK_CANCEL_TIME_LIMIT:
                task = self.cancel_task(task.task_id, "Running for too long", function_name, input_data, agent_id,
                                        description)
                task.error = "Previous Task cancelled due to running for too long"
                return task

            logger.info(
                f"Task running for {running_time} seconds. Date now: {datetime_now} - Created at: {task.created_at}")
            return task

        task = self.create_task(function_name, input_data, agent_id, description)
        logger.info(f"Task created: {task}")
        return task

    def cancel_task(self, task_id: str, reason: str, function_name: str, input_data: Dict[str, Any], agent_id: int,
                    description: str) -> Task:
        supabase = SupabaseDB().client

        # Update the task status to 'cancelled' and log the reason for cancellation
        supabase.schema('real_estate').table('tasks').update({
            "status": "cancelled",
            "error": reason,
            "updated_at": "now()"
        }).eq("task_id", task_id).execute()
        logger.info(f"Task cancelled: {task_id} due to {reason}")

        # Check if the task should be retried
        task_data = supabase.schema('real_estate').from_("tasks").select("retry").eq("task_id", task_id).execute().data
        if task_data and task_data[0]['retry']:
            logger.info(f"Retrying task: {task_id}")
            return self.create_task(function_name, input_data, agent_id, description)

    def create_task(self, function_name: str, input_data: Dict[str, Any], agent_id: int, description: str) -> Task:
        supabase = SupabaseDB().client
        task = celery.send_task(function_name, args=[v for k, v in input_data.items()])
        task_id = task.id

        new_task = {
            "task_id": task_id,
            "function_name": function_name,
            "agent_id": agent_id,
            "description": description,
            "status": TaskStatus.PENDING,
            "input_data": input_data,
            "created_at": str(datetime.now(timezone.utc)),
            "updated_at": str(datetime.now(timezone.utc)),
            "retry": True  # Or set based on some logic
        }

        supabase.schema('real_estate').from_("tasks").insert(new_task).execute()
        logger.info(f"Task created: {str(new_task['created_at'])}")

        new_task['created_at'] = parse_date(new_task['created_at'])
        new_task['updated_at'] = parse_date(new_task['updated_at'])

        return Task(**new_task)

    def cancel_task_message(self, task_id: str, reason: str) -> str:
        return f"Task cancelled: {task_id} due to {reason}"

    def trigger_extract_data_message(self, task_id: str) -> str:
        return f"Task not found in the database. TaskID: {task_id}"

    def existing_extract_data_message(self, running_time: int, task_id: str) -> str:
        return f"Task running for {running_time} seconds. TaskID: {task_id}"
