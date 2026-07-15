from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.response import build_response
from app.schemas.student import StudentCreate, StudentResponse
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("")
def create_student(data: StudentCreate, request: Request, db: Session = Depends(get_db)):
    service = StudentService(db)
    student = service.create_student(data)
    return build_response(
        status_code=201,
        data=StudentResponse.model_validate(student),
        message="Tạo sinh viên thành công",
        request=request,
    )


@router.get("")
def get_students(request: Request, db: Session = Depends(get_db)):
    service = StudentService(db)
    students = service.get_students()
    data = [StudentResponse.model_validate(s) for s in students]
    return build_response(
        status_code=200,
        data=data,
        message="Lấy danh sách sinh viên thành công",
        request=request,
    )
