from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.response import build_response
from app.schemas.workshop import WorkshopCreate, WorkshopResponse, WorkshopStudentItem
from app.services.workshop_service import WorkshopService
from app.services.registration_service import RegistrationService

router = APIRouter(prefix="/workshops", tags=["Workshops"])


@router.post("")
def create_workshop(data: WorkshopCreate, request: Request, db: Session = Depends(get_db)):
    service = WorkshopService(db)
    workshop = service.create_workshop(data)
    return build_response(
        status_code=201,
        data=WorkshopResponse.model_validate(workshop),
        message="Tạo workshop thành công",
        request=request,
    )


@router.get("")
def get_workshops(request: Request, db: Session = Depends(get_db)):
    service = WorkshopService(db)
    workshops = service.get_workshops()
    data = [WorkshopResponse.model_validate(w) for w in workshops]
    return build_response(
        status_code=200,
        data=data,
        message="Lấy danh sách workshop thành công",
        request=request,
    )


@router.get("/{workshop_id}")
def get_workshop_detail(workshop_id: int, request: Request, db: Session = Depends(get_db)):
    service = WorkshopService(db)
    workshop = service.get_workshop_by_id(workshop_id)
    return build_response(
        status_code=200,
        data=WorkshopResponse.model_validate(workshop),
        message="Lấy chi tiết workshop thành công",
        request=request,
    )


@router.get("/{workshop_id}/students")
def get_workshop_students(workshop_id: int, request: Request, db: Session = Depends(get_db)):
    service = RegistrationService(db)
    registrations = service.get_workshop_students(workshop_id)
    data = [
        WorkshopStudentItem(
            registration_id=r.id,
            student_id=r.student.id,
            student_code=r.student.student_code,
            full_name=r.student.full_name,
            registration_status=r.status,
        )
        for r in registrations
    ]
    return build_response(
        status_code=200,
        data=data,
        message="Lấy danh sách sinh viên của workshop thành công",
        request=request,
    )
