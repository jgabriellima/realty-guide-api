from typing import Union

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import Client
from app.services.generic_task_service import GenericTaskService
from app.setup_logging import setup_logging
from app.utils.parsers import parse_to_schema

logger = setup_logging("ClientService")


class ClientService(GenericTaskService):

    def lookup(self, whatsapp_number: str) -> Union[str, Client]:
        supabase = SupabaseDB().client

        client_data = supabase.schema('real_estate').rpc("get_client_with_metadata",
                                                         params={"p_whatsapp": whatsapp_number}).execute()
        logger.info(f"Data::get_client_with_metadata: {client_data}")
        client: Client = parse_to_schema(Client, client_data.data)

        if not client:
            return (f"Client not found with whatsapp number: {whatsapp_number}. Before proceed and try again, "
                    f"check if this is the right number. if yes, call `save_client_memory` endpoint to save this client.")

        return client

    def save_client_memory(self, whatsapp_number: str, parameter_name: str, parameter_value_description: str) -> Union[
        str, Client]:
        supabase = SupabaseDB().client

        client_data = supabase.schema('real_estate').rpc("get_client_with_metadata",
                                                         params={"p_whatsapp": whatsapp_number}).execute()
        logger.info(f"Data::get_client_with_metadata: {client_data}")
        client: Client = parse_to_schema(Client, client_data.data)

        if not client:
            # create the new client
            client = supabase.schema('real_estate').table("clients").insert({
                "whatsapp": whatsapp_number
            }).execute()
            logger.info(f"Client created by whatsapp: `{whatsapp_number}`")

        # save the cliente metadata
        client_metadata = supabase.schema('real_estate').table("client_metadata").insert({
            "client_id": client.id,
            "parameter_name": parameter_name,
            "parameter_value_description": parameter_value_description
        }).select()

        return f"Client memory saved successfully {client_metadata}"


if __name__ == '__main__':
    pass
