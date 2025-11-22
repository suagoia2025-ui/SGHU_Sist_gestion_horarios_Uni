# Reglas de Negocio - SGHU

## 📋 Resumen

Este documento describe todas las reglas de negocio implementadas en el sistema de matrícula SGHU. Estas validaciones se ejecutan antes de permitir que un estudiante se matricule en asignaturas.

---

## ✅ Tabla de Validaciones

| Validación             | Tipo       | Bloqueo | Mensaje Usuario                                                 | Código                 |
|------------------------|------------|---------|-----------------------------------------------------------------|------------------------|
| **Estado Financiero**  | Crítico    | Sí      | "Tienes una deuda pendiente de $X"                              | `financial_status`     |
| **Prerrequisitos**     | Crítico    | Sí      | "Debes aprobar [materias] primero"                              | `prerequisites`        |
| **Límite de Créditos** | Crítico    | Sí      | "Máximo permitido: X créditos" o "Mínimo requerido: X créditos" | `credit_limit`         |
| **Cupos Disponibles**  | Crítico    | Sí      | "No hay cupos disponibles en la sección X"                      | `section_capacity`     |
| **Choques de Horario** | Crítico    | Sí      | "Conflicto entre [sección A] y [sección B]"                     | `schedule_conflicts`   |
| **Matrícula Duplicada**| Advertencia| Parcial*| "Ya aprobaste esta asignatura"                                  | `duplicate_enrollment` |

\* *La matrícula duplicada bloquea solo si ya está aprobada. Si fue reprobada, permite repetir.*

---

## 🔍 Detalles de Cada Validación

### 1. Validación de Estado Financiero

**Código:** `financial_status`

**Descripción:**
Verifica si el estudiante tiene deudas pendientes que bloqueen su matrícula.

**Reglas:**
- Si `has_debt = 'true'`, la matrícula está **bloqueada**
- Si `has_debt = 'false'`, la matrícula está **permitida**

**Mensajes:**
- ✅ Válido: "Estado financiero válido"
- ❌ Inválido: "Tienes una deuda pendiente de $X.XX"

**Datos retornados:**
```json
{
  "validation_type": "financial_status",
  "is_valid": false,
  "message": "Tienes una deuda pendiente de $150.00",
  "details": {
    "student_id": 1,
    "has_debt": true,
    "debt_amount": 150.0,
    "payment_status": "pendiente"
  }
}
```

---

### 2. Validación de Prerrequisitos

**Código:** `prerequisites`

**Descripción:**
Verifica que el estudiante haya aprobado todas las asignaturas prerrequisito antes de matricularse en una asignatura.

**Reglas:**
- **Prerrequisito obligatorio:** Debe estar aprobado en el historial académico
- **Correquisito:** Puede estar en la selección actual de matrícula (se valida junto con las otras materias)

**Mensajes:**
- ✅ Válido: "Prerrequisitos cumplidos"
- ❌ Inválido: "Debes aprobar las siguientes materias primero: [Materia 1], [Materia 2]"

**Datos retornados:**
```json
{
  "validation_type": "prerequisites",
  "is_valid": false,
  "message": "Debes aprobar las siguientes materias primero: Fundamentos de Soldadura Terrestre",
  "details": {
    "subject_id": 5,
    "missing_prerequisites": [1],
    "missing_prerequisite_names": ["Fundamentos de Soldadura Terrestre"]
  }
}
```

---

### 3. Validación de Límite de Créditos

**Código:** `credit_limit`

**Descripción:**
Verifica que el total de créditos de las asignaturas seleccionadas esté dentro del rango permitido.

**Reglas:**
- **Máximo:** Definido en `academic_rules` con `rule_type = 'max_credits'` (por defecto: 20)
- **Mínimo:** Definido en `academic_rules` con `rule_type = 'min_credits'` (por defecto: 8)
- Se suman los créditos de todas las asignaturas seleccionadas

**Mensajes:**
- ✅ Válido: "Límite de créditos válido (16 créditos)"
- ❌ Excede máximo: "Excedes el límite máximo de créditos. Máximo permitido: 20 créditos. Seleccionaste: 24 créditos"
- ❌ No cumple mínimo: "No cumples el mínimo de créditos. Mínimo requerido: 8 créditos. Seleccionaste: 6 créditos"

