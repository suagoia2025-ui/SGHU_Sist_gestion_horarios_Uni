"""
Modelos SQLAlchemy del proyecto SGHU
Organizados en esquemas: "source" y "sghu"
"""

# Importar todos los modelos para que SQLAlchemy los reconozca
from app.models.source.academic import Program, Subject, Prerequisite, StudyPlan
from app.models.source.people import Professor, Student
from app.models.source.infrastructure import Classroom
from app.models.source.offer import AcademicPeriod, CourseSection, SectionSchedule
from app.models.source.student_data import AcademicHistory, FinancialStatus
from app.models.source.rules import AcademicRule
from app.models.source.moodle import MoodleCourse, MoodleEnrollment

from app.models.sghu.enrollment import EnrollmentPeriod, StudentEnrollment, EnrollmentSubject
from app.models.sghu.schedule import GeneratedSchedule, ScheduleSlot, ScheduleConflict
from app.models.sghu.system import ProcessingLog

# Exportar todos los modelos
__all__ = [
    # Source schema - Academic
    "Program",
    "Subject",
    "Prerequisite",
    "StudyPlan",
    # Source schema - People
    "Professor",
    "Student",
    # Source schema - Infrastructure
    "Classroom",
    # Source schema - Offer
    "AcademicPeriod",
    "CourseSection",
    "SectionSchedule",
    # Source schema - Student Data
    "AcademicHistory",
    "FinancialStatus",
    # Source schema - Rules
    "AcademicRule",
    # Source schema - Moodle
    "MoodleCourse",
    "MoodleEnrollment",
    # SGHU schema - Enrollment
    "EnrollmentPeriod",
    "StudentEnrollment",
    "EnrollmentSubject",
    # SGHU schema - Schedule
    "GeneratedSchedule",
    "ScheduleSlot",
    "ScheduleConflict",
    # SGHU schema - System
    "ProcessingLog",
]
