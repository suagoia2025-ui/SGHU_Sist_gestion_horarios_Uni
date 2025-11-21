"""
Repository base con operaciones comunes
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import NotFoundError, DatabaseError

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Repository base con operaciones CRUD comunes"""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Obtiene un registro por ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error al obtener {self.model.__name__}: {str(e)}")
    
    def get_by_id_or_404(self, id: int) -> ModelType:
        """Obtiene un registro por ID o lanza 404"""
        obj = self.get_by_id(id)
        if obj is None:
            raise NotFoundError(self.model.__name__, id)
        return obj
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtiene todos los registros con paginación"""
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Error al obtener {self.model.__name__}: {str(e)}")
    
    def create(self, obj_data: dict) -> ModelType:
        """Crea un nuevo registro"""
        try:
            obj = self.model(**obj_data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error al crear {self.model.__name__}: {str(e)}")
    
    def update(self, id: int, obj_data: dict) -> ModelType:
        """Actualiza un registro"""
        try:
            obj = self.get_by_id_or_404(id)
            for key, value in obj_data.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error al actualizar {self.model.__name__}: {str(e)}")
    
    def delete(self, id: int) -> bool:
        """Elimina un registro"""
        try:
            obj = self.get_by_id_or_404(id)
            self.db.delete(obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Error al eliminar {self.model.__name__}: {str(e)}")

