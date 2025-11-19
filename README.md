# SGHU - Sistema de Gestión de Horarios Universitarios

Sistema para gestionar la matrícula y generación automática de horarios en una universidad, con motor de optimización híbrido (Constraint Programming + Algoritmos Genéticos).

## 🎯 Características Principales

- ✅ Gestión completa del proceso de matrícula
- 🤖 Generación automática de horarios optimizados
- 🔄 Procesamiento asíncrono con Celery
- 📊 Validación exhaustiva de reglas académicas
- 🎨 Motor híbrido de optimización (OR-Tools + DEAP)
- 📡 API REST completa con FastAPI
- 🗄️ PostgreSQL para persistencia
- 🔧 Simulación de integraciones (Odoo, Moodle)

## 🏗️ Arquitectura
```
┌─────────────────┐
│   Frontend      │  (Simulado con scripts)
│   (Vue.js)      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   API Gateway   │  FastAPI
│   (FastAPI)     │  ├─ Validaciones
└────────┬────────┘  ├─ Motor de horarios
         │           └─ Workers asíncronos
         v
┌─────────────────┐
│   PostgreSQL    │  ├─ Schema "source" (simulado)
│                 │  └─ Schema "sghu" (sistema)
└─────────────────┘
```

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recomendado)

## 🚀 Quick Start

### Opción A: Setup Automático (Recomendado)

**Linux/Mac:**
```bash
cd backend
./setup.sh
```

**Windows:**
```cmd
cd backend
setup.bat
```

El script automáticamente:
- Crea el entorno virtual
- Instala todas las dependencias
- Crea el archivo `.env` desde `.env.example`

### Opción B: Setup Manual

### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/sghu.git
cd sghu
```

### 2. Setup con Docker
```bash
cd backend
docker-compose up -d
```

### 3. Instalar dependencias
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar base de datos
```bash
alembic upgrade head
```

### 6. Poblar con datos simulados
```bash
python scripts/populate_db.py
```

### 7. Iniciar servidor
```bash
uvicorn app.main:app --reload
```

### 8. Iniciar workers (en otra terminal)
```bash
celery -A app.core.celery_app worker --loglevel=info
```

## 📚 Documentación

- [Arquitectura del Sistema](docs/arquitectura.md)
- [Motor de Horarios](docs/motor-horarios.md)
- [Workers Asíncronos](docs/workers-asincrono.md)
- [Reglas de Negocio](docs/reglas-negocio.md)
- [API Reference](http://localhost:8000/docs) (Swagger)

## 🧪 Testing
```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/
```

## 📊 Simulaciones
```bash
# Simular flujo de un estudiante
python scripts/simulate_student_flow.py --student-id 1

# Simular matrícula masiva
python scripts/simulate_mass_enrollment.py --students 100 --workers 10

### Analizar resultados
python scripts/analyze_simulation_results.py mass_enrollment_results.json
```

## 🔧 Tecnologías

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0
- Pydantic V2
- Celery + Redis
- Google OR-Tools
- DEAP (Genetic Algorithms)

**Database:**
- PostgreSQL 15+

**Testing:**
- Pytest
- HTTPx

## 📈 Performance

| Métrica | Valor |
|---------|-------|
| Generación CP-SAT | < 2s |
| Optimización AG | < 10s |
| Throughput | > 5 estudiantes/s |
| Coverage | > 80% |

## 🤝 Contribuir

Este es un proyecto de aprendizaje. Para contribuir:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE)

## 👤 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Google OR-Tools por el solver de constraints
- DEAP por el framework de algoritmos genéticos
- FastAPI por el excelente framework web