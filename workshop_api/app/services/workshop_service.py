from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.workshop import Workshop
from app.schemas.workshop import WorkshopCreate


class WorkshopService:
    def __init__(self, db: Session):
        self.db = db

    def create_workshop(self, data: WorkshopCreate) -> Workshop:
        workshop = Workshop(
            title=data.title,
            description=data.description,
            maximum_participants=data.maximum_participants,
            status=data.status,
            start_time=data.start_time,
        )
        self.db.add(workshop)
        self.db.flush()
        self.db.refresh(workshop)
        return workshop

    def get_workshops(self) -> List[Workshop]:
        return list(self.db.execute(select(Workshop)).scalars().all())

    def get_workshop_by_id(self, workshop_id: int) -> Workshop:
        workshop = self.db.execute(
            select(Workshop).where(Workshop.id == workshop_id)
        ).scalar_one_or_none()
        if workshop is None:
            raise HTTPException(status_code=404, detail="Workshop không tồn tại")
        return workshop
