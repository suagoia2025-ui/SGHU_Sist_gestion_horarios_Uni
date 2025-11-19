#!/bin/bash

# Script de setup para SGHU - FASE 0
# Este script ayuda a configurar el entorno de desarrollo

set -e

echo "🚀 Configurando SGHU - Sistema de Gestión de Horarios Universitarios"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar Python
echo "📦 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# 2. Crear entorno virtual
echo ""
echo "🔧 Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "⚠️  Entorno virtual ya existe"
fi

# 3. Activar entorno virtual e instalar dependencias
echo ""
echo "📥 Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencias instaladas"

# 4. Crear archivo .env si no existe
echo ""
echo "⚙️  Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Archivo .env creado desde .env.example"
    echo "⚠️  Por favor revisa y ajusta las variables en .env si es necesario"
else
    echo "⚠️  Archivo .env ya existe"
fi

# 5. Verificar Docker
echo ""
echo "🐳 Verificando Docker..."
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker y Docker Compose encontrados"
    echo "💡 Para iniciar los servicios, ejecuta: docker-compose up -d"
else
    echo "⚠️  Docker no está instalado. Instálalo para usar PostgreSQL y Redis."
fi

echo ""
echo "${GREEN}✨ Setup completado!${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Activa el entorno virtual: source venv/bin/activate"
echo "2. Inicia los servicios: docker-compose up -d"
echo "3. Inicializa la BD: alembic upgrade head"
echo "4. Inicia el servidor: uvicorn app.main:app --reload"

