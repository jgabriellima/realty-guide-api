from dotenv import load_dotenv
from langsmith import traceable

from app.core.settings import settings
from app.services.assistants.web_search import internet_search_expert

load_dotenv()
from datetime import datetime
import googlemaps

from marvin.beta.assistants import Assistant

gmaps = googlemaps.Client(key=settings.google_api_key)


@traceable(run_type="tool")
def geocode(address: str):
    """
    Userful to converting addresses (like ``"1600 Amphitheatre Parkway, Mountain View, CA"``) into geographic coordinates (like latitude 37.423021 and longitude -122.083739)
    """
    geocode_result = gmaps.geocode(address)
    return geocode_result


@traceable(run_type="tool")
def places_nearby(longitude: float, latitude: float, type: str, keyword=None, name=None, open_now=True):
    """
    Returns a list of places nearby the given location ranked by `distance`:

    types = relevant_places = [ "airport", "art_gallery", "atm", "bakery", "bank", "beauty_salon", "bus_station",
    "cafe", "church", "city_hall", "convenience_store", "dentist", "doctor", "drugstore", "fire_station", "florist",
    "furniture_store", "gas_station", "gym", "hair_care", "hardware_store", "hospital", "library", "park", "parking",
    "pharmacy", "physiotherapist", "police", "post_office", "primary_school", "real_estate_agency", "restaurant",
    "school", "secondary_school", "shopping_mall", "spa", "stadium", "store", "subway_station", "supermarket",
    "train_station", "transit_station", "university" ]

    keyword: A term to be matched against all content that Google has
                    indexed for this place, including but not limited to name,
    """
    return gmaps.places_nearby(location=(latitude, longitude), keyword=keyword, name=name, open_now=open_now, type=type,
                               rank_by='distance')


@traceable(run_type="tool")
def directions(origin_address: str, destination_address: str,
               mode: str = 'driving',
               traffic_model: str = 'best_guess') -> dict:
    """
    Request directions via public transit

    Parameters:
    - origin_address: str
    - destination_address: str
    - mode: str (default: 'driving')
    - traffic_model: str (default: 'best_guess')

    Returns:
    - dict: Directions result from Google Maps API
    """

    return gmaps.directions(origin_address,
                            destination_address,
                            mode=mode,
                            traffic_model=traffic_model,
                            departure_time=datetime.now())


@traceable(run_type="llm")
def geo_assistant(query_and_context):
    # Integrate custom tools with the assistant
    ai = Assistant(tools=[geocode,
                          places_nearby,
                          directions,
                          internet_search_expert],
                   model="gpt-4o",
                   instructions=f""""
    You are a virtual real estate Geo-Assistant specialized in providing detailed information about specific addresses. Your tasks include the following:
1. First of all, create a detailed plan based on the given address and the user's query to determine the sequence and criteria for using each tool. This plan should align with the objective of generating compelling sales arguments for the real estate agent and take into account all inputted information to construct an effective plan.
2. Utilize the appropriate tools based on the plan. The available tools include:
   - 'geocode': To validate and gather precise coordinates for the given address if needed.
   - 'places_nearby': To search for and provide detailed information on nearby relevant places of interest around the address.
   - 'directions': To calculate and report on the distance and travel time by car during peak hours to specific points of interest, including traffic conditions and best travel routes when necessary.
   - 'internet_search_expert': To gather additional relevant information from the web about the address and its surroundings, such as security, infrastructure, quality of life, and other relevant aspects based on the user's concerns and interests.

Your responses should be concise, accurate, and provide comprehensive information to assist in making informed decisions about the location. Be realistic and transparent about both the positive and negative aspects of the area to help the real estate agent build trust with their clients. Highlight the strengths of the location while honestly addressing any potential concerns. 
The ultimate goal is to generate information that can be used as compelling and truthful sales arguments by the real estate agent using this assistant.
    
    <parameters>
    - Date Time Now: {str(datetime.now())}
    </parameters>
    """)

    res = ai.say(query_and_context)

    return res


if __name__ == '__main__':
    """
    # "meu cliente é divorciado e adora surfar, está procurando uma companheira nova entre 20 e 30 anos, ele tbm tem 2 filhos de 14 e 16 anos, ambos gostam de futebol, está interessado no imovel na Avenida Pequeno Principe 3030, e gostaria de saber qualquer informação relevante para convencer ele a comprar o imovel")
        # "meu cliente tem 70 anos e esta interessado num imovel na Avenida Pequeno Principe 3030, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida.")
        # "meu cliente tem 70 anos e esta interessado num imovel na R. Raul Antônio da Silva, 236 - Aririu da Formiga, Palhoça - SC, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida.")
        "meu cliente tem 70 anos e esta interessado num imovel na comunidade Caminho Novo, em Palhoça, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida.")
    """
    query = "meu cliente tem 70 anos e esta interessado num imovel na comunidade Caminho Novo, em Palhoça, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida."
    res = geo_assistant(query)
    print(res)
