from fastapi import APIRouter

from app.api.endpoints.v1.api_agent import agent_router
from app.api.endpoints.v1.api_client import client_router
from app.api.endpoints.v1.api_page_loader import page_loader
from app.api.endpoints.v1.api_property import property_router
from app.api.endpoints.v1.api_task import api_task_router

api_router = APIRouter()

api_router.include_router(property_router, prefix="/properties", tags=["properties"])
api_router.include_router(client_router, prefix="/clients", tags=["clients"])
api_router.include_router(agent_router, prefix="/agents", tags=["agents"])
api_router.include_router(agent_router, prefix="/agents", tags=["agents"])
api_router.include_router(api_task_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(page_loader, prefix="/pages", tags=["loaders"])
