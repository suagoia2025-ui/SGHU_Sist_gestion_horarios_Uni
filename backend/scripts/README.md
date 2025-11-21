# Scripts de Simulación - FASE 2

Scripts para poblar la base de datos con datos realistas simulados.

## 📋 Scripts Disponibles

### 1. `parse_programs.py`
Parser que extrae información de programas desde archivos markdown en `/docs`.

**Uso:**
```bash
python scripts/parse_programs.py
```

### 2. `simulate_odoo.py`
Simula datos del sistema Odoo (externo):
- 5 programas académicos (desde archivos markdown)
- 100 asignaturas (20 por programa)
- Red de prerrequisitos
- Malla curricular
- 35 profesores
- 23 aulas (aulas, laboratorios, auditorios)
- Reglas académicas

**Uso:**
```bash
python scripts/simulate_odoo.py
```

### 3. `simulate_students.py`
Simula datos de estudiantes:
- 200+ estudiantes (distribuidos en programas)
- Historial académico coherente
- Estados financieros (80% sin deuda, 20% con deuda)

**Uso:**
```bash
# Por defecto crea 200 estudiantes
python scripts/simulate_students.py

# Especificar cantidad
python scripts/simulate_students.py --num-students 300
```

### 4. `simulate_offer.py`
Simula oferta académica:
- Período académico activo (ciclo Feb-May o Ago-Nov)
- Secciones para cada asignatura (1-3 secciones)
- Horarios sin conflictos (profesores y aulas)

**Uso:**
```bash
# Primer ciclo 2025 (Febrero-Mayo)
python scripts/simulate_offer.py --year 2025 --cycle 1

# Segundo ciclo 2025 (Agosto-Noviembre)
python scripts/simulate_offer.py --year 2025 --cycle 2
```

### 5. `populate_db.py` ⭐ **SCRIPT MAESTRO**
Ejecuta todos los simuladores en orden correcto.

**Uso básico:**
```bash
# Poblar BD completa
python scripts/populate_db.py

# Limpiar BD antes de poblar
python scripts/populate_db.py --clean-db

# Personalizar parámetros
python scripts/populate_db.py \
    --clean-db \
    --num-students 250 \
    --year 2025 \
    --cycle 1
```

**Opciones:**
- `--clean-db`: Limpia la BD antes de poblar
- `--num-students N`: Número de estudiantes a crear (default: 200)
- `--year YYYY`: Año del período académico (default: 2025)
- `--cycle N`: Ciclo (1=Feb-May, 2=Ago-Nov, default: 1)
- `--skip-odoo`: Omitir simulación de Odoo
- `--skip-students`: Omitir simulación de estudiantes
- `--skip-offer`: Omitir simulación de oferta

### 6. `reset_db.py`
Limpia completamente la base de datos.

**Uso:**
```bash
# Requiere confirmación
python scripts/reset_db.py --confirm
```

## 🚀 Flujo Recomendado

### Primera vez (BD vacía):
```bash
# 1. Asegurar que Docker está corriendo
docker compose up -d

# 2. Poblar BD completa
cd backend
source venv/bin/activate
python scripts/populate_db.py --clean-db
```

### Actualizar datos:
```bash
# Solo actualizar oferta académica
python scripts/populate_db.py --skip-odoo --skip-students

# Solo agregar más estudiantes
python scripts/populate_db.py --skip-odoo --skip-offer --num-students 300
```

## 📊 Estructura de Datos Generados

### Programas (5):
- PR001: Técnico Superior en Asistencia de Tripulación Aérea
- PR002: Técnico Superior en Soldadura Subacuática
- PR003: Técnico Superior en Logística Internacional
- PR004: Técnico Superior en Mecánica de Equipo Pesado
- PR005: Técnico Superior en Topografía

### Por Programa:
- 20 asignaturas (4 créditos cada una, 2 horas semanales)
- Malla curricular distribuida en 4 semestres (5 materias por semestre)
- Red de prerrequisitos lógica

### Estudiantes:
- 200+ estudiantes (40 por programa aproximadamente)
- Distribuidos en semestres 1-10
- Historial académico coherente según semestre
- 80% sin deudas, 20% con deudas variadas

### Oferta Académica:
- Período activo según ciclo (Feb-May o Ago-Nov)
- Secciones: 1-3 por asignatura según popularidad
- Horarios sin conflictos (profesores y aulas)
- Distribución en semana (Lunes-Sábado, 7am-9pm)

## ⚠️ Notas Importantes

1. **Orden de ejecución**: Los scripts deben ejecutarse en orden:
   - Primero: `simulate_odoo.py` (crea programas, materias, profesores, aulas)
   - Segundo: `simulate_students.py` (necesita programas)
   - Tercero: `simulate_offer.py` (necesita programas, profesores, aulas)

2. **Ciclos académicos**:
   - Ciclo 1: Febrero-Mayo (semestres 1 y 2)
   - Ciclo 2: Agosto-Noviembre (semestres 3 y 4)
   - Cada ciclo = 4 meses
   - 2 ciclos = 1 semestre académico

3. **Prerrequisitos**: Se crean automáticamente desde los archivos markdown.

4. **Reproducibilidad**: Los scripts usan seeds fijos para generar datos consistentes.

## 🔍 Verificar Datos

Después de poblar, puedes verificar en PostgreSQL:

```bash
# Conectarse a la BD
docker exec -it sghu-postgres psql -U sghu_user -d sghu

# Ver programas
SELECT code, name FROM source.programs;

# Contar estudiantes por programa
SELECT p.code, COUNT(s.id) as estudiantes
FROM source.programs p
LEFT JOIN source.students s ON s.program_id = p.id
GROUP BY p.code;

# Ver secciones del período activo
SELECT cs.section_number, s.name, p.first_name || ' ' || p.last_name as profesor
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
JOIN source.professors p ON p.id = cs.professor_id
JOIN source.academic_periods ap ON ap.id = cs.period_id
WHERE ap.status = 'active';
```

