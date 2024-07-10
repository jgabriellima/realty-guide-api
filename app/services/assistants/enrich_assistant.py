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
def geo_assistant(query_and_context, property_data: dict):
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
