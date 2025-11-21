from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.api.deps import get_db
from app.api.v1 import api_router
from app.core.logging import logger


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "SGHU API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX
    }


@app.get("/health")
def health_check():
    """Health check básico del servidor"""
    return {"status": "ok", "service": "sghu-api"}


@app.get(f"{settings.API_V1_PREFIX}/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Health check de la base de datos"""
    try:
        # Ejecutar query simple para verificar conexión
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "configured"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"API available at {settings.API_V1_PREFIX}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    logger.info("Shutting down SGHU API")

