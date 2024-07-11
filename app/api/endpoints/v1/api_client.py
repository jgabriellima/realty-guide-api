from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import Client
from app.schemas.tools import LookupRequest, PreferencesRequest
from app.services.client_service import ClientService

client_router = APIRouter()


@client_router.post("/client_lookup", response_model=Union[str, Client])
def client_lookup(request: LookupRequest):
    client = ClientService().lookup(whatsapp_number=request.whatsapp_number)
    return client


@client_router.post("/save_client_memory_preferences", response_model=str)
def save_client_memory_preferences(request: PreferencesRequest):
    client = ClientService().save_client_memory(whatsapp_number=request.whatsapp_number,
                                                parameter_name=request.parameter_name,
                                                parameter_value_description=request.parameter_value_description)

    return client
