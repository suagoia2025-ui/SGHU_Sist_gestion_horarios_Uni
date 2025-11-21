from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text

from alembic import context

# Importar configuración y modelos
from app.config import settings
from app.database import Base

# Importar TODOS los modelos para que Alembic los detecte
from app.models.source import academic, people, infrastructure, offer, student_data, rules, moodle
from app.models.sghu import enrollment, schedule, system

# Configuración de Alembic
config = context.config

# Configurar URL de base de datos desde settings
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Interpretar el archivo de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de los modelos
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="public",
        include_schemas=True,  # IMPORTANTE para múltiples schemas
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Crear schemas si no existen
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS source"))
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS sghu"))
        
        # Crear tabla de versiones de Alembic si no existe (con commit explícito)
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS public.alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        connection.commit()  # Commit explícito para que la tabla esté visible
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="public",  # Tabla de versiones en schema public
            include_schemas=True,  # IMPORTANTE para múltiples schemas
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
