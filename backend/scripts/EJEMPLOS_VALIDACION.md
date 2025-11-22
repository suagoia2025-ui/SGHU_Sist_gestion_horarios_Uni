# 📋 Ejemplos de JSON para Probar Endpoints de Validación

## 🎯 Endpoints Disponibles

1. **POST** `/api/v1/enrollment/validate` - Validar solicitud de matrícula
2. **GET** `/api/v1/students/{student_id}/eligible-subjects` - Asignaturas elegibles
3. **GET** `/api/v1/students/{student_id}/enrollment-status` - Estado de matrícula

---

## 1️⃣ POST /api/v1/enrollment/validate

### Ejemplo 1: Matrícula Válida (5 asignaturas)

**Request:**
```json
{
  "student_id": 1,
  "academic_period_id": 1,
  "section_ids": [1, 2, 4, 6, 9]
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/enrollment/validate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "academic_period_id": 1,
    "section_ids": [1, 2, 4, 6, 9]
  }' | python3 -m json.tool
```

**Response esperado:**
```json
{
  "is_valid": false,
  "can_proceed": true,
  "validations": [
    {
      "validation_type": "financial_status",
      "is_valid": true,
      "message": "Estado financiero válido",
      "details": {
        "student_id": 1,
        "has_debt": false,
        "payment_status": "al día"
      }
    },
    {
      "validation_type": "prerequisites",
      "is_valid": true,
      "message": "La asignatura no tiene prerrequisitos",
      "details": {
        "subject_id": 1
      }
    },
    {
      "validation_type": "prerequisites",
      "is_valid": true,
      "message": "La asignatura no tiene prerrequisitos",
      "details": {
        "subject_id": 2
      }
    },
    {
      "validation_type": "prerequisites",
      "is_valid": true,
      "message": "La asignatura no tiene prerrequisitos",
      "details": {
        "subject_id": 3
      }
    },
    {
      "validation_type": "prerequisites",
      "is_valid": true,
      "message": "La asignatura no tiene prerrequisitos",
      "details": {
        "subject_id": 4
      }
    },
    {
      "validation_type": "prerequisites",
      "is_valid": true,
      "message": "Prerrequisitos cumplidos",
      "details": {
        "subject_id": 5
      }
    },
    {
      "validation_type": "section_capacity",
      "is_valid": true,
      "message": "Cupos disponibles: 46 de 46",
      "details": {
        "section_id": 1,
        "capacity": 46,
        "enrolled_count": 0,
        "available": 46
      }
    },
    {
      "validation_type": "section_capacity",
      "is_valid": true,
      "message": "Cupos disponibles: 16 de 16",
      "details": {
        "section_id": 2,
        "capacity": 16,
        "enrolled_count": 0,
        "available": 16
      }
    },
    {
      "validation_type": "section_capacity",
      "is_valid": true,
      "message": "Cupos disponibles: 169 de 169",
      "details": {
        "section_id": 4,
        "capacity": 169,
        "enrolled_count": 0,
        "available": 169
      }
    },
    {
      "validation_type": "section_capacity",
      "is_valid": true,
      "message": "Cupos disponibles: 15 de 15",
      "details": {
        "section_id": 6,
        "capacity": 15,
        "enrolled_count": 0,
        "available": 15
      }
    },
    {
      "validation_type": "section_capacity",
      "is_valid": true,
      "message": "Cupos disponibles: 20 de 20",
      "details": {
        "section_id": 9,
        "capacity": 20,
        "enrolled_count": 0,
        "available": 20
      }
    },
    {
      "validation_type": "credit_limit",
      "is_valid": true,
      "message": "Límite de créditos válido (20 créditos)",
      "details": {
        "total_credits": 20,
        "max_allowed": 20,
        "min_required": 8
      }
    },
    {
      "validation_type": "schedule_conflicts",
      "is_valid": true,
      "message": "No hay conflictos de horario",
      "details": {
        "section_ids": [1, 2, 4, 6, 9]
      }
    },
    {
      "validation_type": "duplicate_enrollment",
      "is_valid": true,
      "message": "Puedes repetir esta asignatura (fue reprobada anteriormente)",
      "details": {
        "student_id": 1,
        "subject_id": 1,
        "status": "repeticion",
        "previous_grade": 2.0,
        "previous_period": "2024-2"
      }
    },
    {
      "validation_type": "duplicate_enrollment",
      "is_valid": false,
      "message": "Ya aprobaste esta asignatura con calificación 3.1",
      "details": {
        "student_id": 1,
        "subject_id": 2,
        "status": "ya_aprobado",
        "grade": 3.1,
        "period": "2024-2"
      }
    },
    {
      "validation_type": "duplicate_enrollment",
      "is_valid": false,
      "message": "Ya aprobaste esta asignatura con calificación 4.1",
      "details": {
        "student_id": 1,
        "subject_id": 3,
        "status": "ya_aprobado",
        "grade": 4.1,
        "period": "2024-2"
      }
    },
    {
      "validation_type": "duplicate_enrollment",
      "is_valid": false,
      "message": "Ya aprobaste esta asignatura con calificación 3.1",
      "details": {
        "student_id": 1,
        "subject_id": 4,
        "status": "ya_aprobado",
        "grade": 3.1,
        "period": "2024-2"
      }
    },
    {
      "validation_type": "duplicate_enrollment",
      "is_valid": false,
      "message": "Ya aprobaste esta asignatura con calificación 4.9",
      "details": {
        "student_id": 1,
        "subject_id": 5,
        "status": "ya_aprobado",
        "grade": 4.9,
        "period": "2024-2"
      }
    }
  ],
  "error_summary": "Ya aprobaste esta asignatura con calificación 3.1; Ya aprobaste esta asignatura con calificación 4.1; Ya aprobaste esta asignatura con calificación 3.1; Ya aprobaste esta asignatura con calificación 4.9"
}
```

