from typing import Union

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import RealEstateAgent
from app.services.generic_task_service import GenericTaskService
from app.setup_logging import setup_logging
from app.utils.parsers import parse_to_schema

logger = setup_logging("RealEstateAgentService")

SYSTEM_VIOLATION = (
    "Agent not found with ID: {id}. This can be a violation of the terms: "
    "'An agent must be created by the admin first before start to use the system.'. "
    "CAUTION: Do not continue the conversation!")


class RealEstateAgentService(GenericTaskService):

    def lookup(self, whatsapp_number: str) -> Union[str, RealEstateAgent]:
        supabase = SupabaseDB().client

        agent_data = supabase.schema('real_estate').rpc("get_agent_with_metadata",
                                                        params={"p_whatsapp": whatsapp_number, "p_id": None}).execute()
        logger.info(f"Data::get_agent_with_metadata: {agent_data}")
        agent: RealEstateAgent = parse_to_schema(RealEstateAgent, agent_data.data)

        if not agent:
            return SYSTEM_VIOLATION.format(id=whatsapp_number)

        return agent

    def save_agent_memory(self, real_estate_agent_id: Union[int, str], parameter_name: str,
                          parameter_value_description: str) -> Union[
        str, RealEstateAgent]:
        supabase = SupabaseDB().client

        agent_data = supabase.schema('real_estate').rpc("get_agent_with_metadata",
                                                        params={"p_whatsapp": None,
                                                                "p_id": real_estate_agent_id}).execute()
        logger.info(f"Data::get_agent_with_metadata: {agent_data}")
        agent: RealEstateAgent = parse_to_schema(RealEstateAgent, agent_data.data)

        if not agent:
            return SYSTEM_VIOLATION.format(id=real_estate_agent_id)

        # save the agent metadata
        agent_metadata = supabase.schema('real_estate').table("agent_metadata").insert({
            "agent_id": agent.id,
            "parameter_name": parameter_name,
            "parameter_value_description": parameter_value_description
        }).execute()

        return f"Agent memory saved successfully. {agent_metadata}"


if __name__ == '__main__':
    pass
