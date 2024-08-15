from typing import List

from supabase import Client

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import Property, PropertyMetadata, PropertyImages
from app.core.setup_logging import setup_logging

# Supabase connection
supabase: Client = SupabaseDB().client
logger = setup_logging("SavePropertyService")


def save_property(property_data: Property):
    # Insert the property
    if property_data:
        property_dict = property_data.model_dump(exclude={"property_metadata", "property_images"})
        del property_dict["id"]
        del property_dict["assistant_instructions"]

        response = supabase.schema("real_estate").table("property").insert(property_dict).execute()

        if response.data:
            # Get the inserted property id
            property_id = response.data[0]["id"]
            logger.info(f"Saving property {property_id}")

            # Insert the property metadata
            logger.info(f"Saving metadata for property {property_id}")
            save_metadata(property_id, property_data.property_metadata)

            logger.info(f"Saving Images metadata for property {property_id}")
            save_images_metadata(property_id, property_data.property_images)

            return {"status": "success", "message": "Property and metadata saved successfully"}
        else:
            return {"status": "error", "message": response}


def save_metadata(property_id: int, property_metadata: List[PropertyMetadata]):
    """
    Save the metadata for a property

    :param property_id: The property id
    :param property_metadata: The metadata to save
    :return: dict
    """
    logger.info(f"Saving metadata for property {property_id}")
    objs_to_persist = []
    for metadata in property_metadata:
        metadata_dict = metadata.model_dump()
        del metadata_dict["id"]
        metadata_dict["property_id"] = property_id

        objs_to_persist.append(metadata_dict)

    supabase.schema("real_estate").table("property_metadata").insert(objs_to_persist).execute()

    return {"status": "success", "message": "Metadata saved successfully"}


def save_images_metadata(property_id: int, property_images_metadata: List[PropertyImages]):
    """
    Save the images metadata for a property

    :param property_id: The property id
    :param property_images_metadata: The images metadata to save
    :return dict
    """
    logger.info(f"Saving Images metadata for property {property_id}")
    objs_to_persist = []
    for metadata in property_images_metadata:
        metadata_dict = metadata.model_dump()
        del metadata_dict["id"]
        metadata_dict["property_id"] = property_id
        objs_to_persist.append(metadata_dict)

    supabase.schema("real_estate").table("property_images").insert(objs_to_persist).execute()

    return {"status": "success", "message": "Images Metadata saved successfully"}
