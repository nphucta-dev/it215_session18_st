from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RegistrationCreate(BaseModel):
    student_id: int
    workshop_id: int


class RegistrationResponse(BaseModel):
    id: int
    student_id: int
    workshop_id: int
    registered_at: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)
