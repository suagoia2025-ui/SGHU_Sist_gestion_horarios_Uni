# Índice de Documentación del Proyecto SGHU

## Fecha de Actualización: 2025-11-22

---

## 📚 Documentación Principal

### Planificación y Diseño
- [Plan de Trabajo](plan_trabajo.md) - Fases completas del proyecto
- [Fase 1: Base de Datos](fase1-base-datos.md) ✅ Completada
- [Fase 6: Motor de Horarios - Optimización](fase6-motor-horarios-optimizacion.md) ✅ Completada
- [Reglas de Negocio](reglas-negocio.md) ✅ Completada

### Programas Académicos
- [Programa: Técnico Superior en Tripulación Aérea](programa_tecnico_tripulacion_aerea.md)
- [Programa: Técnico Superior en Soldadura Subacuática](programa_tecnico_soldadura_subacuatica.md)
- [Programa: Técnico Superior en Logística Internacional](programa_tecnico_logistica_internacional.md)
- [Programa: Técnico Superior en Mecánica de Equipo Pesado](programa_tecnico_mecanica_equipo_pesado.md)
- [Programa: Técnico Superior en Topografía](programa_tecnico_topografia.md)

---

## 🔧 Documentación Técnica (Backend)

### Endpoints y API
- [Ejemplos de Validación](../backend/scripts/EJEMPLOS_VALIDACION.md) - Ejemplos de uso de endpoints de validación
- [Ejemplos de Consulta de Horarios](../backend/scripts/EJEMPLOS_ENDPOINTS_CONSULTA.md) - Ejemplos de endpoints de consulta
- [Resumen de Endpoints de Consulta](../backend/scripts/RESUMEN_ENDPOINTS_CONSULTA.md) - Resumen de endpoints implementados

### Motor de Horarios
- [Resultados de Pruebas de Optimización](../backend/scripts/RESULTADOS_PRUEBAS_OPTIMIZACION.md) - Pruebas básicas
- [Resultados de Pruebas Avanzadas](../backend/scripts/RESULTADOS_PRUEBAS_AVANZADAS.md) - Pruebas exhaustivas
- [Resultados de Pruebas Específicas](../backend/scripts/RESULTADOS_PRUEBAS_ESPECIFICAS.md) - Validación de componentes
- [Ajuste de Pesos de Fitness](../backend/scripts/AJUSTE_PESOS_FITNESS.md) - Proceso de ajuste
- [Resultados con Pesos Ajustados](../backend/scripts/RESULTADOS_PRUEBAS_PESOS_AJUSTADOS.md) - Validación final
- [Resultados de Persistencia](../backend/scripts/RESULTADOS_PERSISTENCIA.md) - Pruebas de persistencia
- [README Test Fitness](../backend/scripts/README_TEST_FITNESS.md) - Guía de pruebas de fitness

### Base de Datos
- [Guía de Visualización de Tablas](../backend/scripts/GUIA_VISUALIZACION_TABLAS.md) - Cómo ver datos en la BD
- [Queries Útiles](../backend/scripts/QUERIES_UTILES.md) - Consultas SQL útiles

### Calidad y Auditoría
- [Auditoría del Proyecto](../backend/AUDITORIA_PROYECTO.md) - Revisión de código y estructura
- [Código Hardcodeado](../backend/CODIGO_HARDCODEADO.md) - Valores hardcodeados y su gestión
- [Casos de Error Corregidos](../backend/scripts/CASOS_ERROR_CORREGIDOS.md) - Errores encontrados y solucionados
- [Explicación de Mensajes de Validación](../backend/scripts/EXPLICACION_MENSAJES_VALIDACION.md) - Significado de mensajes

### Scripts
- [README de Scripts](../backend/scripts/README.md) - Documentación de scripts de simulación

---

## 📖 Guías de Uso

### Para Desarrolladores

