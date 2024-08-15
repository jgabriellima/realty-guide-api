from typing import Union

from app.core.db.supabase_conn import SupabaseDB
from app.core.setup_logging import setup_logging
from app.schemas.real_estate import Property, Task, TaskStatus
from app.services.assistants.data_checker_assistant import DataCheckerOutput, data_checker
from app.services.task.generic_task_service import GenericTaskService
from app.utils.parsers import parse_to_schema

logger = setup_logging("PropertyTaskService")


class PropertyService(GenericTaskService):
    PROPERTY_TRIGGER_EXTRACT_DATA_TASK_MESSAGE = (
        "Property not found in the database. Please wait a few seconds while we "
        "process this URL and obtain the property details. I'll let you "
        "know when it's done. TaskID: {task_id}")

    PROPERTY_EXISTING_EXTRACT_DATA_TASK_MESSAGE = (
        "There is already a task running to extract the data for this "
        "property. It's running for about {running_time} seconds. Please "
        "wait a few seconds while we process this URL. "
        "I'll let you know when it's done. TaskID: {task_id}")

    def lookup(self, url: str, real_estate_agent_id: Union[str, int] = None, conversation_id=None) -> Union[
        str, Property]:
        supabase = SupabaseDB().client

        res = supabase.schema('real_estate').rpc("get_property_with_metadata",
                                                 params={"p_url": url, "p_slug": None, "p_id": None}).execute()
        logger.info(f"Data::get_property_with_metadata: {res}")

        property: Property = parse_to_schema(Property, res.data)
        if not property:
            task_data = supabase.schema('real_estate').rpc("get_task_by_url",
                                                           params={"url": url,
                                                                   "statuses": ['pending', 'running']}).execute()
            logger.info(f"Data::get_task_by_url: {task_data}")
            task: Task = parse_to_schema(Task, task_data.data)

            task = self.handle_task(task, 'process_property_url', {"url": url,
                                                                   "conversation_id": conversation_id},
                                    real_estate_agent_id,
                                    f"Processing property URL {url} for agent {real_estate_agent_id}")

            if task.status == TaskStatus.PENDING:
                if task.error:
                    return self.trigger_extract_data_message(task.task_id) + f". Note: {task.error}"
                return self.trigger_extract_data_message(task.task_id)

            if task.status == TaskStatus.RUNNING:
                return self.existing_extract_data_message(running_time=task.running_time, task_id=task.task_id)

        return property

    def trigger_extract_data_message(self, task_id: str) -> str:
        return self.PROPERTY_TRIGGER_EXTRACT_DATA_TASK_MESSAGE.format(task_id=task_id)

    def existing_extract_data_message(self, running_time: int, task_id: str) -> str:
        return self.PROPERTY_EXISTING_EXTRACT_DATA_TASK_MESSAGE.format(running_time=running_time, task_id=task_id)

    def enrich_property(self, property_id, real_estate_agent_id, request_details, conversation_id=None) -> Union[str, Property, Task]:
        supabase = SupabaseDB().client

        logger.info(f"Enriching property with ID: {property_id}")
        res = supabase.schema('real_estate').rpc("get_property_with_metadata",
                                                 params={"p_url": None, "p_slug": None, "p_id": property_id}).execute()
        # enrich property
        property: Property = parse_to_schema(Property, res.data)
        if not property:
            raise Exception(f"Property not found with ID: {property_id}")

        logger.info(f"Property found: {property.model_dump_json()}")

        res: DataCheckerOutput = data_checker(request_details, property.model_dump_json())
        if res.contains_the_answer:
            property.assistant_instructions = (
                f"The answer for this query: `{request_details}` can be: `{res.response}`. "
                f"Check if make sense based on the user's query and provide this information to him with your own words. "
                f"If necessary, lookup the property for the complete details. Or call the `query_and_enrich_property_data` "
                f"tool  with a more detailed request_details query.")
            return property.assistant_instructions
        else:
            params = {
                "p_real_estate_agent_id": real_estate_agent_id,
                "p_function_name": "enrich_property_data",
                "p_statuses": ["pending", "running"]
            }
            response = supabase.schema('real_estate').rpc("get_tasks_by_agent_function_status", params=params).execute()
            task: Task = parse_to_schema(Task, response.data)

            if isinstance(task, list):
                task = task[0]

            task = self.handle_task(task, 'enrich_property_data',
                                    {"property_id": property_id,

                                     "request_details": request_details,
                                     "conversation_id": conversation_id},
                                    real_estate_agent_id,
                                    f"Data Enrichment for Property {property.id} for agent {real_estate_agent_id}. Request: {request_details}")

            if task.status == TaskStatus.PENDING:
                return (
                    f"I need to make some researches to get this information. This is a asynchronous task. "
                    f"I'll let you know when done or yu can always call the `check_task_status` tool to check "
                    f"the status and if ready, make this function call again. "
                    f"Data Enrichment task created for Property {property.id}. TaskID: {task.task_id}. "
                    f"Remainder: Check again in about 10 seconds.")
            elif task.status == TaskStatus.RUNNING:
                return (
                    f"I'm already working on this asynchronous task. "
                    f"I'll let you know when done or you can always call the "
                    f"`check_task_status` tool to check the status and if ready, make this function call again. "
                    f"Data Enrichment task is already running for Property {property.id}. TaskID: {task.task_id}. "
                    f"Remainder: Check again in about 10 seconds.")

            return task


if __name__ == '__main__':
    print(PropertyService().enrich_property(
        "gralhaalugueis-com-br-imovel-aluguel-apartamento-2-quartos-itacorubi-florianopolis-sc-125-51m2-rs6000-1569",
        "request_details"))
    #
    # url = "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+3-quartos+canajure+florianopolis+sc+147,13m2+rs10000/1658"
    # url = "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+3-quartos+canajure+florianopolis+sc+147,13m2+rs10000/1658"
    # supabase = SupabaseDB().client
    # res = supabase.schema('real_estate').rpc("get_property_with_metadata",
    #                                          params={"p_url": url, "p_slug": None, "p_id": None}).execute()
    #
    # print(res)
