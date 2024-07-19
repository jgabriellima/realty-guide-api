from typing import Union

from fastapi import APIRouter

from app.schemas.real_estate import RealEstateAgent
from app.schemas.tools import SchedulerReminderRequest, AgentPreferencesRequest, \
    AgentLookupRequest
from app.services.real_estate_agent.real_estate_agent_service import RealEstateAgentService
from app.tasks.tasks import trigger_scheduled_remainder

agent_router = APIRouter()


@agent_router.post("/save_agent_memory_preferences", operation_id="save_agent_memory_preferences", response_model=str)
def save_agent_memory_preferences(request: AgentPreferencesRequest):
    """
    Save agent memory preferences
    :param request: AgentPreferencesRequest
    :return: str
    """
    agent = RealEstateAgentService().save_agent_memory(real_estate_agent_id=request.real_estate_agent_id,
                                                       parameter_name=request.parameter_name,
                                                       parameter_value_description=request.parameter_value_description)

    return agent


@agent_router.post("/agent_lookup", operation_id="agent_lookup", response_model=Union[str, RealEstateAgent])
def agent_lookup(request: AgentLookupRequest):
    """
    Lookup agent
    :param request: AgentLookupRequest
    :return: Union[str, RealEstateAgent]
    """
    agent = RealEstateAgentService().lookup(whatsapp_number=request.agent_whatsapp_number)
    return agent


@agent_router.post("/schedule_remainder", operation_id="schedule_remainder")
def schedule_remainder(request: SchedulerReminderRequest):
    """
    Schedule a remainder
    :param request: SchedulerReminderRequest
    :return: dict
    """
    trigger_scheduled_remainder.apply_async(args=[request.real_estate_agent_id, request.remainder_description],
                                            countdown=request.remainder_time_in_seconds)

    return {"message": "Remainder scheduled successfully."}
