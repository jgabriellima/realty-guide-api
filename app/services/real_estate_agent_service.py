from typing import Union

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import RealEstateAgent
from app.services.generic_task_service import GenericTaskService
from app.setup_logging import setup_logging
from app.utils.parsers import parse_to_schema

logger = setup_logging("RealEstateAgentService")


class RealEstateAgentService(GenericTaskService):

    def lookup(self, whatsapp_number: str) -> Union[str, RealEstateAgent]:
        supabase = SupabaseDB().client

        agent_data = supabase.schema('real_estate').rpc("get_agent_with_metadata",
                                                        params={"p_whatsapp": whatsapp_number, "p_id": None}).execute()
        logger.info(f"Data::get_agent_with_metadata: {agent_data}")
        agent: RealEstateAgent = parse_to_schema(RealEstateAgent, agent_data.data)

        if not agent:
            return (f"Agent not found with whatsapp number: {whatsapp_number}. Before proceed and try again, "
                    f"check if this is the right number. if yes, call `save_agent_memory` endpoint to save this real estate agent.")

        return agent

    def save_agent_memory(self, whatsapp_number: str, parameter_name: str, parameter_value_description: str) -> Union[
        str, RealEstateAgent]:
        supabase = SupabaseDB().client

        agent_data = supabase.schema('real_estate').rpc("get_agent_with_metadata",
                                                        params={"p_whatsapp": whatsapp_number, "p_id": None}).execute()
        logger.info(f"Data::get_agent_with_metadata: {agent_data}")
        agent: RealEstateAgent = parse_to_schema(RealEstateAgent, agent_data.data)

        if not agent:
            # create the new agent
            agent_data = supabase.schema('real_estate').table("real_estate_agents").insert({
                "whatsapp": whatsapp_number
            }).select()
            agent: RealEstateAgent = parse_to_schema(RealEstateAgent, agent_data.data)

            logger.info(f"Agent created by whatsapp: `{whatsapp_number}`")

        # save the agent metadata
        agent_metadata = supabase.schema('real_estate').table("agent_metadata").insert({
            "agent_id": agent.id,
            "parameter_name": parameter_name,
            "parameter_value_description": parameter_value_description
        }).select()

        return f"Agent memory saved successfully. {agent_metadata}"


if __name__ == '__main__':
    pass
