from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.student import Student
from app.schemas.student import StudentCreate


class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def create_student(self, data: StudentCreate) -> Student:
        existing_code = self.db.execute(
            select(Student).where(Student.student_code == data.student_code)
        ).scalar_one_or_none()
        if existing_code:
            raise HTTPException(status_code=400, detail="Mã sinh viên đã tồn tại")

        existing_email = self.db.execute(
            select(Student).where(Student.email == data.email)
        ).scalar_one_or_none()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email đã tồn tại")

        student = Student(
            student_code=data.student_code,
            full_name=data.full_name,
            email=data.email,
            status=data.status,
        )
        self.db.add(student)
        self.db.flush()
        self.db.refresh(student)
        return student

    def get_students(self) -> List[Student]:
        return list(self.db.execute(select(Student)).scalars().all())

    def get_student_by_id(self, student_id: int) -> Student:
        student = self.db.execute(
            select(Student).where(Student.id == student_id)
        ).scalar_one_or_none()
        if student is None:
            raise HTTPException(status_code=404, detail="Sinh viên không tồn tại")
        return student
