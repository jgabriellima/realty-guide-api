from typing import Type, TypeVar, List, Union

from app.core.setup_logging import setup_logging

T = TypeVar('T')

logger = setup_logging("ParsersUtils")


def parse_to_schema(schema: Type[T], data: List[dict]) -> Union[T, List[T], None]:
    """
    Parse data to a Pydantic schema

    :param schema: Pydantic schema
    :param data: Data to be parsed

    :return: Pydantic schema
    """
    logger.info(f"parse_to_schema:Data:: {data}")
    parsed_data = [schema(**item) for item in data]
    if len(parsed_data) == 1:
        return parsed_data[0]
    elif len(parsed_data) > 1:
        return parsed_data
    else:
        return None
