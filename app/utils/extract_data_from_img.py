import json

from dotenv import load_dotenv

load_dotenv()

from marvin.types import ChatResponse

from app.utils.costs_calculator import calculate_price, CompletionUsage
from app.utils.timer import Timer

from app.utils.custom_marvin.custom_marvin_extractor import extract_from_image
import marvin

from app.schemas.real_estate import Property

input_filename = 'ibagy-com-br-imovel-123730-casa-em-condominio-3-quartos-jardim-ribeirao-ribeirao-da-ilha-florianopolis.png'

img = marvin.Image(
    data=open(input_filename, 'rb').read(),
)

with Timer("Image Data Extraction"):
    results: ChatResponse = extract_from_image(img,
                                               target=Property,
                                               instructions="You're a expert on data extraction from images. Extract the data following your instructions schema",
                                               model_kwargs={"model": "gpt-4o", "temperature": 0})
    usage: CompletionUsage = results.response.usage
    print(f"Cost: {calculate_price(usage)}")

    properties = []
    for property in results.tool_outputs[0]:
        properties.append(property.dict())

    with open(f'{input_filename}.json', 'w') as f:
        f.write(json.dumps(properties))
