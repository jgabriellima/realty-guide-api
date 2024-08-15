from fastapi import APIRouter

from app.api.endpoints.v1.api_agent import agent_router
from app.api.endpoints.v1.api_client import client_router
from app.api.endpoints.v1.api_property import property_router
from app.api.endpoints.v1.api_task import api_task_router
from app.api.endpoints.v1.api_whatsapp import api_whatsapp_router

api_router = APIRouter()

api_router.include_router(property_router, prefix="/properties", tags=["Property"])
api_router.include_router(client_router, prefix="/clients", tags=["Client"])
api_router.include_router(agent_router, prefix="/agents", tags=["Agent"])
api_router.include_router(api_task_router, prefix="/tasks", tags=["Task"])
api_router.include_router(api_whatsapp_router, prefix="/whatsapp", tags=["Whatsapp"])
