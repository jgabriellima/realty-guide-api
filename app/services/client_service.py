from typing import Union

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import Client
from app.services.generic_task_service import GenericTaskService
from app.setup_logging import setup_logging
from app.utils.parsers import parse_to_schema

logger = setup_logging("ClientService")


class ClientService(GenericTaskService):

    def lookup(self, whatsapp_number: str, real_estate_agent_id: int = None) -> Union[str, Client]:
        supabase = SupabaseDB().client

        client_data = supabase.schema('real_estate').rpc("get_client_with_metadata",
                                                         params={"p_whatsapp": whatsapp_number}).execute()
        logger.info(f"Data::get_client_with_metadata: {client_data}")
        client: Client = parse_to_schema(Client, client_data.data)

        if not client:
            client: Client = parse_to_schema(Client, supabase.schema('real_estate').table("clients").insert(
                {"whatsapp": whatsapp_number, "real_estate_agent_id": real_estate_agent_id}).execute().data)
            logger.info(f"Client created by whatsapp: `{whatsapp_number}`")

        return client

    def save_client_memory(self, client_id: Union[int, str],
                           parameter_name: str,
                           parameter_value_description: str,
                           real_estate_agent_id: Union[None, int] = None) -> Union[str, Client]:
        supabase = SupabaseDB().client

        client_data = supabase.schema('real_estate').rpc("get_client_with_metadata",
                                                         params={"p_whatsapp": None,
                                                                 "p_client_id": client_id}).execute()
        logger.info(f"Data::get_client_with_metadata: {client_data}")
        client: Client = parse_to_schema(Client, client_data.data)

        if not client:
            logger.info(f"Client not found with id: `{client_id}`")
            return (f"Client not found with id: `{client_id}`. Use the `client_lookup` tool first to initiate "
                    f"the client and then you'll be able to save memories and preferences.")

        metadata_to_insert = {
            "client_id": client.id,
            "parameter_name": parameter_name,
            "parameter_value_description": parameter_value_description
        }
        # save the client metadata
        if real_estate_agent_id:
            metadata_to_insert["real_estate_agent_id"] = real_estate_agent_id
        client_metadata = supabase.schema('real_estate').table("client_metadata").insert(metadata_to_insert).execute()

        return f"Client memory saved successfully {client_metadata}"


if __name__ == '__main__':
    pass
