from typing import List

from pydantic import BaseModel, Field


class PropertyMetadata(BaseModel):
    """
    PropertyMetadata model to store the property metadata, it means any additional information about the property
    should be stored here. Parameter name must be in English.
    """
    parameter_name: str = Field(..., description="Parameter name in EN of the property metadata")
    parameter_value: str = Field(..., description="Parameter value of the property metadata")
    description: str = Field(..., description="Description of the property metadata")


class Property(BaseModel):
    """
    Property model to store the property details
    """
    property_id: str
    url: str = None
    slug: str = None
    title: str
    description: str = Field(..., description="Property refined description")
    price: str
    neighborhood: str
    full_address: str
    property_metadata: List[PropertyMetadata] = Field(..., default_factory=list)
    property_metadata_founded_keys: List[str] = Field(..., default_factory=list,
                                                      description="List of founded keys in the property metadata")
    images: List[str] = []
