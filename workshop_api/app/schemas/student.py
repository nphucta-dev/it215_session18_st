from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class StudentCreate(BaseModel):
    student_code: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    status: str = "ACTIVE"


class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class StudentWorkshopItem(BaseModel):
    registration_id: int
    workshop_id: int
    title: str
    start_time: str
    registration_status: str
    model_config = ConfigDict(from_attributes=True)
