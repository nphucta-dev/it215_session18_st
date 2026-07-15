from datetime import datetime
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.student import Student, StudentStatus
from app.models.workshop import Workshop, WorkshopStatus
from app.models.registration import Registration, RegistrationStatus
from app.schemas.registration import RegistrationCreate


class RegistrationService:
    def __init__(self, db: Session):
        self.db = db

    def _get_student_or_404(self, student_id: int) -> Student:
        student = self.db.execute(
            select(Student).where(Student.id == student_id)
        ).scalar_one_or_none()
        if student is None:
            raise HTTPException(status_code=404, detail="Sinh viên không tồn tại")
        return student

    def _get_workshop_or_404(self, workshop_id: int) -> Workshop:
        workshop = self.db.execute(
            select(Workshop).where(Workshop.id == workshop_id)
        ).scalar_one_or_none()
        if workshop is None:
            raise HTTPException(status_code=404, detail="Workshop không tồn tại")
        return workshop

    def register(self, data: RegistrationCreate) -> Registration:
        # 1. Sinh viên phải tồn tại
        student = self._get_student_or_404(data.student_id)

        # 2. Sinh viên không hoạt động thì không được đăng ký
        if student.status != StudentStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Sinh viên không ở trạng thái hoạt động")

        # 3. Workshop phải tồn tại
        workshop = self._get_workshop_or_404(data.workshop_id)

        # 4. Workshop phải đang mở đăng ký
        if workshop.status == WorkshopStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Workshop đã bị hủy")
        if workshop.status == WorkshopStatus.CLOSED:
            raise HTTPException(status_code=400, detail="Workshop đã đóng đăng ký")

        # 5. Workshop đã bắt đầu thì không cho đăng ký
        if workshop.start_time <= datetime.now():
            raise HTTPException(status_code=400, detail="Workshop đã bắt đầu, không thể đăng ký")

        # 6. Không cho đăng ký trùng (chỉ tính các đăng ký đang REGISTERED)
        duplicate = self.db.execute(
            select(Registration).where(
                Registration.student_id == data.student_id,
                Registration.workshop_id == data.workshop_id,
                Registration.status == RegistrationStatus.REGISTERED,
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(status_code=400, detail="Sinh viên đã đăng ký workshop này")

        # 7. Không vượt quá số lượng tối đa
        current_count = self.db.execute(
            select(func.count()).select_from(Registration).where(
                Registration.workshop_id == data.workshop_id,
                Registration.status == RegistrationStatus.REGISTERED,
            )
        ).scalar_one()
        if current_count >= workshop.maximum_participants:
            raise HTTPException(status_code=400, detail="Workshop đã đủ số lượng đăng ký")

        registration = Registration(
            student_id=data.student_id,
            workshop_id=data.workshop_id,
            status=RegistrationStatus.REGISTERED,
        )
        self.db.add(registration)
        self.db.flush()
        self.db.refresh(registration)
        return registration

    def cancel_registration(self, registration_id: int) -> Registration:
        registration = self.db.execute(
            select(Registration).where(Registration.id == registration_id)
        ).scalar_one_or_none()
        if registration is None:
            raise HTTPException(status_code=404, detail="Đăng ký không tồn tại")

        if registration.status == RegistrationStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Đăng ký đã được hủy trước đó")

        registration.status = RegistrationStatus.CANCELLED
        self.db.flush()
        self.db.refresh(registration)
        return registration

    def get_student_workshops(self, student_id: int) -> List[Registration]:
        self._get_student_or_404(student_id)
        return list(
            self.db.execute(
                select(Registration).where(Registration.student_id == student_id)
            ).scalars().all()
        )

    def get_workshop_students(self, workshop_id: int) -> List[Registration]:
        self._get_workshop_or_404(workshop_id)
        return list(
            self.db.execute(
                select(Registration).where(Registration.workshop_id == workshop_id)
            ).scalars().all()
        )
