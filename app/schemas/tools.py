from typing import Dict, Any, Union, Optional

from pydantic import BaseModel


class PropertyLookupRequest(BaseModel):
    url: str
    real_estate_agent_id: Union[str, int]


class EnrichPropertyDataRequest(BaseModel):
    property_slug: str
    request_details: str
    real_estate_agent_id: Union[str, int]


class EnrichPropertyDataResponse(BaseModel):
    property_id: str
    enriched_data: Dict[str, Any]


class LookupRequest(BaseModel):
    whatsapp_number: str


class ClientLookupRequest(LookupRequest):
    real_estate_agent_id: Union[str, int]


class ClientProfileLookupResponse(BaseModel):
    client_id: str
    profile: Dict[str, Any]


class GetEnrichmentDataRequest(BaseModel):
    property_id: str
    data_type: str


class GetEnrichmentDataResponse(BaseModel):
    property_id: str
    data: Dict[str, Any]


class PreferencesRequest(BaseModel):
    whatsapp_number: str
    parameter_name: str
    parameter_value_description: str
    real_estate_agent_id: Optional[int] = None


class SchedulerReminderRequest(BaseModel):
    real_estate_agent_id: Union[str, int]
    remainder_description: Dict[str, Any]
    remainder_time_in_seconds: int
