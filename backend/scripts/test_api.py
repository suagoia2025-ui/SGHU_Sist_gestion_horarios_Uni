"""
Script para probar los endpoints de la API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Prueba el health check"""
    print("\n🔍 Probando health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_db_health():
    """Prueba el health check de BD"""
    print("\n🔍 Probando health check de BD...")
    response = requests.get(f"{BASE_URL}/api/v1/health/db")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_get_students():
    """Prueba obtener lista de estudiantes"""
    print("\n🔍 Probando GET /api/v1/students...")
    response = requests.get(f"{BASE_URL}/api/v1/students?limit=5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total estudiantes: {len(data)}")
        if data:
            print(f"Primer estudiante: {json.dumps(data[0], indent=2, default=str)}")
    return response.status_code == 200


def test_get_student_by_id():
    """Prueba obtener estudiante por ID"""
    print("\n🔍 Probando GET /api/v1/students/1...")
    response = requests.get(f"{BASE_URL}/api/v1/students/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Estudiante: {json.dumps(response.json(), indent=2, default=str)}")
    return response.status_code == 200


def test_get_subjects():
    """Prueba obtener lista de asignaturas"""
    print("\n🔍 Probando GET /api/v1/subjects...")
    response = requests.get(f"{BASE_URL}/api/v1/subjects?limit=5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total asignaturas: {len(data)}")
    return response.status_code == 200


def test_get_programs():
    """Prueba obtener lista de programas"""
    print("\n🔍 Probando GET /api/v1/programs...")
    response = requests.get(f"{BASE_URL}/api/v1/programs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total programas: {len(data)}")
        for program in data:
            print(f"  - {program['code']}: {program['name']}")
    return response.status_code == 200


def test_get_current_period():
    """Prueba obtener período académico activo"""
    print("\n🔍 Probando GET /api/v1/academic-periods/current...")
    response = requests.get(f"{BASE_URL}/api/v1/academic-periods/current")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Período: {json.dumps(response.json(), indent=2, default=str)}")
    return response.status_code in [200, 404]  # 404 es válido si no hay período activo


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DE API - SGHU")
    print("=" * 60)
    
    results = []
    
    results.append(("Health Check", test_health()))
    results.append(("DB Health Check", test_db_health()))
    results.append(("Get Students", test_get_students()))
    results.append(("Get Student by ID", test_get_student_by_id()))
    results.append(("Get Subjects", test_get_subjects()))
    results.append(("Get Programs", test_get_programs()))
    results.append(("Get Current Period", test_get_current_period()))
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} pruebas pasaron")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

