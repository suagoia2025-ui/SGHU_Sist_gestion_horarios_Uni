"""
Funciones utilitarias
"""
from typing import Optional
from datetime import date, datetime


def format_date(date_obj: Optional[date]) -> Optional[str]:
    """Formatea una fecha a string"""
    if date_obj is None:
        return None
    return date_obj.isoformat()


def format_datetime(datetime_obj: Optional[datetime]) -> Optional[str]:
    """Formatea un datetime a string"""
    if datetime_obj is None:
        return None
    return datetime_obj.isoformat()


def get_day_name(day_of_week: int) -> str:
    """Convierte número de día a nombre"""
    days = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }
    return days.get(day_of_week, "Desconocido")

