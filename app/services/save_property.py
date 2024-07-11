from typing import List

from supabase import Client

from app.core.db.supabase_conn import SupabaseDB
from app.schemas.real_estate import Property, PropertyMetadata
from app.setup_logging import setup_logging

# Supabase connection
supabase: Client = SupabaseDB().client
logger = setup_logging("SavePropertyService")

def save_property(property_data: Property):
    # Insert the property
    property_dict = property_data.model_dump(exclude={"property_metadata"})
    del property_dict["id"]
    del property_dict["assistant_instructions"]
    response = supabase.schema("real_estate").table("property").insert(property_dict).execute()

    if response.data:
        # Get the inserted property id
        property_id = response.data[0]["id"]

        # Insert the property metadata
        property_metadata_list = property_data.property_metadata
        for metadata in property_metadata_list:
            metadata_dict = metadata.model_dump()
            del metadata_dict["id"]
            metadata_dict["property_id"] = property_id
            supabase.table("property_metadata").insert(metadata_dict).execute()

        return {"status": "success", "message": "Property and metadata saved successfully"}
    else:
        return {"status": "error", "message": response.json()}


def save_metadata(property_id: int, property_metadata: List[PropertyMetadata]):
    # Insert the property metadata
    logger.info(f"Saving metadata for property {property_id}")
    for metadata in property_metadata:
        metadata_dict = metadata.model_dump()
        del metadata_dict["id"]
        metadata_dict["property_id"] = property_id
        supabase.table("property_metadata").insert(metadata_dict).execute()

    return {"status": "success", "message": "Metadata saved successfully"}

# # Example usage
# property_data = Property(
#     id_reference="-27.590847,-48.498135",
#     title="Apartamento para aluguel com 2 quartos, em Itacorubi com 125.51 m²",
#     description="Apartamento de 2 quartos, ampla suíte com closet, banheira de hidromassagem e sacada. Sala ampla com sacada, móveis planejados e eletrodomésticos, ar condicionado em ambos os quartos, 2 vagas de garagem, todas cobertas e livres. Condomínio São Jorge, com portaria 24 horas, piscina, quadra esportiva, salão de festas, gás encanado, playground e espaço gourmet na área comum, o Condomínio São Jorge é preparado para atender às necessidades dos moradores que buscam lazer e conforto em um só lugar. A proximidade com a Universidade do Estado de Santa Catarina (UDESC), quando falamos, o Itacorubi é o bairro perfeito para quem busca fácil acesso às praias e ao centro da cidade. Ele está localizado a poucos minutos do Centro e da Lagoa da Conceição, um dos pontos turísticos mais conhecidos de Florianópolis.",
#     slug="gralhaalugueis-com-br-imovel-aluguel-apartamento-2-quartos-itacorubi-florianopolis-sc-125-51m2-rs6000-1569",
#     url="https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569",
#     total_price=6000.0,
#     iptu=270.0,
#     condominium_fee=1065.0,
#     neighborhood="Itacorubi",
#     full_address="Avenida Avenida Itamarati, 380 - Itacorubi, Florianópolis, SC - São Jorge",
#     property_metadata=[
#         PropertyMetadata(property_id=1, parameter_name="Área", parameter_value_description="125.51 m²"),
#         PropertyMetadata(property_id=1, parameter_name="Quartos", parameter_value_description="2 quartos (1 suíte)"),
#         PropertyMetadata(property_id=1, parameter_name="Banheiros", parameter_value_description="3 banheiros"),
#         PropertyMetadata(property_id=1, parameter_name="Vagas", parameter_value_description="2 vagas"),
#         PropertyMetadata(property_id=1, parameter_name="Características do Imóvel",
#                          parameter_value_description="Ar Condicionado, Churrasqueira, Piscina"),
#         PropertyMetadata(property_id=1, parameter_name="Área Comum", parameter_value_description="Guarita, Playground")
#     ]
# )
#
# response = save_property(property_data)
# print(response)
