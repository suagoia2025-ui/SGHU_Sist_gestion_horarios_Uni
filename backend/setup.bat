@echo off
REM Script de setup para SGHU - FASE 0 (Windows)
REM Este script ayuda a configurar el entorno de desarrollo

echo 🚀 Configurando SGHU - Sistema de Gestión de Horarios Universitarios
echo.

REM 1. Verificar Python
echo 📦 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instálalo primero.
    exit /b 1
)
echo ✅ Python encontrado

REM 2. Crear entorno virtual
echo.
echo 🔧 Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ⚠️  Entorno virtual ya existe
)

REM 3. Activar entorno virtual e instalar dependencias
echo.
echo 📥 Instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Dependencias instaladas

REM 4. Crear archivo .env si no existe
echo.
echo ⚙️  Configurando variables de entorno...
if not exist ".env" (
    copy .env.example .env
    echo ✅ Archivo .env creado desde .env.example
    echo ⚠️  Por favor revisa y ajusta las variables en .env si es necesario
) else (
    echo ⚠️  Archivo .env ya existe
)

echo.
echo ✨ Setup completado!
echo.
echo Próximos pasos:
echo 1. Activa el entorno virtual: venv\Scripts\activate
echo 2. Inicia los servicios: docker-compose up -d
echo 3. Inicializa la BD: alembic upgrade head
echo 4. Inicia el servidor: uvicorn app.main:app --reload