**Nota importante:** 
- El endpoint retorna **una validación por cada asignatura única** para `prerequisites` y `duplicate_enrollment`
- El endpoint retorna **una validación por cada sección** para `section_capacity`
- `is_valid: false` porque hay asignaturas ya aprobadas, pero `can_proceed: true` porque las validaciones críticas (financiera, prerrequisitos, créditos, cupos, choques) pasaron
- Las validaciones de `duplicate_enrollment` con `is_valid: false` indican que el estudiante ya aprobó esas asignaturas

---

### Ejemplo 2: Estudiante con Deuda (Bloqueado)

**Request:**
```json
{
  "student_id": 3,
  "academic_period_id": 1,
  "section_ids": [1, 2, 3]
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/enrollment/validate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 3,
    "academic_period_id": 1,
    "section_ids": [1, 2, 3]
  }' | python3 -m json.tool
```

**Response esperado:**
```json
{
  "is_valid": false,
  "can_proceed": false,
  "validations": [
    {
      "validation_type": "financial_status",
      "is_valid": false,
      "message": "Tienes una deuda pendiente de $158.48",
      "details": {
        "student_id": 3,
        "has_debt": true,
        "debt_amount": 158.48,
        "payment_status": "pendiente"
      }
    }
  ],
  "error_summary": "Bloqueo financiero: Tienes una deuda pendiente de $158.48"
}
```

---

### Ejemplo 3: Excede Límite de Créditos

**Request:**
```json
{
  "student_id": 1,
  "academic_period_id": 1,
  "section_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/enrollment/validate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "academic_period_id": 1,
    "section_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  }' | python3 -m json.tool
```