1. **Setup Inicial**: Ver [README.md](../README.md#-quick-start)
2. **Estructura de Base de Datos**: Ver [Fase 1: Base de Datos](fase1-base-datos.md)
3. **Reglas de Negocio**: Ver [Reglas de Negocio](reglas-negocio.md)
4. **Motor de Horarios**: Ver [Fase 6: Motor de Horarios](fase6-motor-horarios-optimizacion.md)

### Para Usuarios de la API

1. **Validación de Matrícula**: Ver [Ejemplos de Validación](../backend/scripts/EJEMPLOS_VALIDACION.md)
2. **Generación de Horarios**: Ver [Ejemplos de Consulta](../backend/scripts/EJEMPLOS_ENDPOINTS_CONSULTA.md)
3. **API Reference**: http://localhost:8000/docs (Swagger UI)

### Para Análisis y Pruebas

1. **Pruebas de Optimización**: Ver [Resultados de Pruebas](../backend/scripts/RESULTADOS_PRUEBAS_OPTIMIZACION.md)
2. **Pruebas Avanzadas**: Ver [Resultados Avanzados](../backend/scripts/RESULTADOS_PRUEBAS_AVANZADAS.md)
3. **Pruebas Específicas**: Ver [Resultados Específicos](../backend/scripts/RESULTADOS_PRUEBAS_ESPECIFICAS.md)

---

## 🗂️ Organización de Archivos

### Documentación por Categoría

#### ✅ Completadas
- FASE 0: Setup del Proyecto
- FASE 1: Base de Datos
- FASE 2: Scripts de Simulación
- FASE 3: Estructura FastAPI
- FASE 4: Lógica de Validación
- FASE 5: Motor de Horarios - Restricciones Duras
- FASE 6: Motor de Horarios - Optimización

#### 🚧 Pendientes
- FASE 7: Workers Asíncronos
- FASE 8: Testing y Refinamiento
- FASE 9: Simulador Frontend

---

## 🔍 Búsqueda Rápida

### Por Tema

- **Base de Datos**: `fase1-base-datos.md`, `GUIA_VISUALIZACION_TABLAS.md`
- **Validación**: `reglas-negocio.md`, `EJEMPLOS_VALIDACION.md`
- **Horarios**: `fase6-motor-horarios-optimizacion.md`, `RESULTADOS_PRUEBAS_*.md`
- **API**: `EJEMPLOS_ENDPOINTS_CONSULTA.md`, `RESUMEN_ENDPOINTS_CONSULTA.md`
- **Pruebas**: `RESULTADOS_PRUEBAS_*.md`, `README_TEST_FITNESS.md`
- **Troubleshooting**: `CASOS_ERROR_CORREGIDOS.md`, `AUDITORIA_PROYECTO.md`

### Por Tipo de Usuario

- **Desarrollador Nuevo**: `README.md`, `plan_trabajo.md`, `fase1-base-datos.md`
- **Desarrollador Backend**: `AUDITORIA_PROYECTO.md`, `CODIGO_HARDCODEADO.md`
- **Tester**: `RESULTADOS_PRUEBAS_*.md`, `EJEMPLOS_*.md`
- **Usuario de API**: `EJEMPLOS_ENDPOINTS_CONSULTA.md`, `EJEMPLOS_VALIDACION.md`

---

## 📝 Notas Importantes

### Organización de Días de la Semana

El campo `day_of_week` usa el estándar de Python `datetime.weekday()`:
- **0** = Lunes
- **1** = Martes
- **2** = Miércoles
- **3** = Jueves
- **4** = Viernes
- **5** = Sábado
- **6** = Domingo

### Niveles de Optimización

- **`none`**: Solo restricciones duras (OR-Tools CP-SAT) - ~0.04s
- **`low`**: Optimización ligera - ~0.07s
- **`medium`**: Optimización balanceada ⭐ Recomendado - ~0.11s
- **`high`**: Optimización máxima - ~0.29s

### Pesos de Fitness (Actualizados)

- **Gaps**: 0.08 por minuto
- **Balance**: 40.0 (aumentado para priorizar distribución)
- **Preferencias de horario**: 5-20 puntos
- **Días libres**: -20 por día

---

**Última actualización**: 2025-11-22
**Estado**: ✅ Documentación actualizada con FASE 6

