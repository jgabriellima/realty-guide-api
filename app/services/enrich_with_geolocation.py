from dotenv import load_dotenv
load_dotenv()
from marvin.types import ChatResponse

from app.schemas.real_estate import Property

INPUT_DATA = """
Informações Adicionais
Coordenadas do Imóvel
Endereço: Av. Itamarati, 380 - Itacorubi, Florianópolis - SC, 88034-400, Brasil
Latitude/Longitude: -27.5908697, -48.4984375
Pontos de Interesse Próximos
Supermercados

Supermercados Hiper Select Lagoa

Distância: ~2.6 km
Avaliação: 4.2
Mercado Engenho Novo

Distância: ~2.9 km
Avaliação: 4.4
Restaurantes

Vó Flor Bakery

Distância: ~0.8 km
Avaliação: 4.3
Pegue Leve Sempre

Distância: ~0.9 km
Avaliação: Não disponível
Escolas

Escola Sarapiquá

Distância: ~1.8 km
Avaliação: 4.8
Dual International School

Distância: ~0.9 km
Avaliação: 4.3
Parques

Praça da FIESC

Distância: ~0.8 km
Avaliação: 4.2
Praça Caiçara

Distância: ~1.3 km
Avaliação: 4.8
Hospitais

Canto da Lagoa Espaço Saúde

Distância: ~2.8 km
Avaliação: 5.0
Prontomed Clinic

Distância: ~3.0 km
Avaliação: 4.1
Academias

Manipura Yoga Floripa

Distância: ~1.9 km
Avaliação: 5.0
SESI Academia - FIESC

Distância: ~0.8 km
Avaliação: 4.7
Distâncias e Tempos de Viagem
Para Pontos Principais de Interesse
Centro de Florianópolis

Distância: ~6 km
Tempo de Viagem em Horário de Pico: ~15 minutos de carro
Universidade do Estado de Santa Catarina (UDESC)

Distância: ~1.5 km
Tempo de Viagem em Horário de Pico: ~5 minutos de carro
Lagoa da Conceição

Distância: ~6 km
Tempo de Viagem em Horário de Pico: ~12 minutos de carro
Avaliação da Localidade
Segurança: A área de Itacorubi é considerada segura, com patrulhamento constante, especialmente devido à presença de instituições importantes como a UDESC.

Qualidade de Vida: Ótima, com diversas opções de lazer, parques e proximidade a supermercados, academias e restaurantes renomados.

Infraestrutura: Completamente equipada, com disponibilidade de escolas, hospitais e serviços diversos nas proximidades.

Transporte Público: Bem atendido por várias linhas de ônibus, facilidade de acesso ao transporte público que conecta o bairro ao restante da cidade.

Conclusão
O apartamento no Condomínio São Jorge, em Itacorubi, apresenta uma localização privilegiada. A proximidade com supermercados renomados, restaurantes, escolas de qualidade, parques e hospitais torna a vida muito conveniente para os moradores. Além disso, a infraestrutura do condomínio agrega um ótimo valor ao imóvel.

Argumentos de Venda
Localização Central: Fácil acesso ao centro da cidade e às praias.
Infraestrutura Completa: Ótimos supermercados, academias e hospitais nas proximidades.
Qualidade de Vida: Área segura, com muitas opções de lazer e comodidades.
Conveniência: Várias escolas e universidades de alto nível nas proximidades, excelente para famílias e estudantes.
Essas são ótimas informações que podem ajudar a impressionar potenciais inquilinos, demonstrando que o imóvel não só é confortável e bem equipado, mas também está localizado em uma área estratégica de Florianópolis.
"""

from app.utils.custom_marvin.custom_marvin_extractor import extract_from_image

results: ChatResponse = extract_from_image(
    INPUT_DATA,
    target=Property,
    instructions="You are an intelligent AI assistant specialized in extracting geolocation, spatial, and neighborhood data about real estate properties. Please structure the output according to the specified schema.",
    model_kwargs={
        "model": "gpt-4o",
        "temperature": 0.0,
    }
)

target_data = [extracted_data.dict() for extracted_data in results.tool_outputs[0]]

print(target_data)
