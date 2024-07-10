import json
from datetime import datetime

import googlemaps
from langsmith import traceable
from marvin.beta.assistants import Assistant

from app.core.settings import settings
from app.services.assistants.promtps import ENRICH_ASSISTANT_PROMPT
from app.services.assistants.tools.geo_tools import geocode, places_nearby, directions
from app.services.assistants.web_search import internet_search_expert

gmaps = googlemaps.Client(key=settings.google_api_key)


@traceable(run_type="llm")
def enrich_assistant(query_and_context, property_data: dict):
    # Integrate custom tools with the assistant
    ai = Assistant(tools=[geocode,
                          places_nearby,
                          directions,
                          internet_search_expert],
                   model="gpt-4o",
                   instructions=ENRICH_ASSISTANT_PROMPT.format(datetime_now=str(datetime.now()),
                                                               property_data=json.dumps(property_data)))

    res = ai.say(query_and_context)

    return res
