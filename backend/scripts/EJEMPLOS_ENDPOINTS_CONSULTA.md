# Ejemplos de Uso de Endpoints de Consulta

## Fecha: 2025-11-22

### Resumen

Endpoints para consultar, comparar y analizar los horarios generados por el sistema.

---

## 1. Listar Horarios de un Estudiante

### Endpoint
```
GET /api/v1/schedules/students/{student_id}?limit=10
```

### Ejemplo
```bash
curl -X GET "http://localhost:8000/api/v1/schedules/students/1?limit=10" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### Respuesta
```json
{
  "student_id": 1,
  "total_schedules": 3,
  "schedules": [
    {
      "id": 1,
      "enrollment_id": 1,
      "student_id": 1,
      "generation_method": "hybrid",
      "quality_score": -17.41,
      "processing_time": 0.032,
      "status": "completed",
      "created_at": "2025-11-22T22:57:57.990187",
      "schedule_slots": [
        {
          "id": 1,
          "schedule_id": 1,
          "section_id": 1,
          "day_of_week": 1,
          "start_time": "07:00:00",
          "end_time": "09:00:00",
          "section_number": 1,
          "subject_code": "PR001-SUB001",
          "subject_name": "Fundamentos de Soldadura Terrestre",
          "professor_name": "Juan Pérez",
          "classroom_code": "A101"
        }
      ]
    }
  ]
}
```

---

## 2. Obtener Detalles de un Horario Específico

### Endpoint
```
GET /api/v1/schedules/{schedule_id}
```

### Ejemplo
```bash
curl -X GET "http://localhost:8000/api/v1/schedules/1" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### Respuesta
```json
{
  "id": 1,
  "enrollment_id": 1,
  "student_id": 1,
  "generation_method": "hybrid",
  "quality_score": -17.41,
  "processing_time": 0.032,
  "status": "completed",
  "created_at": "2025-11-22T22:57:57.990187",
  "schedule_slots": [
    {
      "id": 1,
      "schedule_id": 1,
      "section_id": 1,
      "day_of_week": 1,
      "start_time": "07:00:00",
      "end_time": "09:00:00",
      "section_number": 1,
      "subject_code": "PR001-SUB001",
      "subject_name": "Fundamentos de Soldadura Terrestre",
      "professor_name": "Juan Pérez",
      "classroom_code": "A101"
    }
  ]
}
```

---

## 3. Comparar Dos Horarios

### Endpoint
```
GET /api/v1/schedules/{schedule_id}/compare/{other_schedule_id}
```

### Ejemplo
```bash
curl -X GET "http://localhost:8000/api/v1/schedules/1/compare/2" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### Respuesta
```json
{
  "schedule_1": {
    "id": 1,
    "enrollment_id": 1,
    "student_id": 1,
    "generation_method": "hybrid",
    "quality_score": -17.41,
    "processing_time": 0.032,
    "status": "completed",
    "created_at": "2025-11-22T22:57:57.990187",
    "schedule_slots": [...]
  },
  "schedule_2": {
    "id": 2,
    "enrollment_id": 1,
    "student_id": 1,
    "generation_method": "constraint_solver",
    "quality_score": -17.41,
    "processing_time": 0.022,
    "status": "completed",
    "created_at": "2025-11-22T22:57:58.123456",
    "schedule_slots": [...]
  },
  "comparison": {
    "quality_score_diff": 0.0,
    "processing_time_diff": 0.01,
    "sections_count_1": 5,
    "sections_count_2": 5,
    "slots_count_1": 5,
    "slots_count_2": 5,
    "days_distribution_1": {
      "0": 1,
      "1": 2,
      "2": 1,
      "3": 1
    },
    "days_distribution_2": {
      "0": 1,
      "1": 2,
      "2": 1,
      "3": 1
    },
    "better_quality": null
  }
}
```

---

## 4. Estadísticas de Horarios de un Estudiante

### Endpoint
```
GET /api/v1/schedules/students/{student_id}/stats
```

### Ejemplo
```bash
curl -X GET "http://localhost:8000/api/v1/schedules/students/1/stats" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### Respuesta
```json
{
  "student_id": 1,
  "total_schedules": 3,
  "completed_schedules": 3,
  "failed_schedules": 0,
  "average_quality_score": -17.41,
  "best_quality_score": -17.41,
  "worst_quality_score": -17.41,
  "average_processing_time": 0.045,
  "generation_methods": {
    "hybrid": 2,
    "constraint_solver": 1
  }
}
```

