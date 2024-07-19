import json
from datetime import datetime

from app.core.db.supabase_conn import SupabaseDB

from langsmith import traceable
from marvin.types import ChatResponse
from pydantic import BaseModel, Field

from app.services.assistants.prompts.system_prompts import DATA_CHECKER
from app.utils.custom_marvin.custom_marvin_extractor import custom_data_extractor



class DataCheckerOutput(BaseModel):
    """
    Data Checker Output
    """
    query_instructions: str
    response: str
    contains_the_answer: bool = Field(..., description="Only check as `true` if the user's query is full answered, "
                                                       "for all the other scenarios, it should be `false`.")


@traceable(run_type="llm")
def data_checker(query_and_context, property_data: dict):
    results: ChatResponse = custom_data_extractor(
        query_and_context,
        target=DataCheckerOutput,
        instructions=DATA_CHECKER.format(datetime_now=str(datetime.now()),
                                         property_data=json.dumps(property_data)),
        model_kwargs={
            "model": "gpt-4o",
            "temperature": 0.0,
        }
    )

    target_data = [extracted_data for extracted_data in results.tool_outputs[0]]
    return target_data[0]


if __name__ == '__main__':
    query = "academias próximas"
    supabase = SupabaseDB().client
    json_data = supabase.schema('real_estate').rpc("get_property_with_metadata", params={
        "p_url": None,
        "p_slug": None,
        "p_id": 15
    }).execute().data

    if json_data:
        json_data = json_data[0]

    res: DataCheckerOutput = data_checker(query, json_data)
    print(res)

    # if not res.contains_the_answer:
    #     result = enrich_assistant(query, json_data)
        # result = PropertyLookup().enrich_property_metadata(Property(**json_data), query)
        # print(result)
