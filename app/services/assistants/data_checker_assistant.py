import json
from datetime import datetime
from app.core.settings import settings

import googlemaps
from langsmith import traceable
from marvin.types import ChatResponse
from pydantic import BaseModel, Field

from app.schemas.real_estate import Property
from app.services.assistants.enrich_assistant import enrich_assistant
from app.services.assistants.promtps import DATA_CHECKER
from app.services.property_tasks_service import PropertyLookup
from app.utils.custom_marvin.custom_marvin_extractor import custom_data_extractor



class DataCheckerOutput(BaseModel):
    """
    Data Checker Output
    """
    query_instructions: str
    response: str
    contains_the_answer: bool = Field(..., description="Only check as true if the user's query is full answered, for all the other scenarios, it should be false.")


@traceable(run_type="llm")
def data_checker(query_and_context, property_data: dict):
    results: ChatResponse = custom_data_extractor(
        query_and_context,
        target=DataCheckerOutput,
        instructions=DATA_CHECKER.format(datetime_now=str(datetime.now()),
                                         property_data=json.dumps(property_data)),
        model_kwargs={
            "model": "gpt-4o",
            "temperature": 0.0,
        }
    )

    target_data = [extracted_data for extracted_data in results.tool_outputs[0]]
    return target_data[0]


if __name__ == '__main__':
    """
    # "meu cliente é divorciado e adora surfar, está procurando uma companheira nova entre 20 e 30 anos, ele tbm tem 2 filhos de 14 e 16 anos, ambos gostam de futebol, está interessado no imovel na Avenida Pequeno Principe 3030, e gostaria de saber qualquer informação relevante para convencer ele a comprar o imovel")
        # "meu cliente tem 70 anos e esta interessado num imovel na Avenida Pequeno Principe 3030, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida.")
        # "meu cliente tem 70 anos e esta interessado num imovel na R. Raul Antônio da Silva, 236 - Aririu da Formiga, Palhoça - SC, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida.")
        "meu cliente tem 70 anos e esta interessado num imovel na comunidade Caminho Novo, em Palhoça, mas está preocupado com a segurança do local, pois ele veio de um lugar muito perigoso e esta buscanod melhor qualidade de vida.")
    """
    query = "além da universidade, Quais sao as escolas proximas à esse imovel?"
    json_data = {"id": 13, "id_reference": "-27.590847,-48.498135",
                 "title": "Apartamento para aluguel com 2 quartos, em Itacorubi com 125.51 m²",
                 "description": "Apartamento de 2 quartos, ampla suíte com closet, banheira de hidromassagem e sacada. Sala ampla com sacada, móveis planejados e eletrodomésticos, ar condicionado em ambos os quartos, 2 vagas de garagem, todas cobertas e livres. Condomínio São Jorge, com portaria 24 horas, piscina, quadra esportiva, salão de festas, gás encanado, playground e espaço gourmet na área comum, o Condomínio São Jorge é preparado para atender às necessidades dos moradores que buscam lazer e conforto em um só lugar. A proximidade com a Universidade do Estado de Santa Catarina (UDESC), quando falamos, o Itacorubi é o bairro perfeito para quem busca fácil acesso às praias e ao centro da cidade. Ele está localizado a poucos minutos do Centro e da Lagoa da Conceição, um dos pontos turísticos mais conhecidos de Florianópolis.",
                 "slug": "gralhaalugueis-com-br-imovel-aluguel-apartamento-2-quartos-itacorubi-florianopolis-sc-125-51m2-rs6000-1569",
                 "url": "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569",
                 "total_price": 6000.0, "iptu": 270.0, "condominium_fee": 1065.0, "neighborhood": "Itacorubi",
                 "full_address": "Avenida Avenida Itamarati, 380 - Itacorubi, Florianópolis, SC - São Jorge",
                 "property_metadata": [{"id": None, "property_id": None, "parameter_name": "Área",
                                        "parameter_value_description": "125.51 m²"},
                                       {"id": None, "property_id": None, "parameter_name": "Quartos",
                                        "parameter_value_description": "2 quartos (1 suíte)"},
                                       {"id": None, "property_id": None, "parameter_name": "Banheiros",
                                        "parameter_value_description": "3 banheiros"},
                                       {"id": None, "property_id": None, "parameter_name": "Vagas",
                                        "parameter_value_description": "2 vagas"},
                                       {"id": None, "property_id": None, "parameter_name": "Características do Imóvel",
                                        "parameter_value_description": "Ar Condicionado, Churrasqueira, Piscina"},
                                       {"id": None, "property_id": None, "parameter_name": "Área Comum",
                                        "parameter_value_description": "Guarita, Playground"}],
                 "assistant_instructions": None}

    res: DataCheckerOutput = data_checker(query, json_data)
    print(res)

    if not res.contains_the_answer:
        # result = enrich_assistant(query, json_data)
        result = PropertyLookup().enrich_property_metadata(Property(**json_data), query)
        print(result)
