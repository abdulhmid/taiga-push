from pydantic import BaseModel, Field
from datetime import datetime


class TaskCreate(BaseModel):
    subject: str = Field(..., max_length=255)
    description: str
    talent: str = Field(..., max_length=100)
    estimation: float


class TaskRead(TaskCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
