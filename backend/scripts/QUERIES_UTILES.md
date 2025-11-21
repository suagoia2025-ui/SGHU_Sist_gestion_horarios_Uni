# Consultas SQL Útiles para Explorar la Base de Datos

## 📋 Ver Todas las Tablas

### Por Schema
```bash
# Tablas del schema "source"
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt source.*"

# Tablas del schema "sghu"
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt sghu.*"

# Todas las tablas
docker exec sghu-postgres psql -U sghu_user -d sghu -c "\dt *.*"
```

### Usando el script Python
```bash
# Ver todas las tablas con conteo de registros
python scripts/view_tables.py

# Ver estructura de una tabla específica
python scripts/view_tables.py --schema source --table students --structure

# Ver muestra de datos
python scripts/view_tables.py --schema source --table students --sample --limit 10
```

## 🔍 Consultas Útiles

### Ver Programas y sus Materias
```sql
SELECT 
    p.code as programa,
    p.name as nombre_programa,
    COUNT(s.id) as total_materias
FROM source.programs p
LEFT JOIN source.subjects s ON s.program_id = p.id
GROUP BY p.id, p.code, p.name
ORDER BY p.code;
```

### Ver Estudiantes por Programa
```sql
SELECT 
    p.code as programa,
    COUNT(s.id) as estudiantes,
    AVG(s.current_semester)::numeric(4,2) as promedio_semestre
FROM source.programs p
LEFT JOIN source.students s ON s.program_id = p.id
GROUP BY p.id, p.code
ORDER BY p.code;
```

### Ver Materias con Prerrequisitos
```sql
SELECT 
    s.code,
    s.name as materia,
    COUNT(pr.id) as num_prerrequisitos,
    STRING_AGG(ps.name, ', ') as prerrequisitos
FROM source.subjects s
LEFT JOIN source.prerequisites pr ON pr.subject_id = s.id
LEFT JOIN source.subjects ps ON ps.id = pr.prerequisite_subject_id
GROUP BY s.id, s.code, s.name
HAVING COUNT(pr.id) > 0
ORDER BY COUNT(pr.id) DESC;
```

### Ver Oferta Académica del Período Activo
```sql
SELECT 
    ap.code as periodo,
    s.code as codigo_materia,
    s.name as materia,
    cs.section_number as seccion,
    p.first_name || ' ' || p.last_name as profesor,
    c.code as aula,
    cs.capacity as capacidad,
    cs.enrolled_count as inscritos
FROM source.academic_periods ap
JOIN source.course_sections cs ON cs.period_id = ap.id
JOIN source.subjects s ON s.id = cs.subject_id
JOIN source.professors p ON p.id = cs.professor_id
JOIN source.classrooms c ON c.id = cs.classroom_id
WHERE ap.status = 'active'
ORDER BY s.code, cs.section_number;
```

### Ver Horarios de una Sección
```sql
SELECT 
    s.code as codigo_materia,
    s.name as materia,
    cs.section_number as seccion,
    CASE ss.day_of_week
        WHEN 0 THEN 'Lunes'
        WHEN 1 THEN 'Martes'
        WHEN 2 THEN 'Miércoles'
        WHEN 3 THEN 'Jueves'
        WHEN 4 THEN 'Viernes'
        WHEN 5 THEN 'Sábado'
        WHEN 6 THEN 'Domingo'
    END as dia,
    ss.start_time as inicio,
    ss.end_time as fin,
    ss.session_type as tipo
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
JOIN source.section_schedules ss ON ss.section_id = cs.id
WHERE cs.id = 1  -- Cambiar por ID de sección
ORDER BY ss.day_of_week, ss.start_time;
```

### Ver Historial Académico de un Estudiante
```sql
SELECT 
    s.code as codigo_estudiante,
    s.first_name || ' ' || s.last_name as estudiante,
    subj.code as codigo_materia,
    subj.name as materia,
    ah.period as periodo,
    ah.grade as calificacion,
    ah.status as estado,
    ah.credits_earned as creditos
FROM source.students s
JOIN source.academic_history ah ON ah.student_id = s.id
JOIN source.subjects subj ON subj.id = ah.subject_id
WHERE s.id = 1  -- Cambiar por ID de estudiante
ORDER BY ah.period, subj.code;
```

### Ver Estudiantes con Deuda
```sql
SELECT 
    s.code as codigo,
    s.first_name || ' ' || s.last_name as estudiante,
    p.code as programa,
    fs.debt_amount as deuda,
    fs.payment_status as estado_pago
FROM source.students s
JOIN source.financial_status fs ON fs.student_id = s.id
JOIN source.programs p ON p.id = s.program_id
WHERE fs.has_debt = 'true'
ORDER BY fs.debt_amount DESC;
```

### Ver Profesores y sus Secciones
```sql
SELECT 
    p.code as codigo_profesor,
    p.first_name || ' ' || p.last_name as profesor,
    p.department as departamento,
    COUNT(cs.id) as secciones_asignadas
FROM source.professors p
LEFT JOIN source.course_sections cs ON cs.professor_id = p.id
GROUP BY p.id, p.code, p.first_name, p.last_name, p.department
ORDER BY COUNT(cs.id) DESC;
```

### Ver Aulas y su Uso
```sql
SELECT 
    c.code as codigo_aula,
    c.building as edificio,
    c.floor as piso,
    c.capacity as capacidad,
    c.type as tipo,
    COUNT(cs.id) as secciones_asignadas
FROM source.classrooms c
LEFT JOIN source.course_sections cs ON cs.classroom_id = c.id
GROUP BY c.id, c.code, c.building, c.floor, c.capacity, c.type
ORDER BY c.type, c.code;
```

### Ver Distribución de Horarios por Día
```sql
SELECT 
    CASE ss.day_of_week
        WHEN 0 THEN 'Lunes'
        WHEN 1 THEN 'Martes'
        WHEN 2 THEN 'Miércoles'
        WHEN 3 THEN 'Jueves'
        WHEN 4 THEN 'Viernes'
        WHEN 5 THEN 'Sábado'
        WHEN 6 THEN 'Domingo'
    END as dia,
    COUNT(*) as total_clases,
    MIN(ss.start_time) as primera_clase,
    MAX(ss.end_time) as ultima_clase
FROM source.section_schedules ss
GROUP BY ss.day_of_week
ORDER BY ss.day_of_week;
```

## 🔧 Comandos Útiles de psql

### Conectarse a la BD
```bash
docker exec sghu-postgres psql -U sghu_user -d sghu
```

### Dentro de psql:
```sql
-- Listar todas las tablas
\dt *.*

-- Describir estructura de una tabla
\d source.students

-- Ver esquemas
\dn

-- Cambiar formato de salida
\x  -- Modo expandido (vertical)
\timing  -- Mostrar tiempo de ejecución

-- Salir
\q
```

## 📊 Estadísticas Generales

```sql
-- Resumen completo de la BD
SELECT 
    'Programas' as categoria, COUNT(*)::text as cantidad FROM source.programs
UNION ALL
SELECT 'Asignaturas', COUNT(*)::text FROM source.subjects
UNION ALL
SELECT 'Estudiantes', COUNT(*)::text FROM source.students
UNION ALL
SELECT 'Profesores', COUNT(*)::text FROM source.professors
UNION ALL
SELECT 'Aulas', COUNT(*)::text FROM source.classrooms
UNION ALL
SELECT 'Secciones', COUNT(*)::text FROM source.course_sections
UNION ALL
SELECT 'Períodos', COUNT(*)::text FROM source.academic_periods;
```

