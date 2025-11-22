#!/bin/bash
# Script para visualizar tablas de la base de datos - Presentación del Proyecto

echo "═══════════════════════════════════════════════════════════════"
echo "  SGHU - Sistema de Gestión de Horarios Universitarios"
echo "  Visualización de Tablas de Base de Datos"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colores para mejor presentación
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para ejecutar consultas
run_query() {
    docker exec sghu-postgres psql -U sghu_user -d sghu -c "$1"
}

echo -e "${BLUE}📊 SCHEMA: source (Datos de Sistemas Externos)${NC}"
echo "─────────────────────────────────────────────────────────────"
run_query "\d+ source.programs" | head -15
echo ""

echo -e "${BLUE}📋 Lista de Programas Académicos:${NC}"
run_query "SELECT id, code, name, faculty, duration_semesters, credits_required FROM source.programs ORDER BY id;"
echo ""

echo -e "${BLUE}📚 Lista de Asignaturas (primeras 10):${NC}"
run_query "SELECT id, code, name, credits, program_id FROM source.subjects ORDER BY program_id, id LIMIT 10;"
echo ""

echo -e "${BLUE}👥 Estudiantes (primeros 5):${NC}"
run_query "SELECT id, code, first_name, last_name, email, program_id FROM source.students ORDER BY id LIMIT 5;"
echo ""

echo -e "${BLUE}👨‍🏫 Profesores (primeros 5):${NC}"
run_query "SELECT id, code, first_name, last_name, email, department FROM source.professors ORDER BY id LIMIT 5;"
echo ""

echo -e "${BLUE}🏫 Aulas (primeras 5):${NC}"
run_query "SELECT id, code, building, floor, capacity, type FROM source.classrooms ORDER BY id LIMIT 5;"
echo ""

echo -e "${BLUE}📅 Períodos Académicos:${NC}"
run_query "SELECT id, code, name, start_date, end_date, status FROM source.academic_periods ORDER BY start_date DESC;"
echo ""

echo -e "${BLUE}📖 Secciones de Cursos (primeras 5):${NC}"
run_query "SELECT cs.id, cs.subject_id, s.name as subject_name, cs.section_number, cs.capacity, cs.enrolled_count FROM source.course_sections cs JOIN source.subjects s ON s.id = cs.subject_id ORDER BY cs.id LIMIT 5;"
echo ""

echo -e "${BLUE}⏰ Horarios de Secciones (primeros 5):${NC}"
run_query "SELECT ss.id, ss.section_id, ss.day_of_week, ss.start_time, ss.end_time, ss.session_type FROM source.section_schedules ss ORDER BY ss.id LIMIT 5;"
echo ""

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📊 SCHEMA: sghu (Datos del Sistema)${NC}"
echo "─────────────────────────────────────────────────────────────"

echo -e "${BLUE}📝 Períodos de Matrícula:${NC}"
run_query "SELECT id, period_id, start_date, end_date, status FROM sghu.enrollment_periods ORDER BY start_date DESC;"
echo ""

echo -e "${BLUE}🎓 Matrículas de Estudiantes (primeras 5):${NC}"
run_query "SELECT id, student_id, enrollment_period_id, status, created_at FROM sghu.student_enrollments ORDER BY created_at DESC LIMIT 5;"
echo ""

echo -e "${BLUE}📋 Asignaturas Matriculadas (primeras 5):${NC}"
run_query "SELECT id, enrollment_id, subject_id, status FROM sghu.enrollment_subjects ORDER BY id LIMIT 5;"
echo ""

echo -e "${BLUE}📅 Horarios Generados (primeros 5):${NC}"
run_query "SELECT id, student_id, academic_period_id, generation_method, quality_score, status FROM sghu.generated_schedules ORDER BY created_at DESC LIMIT 5;"
echo ""

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📈 ESTADÍSTICAS GENERALES${NC}"
echo "─────────────────────────────────────────────────────────────"

echo -e "${BLUE}Total de Programas:${NC}"
run_query "SELECT COUNT(*) as total_programas FROM source.programs;"
echo ""

echo -e "${BLUE}Total de Asignaturas:${NC}"
run_query "SELECT COUNT(*) as total_asignaturas FROM source.subjects;"
echo ""

echo -e "${BLUE}Total de Estudiantes:${NC}"
run_query "SELECT COUNT(*) as total_estudiantes FROM source.students;"
echo ""

echo -e "${BLUE}Total de Profesores:${NC}"
run_query "SELECT COUNT(*) as total_profesores FROM source.professors;"
echo ""

echo -e "${BLUE}Total de Secciones en Período Actual:${NC}"
run_query "SELECT COUNT(*) as total_secciones FROM source.course_sections WHERE period_id = 1;"
echo ""

echo -e "${BLUE}Total de Horarios Generados:${NC}"
run_query "SELECT COUNT(*) as total_horarios FROM sghu.generated_schedules;"
echo ""

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo "✅ Visualización completada"
echo ""

