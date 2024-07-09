import asyncio

from dotenv import load_dotenv

from app.core.settings import settings

load_dotenv()

from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)
from tenacity import retry, stop_after_attempt


@retry(stop=stop_after_attempt(3))
async def take_screenshot(url: str) -> str:
    logger.info(f'take_screenshot:: Starting passing HTML to Image')
    async with async_playwright() as p:
        logger.info(f'html_to_image:: Connecting to browserless')
        browser = await p.chromium.connect(f"{settings.browserless_url}&headless=true")
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        img_bytes = await page.screenshot(full_page=True)
        logger.info(f'take_screenshot:: Screenshot taken')
        return img_bytes


if __name__ == '__main__':
    img = asyncio.run(take_screenshot(
        'https://ibagy.com.br/imovel/123730/casa-em-condominio-3-quartos-jardim-ribeirao-ribeirao-da-ilha-florianopolis/'))

    with open('screenshot.png', 'wb') as f:
        f.write(img)
