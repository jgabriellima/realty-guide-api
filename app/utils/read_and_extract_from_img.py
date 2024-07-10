import json
import logging
from typing import Union, Optional, Dict, Any, List, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.schemas.real_estate import Property
from app.utils.html_injection import generate_script_to_mark_elements

load_dotenv()

import marvin

import requests

from marvin.types import ChatResponse, MarvinType


class CustomImageUrl(MarvinType):
    url: str = Field(
        description="URL of the image to be sent or a base64 encoded image."
    )
    detail: str = "high"  # auto, low, high


marvin.types.ImageUrl = CustomImageUrl

from app.core.settings import settings
from app.utils.costs_calculator import calculate_price, CompletionUsage
from app.utils.custom_marvin.custom_marvin_extractor import extract_from_image
from app.utils.slug import url_to_slug
from app.utils.timer import Timer

T = TypeVar('T')


class ImageURL(BaseModel):
    """
    Image URL detected in the image.
    """
    urls: List[str]


def capture_screenshot(target_url: str, custom_js_script: str = None, optimize_for_speed=True) -> Optional[bytes]:
    """
    Capture a screenshot of the given URL.

    Args:
        target_url (str): The URL of the webpage to capture.
        api_token (str): The API token for authentication.

    Returns:
        Optional[bytes]: The screenshot image in bytes if successful, None otherwise.
    """
    URL = 'https://browserless-production-cbb6.up.railway.app/screenshot'
    API_TOKEN = settings.browserless_key

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }
    data = {
        'url': target_url,
        'options': {
            'fullPage': True,
            'type': 'png'
        },
        'addScriptTag': []
    }

    if custom_js_script:
        data['addScriptTag'].append({
            "content": custom_js_script
        })

    try:
        response = requests.post(URL, headers=headers, json=data, params={'token': API_TOKEN})
        response.raise_for_status()
        logging.info('Screenshot taken successfully')
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to capture screenshot: {e}")
        return None


def extract_data_from_image(image: Union[str, bytes], target: Union[BaseModel, T] = None, custom_prompt: str = None) -> \
        Optional[
            Dict[str, Any]]:
    """
    Extract data from an image.

    Args:
        image (Union[str, bytes]): The image file path or image bytes.

    Returns:
        Optional[Dict[str, Any]]: Extracted data and cost information if successful, None otherwise.
    """

    if not image or not target:
        raise ValueError("Invalid image or target")

    if isinstance(image, str):  # If image is a path to the file
        img = marvin.Image(data=open(image, 'rb').read())
    elif isinstance(image, bytes):  # If image is in bytes
        img = marvin.Image(data=image)
    else:
        logging.error("Invalid image input")
        return None

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
        return None


def save_extracted_data(data: Dict[str, Any], output_filename: str) -> None:
    """
    Save extracted data to a JSON file.

    Args:
        data (Dict[str, Any]): The data to save.
        output_filename (str): The filename to save the data to.
    """
    try:
        with open(output_filename, 'w') as f:
            f.write(json.dumps(data))
        logging.info(f'Data extracted and saved as {output_filename}')
    except IOError as e:
        logging.error(f"Failed to save extracted data: {e}")


def process_url(target_url: str) -> Optional[Dict[str, Any]]:
    """
    Process a URL: capture a screenshot, extract data, and save the results.

    Args:
        target_url (str): The URL to process.

    Returns:
        Optional[Dict[str, Any]]: The extracted data and cost information if successful, None otherwise.
    """
    full_page_screenshot_filename = f'{url_to_slug(target_url)}.png'
    image_table_only_screenshot_filename = f'{url_to_slug(target_url)}_images_list.png'

    # First step: Capture the screenshot of the full screen
    with Timer("Full page Screenshot capture") as timer:

        script_to_cleanup_the_page_elements = generate_script_to_mark_elements(mark_image=False, mark_map=True,
                                                                               remove_headers=True, remove_footers=True,
                                                                               remove_ads=True, remove_forms=True)

        full_page_screenshot_data = capture_screenshot(target_url, custom_js_script=script_to_cleanup_the_page_elements)
        if not full_page_screenshot_data:
            return None

        with open(full_page_screenshot_filename, 'wb') as f:
            f.write(full_page_screenshot_data)

    # Second Step: Capture Screenshot of the list of the images only
    with Timer("Images tabel Only Screenshot capture") as timer:

        script_to_remove_all_elements_and_keep_only_the_images_table = generate_script_to_mark_elements(
            show_only_image_urls=True)

        images_table_only_screenshot_data = capture_screenshot(target_url,
                                                               custom_js_script=script_to_remove_all_elements_and_keep_only_the_images_table)
        if not images_table_only_screenshot_data:
            return None

        with open(image_table_only_screenshot_filename, 'wb') as f:
            f.write(images_table_only_screenshot_data)

    obj = {
        "property_data": {},
        "property_images": {},
    }

    with Timer("Data Extraction - Full Page"):
        extracted_data = extract_data_from_image(full_page_screenshot_data, target=Property)
        if extracted_data is None:
            return None
        obj["property_data"] = extracted_data

    with Timer("Data Extraction - Images Table"):
        extracted_data = extract_data_from_image(images_table_only_screenshot_data, target=ImageURL)
        if extracted_data is None:
            return None
        obj["property_images"] = extracted_data

    save_extracted_data(obj, f'{full_page_screenshot_filename}.json')

    return obj


def main() -> None:
    """
    Main function to process a list of URLs.
    """
    urls = [
        # "https://www.vivareal.com.br/imovel/casa-3-quartos-ingleses-do-rio-vermelho-bairros-florianopolis-com-garagem-136m2-venda-RS530000-id-2726145964/",
        # "https://www.sanremoimoveis.com.br/imovel/aluguel+casa+3-quartos+corrego-grande+florianopolis+sc+120m2+rs4900/3208",
        # "https://www.chavesnamao.com.br/imovel/apartamento-a-venda-3-quartos-com-garagem-sc-florianopolis-joao-paulo-134m2-RS2935971/id-20486220/?gal=1",
        "https://www.gralhaalugueis.com.br/imovel/aluguel+apartamento+2-quartos+itacorubi+florianopolis+sc+125,51m2+rs6000/1569"
    ]

    for url in urls:
        result = process_url(url)
        print(result)


if __name__ == "__main__":
    main()

    # images_table_only_screenshot_data = open("gralhaalugueis-com-br-imovel-aluguel-apartamento-2-quartos-itacorubi-florianopolis-sc-125-51m2-rs6000-1569.png", "rb").read()
    # extracted_data = extract_data_from_image(images_table_only_screenshot_data, target=Property)

    # print(extracted_data)
