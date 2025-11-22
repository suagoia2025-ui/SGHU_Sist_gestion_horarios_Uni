-- ================================================================
-- QUERIES ÚTILES PARA PRESENTACIÓN DEL PROYECTO SGHU
-- ================================================================

-- 1. ESTRUCTURA DE TABLAS
-- Ver todas las tablas del schema source
\dt source.*

-- Ver todas las tablas del schema sghu
\dt sghu.*

-- Ver estructura de una tabla específica
\d+ source.programs
\d+ source.subjects
\d+ source.students
\d+ source.course_sections

-- ================================================================
-- 2. DATOS DE PROGRAMA ACADÉMICO
-- ================================================================

-- Listar todos los programas
SELECT id, code, name, level, duration_semesters, modality
FROM source.programs
ORDER BY id;

-- Asignaturas por programa
SELECT 
    p.code as programa_codigo,
    p.name as programa_nombre,
    COUNT(s.id) as total_asignaturas,
    SUM(s.credits) as total_creditos
FROM source.programs p
LEFT JOIN source.subjects s ON s.program_id = p.id
GROUP BY p.id, p.code, p.name
ORDER BY p.id;

-- ================================================================
-- 3. ESTUDIANTES
-- ================================================================

-- Estudiantes por programa
SELECT 
    p.code as programa,
    COUNT(st.id) as total_estudiantes
FROM source.programs p
LEFT JOIN source.students st ON st.program_id = p.id
GROUP BY p.id, p.code
ORDER BY p.id;

-- Historial académico de un estudiante
SELECT 
    s.code as estudiante,
    sub.code as asignatura,
    sub.name as nombre_asignatura,
    ah.grade,
    ah.status,
    ah.period
FROM source.students s
JOIN source.academic_history ah ON ah.student_id = s.id
JOIN source.subjects sub ON sub.id = ah.subject_id
WHERE s.id = 1
ORDER BY ah.period, sub.code;

-- ================================================================
-- 4. OFERTA ACADÉMICA
-- ================================================================

-- Secciones disponibles en el período actual
SELECT 
    cs.id as seccion_id,
    s.code as asignatura_codigo,
    s.name as asignatura_nombre,
    cs.section_number,
    cs.capacity,
    cs.enrolled_count,
    (cs.capacity - cs.enrolled_count) as cupos_disponibles,
    p.code as profesor_codigo,
    CONCAT(p.first_name, ' ', p.last_name) as profesor_nombre,
    c.code as aula
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
JOIN source.professors p ON p.id = cs.professor_id
JOIN source.classrooms c ON c.id = cs.classroom_id
WHERE cs.period_id = 1
ORDER BY s.code, cs.section_number
LIMIT 20;

-- Horarios de una sección específica
SELECT 
    cs.id as seccion_id,
    s.code as asignatura,
    cs.section_number,
    CASE ss.day_of_week
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END as dia,
    ss.start_time,
    ss.end_time,
    ss.session_type
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
JOIN source.section_schedules ss ON ss.section_id = cs.id
WHERE cs.id = 1
ORDER BY ss.day_of_week, ss.start_time;

-- ================================================================
-- 5. PRERREQUISITOS
-- ================================================================

-- Red de prerrequisitos de un programa
SELECT 
    s1.code as asignatura,
    s1.name as nombre_asignatura,
    p.type as tipo_prerequisito,
    s2.code as prerequisito,
    s2.name as nombre_prerequisito
FROM source.prerequisites p
JOIN source.subjects s1 ON s1.id = p.subject_id
JOIN source.subjects s2 ON s2.id = p.prerequisite_subject_id
WHERE s1.program_id = 1
ORDER BY s1.code, p.type;

-- ================================================================
-- 6. HORARIOS GENERADOS
-- ================================================================

-- Horarios generados para un estudiante
SELECT 
    gs.id as horario_id,
    s.code as estudiante,
    gs.generation_method,
    gs.quality_score,
    gs.processing_time,
    gs.status,
    gs.created_at
FROM sghu.generated_schedules gs
JOIN sghu.student_enrollments se ON se.id = gs.enrollment_id
JOIN source.students s ON s.id = se.student_id
WHERE se.student_id = 1
ORDER BY gs.created_at DESC;

-- Detalles de un horario generado
SELECT 
    gs.id as horario_id,
    s.code as estudiante,
    sub.code as asignatura,
    sub.name as nombre_asignatura,
    cs.section_number,
    CASE ss.day_of_week
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sábado'
    END as dia,
    ss.start_time,
    ss.end_time
FROM sghu.generated_schedules gs
JOIN sghu.student_enrollments se ON se.id = gs.enrollment_id
JOIN source.students s ON s.id = se.student_id
JOIN sghu.schedule_slots sl ON sl.schedule_id = gs.id
JOIN source.course_sections cs ON cs.id = sl.section_id
JOIN source.subjects sub ON sub.id = cs.subject_id
JOIN source.section_schedules ss ON ss.section_id = cs.id
WHERE gs.id = 1
ORDER BY ss.day_of_week, ss.start_time;

-- ================================================================
-- 7. ESTADÍSTICAS GENERALES
-- ================================================================

-- Resumen general del sistema
SELECT 
    'Programas' as categoria,
    COUNT(*)::text as total
FROM source.programs
UNION ALL
SELECT 
    'Asignaturas' as categoria,
    COUNT(*)::text as total
FROM source.subjects
UNION ALL
SELECT 
    'Estudiantes' as categoria,
    COUNT(*)::text as total
FROM source.students
UNION ALL
SELECT 
    'Profesores' as categoria,
    COUNT(*)::text as total
FROM source.professors
UNION ALL
SELECT 
    'Aulas' as categoria,
    COUNT(*)::text as total
FROM source.classrooms
UNION ALL
SELECT 
    'Secciones (Período 1)' as categoria,
    COUNT(*)::text as total
FROM source.course_sections
WHERE period_id = 1
UNION ALL
SELECT 
    'Horarios Generados' as categoria,
    COUNT(*)::text as total
FROM sghu.generated_schedules;

-- ================================================================
-- 8. CONSULTAS PARA DEMOSTRACIÓN
-- ================================================================

-- Ejemplo: Verificar datos de un estudiante completo
SELECT 
    s.id,
    s.code,
    CONCAT(s.first_name, ' ', s.last_name) as nombre_completo,
    s.email,
    p.code as programa,
    p.name as programa_nombre
FROM source.students s
JOIN source.programs p ON p.id = s.program_id
WHERE s.id = 1;

-- Ejemplo: Ver secciones disponibles para asignaturas específicas
SELECT 
    s.code as asignatura,
    s.name as nombre,
    cs.section_number,
    cs.capacity,
    cs.enrolled_count,
    (cs.capacity - cs.enrolled_count) as disponibles
FROM source.course_sections cs
JOIN source.subjects s ON s.id = cs.subject_id
WHERE cs.period_id = 1 
  AND cs.subject_id IN (1, 2, 3)
ORDER BY s.code, cs.section_number;

