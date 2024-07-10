from typing import Dict, Any, List, Union

from pydantic import BaseModel


class PropertyLookupRequest(BaseModel):
    url: str
    real_estate_agent_id: Union[str, int]


class EnrichPropertyDataRequest(BaseModel):
    property_id: str


class EnrichPropertyDataResponse(BaseModel):
    property_id: str
    enriched_data: Dict[str, Any]


class ClientProfileLookupRequest(BaseModel):
    client_id: str


class ClientProfileLookupResponse(BaseModel):
    client_id: str
    profile: Dict[str, Any]


class GetEnrichmentDataRequest(BaseModel):
    property_id: str
    data_type: str


class GetEnrichmentDataResponse(BaseModel):
    property_id: str
    data: Dict[str, Any]


class SaveClientPreferencesRequest(BaseModel):
    client_id: str
    preferences: Dict[str, Any]


class SaveClientPreferencesResponse(BaseModel):
    status: str


class GetCustomizedRecommendationsRequest(BaseModel):
    property_id: str
    client_id: str


class GetCustomizedRecommendationsResponse(BaseModel):
    recommendations: List[str]


class StoreAgentDataRequest(BaseModel):
    agent_id: str
    interaction_data: Dict[str, Any]


class StoreAgentDataResponse(BaseModel):
    status: str


class RetrieveAgentDataRequest(BaseModel):
    agent_id: str


class RetrieveAgentDataResponse(BaseModel):
    interaction_data: Dict[str, Any]
