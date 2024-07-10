# read json from file
import json

from dotenv import load_dotenv

load_dotenv()
from marvin.beta.assistants.runs import Run

from app.schemas.real_estate import Property
from app.services.assistants.geo_assistant import geo_assistant

with open(
        "gralhaalugueis-com-br-imovel-aluguel-apartamento-2-quartos-itacorubi-florianopolis-sc-125-51m2-rs6000-1569.png.json",
        'r') as f:
    data = json.load(f)
    print(data)

    property = Property(**data["property_data"]['target_data'][0])
    print(property)

    print(property.property_metadata_founded_keys)

    for metadata in property.property_metadata:
        print(f"{metadata.parameter_name} : {metadata.parameter_value}")

    result: Run = geo_assistant(
        f"Meu cliente está interessado nesse imóvel: <property>{property.model_dump_json()}</property>. Vamos enriquecer as informações?")

    print(result.messages)
    all_msg = []
    for message in result.messages:
        print(message)
        for m in message.content:
            all_msg.append(m.dict())

    # save result
    with open("result.json", 'w') as f:
        json.dump(all_msg, f)
