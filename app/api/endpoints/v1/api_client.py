from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import Client
from app.schemas.tools import LookupRequest, PreferencesRequest, ClientLookupRequest
from app.services.client_service import ClientService

client_router = APIRouter()


@client_router.post("/client_lookup", operation_id="client_lookup", response_model=Union[str, Client])
def client_lookup(request: ClientLookupRequest):
    client = ClientService().lookup(whatsapp_number=request.whatsapp_number)
    return client


@client_router.post("/save_client_memory_preferences", operation_id="save_client_memory_preferences",
                    response_model=str)
def save_client_memory_preferences(request: PreferencesRequest):
    client = ClientService().save_client_memory(whatsapp_number=request.whatsapp_number,
                                                parameter_name=request.parameter_name,
                                                parameter_value_description=request.parameter_value_description)

    return client


if __name__ == '__main__':
    client = ClientService().save_client_memory(**{
        "whatsapp_number": "48991302288",
        "parameter_name": "filhos",
        "parameter_value_description": "3, duas meninas de 2 e 3 anos e um menino de 5 anos"
    })

    print(client)
