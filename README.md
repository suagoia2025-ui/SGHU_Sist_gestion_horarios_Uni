# SGHU - Sistema de Gestión de Horarios Universitarios

Sistema para gestionar la matrícula y generación automática de horarios en una universidad, con motor de optimización híbrido (Constraint Programming + Algoritmos Genéticos).

## 🎯 Características Principales

- ✅ Gestión completa del proceso de matrícula
- ✅ Generación automática de horarios optimizados ✅ **FASE 5-6 COMPLETADA**
- 🔄 Procesamiento asíncrono con Celery (FASE 7)
- ✅ Validación exhaustiva de reglas académicas ✅ **COMPLETADO**
- ✅ Motor híbrido de optimización (OR-Tools + DEAP) ✅ **COMPLETADO**
- ✅ API REST completa con FastAPI ✅ **COMPLETADO**
- ✅ PostgreSQL para persistencia ✅ **COMPLETADO**
- ✅ Simulación de integraciones (Odoo, Moodle) ✅ **COMPLETADO**
- ✅ Persistencia de horarios generados ✅ **COMPLETADO**
- ✅ Endpoints de consulta y análisis ✅ **COMPLETADO**

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

### 7. Iniciar servidor FastAPI
```bash
# Desde el directorio backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **DB Health Check**: http://localhost:8000/api/v1/health/db

### Endpoints Disponibles

#### Estudiantes
- `GET /api/v1/students` - Lista estudiantes
- `GET /api/v1/students/{id}` - Obtener estudiante
- `GET /api/v1/students/{id}/academic-history` - Historial académico
- `GET /api/v1/students/{id}/financial-status` - Estado financiero
- `GET /api/v1/students/{id}/eligible-subjects` - Asignaturas elegibles
- `GET /api/v1/students/{id}/enrollment-status` - Estado de matrícula

#### Asignaturas y Programas
- `GET /api/v1/programs` - Lista programas
- `GET /api/v1/subjects` - Lista asignaturas
- `GET /api/v1/course-sections` - Lista secciones
- `GET /api/v1/academic-periods/current` - Período activo

#### Validación de Matrícula
- `POST /api/v1/enrollment/validate` - Validar solicitud de matrícula
  ```json
  {
    "student_id": 1,
    "academic_period_id": 1,
    "section_ids": [1, 2, 3, 4, 5]
  }
  ```

#### Generación de Horarios
- `POST /api/v1/schedules/generate` - Generar horario optimizado
  ```json
  {
    "student_id": 1,
    "selected_subject_ids": [1, 2, 3, 4, 5],
    "academic_period_id": 1,
    "optimization_level": "medium"  // "none" | "low" | "medium" | "high"
  }
  ```

#### Consulta de Horarios
- `GET /api/v1/schedules/students/{student_id}` - Listar horarios de un estudiante
- `GET /api/v1/schedules/{schedule_id}` - Detalles de un horario específico
- `GET /api/v1/schedules/{schedule_id}/compare/{other_schedule_id}` - Comparar dos horarios
- `GET /api/v1/schedules/students/{student_id}/stats` - Estadísticas de horarios

Ver [Ejemplos de Validación](backend/scripts/EJEMPLOS_VALIDACION.md) y [Ejemplos de Consulta](backend/scripts/EJEMPLOS_ENDPOINTS_CONSULTA.md) para más detalles.

### 8. Probar la API
```bash
# Ejecutar script de pruebas básicas
python scripts/test_api.py

# Ejecutar script de pruebas de validación
./scripts/test_validaciones.sh

# O probar manualmente con curl
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/students?limit=5
curl http://localhost:8000/api/v1/programs