**Response esperado:**
```json
{
  "is_valid": false,
  "can_proceed": false,
  "validations": [
    {
      "validation_type": "financial_status",
      "is_valid": true,
      "message": "Estado financiero válido",
      "details": {
        "student_id": 1,
        "has_debt": false,
        "payment_status": "al día"
      }
    },
    {
      "validation_type": "prerequisites",
      "is_valid": true,
      "message": "La asignatura no tiene prerrequisitos",
      "details": {
        "subject_id": 1
      }
    },
    {
      "validation_type": "section_capacity",
      "is_valid": true,
      "message": "Cupos disponibles: 46 de 46",
      "details": {
        "section_id": 1,
        "capacity": 46,
        "enrolled_count": 0,
        "available": 46
      }
    },
    {
      "validation_type": "credit_limit",
      "is_valid": false,
      "message": "Excedes el límite máximo de créditos. Máximo permitido: 20 créditos. Seleccionaste: 40 créditos",
      "details": {
        "total_credits": 40,
        "max_allowed": 20,
        "min_required": 8,
        "excess": 20
      }
    },
    {
      "validation_type": "schedule_conflicts",
      "is_valid": true,
      "message": "No hay conflictos de horario",
      "details": {
        "section_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
      }
    }
  ],
  "error_summary": "Excedes el límite máximo de créditos. Máximo permitido: 20 créditos. Seleccionaste: 40 créditos"
}
```

**Nota:** La respuesta incluirá también validaciones de `prerequisites` y `section_capacity` para cada asignatura/sección, y `duplicate_enrollment` para cada asignatura única. Se muestra solo la parte relevante del error.

---

### Ejemplo 4: Prerrequisitos Faltantes

**Request:**
```json
{
  "student_id": 1,
  "academic_period_id": 1,
  "section_ids": [6]
}
```

**Nota:** La sección 6 es "Procesos de Soldadura Húmeda y Seca" que requiere "Fundamentos de Soldadura Terrestre" (sección 1) como prerrequisito.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/enrollment/validate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "academic_period_id": 1,
    "section_ids": [6]
  }' | python3 -m json.tool
```

**Response esperado:**
```json
{
  "is_valid": false,
  "can_proceed": false,
  "validations": [
    {
      "validation_type": "financial_status",
      "is_valid": true,
      "message": "Estado financiero válido"
    },
    {
      "validation_type": "prerequisites",
      "is_valid": false,
      "message": "Debes aprobar las siguientes materias primero: Fundamentos de Soldadura Terrestre",
      "details": {
        "subject_id": 6,
        "missing_prerequisites": [1],
        "missing_prerequisite_names": ["Fundamentos de Soldadura Terrestre"]
      }
    }
  ],
  "error_summary": "Debes aprobar las siguientes materias primero: Fundamentos de Soldadura Terrestre"
}
```

---

### Ejemplo 5: Con Prerrequisito (Válido)

**Request:**
```json
{
  "student_id": 1,
  "academic_period_id": 1,
  "section_ids": [1, 6]
}
```

**Nota:** Incluye tanto el prerrequisito (sección 1) como la materia que lo requiere (sección 6).

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/enrollment/validate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "academic_period_id": 1,
    "section_ids": [1, 6]
  }' | python3 -m json.tool
```

---

## 2️⃣ GET /api/v1/students/{student_id}/eligible-subjects

### Ejemplo 1: Sin período específico (usa activo)

**URL:**
```
http://localhost:8000/api/v1/students/1/eligible-subjects
```

**cURL:**
```bash
curl http://localhost:8000/api/v1/students/1/eligible-subjects | python -m json.tool
```

**Response esperado:**
```json
[
  {
    "subject_id": 1,
    "subject_code": "PR002-SUB001",
    "subject_name": "Fundamentos de Soldadura Terrestre",
    "credits": 4,
    "is_eligible": true,
    "prerequisites_met": [],
    "prerequisites_missing": [],
    "prerequisite_names_missing": [],
    "can_enroll": true,
    "reason": null
  },
  {
    "subject_id": 2,
    "subject_code": "PR002-SUB002",
    "subject_name": "Física Aplicada a la Soldadura Subacuática",
    "credits": 4,
    "is_eligible": true,
    "prerequisites_met": [],
    "prerequisites_missing": [],
    "prerequisite_names_missing": [],
    "can_enroll": true,
    "reason": null
  },
  {
    "subject_id": 6,
    "subject_code": "PR002-SUB006",
    "subject_name": "Procesos de Soldadura Húmeda y Seca",
    "credits": 4,
    "is_eligible": false,
    "prerequisites_met": [],
    "prerequisites_missing": [1],
    "prerequisite_names_missing": ["Fundamentos de Soldadura Terrestre"],
    "can_enroll": false,
    "reason": "Debes aprobar las siguientes materias primero: Fundamentos de Soldadura Terrestre"
  }
]
```

