from firecrawl import FirecrawlApp

from app.core.settings import settings
from app.schemas.real_estate import Property


def get_property_data(url: str):
    app = FirecrawlApp(api_key=settings.firecrawl_api_key)
    data = app.scrape_url(
        url,
        {
            'extractorOptions': {
                'extractionSchema': Property.model_json_schema(),
                'mode': 'llm-extraction'
            },
            'pageOptions': {
                'onlyMainContent': True
            }
        })
    return data["llm_extraction"]
