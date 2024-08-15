import concurrent.futures
import json
import logging
from typing import Union, Optional, Dict, Any, List, TypeVar

import requests
from dotenv import load_dotenv
from openai.types import CompletionUsage
from pydantic import BaseModel

from app.core.settings import settings
from app.schemas.real_estate import Property, PropertyImages
from app.services.assistants.enrich_assistant import enrich_assistant
from app.services.property.prompts.property_prompts import ENRICH_PROPERTY, EXTRACT_DATA_FROM_IMAGE_DEFAULT_PROMPT
from app.services.property.property_data import save_property
from app.utils.custom_marvin.custom_marvin_extractor import custom_data_extractor
from app.utils.html import generate_script_to_mark_elements
from app.utils.timer import Timer
from app.utils.utils import calculate_price, url_to_slug

load_dotenv()
import marvin
from marvin.types import ChatResponse, MarvinType, Run
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger("PropertyTasksService")


class CustomImageUrl(MarvinType):
    url: str
    detail: str = "high"


marvin.types.ImageUrl = CustomImageUrl

T = TypeVar('T')


class ImageURL(BaseModel):
    urls: List[str]


class PropertyLookup:
    def __init__(self, debug: bool = False, http_client: Optional[requests.Session] = None):
        self.debug = debug
        self.http_client = http_client or requests.Session()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def capture_screenshot(self, target_url: str, custom_js_script: str = None) -> bytes:
        headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
        data = {
            'url': target_url,
            'options': {'fullPage': True, 'type': 'png'},
            'addScriptTag': []
        }

        if custom_js_script:
            data['addScriptTag'].append({"content": custom_js_script})

        try:
            response = self.http_client.post(f'{settings.browserless_url}/screenshot', headers=headers, json=data,
                                             params={'token': settings.browserless_key})
            response.raise_for_status()
            logging.info('Screenshot taken successfully')
            return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to capture screenshot: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def extract_data_from_image(self, image: Union[str, bytes], target: Union[BaseModel, T] = None,
                                custom_prompt: str = None) -> Dict[str, Any]:
        if not image or not target:
            raise ValueError("Invalid image or target")

        if isinstance(image, str):
            img = marvin.Image(data=open(image, 'rb').read())
        elif isinstance(image, bytes):
            img = marvin.Image(data=image)
        else:
            logging.error("Invalid image input")
            raise ValueError("Invalid image input")

        try:
            prompt = custom_prompt or EXTRACT_DATA_FROM_IMAGE_DEFAULT_PROMPT

            results: ChatResponse = custom_data_extractor(
                img,
                target=target,
                instructions=prompt,
                model_kwargs={"model": "gpt-4o", "temperature": 0}
            )
            usage: CompletionUsage = results.response.usage
            cost = calculate_price(usage)

            target_data = [extracted_data.dict() for extracted_data in results.tool_outputs[0]]

            return {
                'target_data': target_data,
                'cost': {
                    'input_tokens': usage.prompt_tokens,
                    'output_tokens': usage.completion_tokens,
                    'total_tokens': usage.total_tokens,
                    'price': cost
                }
            }
        except Exception as e:
            logging.error(f"Failed to extract data from image: {e}")
            raise

    def save_extracted_data(self, data: Dict[str, Any], output_filename: str) -> None:
        try:
            with open(output_filename, 'w') as f:
                f.write(json.dumps(data))
            logging.info(f'Data extracted and saved as {output_filename}')
        except IOError as e:
            logging.error(f"Failed to save extracted data: {e}")

    def process_url(self, target_url: str) -> Optional[Property]:
        """
        Process a URL to capture screenshots, extract data, and consolidate results.

        Args:
            target_url (str): The URL of the property to process.

        Returns:
            Optional[Property]: The consolidated data extracted from the property page and images.
        """
        def capture_screenshot_task(url, script, filename):
            screenshot_data = self.capture_screenshot(url, custom_js_script=script)
            if not screenshot_data:
                logging.error(f"Screenshot capture failed for URL: {url}")
                return None
            if self.debug:
                with open(filename, 'wb') as f:
                    f.write(screenshot_data)
            return screenshot_data

        def extract_data_task(screenshot_data, target):
            extracted_data = self.extract_data_from_image(screenshot_data, target=target)
            if not extracted_data:
                logging.error(f"Data extraction failed for target: {target}")
                return None
            return extracted_data["target_data"][0]

        full_page_screenshot_filename = f'{url_to_slug(target_url)}.png'
        image_table_only_screenshot_filename = f'{url_to_slug(target_url)}_images_list.png'

        try:
            with Timer("Full page Screenshot capture"):
                script_to_cleanup_the_page_elements = generate_script_to_mark_elements(
                    mark_image=False, mark_map=True, remove_headers=True, remove_footers=True,
                    remove_ads=True, remove_forms=True
                )
                script_to_remove_all_elements_and_keep_only_the_images_table = generate_script_to_mark_elements(
                    show_only_image_urls=True
                )

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_full_page = executor.submit(capture_screenshot_task, target_url, script_to_cleanup_the_page_elements, full_page_screenshot_filename)
                    future_images_table = executor.submit(capture_screenshot_task, target_url, script_to_remove_all_elements_and_keep_only_the_images_table, image_table_only_screenshot_filename)

                    full_page_screenshot_data = future_full_page.result()
                    images_table_only_screenshot_data = future_images_table.result()

                    if not full_page_screenshot_data or not images_table_only_screenshot_data:
                        return None

            obj = {"property_data": {}, "property_images": {}}

            with Timer("Data Extraction"):
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_data_extraction_full_page = executor.submit(extract_data_task, full_page_screenshot_data, Property)
                    future_data_extraction_images_table = executor.submit(extract_data_task, images_table_only_screenshot_data, ImageURL)

                    extracted_data_full_page = future_data_extraction_full_page.result()
                    extracted_data_images_table = future_data_extraction_images_table.result()

                    if not extracted_data_full_page or not extracted_data_images_table:
                        return None

                    obj["property_data"] = extracted_data_full_page
                    obj["property_images"] = extracted_data_images_table

                    obj["property_data"]["property_images"] = [PropertyImages(url=url).model_dump() for url in obj["property_images"]["urls"]]

                if self.debug:
                    self.save_extracted_data(obj, f'{full_page_screenshot_filename}.json')

                property = Property(**obj.get("property_data")) if obj.get("property_data") else None
                property.url = target_url
                property.slug = url_to_slug(target_url)

                return property

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while processing URL {target_url}: {e}")
            return None
        except ValueError as e:
            logging.error(f"Value error while processing URL {target_url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error while processing URL {target_url}: {e}")
            return None

    def enrich_property_metadata(self, property: Property, query: str = None) -> Union[None, Property]:
        """
        Enriches the property metadata by adding additional information to the property metadata list.

        Args:
            property (Property): The property object to enrich.

        Returns:
            Property: The enriched property object.
        """
        if not property:
            return None

        logger.info(f"Property found: {property.model_dump_json()}.  Calling enrich_assistant")

        result: Run = enrich_assistant(query, property.model_dump_json())

        assistant_only = [msg for msg in result.messages if msg.role == "assistant"]
        if len(assistant_only) > 1:
            assistant_only.pop(0)

        all_messages = []
        for ao in assistant_only:
            all_messages.append(ao.content[0].text.value)

        if not all_messages:
            logger.error("No messages found in the assistant response: ")
            return None

        data_to_extract = '\n'.join(all_messages)

        results: ChatResponse = custom_data_extractor(
            f" <property>{property.model_dump_json()}</property> | <data_to_extract>{data_to_extract}</data_to_extract>",
            target=Property,
            instructions=ENRICH_PROPERTY,
            model_kwargs={
                "model": "gpt-4o",
                "temperature": 0.0,
            }
        )

        target_data = [extracted_data for extracted_data in results.tool_outputs[0]]

        logger.info(f"target_data: {target_data}")

        if target_data:
            enriched_property = target_data[0]
            return enriched_property


if __name__ == '__main__':
    # url = "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+centro+florianopolis+sc+120m2+rs4500/1592"
    url = "https://qualitefloripaimoveis.com.br/imovel/casas/florianopolis/cacupe-casa-4-quartos-casa-a-venda-em-condominio-fechado-no-cacupe-cod-148621"
    property: Property = PropertyLookup(debug=True).process_url(url)

    property_json = property.model_dump_json()
    with open(f"{url_to_slug(url)}.json", "w") as f:
        f.write(property_json)


    res = save_property(property)
    print(res)