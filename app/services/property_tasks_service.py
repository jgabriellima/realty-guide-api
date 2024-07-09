import json
import logging
from typing import Union, Optional, Dict, Any, List, TypeVar

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from app.core.settings import settings
from app.schemas.property import Property
from app.services.assistants.geo_assistant import geo_assistant
from app.utils.costs_calculator import calculate_price, CompletionUsage
from app.utils.custom_marvin.custom_marvin_extractor import extract_from_image
from app.utils.html_injection import generate_script_to_mark_elements
from app.utils.slug import url_to_slug
from app.utils.timer import Timer

load_dotenv()
import marvin
from marvin.types import ChatResponse, MarvinType, Run
from tenacity import retry, stop_after_attempt, wait_fixed


class CustomImageUrl(MarvinType):
    url: str
    detail: str = "high"


marvin.types.ImageUrl = CustomImageUrl

T = TypeVar('T')


class ImageURL(BaseModel):
    urls: List[str]


class PropertyTasksService:
    def __init__(self, debug: bool = False, http_client: Optional[requests.Session] = None):
        self.debug = debug
        self.http_client = http_client or requests.Session()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def capture_screenshot(self, target_url: str, custom_js_script: str = None,
                           optimize_for_speed: bool = True) -> bytes:
        URL = 'https://browserless-production-cbb6.up.railway.app/screenshot'
        API_TOKEN = settings.browserless_key
        headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
        data = {
            'url': target_url,
            'options': {'fullPage': True, 'type': 'png'},
            'addScriptTag': []
        }

        if custom_js_script:
            data['addScriptTag'].append({"content": custom_js_script})

        try:
            response = self.http_client.post(URL, headers=headers, json=data, params={'token': API_TOKEN})
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
            default_prompt = "You're an expert on data extraction from images. Extract the data following your instructions schema."
            prompt = custom_prompt or default_prompt

            results: ChatResponse = extract_from_image(
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
            Optional[Dict[str, Any]]: The consolidated data extracted from the property page and images.
        """
        full_page_screenshot_filename = f'{url_to_slug(target_url)}.png'
        image_table_only_screenshot_filename = f'{url_to_slug(target_url)}_images_list.png'

        try:
            with Timer("Full page Screenshot capture"):
                script_to_cleanup_the_page_elements = generate_script_to_mark_elements(
                    mark_image=False, mark_map=True, remove_headers=True, remove_footers=True,
                    remove_ads=True, remove_forms=True
                )

                full_page_screenshot_data = self.capture_screenshot(target_url,
                                                                    custom_js_script=script_to_cleanup_the_page_elements)
                if not full_page_screenshot_data:
                    logging.error(f"Full page screenshot failed for URL: {target_url}")
                    return None

                if self.debug:
                    with open(full_page_screenshot_filename, 'wb') as f:
                        f.write(full_page_screenshot_data)

            with Timer("Images table Only Screenshot capture"):
                script_to_remove_all_elements_and_keep_only_the_images_table = generate_script_to_mark_elements(
                    show_only_image_urls=True
                )

                images_table_only_screenshot_data = self.capture_screenshot(target_url,
                                                                            custom_js_script=script_to_remove_all_elements_and_keep_only_the_images_table)
                if not images_table_only_screenshot_data:
                    logging.error(f"Images table screenshot failed for URL: {target_url}")
                    return None

                if self.debug:
                    with open(image_table_only_screenshot_filename, 'wb') as f:
                        f.write(images_table_only_screenshot_data)

            obj = {"property_data": {}, "property_images": {}}

            with Timer("Data Extraction - Full Page"):
                extracted_data = self.extract_data_from_image(full_page_screenshot_data, target=Property)
                if not extracted_data:
                    logging.error(f"Data extraction from full page screenshot failed for URL: {target_url}")
                    return None
                obj["property_data"] = extracted_data

            with Timer("Data Extraction - Images Table"):
                extracted_data = self.extract_data_from_image(images_table_only_screenshot_data, target=ImageURL)
                if not extracted_data:
                    logging.error(f"Data extraction from images table screenshot failed for URL: {target_url}")
                    return None
                obj["property_images"] = extracted_data

            if "target_data" in obj["property_images"]:
                obj["property_data"]["target_data"][0]["images"] = obj["property_images"]["target_data"][0]["urls"]

            total_cost = obj["property_data"]["cost"]["price"] + obj["property_images"]["cost"]["price"]
            obj["property_data"]["cost"]["total_price"] = total_cost

            if self.debug:
                self.save_extracted_data(obj, f'{full_page_screenshot_filename}.json')

            property = Property(**obj.get("property_data").get("target_data")[0]) if obj.get("property_data") else None
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

    def enrich_property_metadata(self, property: Property, query: str = None) -> Property:
        """
        Enriches the property metadata by adding additional information to the property metadata list.

        Args:
            property (Property): The property object to enrich.

        Returns:
            Property: The enriched property object.
        """
        if not property:
            return None

        property_data = f"<property>{property.model_dump_json()}</property>"
        result: Run = geo_assistant(
            f"{property_data}. Query/Commands: {query or 'Meu cliente está interessado nesse imóvel. Vamos enriquecer as informações?'}")

        assistant_only = [msg for msg in result.messages if msg.role == "assistant"]
        assistant_only.pop(0)

        all_messages = []
        for ao in assistant_only:
            all_messages.append(ao.content[0].text.value)

        results: ChatResponse = extract_from_image(
            f" <data_to_extract>{'\n'.join(all_messages)}</data_to_extract>",
            target=Property,
            instructions="You are an intelligent AI assistant specialized in extracting geolocation, spatial, and neighborhood data about real estate properties. Please structure the output according to the specified schema.",
            model_kwargs={
                "model": "gpt-4o",
                "temperature": 0.0,
            }
        )

        target_data = [extracted_data.dict() for extracted_data in results.tool_outputs[0]]

        prop_final = property.to_dict()
        prop_metadata = prop_final.get("property_metadata") + target_data[0].get("property_metadata")
        prop_final.update({"property_metadata": prop_metadata})

        return Property(**prop_final)


if __name__ == '__main__':
    # url = "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569"
    # service = PropertyDataService(debug=True)
    # result: Property = service.process_url(url)
    # print(result.model_dump_json())

    print(generate_script_to_mark_elements(
        mark_image=False, mark_map=True, remove_headers=True, remove_nav=False, remove_footers=True,
        remove_ads=True, remove_forms=True
    ))
