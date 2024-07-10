from datetime import datetime, timezone
from typing import Union, List, TypeVar, Dict, Any, Type

from dotenv import load_dotenv

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import Property, Task
from app.setup_logging import setup_logging
from app.worker import celery

load_dotenv()

T = TypeVar('T')
logger = setup_logging("PropertyService")


def parse_to_schema(schema: Type[T], data: List[dict]) -> Union[T, List[T], None]:
    logger.info(f"parse_to_schema:Data:: {data}")
    parsed_data = [schema(**item) for item in data]
    if len(parsed_data) == 1:
        return parsed_data[0]
    elif len(parsed_data) > 1:
        return parsed_data
    else:
        return None


class PropertyService:
    PROPERTY_TRIGGER_EXTRACT_DATA_TASK_MESSAGE = (
        "Property not found in the database. Please wait a few seconds while we "
        "will process this URL and obtain the property details. I'll let you "
        "know when it's done. TaskID: {task_id}")

    PROPERTY_EXISTING_EXTRACT_DATA_TASK_MESSAGE = (
        "There is already a task running to extract the data for this "
        "property. Its running for about {running_time} seconds. Please "
        "wait a few seconds while we will process this URL."
        "I'll let you know when it's done. TaskID: {task_id}")

    def lookup(self, url: str, real_estate_agent_id: Union[str, int] = None) -> Union[str, Property]:
        supabase = SupabaseDB().client

        res = supabase.schema('real_estate').rpc("get_property_with_metadata", params={"property_url": url}).execute()
        logger.info(f"Data::get_property_with_metadata: {res}")

        property: Property = parse_to_schema(Property, res.data)
        if not property:
            # check if there is a task already running - table tasks
            # , 'completed', 'failed', 'cancelled'
            data = supabase.rpc("get_task_by_url", params={"url": url, "statuses": ['pending', 'running']}).execute()
            logger.info(f"Data::get_task_by_url: {data}")
            task: Task = parse_to_schema(Task, data.data)
            if task:
                datetime_now = datetime.now(timezone.utc)
                if task.created_at.tzinfo is None:
                    task.created_at = task.created_at.replace(tzinfo=timezone.utc)
                running_time = (datetime_now - task.created_at).seconds

                # check if is more than 5min and the call self.task_cancellation
                if running_time > 300:
                    supabase.schema('real_estate').table('tasks').update({
                        "status": "cancelled",
                        "updated_at": "now()"
                    }).eq("task_id", task.task_id).execute()
                    logger.info(f"Task cancelled: {task.task_id}")

                    return self.PROPERTY_TRIGGER_EXTRACT_DATA_TASK_MESSAGE.format(task_id=task.task_id)

                logger.info(f"Task running for {running_time} seconds. Date now: {datetime_now} - Created at: {task.created_at}")
                return self.PROPERTY_EXISTING_EXTRACT_DATA_TASK_MESSAGE.format(running_time=running_time,
                                                                               task_id=task.task_id)
            # if not create a new task and return the task id
            task = self.create_task('process_property_url',
                                    {"url": url},
                                    agent_id=real_estate_agent_id,
                                    description=f"Processing property URL {url} for agent {real_estate_agent_id}")
            logger.info(f"Task created: {task}")
            return self.PROPERTY_TRIGGER_EXTRACT_DATA_TASK_MESSAGE.format(task_id=task.task_id)
        else:
            return property

    def create_task(self, function_name: str, input_data: Dict[str, Any], agent_id: int, description: str) -> Task:
        """
        Create a task in the database and send it to the celery worker

        :param function_name: The name of the function to be executed
        :param description: A description of the task
        :param agent_id: The id of the agent that created the task

        :return: The task id
        """
        supabase = SupabaseDB().client
        task = celery.send_task(function_name, args=[input_data])
        task_id = task.id

        new_task = {
            "task_id": task_id,
            "function_name": function_name,
            "agent_id": agent_id,
            "description": description,
            "status": "pending",
            "input_data": input_data,
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now()),
        }

        supabase.schema('real_estate').from_("tasks").insert(new_task).execute()

        new_task['created_at'] = datetime.strptime(new_task['created_at'], "%Y-%m-%d %H:%M:%S.%f")
        new_task['updated_at'] = datetime.strptime(new_task['updated_at'], "%Y-%m-%d %H:%M:%S.%f")

        return Task(**new_task)


if __name__ == '__main__':
    url = "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569"
    # service = PropertyDataService(debug=True)
    # result: Property = service.process_url(url)
    # print(result.model_dump_json())

    property = PropertyService().lookup(url)
    print(property)
