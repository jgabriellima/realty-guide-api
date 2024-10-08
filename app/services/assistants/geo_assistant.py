from app.core.settings import settings
from datetime import datetime

import googlemaps
from langsmith import traceable
from marvin.beta.assistants import Assistant

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
    
    <property_data>{property_data}</property_data>
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
