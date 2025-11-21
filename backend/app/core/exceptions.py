"""
Excepciones personalizadas para la aplicación
"""
from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Excepción para recursos no encontrados"""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} con id {resource_id} no encontrado"
        )


class ValidationError(HTTPException):
    """Excepción para errores de validación"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class ConflictError(HTTPException):
    """Excepción para conflictos (ej: recurso duplicado)"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


class DatabaseError(HTTPException):
    """Excepción para errores de base de datos"""
    def __init__(self, message: str = "Error en la base de datos"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

