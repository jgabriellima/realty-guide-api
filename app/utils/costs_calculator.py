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


if __name__ == '__main__':
    image_size = ImageSize(width=1280, height=1060)
    print(f"Image request price: ${calculate_price(image_size):.6f}")

    completion_usage = CompletionUsage(completion_tokens=375, prompt_tokens=1597, total_tokens=1972)
    print(f"Completion request price: ${calculate_price(completion_usage):.6f}")
