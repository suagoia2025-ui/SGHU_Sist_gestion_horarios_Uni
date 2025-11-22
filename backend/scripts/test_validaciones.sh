#!/bin/bash

# Script para probar endpoints de validación
# Uso: ./test_validaciones.sh

BASE_URL="http://localhost:8000"

echo "🧪 PRUEBAS DE ENDPOINTS DE VALIDACIÓN"
echo "======================================"
echo ""

echo "=== 1. Estado de Matrícula (Estudiante 1 - Sin deuda) ==="
curl -s "$BASE_URL/api/v1/students/1/enrollment-status" | python3 -m json.tool
echo ""

echo "=== 2. Estado de Matrícula (Estudiante 3 - Con deuda) ==="
curl -s "$BASE_URL/api/v1/students/3/enrollment-status" | python3 -m json.tool
echo ""

echo "=== 3. Asignaturas Elegibles (Estudiante 1) - Primeras 3 ==="
curl -s "$BASE_URL/api/v1/students/1/eligible-subjects" | python3 -m json.tool | head -40
echo ""

echo "=== 4. Validar Matrícula (Estudiante 1 - Válida) ==="
curl -s -X POST "$BASE_URL/api/v1/enrollment/validate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "academic_period_id": 1, "section_ids": [1, 2, 4]}' | python3 -m json.tool
echo ""

echo "=== 5. Validar Matrícula (Estudiante 3 - Bloqueado por deuda) ==="
curl -s -X POST "$BASE_URL/api/v1/enrollment/validate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 3, "academic_period_id": 1, "section_ids": [1, 2]}' | python3 -m json.tool
echo ""

echo "=== 6. Validar Matrícula (Estudiante 1 - Sin prerrequisito) ==="
curl -s -X POST "$BASE_URL/api/v1/enrollment/validate" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "academic_period_id": 1, "section_ids": [6]}' | python3 -m json.tool
echo ""

echo "✅ Pruebas completadas"
echo ""
echo "💡 Para más ejemplos, ver: scripts/EJEMPLOS_VALIDACION.md"

