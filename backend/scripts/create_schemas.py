"""
Script para crear los schemas en PostgreSQL.
Debe ejecutarse antes de las migraciones.

Ejecutar desde backend/ con: python -m scripts.create_schemas
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.config import settings


def create_schemas():
    """Crear schemas si no existen"""
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    with engine.connect() as conn:
        print("🔧 Creando schema 'source'...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS source"))
        
        print("🔧 Creando schema 'sghu'...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS sghu"))
        
        conn.commit()
    
    print("✅ Schemas creados exitosamente")
    engine.dispose()


if __name__ == "__main__":
    create_schemas()

