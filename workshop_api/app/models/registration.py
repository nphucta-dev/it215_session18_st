from datetime import datetime
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RegistrationStatus:
    REGISTERED = "REGISTERED"
    CANCELLED = "CANCELLED"


class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    workshop_id: Mapped[int] = mapped_column(ForeignKey("workshops.id"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=RegistrationStatus.REGISTERED)

    student: Mapped["Student"] = relationship(back_populates="registrations")
    workshop: Mapped["Workshop"] = relationship(back_populates="registrations")