# Probar validación de matrícula
curl -X POST http://localhost:8000/api/v1/enrollment/validate \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "academic_period_id": 1, "section_ids": [1, 2, 3]}' | python3 -m json.tool
```

### 9. Iniciar workers (en otra terminal - FASE 7)
```bash
celery -A app.core.celery_app worker --loglevel=info
```

## 📚 Documentación

### Documentación Principal
- [Índice de Documentación](docs/INDICE_DOCUMENTACION.md) - Índice completo de toda la documentación
- [Plan de Trabajo](docs/plan_trabajo.md) - Fases del proyecto
- [Fase 1: Base de Datos](docs/fase1-base-datos.md) ✅ Completada
- [Fase 6: Motor de Horarios - Optimización](docs/fase6-motor-horarios-optimizacion.md) ✅ Completada
- [Reglas de Negocio](docs/reglas-negocio.md) ✅ Completada
- [API Reference](http://localhost:8000/docs) (Swagger) ✅ Disponible

### Documentación de Endpoints
- [Ejemplos de Validación](backend/scripts/EJEMPLOS_VALIDACION.md) ✅ Disponible
- [Ejemplos de Consulta de Horarios](backend/scripts/EJEMPLOS_ENDPOINTS_CONSULTA.md) ✅ Disponible
- [Resumen de Endpoints de Consulta](backend/scripts/RESUMEN_ENDPOINTS_CONSULTA.md) ✅ Disponible

### Documentación de Motor de Horarios
- [Resultados de Pruebas de Optimización](backend/scripts/RESULTADOS_PRUEBAS_OPTIMIZACION.md) ✅ Disponible
- [Resultados de Pruebas Avanzadas](backend/scripts/RESULTADOS_PRUEBAS_AVANZADAS.md) ✅ Disponible
- [Resultados de Pruebas Específicas](backend/scripts/RESULTADOS_PRUEBAS_ESPECIFICAS.md) ✅ Disponible
- [Ajuste de Pesos de Fitness](backend/scripts/AJUSTE_PESOS_FITNESS.md) ✅ Disponible
- [Resultados con Pesos Ajustados](backend/scripts/RESULTADOS_PRUEBAS_PESOS_AJUSTADOS.md) ✅ Disponible
- [Resultados de Persistencia](backend/scripts/RESULTADOS_PERSISTENCIA.md) ✅ Disponible

### Documentación Técnica
- [Guía de Visualización de Tablas](backend/scripts/GUIA_VISUALIZACION_TABLAS.md) ✅ Disponible
- [Código Hardcodeado](backend/CODIGO_HARDCODEADO.md) ✅ Disponible
- [Auditoría del Proyecto](backend/AUDITORIA_PROYECTO.md) ✅ Disponible

## 🧪 Testing

### Tests Automatizados (FASE 8 - Pendiente)
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

### Pruebas Manuales Disponibles
```bash
# Probar endpoints básicos
python scripts/test_api.py

# Probar validaciones
./scripts/test_validaciones.sh

# Ver ejemplos de uso
cat backend/scripts/EJEMPLOS_VALIDACION.md
```

## 📊 Simulaciones y Scripts

### Scripts de Datos
```bash
# Poblar base de datos con datos simulados
python scripts/populate_db.py

# Ver tablas y datos
python scripts/view_tables.py

# Limpiar base de datos
python scripts/reset_db.py
```

### Scripts de Pruebas
```bash
# Probar endpoints básicos
python scripts/test_api.py

# Probar endpoints de validación
./scripts/test_validaciones.sh

# Probar función de fitness
python scripts/test_fitness.py

# Probar algoritmo de optimización
python scripts/test_optimization.py

# Probar optimización avanzada
python scripts/test_optimization_advanced.py

# Probar optimización específica
python scripts/test_optimization_specific.py

# Probar persistencia
python scripts/test_persistence.py
```

### Simulaciones (FASE 9 - Futuro)
```bash
# Simular flujo de un estudiante
python scripts/simulate_student_flow.py --student-id 1

# Simular matrícula masiva
python scripts/simulate_mass_enrollment.py --students 100 --workers 10

# Analizar resultados
python scripts/analyze_simulation_results.py mass_enrollment_results.json
```

## 🔧 Tecnologías

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0
- Pydantic V2
- Celery + Redis
- Google OR-Tools 9.12+ (CP-SAT Solver)
- DEAP 1.4+ (Algoritmos Genéticos)

**Database:**
- PostgreSQL 15+
- Alembic (Migraciones)

**Testing:**
- Pytest
- HTTPx

**Optimización:**
- OR-Tools CP-SAT: Restricciones duras
- DEAP: Optimización genética de restricciones blandas
- Motor híbrido: Combinación de ambos

## 📈 Estado del Proyecto

### ✅ Fases Completadas

- **FASE 0:** Setup del Proyecto ✅
- **FASE 1:** Diseño de Base de Datos ✅
- **FASE 2:** Scripts de Simulación ✅
- **FASE 3:** Estructura FastAPI Base ✅
- **FASE 4:** Lógica de Validación ✅
- **FASE 5:** Motor de Horarios - Parte 1 (Restricciones Duras) ✅
- **FASE 6:** Motor de Horarios - Parte 2 (Optimización) ✅

### 🚧 Fases Pendientes

- **FASE 7:** Workers Asíncronos
- **FASE 8:** Testing y Refinamiento
- **FASE 9:** Simulador Frontend

### 📊 Métricas Objetivo

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Generación CP-SAT | < 2s | ✅ **0.02-0.05s** |
| Optimización AG (medium) | < 10s | ✅ **0.07-0.14s** |
| Optimización AG (high) | < 30s | ✅ **0.3-0.7s** |
| Throughput | > 5 estudiantes/s | Pendiente (FASE 7) |
| Coverage | > 80% | Pendiente (FASE 8) |
| Validaciones implementadas | 6/6 | ✅ **100%** |
| Endpoints de validación | 3/3 | ✅ **100%** |
| Endpoints de horarios | 5/5 | ✅ **100%** |
| Persistencia de horarios | ✅ | ✅ **Implementada** |
| Restricciones duras preservadas | ✅ | ✅ **100%** |
| Mejora de calidad (optimización) | > 10% | ✅ **1019% promedio** |

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