---

### Ejemplo 2: Con período específico

**URL:**
```
http://localhost:8000/api/v1/students/1/eligible-subjects?academic_period_id=1
```

**cURL:**
```bash
curl "http://localhost:8000/api/v1/students/1/eligible-subjects?academic_period_id=1" | python -m json.tool
```

---

## 3️⃣ GET /api/v1/students/{student_id}/enrollment-status

### Ejemplo 1: Estudiante sin bloqueos

**URL:**
```
http://localhost:8000/api/v1/students/1/enrollment-status
```

**cURL:**
```bash
curl http://localhost:8000/api/v1/students/1/enrollment-status | python -m json.tool
```

**Response esperado:**
```json
{
  "student_id": 1,
  "can_enroll": true,
  "financial_blocked": false,
  "financial_debt_amount": null,
  "financial_message": "Estado financiero válido",
  "eligible_subjects_count": 15,
  "current_enrollments_count": 0,
  "warnings": [],
  "errors": []
}
```

---

### Ejemplo 2: Estudiante con deuda

**URL:**
```
http://localhost:8000/api/v1/students/3/enrollment-status
```

**cURL:**
```bash
curl http://localhost:8000/api/v1/students/3/enrollment-status | python -m json.tool
```

**Response esperado:**
```json
{
  "student_id": 3,
  "can_enroll": false,
  "financial_blocked": true,
  "financial_debt_amount": 158.48,
  "financial_message": "Tienes una deuda pendiente de $158.48",
  "eligible_subjects_count": 0,
  "current_enrollments_count": 0,
  "warnings": [],
  "errors": [
    "Tienes una deuda pendiente de $158.48"
  ]
}
```

---

### Ejemplo 3: Estudiante con deuda mayor

**URL:**
```
http://localhost:8000/api/v1/students/5/enrollment-status
```

**cURL:**
```bash
curl http://localhost:8000/api/v1/students/5/enrollment-status | python -m json.tool
```

**Response esperado:**
```json
{
  "student_id": 5,
  "can_enroll": false,
  "financial_blocked": true,
  "financial_debt_amount": 560.63,
  "financial_message": "Tienes una deuda pendiente de $560.63",
  "eligible_subjects_count": 0,
  "current_enrollments_count": 0,
  "warnings": [],
  "errors": [
    "Tienes una deuda pendiente de $560.63"
  ]
}
```

---

## 📊 Datos Reales de la Base de Datos

### Estudiantes Disponibles

| ID | Código | Nombre | Programa | Semestre | Estado Financiero |
|----|--------|--------|----------|----------|-------------------|
| 1 | EST00001 | Roxana Cabrero | PR002 | 2 | ✅ Sin deuda |
| 2 | EST00002 | Ricardo Lobo | PR002 | 10 | ✅ Sin deuda |
| 3 | EST00003 | Wilfredo Patiño | PR002 | 2 | ❌ Deuda: $158.48 |
| 5 | EST00005 | Pedro Gallego | PR002 | 10 | ❌ Deuda: $560.63 |
| 14 | EST00014 | (verificar) | PR002 | ? | ❌ Deuda: $1822.33 |

### Período Académico

| ID | Código | Nombre | Estado |
|----|--------|--------|--------|
| 1 | 2025-1 | Primer Ciclo 2025 | active |

### Secciones Disponibles (Período 1)

| ID | Sección | Asignatura | Capacidad | Inscritos | Disponibles |
|----|---------|------------|-----------|-----------|-------------|
| 1 | 1 | Fundamentos de Soldadura Terrestre | 46 | 0 | 46 |
| 2 | 1 | Física Aplicada a la Soldadura Subacuática | 16 | 0 | 16 |
| 3 | 2 | Física Aplicada a la Soldadura Subacuática | 31 | 0 | 31 |
| 4 | 1 | Buceo Profesional y Técnicas de Inmersión | 169 | 0 | 169 |
| 5 | 2 | Buceo Profesional y Técnicas de Inmersión | 38 | 0 | 38 |
| 6 | 1 | Procesos de Soldadura Húmeda y Seca | 28 | 0 | 28 |

