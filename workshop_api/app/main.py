from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.database import Base, engine
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.routers import student_router, workshop_router, registration_router

# import models để Base nhận diện đầy đủ bảng trước khi create_all
from app.models import student, workshop, registration  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workshop Registration API")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(student_router.router)
app.include_router(workshop_router.router)
app.include_router(registration_router.router)


@app.get("/")
def root():
    return {"message": "Workshop Registration API is running"}
