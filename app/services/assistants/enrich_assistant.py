from dotenv import load_dotenv

load_dotenv()

import json
from datetime import datetime

from langsmith import traceable

from app.services.assistants.prompts.system_prompts import ENRICH_ASSISTANT_PROMPT
from app.services.assistants.tools.geo_tools import geocode, places_nearby, directions
from app.services.assistants.web_search import internet_search_expert

from marvin.beta.assistants import Assistant

from app.setup_logging import setup_logging

logger = setup_logging("EnrichAssistant")

# marvin.beta.assistants.assistants.logger = logger

@traceable(run_type="llm")
def enrich_assistant(query_and_context, property_data: dict):
    # Integrate custom tools with the assistant
    logger.info(f"Property data: {property_data} - Query and Context: {query_and_context}")
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

    input = {
        "query_and_context": "supermercados próximos",
        "property_data": "{\"id\":17,\"id_reference\":\"1\",\"title\":\"Apartamento para aluguel com 1 quarto, em Centro com 53.25 m²\",\"description\":\"Estúdio mobiliado, equipado e decorado no Centro de Florianópolis! Localizado no Jardim Milano, um empreendimento completo a poucos metros do Shopping Beiramar e da Avenida Beira Mar Norte. Condomínio com portaria 24hs, bicicletário, churrasqueira, elevadores, espaço gourmet, espaço kids, estacionamento para visitantes, heliponto, pet place, piscina adulto e infantil, playground, sala de jogos, sala fitness, sauna e salão de festas.\",\"slug\":\"gralhaalugueis-com-br-imovel-aluguel-apartamento-1-quarto-centro-florianopolis-sc-53-25m2-rs4900-1575\",\"url\":\"https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+1-quarto+centro+florianopolis+sc+53,25m2+rs4900/1575\",\"total_price\":4900.0,\"iptu\":320.8,\"condominium_fee\":546.0,\"neighborhood\":\"Centro\",\"full_address\":\"Avenida Mauro Ramos, 1512 - Centro, Florianópolis, SC - JARDIM MILANO\",\"property_metadata\":[{\"id\":null,\"property_id\":null,\"parameter_name\":\"Área\",\"parameter_value_description\":\"53.25 m²\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Quartos\",\"parameter_value_description\":\"1\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Banheiros\",\"parameter_value_description\":\"1\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Vagas\",\"parameter_value_description\":\"1\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Ar Condicionado\",\"parameter_value_description\":\"Sim\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Cozinha Americana\",\"parameter_value_description\":\"Sim\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Jardim\",\"parameter_value_description\":\"Sim\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Mobiliado\",\"parameter_value_description\":\"Sim\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Piscina Infantil\",\"parameter_value_description\":\"Sim\"},{\"id\":null,\"property_id\":null,\"parameter_name\":\"Sacada\",\"parameter_value_description\":\"Sim\"}],\"assistant_instructions\":null}"
    }

    print(enrich_assistant(input['query_and_context'], json.loads(input['property_data'])))