---

## 5. Casos de Uso

### Caso 1: Ver todos los horarios generados

```bash
# Listar todos los horarios de un estudiante
curl -X GET "http://localhost:8000/api/v1/schedules/students/1?limit=20" | python3 -m json.tool
```

### Caso 2: Analizar un horario específico

```bash
# Obtener detalles completos de un horario
curl -X GET "http://localhost:8000/api/v1/schedules/1" | python3 -m json.tool

# Ver los slots ordenados por día
curl -X GET "http://localhost:8000/api/v1/schedules/1" | python3 -m json.tool | grep -A 5 "schedule_slots"
```

### Caso 3: Comparar diferentes niveles de optimización

```bash
# Generar horarios con diferentes niveles
curl -X POST "http://localhost:8000/api/v1/schedules/generate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "selected_subject_ids": [1,2,3,4,5], "optimization_level": "none"}'

curl -X POST "http://localhost:8000/api/v1/schedules/generate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "selected_subject_ids": [1,2,3,4,5], "optimization_level": "high"}'

# Comparar los dos horarios más recientes
curl -X GET "http://localhost:8000/api/v1/schedules/1/compare/2" | python3 -m json.tool
```

### Caso 4: Analizar rendimiento del sistema

```bash
# Obtener estadísticas
curl -X GET "http://localhost:8000/api/v1/schedules/students/1/stats" | python3 -m json.tool

# Ver distribución de métodos
curl -X GET "http://localhost:8000/api/v1/schedules/students/1/stats" | python3 -m json.tool | grep "generation_methods"
```

---

## 6. Interpretación de Resultados

### Quality Score
- **Menor es mejor**: Un score de -17.41 es mejor que -10.00
- **Rangos típicos**:
  - < 50: Excelente
  - 50-100: Bueno
  - 100-200: Aceptable
  - > 200: Requiere optimización

### Generation Method
- **constraint_solver**: Solo restricciones duras (OR-Tools)
- **hybrid**: Restricciones duras + optimización genética

### Status
- **completed**: Horario generado exitosamente
- **failed**: No se pudo generar un horario factible

### Days Distribution
- Muestra cuántos slots hay cada día de la semana
- 0 = Lunes, 1 = Martes, ..., 6 = Domingo
- Ideal: Distribución balanceada

---

## 7. Scripts de Prueba

### Script para listar horarios
```bash
#!/bin/bash
STUDENT_ID=1
curl -s -X GET "http://localhost:8000/api/v1/schedules/students/${STUDENT_ID}" | python3 -m json.tool
```

### Script para comparar horarios
```bash
#!/bin/bash
SCHEDULE_1=1
SCHEDULE_2=2
curl -s -X GET "http://localhost:8000/api/v1/schedules/${SCHEDULE_1}/compare/${SCHEDULE_2}" | python3 -m json.tool
```

### Script para estadísticas
```bash
#!/bin/bash
STUDENT_ID=1
curl -s -X GET "http://localhost:8000/api/v1/schedules/students/${STUDENT_ID}/stats" | python3 -m json.tool
```

---

## 8. Notas Importantes

1. **Los horarios se ordenan por fecha de creación** (más recientes primero)
2. **El límite por defecto es 10** horarios, máximo 100
3. **Los slots incluyen información completa** de sección, asignatura, profesor y aula
4. **La comparación muestra diferencias** en quality score, tiempo, distribución de días, etc.
5. **Las estadísticas se calculan** sobre todos los horarios del estudiante

---

**Fecha de creación**: 2025-11-22
**Estado**: ✅ **ENDPOINTS IMPLEMENTADOS Y LISTOS PARA USO**

