from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.response import build_response
from app.schemas.registration import RegistrationCreate, RegistrationResponse
from app.schemas.student import StudentWorkshopItem
from app.services.registration_service import RegistrationService

router = APIRouter(tags=["Registrations"])


@router.post("/registrations")
def register_workshop(data: RegistrationCreate, request: Request, db: Session = Depends(get_db)):
    service = RegistrationService(db)
    registration = service.register(data)
    return build_response(
        status_code=201,
        data=RegistrationResponse.model_validate(registration),
        message="Đăng ký workshop thành công",
        request=request,
    )


@router.put("/registrations/{registration_id}")
def cancel_registration(registration_id: int, request: Request, db: Session = Depends(get_db)):
    service = RegistrationService(db)
    registration = service.cancel_registration(registration_id)
    return build_response(
        status_code=200,
        data=RegistrationResponse.model_validate(registration),
        message="Hủy đăng ký thành công",
        request=request,
    )


@router.get("/students/{student_id}/workshops")
def get_student_workshops(student_id: int, request: Request, db: Session = Depends(get_db)):
    service = RegistrationService(db)
    registrations = service.get_student_workshops(student_id)
    data = [
        StudentWorkshopItem(
            registration_id=r.id,
            workshop_id=r.workshop.id,
            title=r.workshop.title,
            start_time=r.workshop.start_time.isoformat(),
            registration_status=r.status,
        )
        for r in registrations
    ]
    return build_response(
        status_code=200,
        data=data,
        message="Lấy danh sách workshop của sinh viên thành công",
        request=request,
    )
