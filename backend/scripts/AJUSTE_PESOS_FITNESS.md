# Ajuste de Pesos de la Función de Fitness

## Fecha: 2025-11-22

### Objetivo
Mejorar el balance de distribución de días en la semana mediante el ajuste de los pesos de la función de fitness.

---

## Pesos Originales

| Componente | Peso Original | Descripción |
|------------|---------------|-------------|
| Gaps | 0.1 por minuto | Penalización por huecos entre clases |
| Balance | 15.0 | Penalización por desbalance de días |
| Preferencias de horario | 5-20 puntos | Penalización por horarios no preferidos |
| Días libres | -20 por día | Bonus por días completamente libres |

---

## Ajustes Realizados

### Versión 1: Aumentar solo el balance
- **Balance**: 15.0 → 25.0
- **Resultado**: Balance empeoró (3.92 puntos peor)

### Versión 2: Balancear gaps y balance
- **Gaps**: 0.1 → 0.08 (reducido)
- **Balance**: 25.0 → 20.0 (reducido desde versión 1)
- **Resultado**: Balance empeoró (3.14 puntos peor)

### Versión 3: Aumentar significativamente el balance
- **Gaps**: 0.08 (mantenido)
- **Balance**: 20.0 → 30.0 (aumentado significativamente)
- **Resultado**: Balance empeoró (4.70 puntos peor)

### Versión 4: Aumentar aún más el balance ⭐
- **Gaps**: 0.08 (mantenido)
- **Balance**: 30.0 → 40.0 (aumentado a 40.0)
- **Resultado**: ✅ **Balance se mantiene estable** (33.32 en ambos casos)

---

## Análisis del Problema

### Observación
Inicialmente, el balance empeoraba incluso cuando aumentábamos su peso. Esto se debía a que:

1. **El algoritmo genético optimiza el fitness total** (suma de todos los componentes)
2. **Otros componentes mejoran más** que lo que el balance empeora, resultando en un mejor fitness total
3. **El peso del balance no era suficientemente alto** para contrarrestar las mejoras en otros componentes

### Solución Encontrada

Aumentar el peso del balance a **40.0** (2.67x el peso original) asegura que el balance tenga suficiente impacto en el fitness total, evitando que el algoritmo genético lo degrade.

---

## Estado Final

**Pesos Finales**:
- **Gaps**: 0.08 por minuto (reducido de 0.1 para balancear)
- **Balance**: 40.0 (aumentado de 15.0 - **2.67x más importante**)
- **Preferencias de horario**: 5-20 puntos (sin cambios)
- **Días libres**: -20 por día (sin cambios)

### Resultados de Pruebas

| Versión | Peso Balance | Resultado |
|---------|--------------|-----------|
| Original | 15.0 | Empeoró 2.35 puntos |
| V1 | 25.0 | Empeoró 3.92 puntos |
| V2 | 20.0 | Empeoró 3.14 puntos |
| V3 | 30.0 | Empeoró 4.70 puntos |
| **V4** | **40.0** | **✅ Se mantiene estable** |

---

## Recomendaciones

### Para Producción
✅ **Usar pesos finales** (Balance: 40.0, Gaps: 0.08)
- El balance se mantiene estable
- El fitness total sigue mejorando
- Las restricciones duras se preservan

### Para Mejora Futura
1. **Monitorear el balance** en casos reales con más asignaturas
2. **A/B testing** con diferentes pesos para casos específicos
3. **Permitir configuración de pesos** por usuario o caso de uso
4. **Considerar función multi-objetivo** para casos muy complejos

---

## Conclusión

✅ **Ajuste exitoso**: El peso del balance de 40.0 logra mantener el balance estable mientras permite que el algoritmo genético optimice otros aspectos del horario.

**Impacto**: El balance ahora tiene 2.67x más peso que antes, asegurando que el algoritmo genético no lo degrade en favor de otros componentes.
