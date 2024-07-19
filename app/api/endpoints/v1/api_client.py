from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import Client
from app.schemas.tools import ClientLookupRequest, ClientPreferencesRequest
from app.services.client.client_service import ClientService

client_router = APIRouter()


@client_router.post("/client_lookup", operation_id="client_lookup", response_model=Union[str, Client])
def client_lookup(request: ClientLookupRequest):
    """
    Lookup client
    :param request: ClientLookupRequest
    :return: Union[str, Client]
    """
    client = ClientService().lookup(whatsapp_number=request.client_whatsapp_number,
                                    real_estate_agent_id=request.real_estate_agent_id)
    return client


@client_router.post("/save_client_memory_preferences", operation_id="save_client_memory_preferences",
                    response_model=str)
def save_client_memory_preferences(request: ClientPreferencesRequest):
    """
    Save client memory preferences
    :param request: ClientPreferencesRequest
    :return: str
    """
    client = ClientService().save_client_memory(client_id=request.client_id,
                                                parameter_name=request.parameter_name,
                                                parameter_value_description=request.parameter_value_description,
                                                real_estate_agent_id=request.real_estate_agent_id)

    return client


if __name__ == '__main__':
    client = ClientService().save_client_memory(**{
        "whatsapp_number": "48991302288",
        "parameter_name": "filhos",
        "parameter_value_description": "3, duas meninas de 2 e 3 anos e um menino de 5 anos"
    })

    print(client)
