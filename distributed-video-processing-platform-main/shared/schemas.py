from pydantic import BaseModel, Field
from typing import Literal

class ProcessRequest(BaseModel):
    resolutions: list[Literal["360p", "720p", "1080p"]] = Field(default_factory=lambda: ["360p", "720p"])

class JobResponse(BaseModel):
    job_id: str
    video_id: str
    status: str
    progress: int = 0
