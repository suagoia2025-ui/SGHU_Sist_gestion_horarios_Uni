#!/usr/bin/env python3
"""
Script para probar y entender la función de fitness
"""
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import time

# Importar directamente los módulos necesarios
# Esto evita problemas si ortools no está instalado
try:
    from app.services.schedule_engine.models import Section, TimeSlot
    from app.services.schedule_engine.fitness import ScheduleFitness
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("\n💡 Asegúrate de:")
    print("  1. Estar en el directorio backend/")
    print("  2. Tener el entorno virtual activado (source venv/bin/activate)")
    print("  3. Tener las dependencias instaladas (pip install -r requirements.txt)")
    sys.exit(1)


def create_test_section(section_id: int, subject_id: int, day: int, start_hour: int, end_hour: int) -> Section:
    """Crea una sección de prueba"""
    return Section(
        id=section_id,
        subject_id=subject_id,
        subject_code=f"SUB{subject_id:03d}",
        subject_name=f"Asignatura {subject_id}",
        professor_id=1,
        classroom_id=1,
        capacity=30,
        enrolled_count=0,
        section_number=1,
        timeslots=[
            TimeSlot(
                id=section_id * 10,
                day_of_week=day,
                start_time=time(start_hour, 0),
                end_time=time(end_hour, 0)
            )
        ]
    )


def print_fitness_analysis(fitness: ScheduleFitness, description: str):
    """Imprime análisis detallado del fitness"""
    print(f"\n{'='*70}")
    print(f"📊 {description}")
    print(f"{'='*70}")
    
    breakdown = fitness.get_fitness_breakdown()
    
    print(f"\n📈 Desglose del Fitness:")
    print(f"  • Fitness Total: {breakdown['total_fitness']:.2f} (menor = mejor)")
    print(f"  • Penalización por Gaps: {breakdown['gaps_penalty']:.2f}")
    print(f"  • Penalización por Desbalance: {breakdown['balance_penalty']:.2f}")
    print(f"  • Penalización por Horarios No Preferidos: {breakdown['time_preference_penalty']:.2f}")
    print(f"  • Bonus por Días Libres: {breakdown['free_days_bonus']:.2f}")
    print(f"\n📅 Estadísticas:")
    print(f"  • Total de Slots: {breakdown['total_slots']}")
    print(f"  • Días con Clases: {breakdown['days_with_classes']}")
    print(f"  • Días Libres: {7 - breakdown['days_with_classes']}")
    
    # Mostrar horario
    print(f"\n⏰ Horario:")
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    for day in range(7):
        day_slots = [s for s in fitness.slots if s.day_of_week == day]
        if day_slots:
            day_slots.sort(key=lambda s: s.start_time)
            slots_str = ", ".join([f"{s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}" 
                                  for s in day_slots])
            print(f"  • {days[day]}: {slots_str}")


def test_case_1_ideal_schedule():
    """Caso 1: Horario ideal - sin gaps, bien distribuido"""
    print("\n" + "="*70)
    print("CASO 1: Horario Ideal")
    print("="*70)
    print("Características:")
    print("  • Clases consecutivas (sin gaps)")
    print("  • Bien distribuidas en la semana")
    print("  • Horarios preferidos (8am-6pm)")
    print("  • Algunos días libres")
    
    sections = [
        create_test_section(1, 1, 0, 8, 10),   # Lunes 8-10
        create_test_section(2, 2, 0, 10, 12),  # Lunes 10-12
        create_test_section(3, 3, 2, 8, 10),   # Miércoles 8-10
        create_test_section(4, 4, 2, 10, 12),  # Miércoles 10-12
        create_test_section(5, 5, 4, 8, 10),   # Viernes 8-10
    ]
    
    fitness = ScheduleFitness(sections)
    print_fitness_analysis(fitness, "Horario Ideal")


