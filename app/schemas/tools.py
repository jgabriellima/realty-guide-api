from typing import Dict, Any, Union, Optional

from pydantic import BaseModel


class PropertyLookupRequest(BaseModel):
    url: str
    real_estate_agent_id: Union[str, int]
    conversation_id: str


class EnrichPropertyDataRequest(BaseModel):
    property_id: int
    request_details: str
    real_estate_agent_id: Union[str, int]
    conversation_id: str


class EnrichPropertyDataResponse(BaseModel):
    property_id: str
    enriched_data: Dict[str, Any]


class LookupRequest(BaseModel):
    whatsapp_number: str


class AgentLookupRequest(BaseModel):
    agent_whatsapp_number: str


class ClientLookupRequest(BaseModel):
    client_whatsapp_number: str
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


class AgentPreferencesRequest(BaseModel):
    parameter_name: str
    parameter_value_description: str
    real_estate_agent_id: Optional[int] = None


class ClientPreferencesRequest(BaseModel):
    client_id: int
    parameter_name: str
    parameter_value_description: str
    real_estate_agent_id: int


class SchedulerReminderRequest(BaseModel):
    real_estate_agent_id: int
    remainder_description: str
    remainder_time_in_seconds: int
