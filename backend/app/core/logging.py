"""
Configuración de logging para la aplicación
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.config import settings


def setup_logging():
    """Configura el sistema de logging"""
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger principal
    logger = logging.getLogger("sghu")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    file_handler = RotatingFileHandler(
        'logs/sghu.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    return logger


# Crear logger global
logger = setup_logging()