def test_case_2_bad_gaps():
    """Caso 2: Horario con muchos gaps"""
    print("\n" + "="*70)
    print("CASO 2: Horario con Gaps")
    print("="*70)
    print("Características:")
    print("  • Grandes gaps entre clases")
    print("  • Clases muy separadas en el tiempo")
    
    sections = [
        create_test_section(1, 1, 0, 7, 9),    # Lunes 7-9
        create_test_section(2, 2, 0, 14, 16),  # Lunes 14-16 (gap de 5 horas)
        create_test_section(3, 3, 2, 8, 10),    # Miércoles 8-10
        create_test_section(4, 4, 2, 19, 21),   # Miércoles 19-21 (gap de 9 horas)
    ]
    
    fitness = ScheduleFitness(sections)
    print_fitness_analysis(fitness, "Horario con Gaps")


def test_case_3_unbalanced():
    """Caso 3: Horario desbalanceado - todas las clases en pocos días"""
    print("\n" + "="*70)
    print("CASO 3: Horario Desbalanceado")
    print("="*70)
    print("Características:")
    print("  • Todas las clases concentradas en 2 días")
    print("  • Muchos días libres pero mal distribuido")
    
    sections = [
        create_test_section(1, 1, 0, 8, 10),   # Lunes 8-10
        create_test_section(2, 2, 0, 10, 12),  # Lunes 10-12
        create_test_section(3, 3, 0, 14, 16),  # Lunes 14-16
        create_test_section(4, 4, 0, 16, 18),  # Lunes 16-18
        create_test_section(5, 5, 1, 8, 10),   # Martes 8-10
        create_test_section(6, 6, 1, 10, 12),  # Martes 10-12
    ]
    
    fitness = ScheduleFitness(sections)
    print_fitness_analysis(fitness, "Horario Desbalanceado")


def test_case_4_bad_times():
    """Caso 4: Horario con horarios no preferidos"""
    print("\n" + "="*70)
    print("CASO 4: Horarios No Preferidos")
    print("="*70)
    print("Características:")
    print("  • Clases muy temprano (antes de 7am)")
    print("  • Clases muy tarde (después de 6pm)")
    
    sections = [
        create_test_section(1, 1, 0, 6, 8),    # Lunes 6-8 (muy temprano)
        create_test_section(2, 2, 0, 19, 21),  # Lunes 19-21 (muy tarde)
        create_test_section(3, 3, 2, 5, 7),    # Miércoles 5-7 (muy temprano)
        create_test_section(4, 4, 2, 20, 22),  # Miércoles 20-22 (muy tarde)
    ]
    
    fitness = ScheduleFitness(sections)
    print_fitness_analysis(fitness, "Horarios No Preferidos")


def test_case_5_well_distributed():
    """Caso 5: Horario bien distribuido con días libres"""
    print("\n" + "="*70)
    print("CASO 5: Horario Bien Distribuido")
    print("="*70)
    print("Características:")
    print("  • Clases distribuidas uniformemente")
    print("  • Varios días libres")
    print("  • Horarios preferidos")
    
    sections = [
        create_test_section(1, 1, 0, 9, 11),   # Lunes 9-11
        create_test_section(2, 2, 1, 9, 11),   # Martes 9-11
        create_test_section(3, 3, 2, 9, 11),   # Miércoles 9-11
        create_test_section(4, 4, 3, 9, 11),   # Jueves 9-11
        # Viernes, Sábado, Domingo libres
    ]
    
    fitness = ScheduleFitness(sections)
    print_fitness_analysis(fitness, "Horario Bien Distribuido")


def main():
    """Ejecuta todos los casos de prueba"""
    print("\n" + "="*70)
    print("🧪 PRUEBAS DE FUNCIÓN DE FITNESS")
    print("="*70)
    print("\nLa función de fitness evalúa la calidad de un horario.")
    print("Menor score = mejor horario (penalizaciones suman, bonificaciones restan)")
    
    test_case_1_ideal_schedule()
    test_case_2_bad_gaps()
    test_case_3_unbalanced()
    test_case_4_bad_times()
    test_case_5_well_distributed()
    
    print("\n" + "="*70)
    print("✅ Pruebas completadas")
    print("="*70)
    print("\n💡 Interpretación:")
    print("  • Fitness < 50: Excelente horario")
    print("  • Fitness 50-100: Buen horario")
    print("  • Fitness 100-200: Horario aceptable")
    print("  • Fitness > 200: Horario con problemas")
    print()


if __name__ == "__main__":
    main()

