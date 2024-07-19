from celery.worker.state import requests
from langsmith import traceable
from tenacity import retry, stop_after_attempt

from app.setup_logging import setup_logging

logger = setup_logging(__name__)


@traceable(run_type="tool")
@retry(stop=stop_after_attempt(3))
def internet_search(query: str) -> dict:
    """
    Fetch additional information from the web using the specified mechanism.

    Parameters:
    - query: str: The search query for fetching additional information.

    Returns:
    - dict: The response from the web request containing additional information.
    """

    logger.info(f"Fetching web info for query: `{query}`")

    url = f"https://s.jina.ai/{query.replace(' ', '%20')}"

    headers = {
        # "X-With-Generated-Alt": "true",
        # "X-With-Images-Summary": "true",
        # "X-With-Links-Summary": "true",
        "X-No-Cache": "true",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Web info fetched successfully for query `{query}`")

        return response.json()
    else:
        response.raise_for_status()
