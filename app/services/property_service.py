from typing import Union, List, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.property import Property

load_dotenv()
import marvin
from marvin.types import ChatResponse, MarvinType


class CustomImageUrl(MarvinType):
    url: str
    detail: str = "high"


marvin.types.ImageUrl = CustomImageUrl

T = TypeVar('T')


class ImageURL(BaseModel):
    urls: List[str]


class PropertyService:

    def property_lookup(self, url: str) -> Union[str, Property]:
        supabase = SupabaseDB().client

        property = supabase.schema('h').from_("properties").select("*").eq("url", url).single().execute()
        # Property = Property(**property)
        return property


if __name__ == '__main__':
    url = "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569"
    # service = PropertyDataService(debug=True)
    # result: Property = service.process_url(url)
    # print(result.model_dump_json())

    property = PropertyService().property_lookup(url)
    print(property)