**Datos retornados:**
```json
{
  "validation_type": "credit_limit",
  "is_valid": false,
  "message": "Excedes el límite máximo de créditos. Máximo permitido: 20 créditos. Seleccionaste: 24 créditos",
  "details": {
    "total_credits": 24,
    "max_allowed": 20,
    "min_required": 8,
    "excess": 4
  }
}
```

---

### 4. Validación de Cupos Disponibles

**Código:** `section_capacity`

**Descripción:**
Verifica que haya cupos disponibles en cada sección seleccionada.

**Reglas:**
- `available = capacity - enrolled_count`
- Si `available <= 0`, la sección está **llena**
- Si `available > 0`, la sección tiene **cupos disponibles**

**Mensajes:**
- ✅ Válido: "Cupos disponibles: 5 de 30"
- ❌ Inválido: "No hay cupos disponibles en la sección 1"

**Datos retornados:**
```json
{
  "validation_type": "section_capacity",
  "is_valid": false,
  "message": "No hay cupos disponibles en la sección 1",
  "details": {
    "section_id": 1,
    "capacity": 30,
    "enrolled_count": 30,
    "available": 0
  }
}
```

---

### 5. Validación de Choques de Horario

**Código:** `schedule_conflicts`

**Descripción:**
Detecta solapamientos de horario entre las secciones seleccionadas.

**Reglas:**
- Dos secciones chocan si tienen horarios en el **mismo día** y **mismo rango de tiempo**
- Se compara `day_of_week`, `start_time` y `end_time` de cada horario
- Un estudiante no puede estar en dos lugares al mismo tiempo

**Mensajes:**
- ✅ Válido: "No hay conflictos de horario"
- ❌ Inválido: "Conflicto de horario detectado: [Asignatura A - Sección 1] y [Asignatura B - Sección 2] (Día 0, 07:00:00-09:00:00 vs 08:00:00-10:00:00)"

**Datos retornados:**
```json
{
  "validation_type": "schedule_conflicts",
  "is_valid": false,
  "message": "Conflicto de horario detectado: ...",
  "details": {
    "conflicts": [
      {
        "section_a_id": 1,
        "section_b_id": 2,
        "day": 0,
        "time_a": "07:00:00-09:00:00",
        "time_b": "08:00:00-10:00:00",
        "section_a_name": "Fundamentos - Sección 1",
        "section_b_name": "Física - Sección 1"
      }
    ],
    "conflict_count": 1
  }
}
```

---

### 6. Validación de Matrícula Duplicada

**Código:** `duplicate_enrollment`

**Descripción:**
Verifica si el estudiante ya está matriculado o ya aprobó la asignatura.

**Reglas:**
- Si la asignatura está **aprobada** (`status = 'aprobado'`), la matrícula está **bloqueada**
- Si la asignatura fue **reprobada** (`status = 'reprobado'`), la matrícula está **permitida** (repetición)
- Si no hay historial, la matrícula está **permitida** (nueva)

**Mensajes:**
- ✅ Nueva: "Matrícula nueva permitida"
- ✅ Repetición: "Puedes repetir esta asignatura (fue reprobada anteriormente)"
- ❌ Ya aprobada: "Ya aprobaste esta asignatura con calificación 4.5"

**Datos retornados:**
```json
{
  "validation_type": "duplicate_enrollment",
  "is_valid": false,
  "message": "Ya aprobaste esta asignatura con calificación 4.5",
  "details": {
    "student_id": 1,
    "subject_id": 5,
    "status": "ya_aprobado",
    "grade": 4.5,
    "period": "2025-1"
  }
}
```

---

## 🔄 Flujo de Validación

Cuando un estudiante solicita matricularse, se ejecutan las validaciones en el siguiente orden:

1. **Estado Financiero** (si falla, se detiene aquí)
2. **Prerrequisitos** (para cada asignatura)
3. **Cupos Disponibles** (para cada sección)
4. **Límite de Créditos** (validación global)
5. **Choques de Horario** (validación global)
6. **Matrículas Duplicadas** (para cada asignatura)

