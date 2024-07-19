from openai.types import CompletionUsage
from pydantic import BaseModel

# Constants
INPUT_TOKEN_COST = 0.0050
OUTPUT_TOKEN_COST = 0.0150
VISION_COST_PER_PIXEL = 0.002125 / (1024 * 150)


class ImageSize(BaseModel):
    width: int
    height: int


def calculate_price(input_data):
    """
    Calculate the price of a request based on the input data

    Args:
        input_data (Union[ImageSize, CompletionUsage]): The input data for the request.

    Returns:
        float: The price of the request

    Raises:
        ValueError: If the input data is not of the correct type
    """
    if isinstance(input_data, ImageSize):
        total_pixels = input_data.width * input_data.height
        price = total_pixels * VISION_COST_PER_PIXEL
    elif isinstance(input_data, CompletionUsage):
        input_cost = (input_data.prompt_tokens / 1000) * INPUT_TOKEN_COST
        output_cost = (input_data.completion_tokens / 1000) * OUTPUT_TOKEN_COST
        price = input_cost + output_cost
    else:
        raise ValueError("Invalid input data type.")

    return price


import re


def url_to_slug(url: str) -> str:
    # Remove 'https://', 'http://', and 'www.' from the URL
    if url.startswith('https://'):
        url = url[len('https://'):]
    elif url.startswith('http://'):
        url = url[len('http://'):]

    if url.startswith('www.'):
        url = url[len('www.'):]

    # Remove trailing slash if present
    if url.endswith('/'):
        url = url[:-1]

    # Remove all non-alphanumeric characters except hyphens and slashes
    url = re.sub(r'[^\w\-\/]', ' ', url)

    # Replace sequences of spaces or slashes with a single hyphen
    slug = re.sub(r'[\s\/]+', '-', url)

    # Convert to lowercase
    slug = slug.lower()

    return slug


def remove_null_values(data):
    """
    Remove keys with null values from a JSON object.

    Args:
        data (dict or list): The JSON object.

    Returns:
        dict or list: The cleaned JSON object.
    """
    if isinstance(data, dict):
        return {k: remove_null_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_null_values(item) for item in data if item is not None]
    else:
        return data


if __name__ == '__main__':
    image_size = ImageSize(width=1280, height=1060)
    print(f"Image request price: ${calculate_price(image_size):.6f}")

    completion_usage = CompletionUsage(completion_tokens=375, prompt_tokens=1597, total_tokens=1972)
    print(f"Completion request price: ${calculate_price(completion_usage):.6f}")
