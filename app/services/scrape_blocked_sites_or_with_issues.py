# https://www.zapimoveis.com.br/lancamento/venda-apartamento-1-quarto-campeche-florianopolis-sc-48m2-id-2567566261/
# https://www.chavesnamao.com.br/imovel/cobertura-a-venda-3-quartos-com-garagem-sc-florianopolis-itacorubi-360m2-RS1990000/id-15908968/
from dotenv import load_dotenv

load_dotenv()

from app.utils.custom_marvin.custom_marvin_extractor import custom_data_extractor

# gpt-4o-mini

from marvin.types import ChatResponse

features: ChatResponse = custom_data_extractor(
    "I love my new phone's camera, but the battery life could be improved.",
    instructions='get any product features that were mentioned',
    model_kwargs={
        'model': 'gpt-4o-mini'
        # 'model': 'gpt-4o'
    }
)
print(features.response.usage)
