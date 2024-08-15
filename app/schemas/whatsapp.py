from typing import List

from pydantic import BaseModel


class SendAudioRequest(BaseModel):
    conversation_id: str
    text_to_audio_message: str


class SendImageRequest(BaseModel):
    conversation_id: str
    image_url: List[str]
