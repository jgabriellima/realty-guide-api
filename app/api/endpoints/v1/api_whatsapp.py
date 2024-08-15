import requests
from fastapi import APIRouter

from app.core.settings import settings
from app.schemas.whatsapp import SendAudioRequest, SendImageRequest

api_whatsapp_router = APIRouter()


@api_whatsapp_router.post("/send_audio", operation_id="send_audio", response_model=str)
async def send_audio(request: SendAudioRequest) -> str:
    """
    Check the status of a task

    :param request: TaskStatusRequest
    :return: Union[str, Task]
    """
    res = requests.post(
        f"{settings.jambu_integrator_url}/v1/whatsapp/send_audio",
        json=request.model_dump(),
    )

    return res.text


@api_whatsapp_router.post("/send_image", operation_id="send_image", response_model=str)
async def send_image(request: SendImageRequest) -> str:
    """
    Check the status of a task

    :param request: TaskStatusRequest
    :return: Union[str, Task]
    """

    res = requests.post(
        f"{settings.jambu_integrator_url}/v1/whatsapp/send_image",
        json=request.model_dump(),
    )

    return res.text


if __name__ == '__main__':
    request = SendImageRequest(**{
        "conversation_id": "a8bf2867-496a-41a2-af58-12b19c8ae025",
        "image_url": ["https://gralhaaluguel.inforcedata.com.br/api/image/3464829.jpg",
                      "https://gralhaaluguel.inforcedata.com.br/api/image/3464830.jpg"]
    }
                               )

    res = requests.post(
        f"http://0.0.0.0:8080/v1/whatsapp/send_image",
        json=request.model_dump(),
    )
    print(res.text)
