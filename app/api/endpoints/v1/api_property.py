from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import Property
from app.schemas.tools import PropertyLookupRequest, EnrichPropertyDataRequest
from app.services.property.property_service import PropertyService
from app.utils.utils import remove_null_values

property_router = APIRouter()


@property_router.post("/lookup", operation_id="property_lookup", response_model=Union[str, dict, Property])
def property_lookup(request: PropertyLookupRequest):
    """
    Lookup property data by URL

    :param request: PropertyLookupRequest
    :return: Union[str, Property]
    """
    property_service_response = PropertyService().lookup(request.url,
                                                         real_estate_agent_id=request.real_estate_agent_id,
                                                         conversation_id=request.conversation_id)

    if isinstance(property_service_response, str):
        return property_service_response

    return remove_null_values(property_service_response.model_dump())


@property_router.post("/query_and_enrich_property_data", operation_id="query_and_enrich_property_data",
                      response_model=Union[str, Property])
def enrich_property_data(request: EnrichPropertyDataRequest):
    """
    Enrich property data by URL

    :param request: EnrichPropertyDataRequest
    :return: Union[str, Property]
    """
    property_service_response = PropertyService().enrich_property(request.property_id,
                                                                  real_estate_agent_id=request.real_estate_agent_id,
                                                                  request_details=request.request_details,
                                                                  conversation_id=request.conversation_id)

    return property_service_response
