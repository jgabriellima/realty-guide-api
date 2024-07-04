from fastapi import APIRouter, HTTPException

from app.api.endpoints.mock_data import mock_agent_data
from app.schemas.tools import StoreAgentDataResponse, StoreAgentDataRequest, RetrieveAgentDataRequest, \
    RetrieveAgentDataResponse

agent_router = APIRouter()


@agent_router.post("/store_data", response_model=StoreAgentDataResponse)
def store_agent_data(request: StoreAgentDataRequest):
    mock_agent_data[request.agent_id] = {"interaction_data": request.interaction_data}
    return StoreAgentDataResponse(status="Data stored successfully")


@agent_router.post("/retrieve_data", response_model=RetrieveAgentDataResponse)
def retrieve_agent_data(request: RetrieveAgentDataRequest):
    if request.agent_id in mock_agent_data:
        return RetrieveAgentDataResponse(interaction_data=mock_agent_data[request.agent_id]["interaction_data"])
    else:
        raise HTTPException(status_code=404, detail="Agent data not found")
