from datetime import datetime

import googlemaps
from langsmith import traceable

from app.core.settings import settings

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