**Nota:** La sección 6 requiere la sección 1 como prerrequisito.

---

## 🧪 Script de Prueba Rápida

Crea un archivo `test_validaciones.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=== 1. Estado de Matrícula (Estudiante 1) ==="
curl -s "$BASE_URL/api/v1/students/1/enrollment-status" | python -m json.tool

echo -e "\n=== 2. Estado de Matrícula (Estudiante 3 - con deuda) ==="
curl -s "$BASE_URL/api/v1/students/3/enrollment-status" | python -m json.tool

echo -e "\n=== 3. Asignaturas Elegibles (Estudiante 1) ==="
curl -s "$BASE_URL/api/v1/students/1/eligible-subjects" | python -m json.tool | head -30

echo -e "\n=== 4. Validar Matrícula (Estudiante 1 - válida) ==="
curl -s -X POST "$BASE_URL/api/v1/enrollment/validate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "academic_period_id": 1, "section_ids": [1, 2, 4]}' | python -m json.tool

echo -e "\n=== 5. Validar Matrícula (Estudiante 3 - bloqueado por deuda) ==="
curl -s -X POST "$BASE_URL/api/v1/enrollment/validate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 3, "academic_period_id": 1, "section_ids": [1, 2]}' | python -m json.tool
```

Ejecutar:
```bash
chmod +x test_validaciones.sh
./test_validaciones.sh
```

---

## 📝 Notas Importantes

### Estructura de la Respuesta

El endpoint `/api/v1/enrollment/validate` retorna **múltiples validaciones**:

1. **1 validación de `financial_status`** - Estado financiero del estudiante
2. **N validaciones de `prerequisites`** - Una por cada **asignatura única** (no por sección)
3. **M validaciones de `section_capacity`** - Una por cada **sección** seleccionada
4. **1 validación de `credit_limit`** - Límite total de créditos
5. **1 validación de `schedule_conflicts`** - Choques de horario entre todas las secciones
6. **N validaciones de `duplicate_enrollment`** - Una por cada **asignatura única** (no por sección)

**Ejemplo:** Si seleccionas 5 secciones de 3 asignaturas diferentes:
- `prerequisites`: 3 validaciones (una por asignatura única)
- `section_capacity`: 5 validaciones (una por sección)
- `duplicate_enrollment`: 3 validaciones (una por asignatura única)

### Campos de la Respuesta

- **`is_valid`**: `true` si TODAS las validaciones pasaron, `false` si alguna falló
- **`can_proceed`**: `true` si las validaciones **críticas** pasaron (financiera, prerrequisitos, créditos, cupos, choques). Puede ser `true` incluso si `is_valid` es `false` (por ejemplo, si hay asignaturas ya aprobadas pero las críticas pasaron)

### Otros Datos

1. **IDs de Secciones:** Los IDs pueden variar. Verifica con:
   ```sql
   SELECT id, section_number, subject_id 
   FROM source.course_sections 
   WHERE period_id = 1 
   ORDER BY id;
   ```

2. **Estudiantes con Deuda:** Para probar bloqueos financieros, usa estudiantes 3, 5 o 14.

3. **Prerrequisitos:** La sección 6 requiere la sección 1. Prueba matricular solo la 6 para ver el error.

4. **Choques de Horario:** Para probar choques, selecciona secciones que tengan horarios en el mismo día y hora.

5. **Límite de Créditos:** Selecciona más de 5 secciones (20+ créditos) para probar el límite.

6. **Asignaturas Ya Aprobadas:** El estudiante 1 tiene varias asignaturas aprobadas. Si intentas matricularlas, verás validaciones de `duplicate_enrollment` con `is_valid: false`.

---

## 🔗 Enlaces Útiles

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

