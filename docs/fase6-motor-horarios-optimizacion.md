# FASE 6: Motor de Horarios - Parte 2 (Optimización)

## Fecha de Completación: 2025-11-22

### Resumen

Implementación completa del motor de optimización de horarios usando Algoritmos Genéticos (DEAP) combinado con OR-Tools CP-SAT para optimizar restricciones blandas.

---

## 🎯 Objetivos Completados

1. ✅ Implementación de función de fitness con restricciones blandas
2. ✅ Implementación de algoritmo genético con DEAP
3. ✅ Motor híbrido (OR-Tools + Algoritmo Genético)
4. ✅ Integración en ScheduleService
5. ✅ Persistencia de horarios en base de datos
6. ✅ Endpoints de consulta y análisis
7. ✅ Pruebas exhaustivas y validación

---

## 📦 Componentes Implementados

### 1. Función de Fitness (`app/services/schedule_engine/fitness.py`)

Evalúa la calidad de un horario considerando:

- **Gaps (Huecos)**: Penaliza tiempo muerto entre clases del mismo día
  - Peso: 0.08 por minuto
- **Balance**: Penaliza distribución desbalanceada en la semana
  - Peso: 40.0 (aumentado para priorizar mejor distribución)
- **Preferencias de horario**: Penaliza clases muy temprano (< 7am) o muy tarde (> 6pm)
  - Peso: 5-20 puntos según horario
- **Días libres**: Bonifica tener días completamente libres
  - Bonus: -20 puntos por cada día libre

**Resultado**: Menor score = mejor horario

### 2. Algoritmo Genético (`app/services/schedule_engine/genetic_optimizer.py`)

Implementado con DEAP:

- **Representación**: Lista de IDs de secciones (un individuo = un horario)
- **Población**: 50-200 individuos según nivel de optimización
- **Generaciones**: 20-100 según nivel
- **Operadores**:
  - Selección: Tournament selection
  - Cruce: Uniform crossover
  - Mutación: Cambio aleatorio de sección
- **Evaluación**: Usa función de fitness

### 3. Motor Híbrido (`app/services/schedule_engine/hybrid_engine.py`)

Combina OR-Tools + Algoritmo Genético:

1. **Fase 1**: OR-Tools CP-SAT encuentra solución viable (restricciones duras)
2. **Fase 2**: Algoritmo Genético optimiza la solución (restricciones blandas)
3. **Comparación**: Retorna la mejor solución entre ambas

### 4. Persistencia (`app/services/schedule_service.py`)

- **`_get_or_create_enrollment()`**: Obtiene o crea StudentEnrollment
- **`_save_schedule()`**: Guarda GeneratedSchedule y ScheduleSlots
- **Métodos de consulta**: `get_generated_schedules_for_student()`, `get_schedule_details()`

### 5. Endpoints de Consulta (`app/api/v1/schedules.py`)

- **GET `/schedules/students/{id}`**: Lista horarios de un estudiante
- **GET `/schedules/{id}`**: Detalles de un horario
- **GET `/schedules/{id}/compare/{other_id}`**: Compara dos horarios
- **GET `/schedules/students/{id}/stats`**: Estadísticas agregadas

---

## 📊 Resultados de Pruebas

### Rendimiento

| Nivel | Tiempo Promedio | Población | Generaciones |
|-------|----------------|-----------|--------------|
| `none` | 0.044s | N/A | N/A |
| `low` | 0.069s | 50 | 20 |
| `medium` | 0.110s | 100 | 50 |
| `high` | 0.290s | 200 | 100 |

### Mejora de Calidad

- **Mejora promedio**: 27.35 puntos (1019.2% de mejora)
- **Rango de mejora**: 13-36 puntos según caso
- **Balance**: Se mantiene estable (no empeora)

### Validaciones

- ✅ **Restricciones duras preservadas**: 100%
- ✅ **Consistencia**: 100% (resultados reproducibles)
- ✅ **Tasa de éxito**: 100% en todas las pruebas

---

## 🔧 Configuración

### Niveles de Optimización

- **`none`**: Solo restricciones duras (OR-Tools CP-SAT)
- **`low`**: Optimización ligera (50 individuos, 20 generaciones)
- **`medium`**: Optimización balanceada (100 individuos, 50 generaciones) ⭐ **Recomendado**
- **`high`**: Optimización máxima (200 individuos, 100 generaciones)

### Pesos de Fitness (Ajustados)

| Componente | Peso | Descripción |
|------------|------|-------------|
| Gaps | 0.08/min | Penalización por huecos |
| Balance | 40.0 | Penalización por desbalance |
| Preferencias | 5-20 pts | Penalización por horarios no preferidos |
| Días libres | -20/día | Bonus por días libres |

---

## 📝 Organización de Días de la Semana

El campo `day_of_week` usa el estándar de Python `datetime.weekday()`:

- **0** = Lunes
- **1** = Martes
- **2** = Miércoles
- **3** = Jueves
- **4** = Viernes
- **5** = Sábado
- **6** = Domingo

---

## 🧪 Scripts de Pruebas

### Pruebas Básicas
```bash
python scripts/test_optimization.py
```

### Pruebas Avanzadas
```bash
python scripts/test_optimization_advanced.py
```

### Pruebas Específicas
```bash
python scripts/test_optimization_specific.py
```

### Pruebas de Persistencia
```bash
python scripts/test_persistence.py
```

### Pruebas de Fitness
```bash
python scripts/test_fitness.py
```

---

## 📚 Documentación Relacionada

- [Resultados de Pruebas de Optimización](backend/scripts/RESULTADOS_PRUEBAS_OPTIMIZACION.md)
- [Resultados de Pruebas Avanzadas](backend/scripts/RESULTADOS_PRUEBAS_AVANZADAS.md)
- [Resultados de Pruebas Específicas](backend/scripts/RESULTADOS_PRUEBAS_ESPECIFICAS.md)
- [Ajuste de Pesos de Fitness](backend/scripts/AJUSTE_PESOS_FITNESS.md)
- [Resultados de Persistencia](backend/scripts/RESULTADOS_PERSISTENCIA.md)
- [Ejemplos de Endpoints de Consulta](backend/scripts/EJEMPLOS_ENDPOINTS_CONSULTA.md)

---

## ✅ Estado

**FASE 6 COMPLETADA** ✅

- ✅ Función de fitness implementada
- ✅ Algoritmo genético implementado
- ✅ Motor híbrido funcionando
- ✅ Persistencia en base de datos
- ✅ Endpoints de consulta
- ✅ Pruebas exhaustivas
- ✅ Documentación completa

---

**Fecha de completación**: 2025-11-22
**Estado**: ✅ **COMPLETADA Y VALIDADA**

