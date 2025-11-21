"""
Script para aplicar la migración inicial manualmente.
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic import op
from app.config import settings

# Crear engine
engine = create_engine(settings.DATABASE_URL)

# Configurar contexto de Alembic
alembic_cfg = Config('alembic.ini')
script = ScriptDirectory.from_config(alembic_cfg)

# Obtener la migración head
head_revision = script.get_current_head()
revision = script.get_revision(head_revision)

# Ejecutar upgrade en una transacción (crear schemas, tabla de versiones y ejecutar migración)
with engine.begin() as conn:
    # Crear schemas y tabla de versiones en la misma transacción
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS source'))
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS sghu'))
    conn.execute(text('''
        CREATE TABLE IF NOT EXISTS public.alembic_version (
            version_num VARCHAR(32) NOT NULL PRIMARY KEY
        )
    '''))
    # Configurar contexto de migración
    context = MigrationContext.configure(conn)
    
    # Configurar op para que funcione usando el método correcto
    from alembic.operations import Operations
    op._proxy = Operations(context)
    
    # Importar y ejecutar upgrade
    import importlib.util
    import glob
    # Buscar el archivo de migración
    migration_files = glob.glob(f'alembic/versions/{revision.revision}_*.py')
    if not migration_files:
        raise FileNotFoundError(f"No se encontró el archivo de migración para {revision.revision}")
    migration_file = migration_files[0]
    spec = importlib.util.spec_from_file_location('migration', migration_file)
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    
    # Ejecutar upgrade
    try:
        migration_module.upgrade()
        print(f'✅ Migración {revision.revision} ejecutada exitosamente')
    except Exception as e:
        print(f'❌ Error al ejecutar migración: {e}')
        raise
    
    # Verificar que la tabla de versiones existe antes de insertar
    result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'alembic_version')"))
    table_exists = result.scalar()
    
    if not table_exists:
        # Crear tabla de versiones si no existe
        conn.execute(text('''
            CREATE TABLE public.alembic_version (
                version_num VARCHAR(32) NOT NULL PRIMARY KEY
            )
        '''))
    
    # Insertar versión
    conn.execute(text(f"INSERT INTO public.alembic_version (version_num) VALUES ('{revision.revision}') ON CONFLICT DO NOTHING"))

print(f'✅ Migración {revision.revision} aplicada exitosamente')

