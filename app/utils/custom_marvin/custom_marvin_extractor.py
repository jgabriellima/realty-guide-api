from typing import (
    GenericAlias,
    Optional,
    TypeVar,
    Union,
)

import marvin
import marvin.utilities.tools
from cachetools import LRUCache
from langsmith import traceable
from marvin.ai.prompts.text_prompts import (
    EXTRACT_PROMPT,
)
from marvin.ai.text import generate_llm_response, prepare_data
from marvin.client.openai import (
    AsyncMarvinClient,
)
from marvin.types import Image, ChatResponse
from marvin.utilities.asyncio import run_sync
from marvin.utilities.logging import get_logger
from pydantic import BaseModel

T = TypeVar("T")
M = TypeVar("M", bound=BaseModel)
FN_INPUT_TYPES = Union[str, Image, list[Union[str, Image]]]

logger = get_logger(__name__)

GENERATE_CACHE = LRUCache(maxsize=1000)
logger = get_logger(__name__)

GENERATE_CACHE = LRUCache(maxsize=1000)


async def _generate_typed_llm_response_with_tool(
        prompt_template: str,
        type_: Union[GenericAlias, type[T]],
        tool_name: Optional[str] = None,
        prompt_kwargs: Optional[dict] = None,
        model_kwargs: Optional[dict] = None,
        client: Optional[AsyncMarvinClient] = None,
) -> ChatResponse:
    """
    Generates a language model response based on a provided prompt template and a specific tool.

    This function uses a language model to generate a response based on a
    provided prompt template. The response is cast to a Python type using a tool
    call. The function supports additional arguments for the prompt and the
    language model.

    Args:
        prompt_template (str): The template for the prompt.
        type_ (Union[GenericAlias, type[T]]): The type of the response to
            generate.
        tool_name (str, optional): The name of the tool to use for the
            generation. Defaults to None.
        prompt_kwargs (dict, optional): Additional keyword arguments for the
            prompt. Defaults to None.
        model_kwargs (dict, optional): Additional keyword arguments for the
            language model. Defaults to None.
        client (MarvinClient, optional): The client to use for the AI function.

    Returns:
        T: The generated response from the language model.
    """
    model_kwargs = model_kwargs or {}
    prompt_kwargs = prompt_kwargs or {}
    tool = marvin.utilities.tools.tool_from_type(type_, tool_name=tool_name)
    tool_choice = {
        "type": "function",
        "function": {"name": tool.function.name},
    }
    model_kwargs.update(tools=[tool], tool_choice=tool_choice)

    # adding the tool parameters to the context helps GPT-4 pay attention to field
    # descriptions. If they are only in the tool signature it often ignores them.
    prompt_kwargs["response_format"] = tool.function.parameters

    response = await generate_llm_response(
        prompt_template=prompt_template,
        prompt_kwargs=prompt_kwargs,
        model_kwargs=model_kwargs,
        client=client,
    )

    return response


async def custom_extract_async(
        data: FN_INPUT_TYPES,
        target: type[T] = None,
        instructions: Optional[str] = None,
        model_kwargs: Optional[dict] = None,
        client: Optional[AsyncMarvinClient] = None,
) -> ChatResponse:
    """
    Extracts entities of a specific type from the provided data.

    This function uses a language model to identify and extract entities of the
    specified type from the input data. The extracted entities are returned as a
    list.

    Note that *either* a target type or instructions must be provided (or both).
    If only instructions are provided, the target type is assumed to be a
    string.

    Args:
        data: Union[str, Image, list[Union[str, Image]]]: the data to which
            the function will be applied.
        target (type, optional): The type of entities to extract.
        instructions (str, optional): Specific instructions for the extraction.
            Defaults to None.
        model_kwargs (dict, optional): Additional keyword arguments for the
            language model. Defaults to None.
        client (MarvinClient, optional): The client to use for the AI function.

    Returns:
        list: A list of extracted entities of the specified type.
    """
    model_kwargs = model_kwargs or {}

    if target is None and instructions is None:
        raise ValueError("Must provide either a target type or instructions.")
    elif target is None:
        target = str

    data = prepare_data(data)

    return await _generate_typed_llm_response_with_tool(
        prompt_template=EXTRACT_PROMPT,
        prompt_kwargs=dict(data=data, instructions=instructions),
        type_=list[target],
        model_kwargs=model_kwargs | dict(temperature=0),
        client=client,
    )


@traceable(run_type="llm")
def custom_data_extractor(
        data: FN_INPUT_TYPES,
        target: type[T] = None,
        instructions: Optional[str] = None,
        model_kwargs: Optional[dict] = None,
        client: Optional[AsyncMarvinClient] = None,
) -> ChatResponse:
    """
    Extracts entities of a specific type from the provided data.

    This function uses a language model to identify and extract entities of the
    specified type from the input data. The extracted entities are returned as a
    list.

    Note that *either* a target type or instructions must be provided (or both).
    If only instructions are provided, the target type is assumed to be a
    string.

    Args:
        data: Union[str, Image, list[Union[str, Image]]]: the data to which
            the function will be applied.
        target (type, optional): The type of entities to extract.
        instructions (str, optional): Specific instructions for the extraction.
            Defaults to None.
        model_kwargs (dict, optional): Additional keyword arguments for the
            language model. Defaults to None.
        client (AsyncMarvinClient, optional): The client to use for the AI function.

    Returns:
        list: A list of extracted entities of the specified type.
    """
    return run_sync(
        custom_extract_async(
            data=data,
            target=target,
            instructions=instructions,
            model_kwargs=model_kwargs,
            client=client,
        )
    )
