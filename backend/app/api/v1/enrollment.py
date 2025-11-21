"""
Endpoints para matrícula (versión básica)
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollment import EnrollmentRead

router = APIRouter()


@router.get("/{enrollment_id}", response_model=EnrollmentRead)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una matrícula por ID
    """
    service = EnrollmentService(db)
    return service.get_enrollment(enrollment_id)


@router.get("/students/{student_id}/enrollments", response_model=List[EnrollmentRead])
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las matrículas de un estudiante
    """
    service = EnrollmentService(db)
    return service.get_enrollments_by_student(student_id)

