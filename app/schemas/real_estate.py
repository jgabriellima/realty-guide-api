from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel


class PropertyMetadata(BaseModel):
    """
    PropertyMetadata schema
    """
    id: Optional[int] = None
    property_id: Optional[int] = None
    parameter_name: str
    parameter_value_description: str


class Property(BaseModel):
    """
    Property schema
    """
    id: Optional[int] = None
    id_reference: str
    title: str
    description: str
    slug: str
    url: str
    total_price: float
    iptu: float
    condominium_fee: float
    neighborhood: Optional[str] = None
    full_address: Optional[str] = None
    property_metadata: List[PropertyMetadata] = []


# Modelo PropertyImages
class PropertyImages(BaseModel):
    """
    Property Images schema
    """
    id: Optional[int] = None
    property_id: int
    url: str
    caption: Optional[str] = None


class Client(BaseModel):
    """
    Client schema
    """
    id: Optional[int] = None
    name: str
    whatsapp: str


class ClientMetadata(BaseModel):
    """
    ClientMetadata schema
    """
    id: Optional[int] = None
    client_id: int
    parameter_name: str
    parameter_value_description: str


class RealEstateAgent(BaseModel):
    """
    RealEstateAgent schema
    """
    id: Optional[int] = None
    name: str
    whatsapp: str


class RealEstateAgentMetadata(BaseModel):
    """
    RealEstateAgentMetadata schema
    """
    id: Optional[int] = None
    agent_id: int
    parameter_name: str
    parameter_value_description: str


class TaskCatalog(BaseModel):
    """
    TaskCatalog schema
    """
    id: Optional[int] = None
    function_name: str
    description: str


class Task(BaseModel):
    id: Optional[int] = None
    task_id: str
    function_name: str
    agent_id: Optional[int] = None
    description: str
    status: str
    error: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
