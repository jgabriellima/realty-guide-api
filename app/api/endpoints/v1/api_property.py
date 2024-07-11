from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import Property
from app.schemas.tools import PropertyLookupRequest, EnrichPropertyDataRequest, SchedulerReminderRequest
from app.services.property_service import PropertyService
from app.tasks import trigger_scheduled_remainder

property_router = APIRouter()


@property_router.post("/lookup", operation_id="property_lookup", response_model=Union[str, Property])
def property_lookup(request: PropertyLookupRequest):
    property_service_response = PropertyService().lookup(request.url, real_estate_agent_id=request.real_estate_agent_id)

    return property_service_response


@property_router.post("/enrich_property_data", operation_id="enrich_property_data", response_model=Union[str, Property])
def enrich_property_data(request: EnrichPropertyDataRequest):
    property_service_response = PropertyService().enrich_property(request.property_slug,
                                                                  real_estate_agent_id=request.real_estate_agent_id,
                                                                  request_details=request.request_details)

    return property_service_response
