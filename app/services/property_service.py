from dotenv import load_dotenv

from app.core.settings import settings

load_dotenv()
import marvin
from firecrawl import FirecrawlApp

if __name__ == '__main__':


    # Initialize the FirecrawlApp with your API key
    app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)

    # Scrape a single URL
    url = 'https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569'
    scraped_data = app.scrape_url(url)

    # Crawl a website
    crawl_url = 'https://mendable.ai'
    params = {
        'pageOptions': {
            'onlyMainContent': True
        }
    }
    crawl_result = app.crawl_url(crawl_url, params=params)