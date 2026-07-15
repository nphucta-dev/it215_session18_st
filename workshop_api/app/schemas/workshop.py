from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WorkshopCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    maximum_participants: int = Field(..., gt=0)
    status: str = "OPEN"
    start_time: datetime


class WorkshopResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    maximum_participants: int
    status: str
    start_time: datetime
    model_config = ConfigDict(from_attributes=True)


class WorkshopStudentItem(BaseModel):
    registration_id: int
    student_id: int
    student_code: str
    full_name: str
    registration_status: str
    model_config = ConfigDict(from_attributes=True)
