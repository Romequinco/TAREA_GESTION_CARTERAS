# RESUMEN TEORIA COMPLETA: MODULO 5ANALISIS_MULTIPUNTO

## OBJETIVO

Extender el analisis de diversificacion para evaluar multiples puntos de interes
de la frontera, no solo el primer N donde la reduccion marginal cae bajo un umbral.

---

## CONCEPTOS CLAVE

1. **Frontera de diversificacion**  
   Mide la evolucion de la volatilidad al aumentar N activos en una cartera equiponderada.

2. **Reducion marginal de riesgo**  
   Se observa con `reduccion_pct`. Cuando cae por debajo de un umbral, se considera
   que se alcanza el limite practico de diversificacion.

3. **Minimos locales y cambios de pendiente**  
   La curva puede presentar puntos donde la volatilidad local es minima o donde
   el ritmo de reduccion cambia de forma significativa.

4. **Seleccion de activos y optimizacion**  
   Para cada N, se seleccionan activos por Sharpe y baja correlacion, y se optimiza
   con Markowitz para maximizar el Sharpe.

---

## FLUJO CONCEPTUAL

1. Simular frontera de diversificacion con el modulo 2.
2. Detectar puntos de interes:
   - Minimos locales
   - Reduccion marginal bajo umbral
   - Cambios de pendiente significativos
3. Ejecutar el pipeline de seleccion + optimizacion (modulo 4) para cada N.
4. Consolidar resultados y comparar carteras.
5. Visualizar y elegir la mejor en funcion de Sharpe y trade-offs.

---

## METRICAS EVALUADAS

- **Sharpe Ratio**: rendimiento ajustado por riesgo.
- **Rentabilidad esperada**: retorno anualizado de la cartera.
- **Volatilidad**: riesgo anualizado.
- **Peso en RF**: asignacion a renta fija (si aplica).
- **Correlacion promedio**: calidad de la seleccion.

---

## USO PRACTICO

Este modulo permite contrastar multiples N posibles y seleccionar el punto que
maximiza el Sharpe sin perder informacion sobre otros puntos relevantes de la
frontera de diversificacion.
