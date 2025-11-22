# 🧪 Cómo Probar la Función de Fitness

## Requisitos

1. **Activar el entorno virtual:**
   ```bash
   cd backend
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate  # Windows
   ```

2. **Ejecutar el script:**
   ```bash
   python3 scripts/test_fitness.py
   ```

## Si obtienes error "ModuleNotFoundError: No module named 'ortools'"

**Solución:** El script ahora funciona sin requerir ortools, pero asegúrate de:

1. Estar en el directorio `backend/`
2. Tener el entorno virtual activado
3. Si aún falla, instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Qué muestra el script

El script ejecuta 5 casos de prueba que demuestran cómo la función de fitness evalúa diferentes tipos de horarios:

1. **Horario Ideal** - Sin gaps, bien distribuido
2. **Horario con Gaps** - Grandes espacios entre clases
3. **Horario Desbalanceado** - Clases concentradas en pocos días
4. **Horarios No Preferidos** - Muy temprano o muy tarde
5. **Horario Bien Distribuido** - Distribución uniforme

Cada caso muestra:
- Fitness total (menor = mejor)
- Desglose de penalizaciones y bonificaciones
- Estadísticas del horario
- Visualización del horario por días

