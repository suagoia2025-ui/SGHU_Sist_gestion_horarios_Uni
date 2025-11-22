# 🔍 Análisis de Código Hardcodeado

Este documento identifica valores hardcodeados en el código que deberían ser configurables.

## ⚠️ Valores Hardcodeados Encontrados

### 1. **Timeout del Solver** ⚠️ CRÍTICO
**Ubicación:** `backend/app/services/schedule_engine/constraint_solver.py:165`

```python
self.solver.parameters.max_time_in_seconds = 30.0  # Timeout de 30 segundos
```

**Problema:** El timeout está hardcodeado a 30 segundos. Debería ser configurable según el tamaño del problema.

**Solución recomendada:**
- Agregar a `app/config.py`: `SCHEDULE_SOLVER_TIMEOUT: float = 30.0`
- Usar variable de entorno: `SCHEDULE_SOLVER_TIMEOUT`

---

### 2. **Límites de Consultas** ⚠️ MEDIO
**Ubicación:** `backend/app/api/v1/enrollment.py:118`

```python
available_sections = section_repo.get_by_period(academic_period_id, skip=0, limit=1000)
```

**Problema:** El límite de 1000 está hardcodeado. Podría no ser suficiente para períodos con muchas secciones.

**Solución recomendada:**
- Agregar a `app/config.py`: `MAX_SECTIONS_PER_QUERY: int = 1000`
- O usar paginación adecuada

---

### 3. **URLs en Scripts de Prueba** ℹ️ BAJO (Solo en scripts)
**Ubicación:** Múltiples archivos en `backend/scripts/`

```bash
http://localhost:8000
```

**Problema:** URLs hardcodeadas en scripts de prueba y documentación.

**Solución recomendada:**
- Usar variables de entorno: `API_BASE_URL`
- O mantener como está (solo afecta scripts de prueba)

---

### 4. **Period ID en Scripts** ℹ️ BAJO (Solo en scripts)
**Ubicación:** Múltiples archivos en `backend/scripts/`

```sql
WHERE period_id = 1
```

**Problema:** Scripts de consulta usan `period_id = 1` hardcodeado.

**Solución recomendada:**
- Usar el período activo dinámicamente
- O documentar que es solo para ejemplos

---

### 5. **Secret Key por Defecto** ⚠️ CRÍTICO (Solo en desarrollo)
**Ubicación:** `backend/app/config.py:16`

```python
SECRET_KEY: str = "your-secret-key-here-change-in-production"
```

**Problema:** Secret key por defecto insegura.

**Solución recomendada:**
- ✅ Ya está configurado para usar `.env`
- ⚠️ Asegurarse de que en producción se use una clave segura
- Agregar validación que falle si es la clave por defecto en producción

---

### 6. **CORS Origins** ℹ️ MEDIO
**Ubicación:** `backend/app/config.py:19-22`

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:8080",
]
```

**Problema:** Orígenes CORS hardcodeados.

**Solución recomendada:**
- ✅ Ya está configurado para usar `.env`
- Agregar más orígenes según necesidad

---

## 📋 Plan de Acción

### Prioridad Alta (Crítico)
1. ✅ **Secret Key**: Ya configurado para `.env`, pero agregar validación en producción
2. ⚠️ **Solver Timeout**: Hacer configurable

### Prioridad Media
3. ⚠️ **Límites de consulta**: Hacer configurable o usar paginación
4. ℹ️ **CORS Origins**: Ya configurado, pero revisar

### Prioridad Baja (Solo scripts)
5. ℹ️ **URLs en scripts**: Mantener como está o usar variables
6. ℹ️ **Period ID en scripts**: Documentar o hacer dinámico

---

## 🔧 Implementación Recomendada

### 1. Agregar configuración para Solver Timeout

**`backend/app/config.py`:**
```python
class Settings(BaseSettings):
    # ... existing code ...
    
    # Schedule Solver
    SCHEDULE_SOLVER_TIMEOUT: float = 30.0  # Segundos
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

**`backend/app/services/schedule_engine/constraint_solver.py`:**
```python
from app.config import settings

# En el método solve():
self.solver.parameters.max_time_in_seconds = settings.SCHEDULE_SOLVER_TIMEOUT
```

### 2. Agregar límite configurable para consultas

**`backend/app/config.py`:**
```python
# API Limits
MAX_SECTIONS_PER_QUERY: int = 1000
MAX_SUBJECTS_PER_QUERY: int = 100
```

### 3. Validación de Secret Key en producción

**`backend/app/config.py`:**
```python
import os

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validar en producción
        if os.getenv("ENVIRONMENT") == "production":
            if self.SECRET_KEY == "your-secret-key-here-change-in-production":
                raise ValueError("SECRET_KEY debe ser cambiada en producción")
```

---

## ✅ Valores que YA están bien configurados

1. ✅ **DATABASE_URL**: Configurado para usar `.env`
2. ✅ **REDIS_URL**: Configurado para usar `.env`
3. ✅ **CORS_ORIGINS**: Configurado para usar `.env`
4. ✅ **LOG_LEVEL**: Configurado para usar `.env`

---

## 📝 Notas

- Los valores hardcodeados en **scripts de prueba/documentación** son aceptables
- Los valores hardcodeados en **código de producción** deben ser configurables
- Priorizar hacer configurables los valores que afectan:
  - Performance (timeouts, límites)
  - Seguridad (secret keys)
  - Comportamiento del sistema (límites de consulta)