### Resultado Consolidado

El sistema retorna un `EnrollmentValidationResult` con:
- `is_valid`: `true` si todas las validaciones pasaron
- `can_proceed`: `true` si todas las validaciones críticas pasaron
- `validations`: Lista de todas las validaciones ejecutadas
- `error_summary`: Resumen de errores (si hay)

---

## 📊 Endpoints de Validación

### POST `/api/v1/enrollment/validate`

Valida una solicitud de matrícula sin persistirla.

**Request:**
```json
{
  "student_id": 1,
  "academic_period_id": 1,
  "section_ids": [1, 2, 3, 4, 5]
}
```

**Response:**
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
      "message": "Debes aprobar las siguientes materias primero: ..."
    }
  ],
  "error_summary": "Debes aprobar las siguientes materias primero: ..."
}
```

### GET `/api/v1/students/{student_id}/eligible-subjects`

Retorna asignaturas que el estudiante puede cursar.

**Response:**
```json
[
  {
    "subject_id": 1,
    "subject_code": "SUB001",
    "subject_name": "Fundamentos de Soldadura",
    "credits": 4,
    "is_eligible": true,
    "prerequisites_met": [],
    "prerequisites_missing": [],
    "prerequisite_names_missing": [],
    "can_enroll": true,
    "reason": null
  }
]
```

### GET `/api/v1/students/{student_id}/enrollment-status`

Estado actual de matrícula del estudiante.

**Response:**
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

## ⚙️ Configuración de Reglas

Las reglas académicas se configuran en la tabla `source.academic_rules`:

```sql
-- Ejemplo: Límite máximo de créditos
INSERT INTO source.academic_rules (rule_type, rule_value, description)
VALUES ('max_credits', '20', 'Máximo de créditos por período');

-- Ejemplo: Límite mínimo de créditos
INSERT INTO source.academic_rules (rule_type, rule_value, description)
VALUES ('min_credits', '8', 'Mínimo de créditos para matricularse');
```

---

## 🧪 Casos de Prueba

### Caso 1: Matrícula Exitosa
- ✅ Estado financiero válido
- ✅ Prerrequisitos cumplidos
- ✅ Créditos dentro del rango
- ✅ Cupos disponibles
- ✅ Sin choques de horario
- ✅ Asignaturas nuevas

**Resultado:** `is_valid: true`, `can_proceed: true`

### Caso 2: Bloqueo Financiero
- ❌ Estado financiero: tiene deuda de $150

**Resultado:** `is_valid: false`, `can_proceed: false` (se detiene aquí)

### Caso 3: Prerrequisitos Faltantes
- ✅ Estado financiero válido
- ❌ Prerrequisitos: falta "Fundamentos de Soldadura"

**Resultado:** `is_valid: false`, `can_proceed: false`

### Caso 4: Excede Límite de Créditos
- ✅ Estado financiero válido
- ✅ Prerrequisitos cumplidos
- ❌ Créditos: 24 (máximo: 20)

**Resultado:** `is_valid: false`, `can_proceed: false`

### Caso 5: Choque de Horario
- ✅ Estado financiero válido
- ✅ Prerrequisitos cumplidos
- ✅ Créditos válidos
- ❌ Choque: Sección 1 (Lunes 7-9) vs Sección 2 (Lunes 8-10)

**Resultado:** `is_valid: false`, `can_proceed: false`

---

## 📝 Notas de Implementación

- Las validaciones se ejecutan en orden de criticidad
- Si una validación crítica falla, se puede detener el proceso (ej: bloqueo financiero)
- Las validaciones no críticas (ej: duplicados) se reportan pero no bloquean si es repetición
- Todos los mensajes están en español y son amigables para el usuario
- Los detalles técnicos se incluyen en el campo `details` para debugging

---

## 🔄 Actualizaciones Futuras

- [ ] Validación de límite de veces que se puede repetir una asignatura
- [ ] Validación de horarios preferidos del estudiante
- [ ] Validación de carga académica recomendada por semestre
- [ ] Validación de disponibilidad de profesor
- [ ] Validación de disponibilidad de aula

