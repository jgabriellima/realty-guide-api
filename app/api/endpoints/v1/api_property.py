from typing import Any, Dict, Union

from fastapi import APIRouter, HTTPException

from app.api.endpoints.mock_data import mock_property_metadata, mock_property_data, mock_enriched_data
from app.schemas.real_estate import Property
from app.schemas.tools import SaveClientPreferencesResponse, PropertyLookupRequest, EnrichPropertyDataRequest, \
    EnrichPropertyDataResponse, GetEnrichmentDataRequest, GetEnrichmentDataResponse
from app.services.property_service import PropertyService

property_router = APIRouter()


@property_router.post("/lookup", response_model=Union[str, Property])
def property_lookup(request: PropertyLookupRequest):
    property_service_response = PropertyService().lookup(request.url, real_estate_agent_id=request.real_estate_agent_id)

    return property_service_response


@property_router.post("/enrich_property", response_model=Union[str, Property])
def enrich_property_data(request: EnrichPropertyDataRequest):
    if request.property_id in mock_enriched_data:
        return EnrichPropertyDataResponse(property_id=request.property_id,
                                          enriched_data=mock_enriched_data[request.property_id])
    else:
        raise HTTPException(status_code=404, detail="Property not found")


#
#
#
#
#

@property_router.post("/get_enrichment_data", response_model=GetEnrichmentDataResponse)
def get_enrichment_data(request: GetEnrichmentDataRequest):
    if request.property_id in mock_enriched_data:
        data = mock_enriched_data[request.property_id].get(request.data_type, {})
        return GetEnrichmentDataResponse(property_id=request.property_id, data={request.data_type: data})
    else:
        raise HTTPException(status_code=404, detail="Property not found")


@property_router.post("/save_metadata", response_model=SaveClientPreferencesResponse)
def save_property_metadata(property_id: int, metadata_key: str, metadata_value: Any):
    if property_id in mock_property_data:
        if property_id not in mock_property_metadata:
            mock_property_metadata[property_id] = {}
        mock_property_metadata[property_id][metadata_key] = metadata_value
        return SaveClientPreferencesResponse(status="Property metadata saved successfully")
    else:
        raise HTTPException(status_code=404, detail="Property not found")


@property_router.get("/get_metadata/{property_id}", response_model=Dict[str, Any])
def get_property_metadata(property_id: int):
    if property_id in mock_property_metadata:
        return mock_property_metadata[property_id]
    else:
        raise HTTPException(status_code=404, detail="Property metadata not found")
