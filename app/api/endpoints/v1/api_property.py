from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import Property, Client, RealEstateAgent
from app.schemas.tools import PropertyLookupRequest, EnrichPropertyDataRequest, PreferencesRequest, LookupRequest, \
    SchedulerReminderRequest
from app.services.client_service import ClientService
from app.services.property_service import PropertyService
from app.services.real_estate_agent_service import RealEstateAgentService
from app.tasks import trigger_scheduled_remainder

property_router = APIRouter()


@property_router.post("/lookup", response_model=Union[str, Property])
def property_lookup(request: PropertyLookupRequest):
    property_service_response = PropertyService().lookup(request.url, real_estate_agent_id=request.real_estate_agent_id)

    return property_service_response


@property_router.post("/enrich_property_data", response_model=Union[str, Property])
def enrich_property_data(request: EnrichPropertyDataRequest):
    property_service_response = PropertyService().enrich_property(request.property_slug,
                                                                  real_estate_agent_id=request.real_estate_agent_id,
                                                                  request_details=request.request_details)

    return property_service_response


@property_router.post("/client_profile_lookup", response_model=Union[str, Client])
def client_profile_lookup(request: LookupRequest):
    client = ClientService().lookup(whatsapp_number=request.whatsapp_number)
    return client


@property_router.post("/save_client_memory_preferences", response_model=str)
def save_client_memory_preferences(request: PreferencesRequest):
    client = ClientService().save_client_memory(whatsapp_number=request.whatsapp_number,
                                                parameter_name=request.parameter_name,
                                                parameter_value_description=request.parameter_value_description)

    return client


@property_router.post("/save_agent_memory_preferences", response_model=str)
def save_agent_memory_preferences(request: PreferencesRequest):
    agent = RealEstateAgentService().save_agent_memory(whatsapp_number=request.whatsapp_number,
                                                       parameter_name=request.parameter_name,
                                                       parameter_value_description=request.parameter_value_description)

    return agent


@property_router.post("/retrieve_agent_data", response_model=Union[str, RealEstateAgent])
def retrieve_agent_data(request: LookupRequest):
    agent = RealEstateAgentService().lookup(whatsapp_number=request.whatsapp_number)
    return agent


@property_router.post("/schedule_remainder")
def schedule_remainder(request: SchedulerReminderRequest):
    trigger_scheduled_remainder.apply_async(args=[request.real_estate_agent_id, request.remainder_description],
                                            countdown=request.remainder_time_in_seconds)

    return {"message": "Remainder scheduled successfully."}
