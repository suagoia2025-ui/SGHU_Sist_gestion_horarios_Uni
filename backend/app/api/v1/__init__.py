"""
API v1 routers
"""
from fastapi import APIRouter
from app.api.v1 import students, subjects, enrollment, schedules

api_router = APIRouter()

# Incluir todos los routers
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(subjects.router, prefix="", tags=["subjects", "programs", "sections"])
api_router.include_router(enrollment.router, prefix="/enrollment", tags=["enrollment"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
