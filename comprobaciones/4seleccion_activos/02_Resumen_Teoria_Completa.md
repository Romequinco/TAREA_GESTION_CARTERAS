# RESUMEN TEORICO: SELECCION DE ACTIVOS PARA OPTIMIZACION

## 1) MOTIVACION: DIMENSIONALIDAD Y ERROR DE ESTIMACION

En optimizacion de carteras, estimar una matriz de covarianzas de N activos requiere
N(N-1)/2 covarianzas. A mayor N, mayor error de estimacion y mayor inestabilidad en
los pesos optimos. Seleccionar un subconjunto reduce ruido y mejora robustez.

---

## 2) FRONTERA DE DIVERSIFICACION

Para carteras equiponderadas se cumple la descomposicion:

σp^2 = (1/n) * Vbarra + (1 - 1/n) * Cbar

En el modulo 2 se usa una aproximacion equivalente:
- Riesgo especifico: (1/n) * Vbarra
- Riesgo sistematico: Cbar

El beneficio marginal de diversificar cae rapido, y existe un N donde agregar mas
activos reduce el riesgo en menos de un umbral (ej: 2%). Ese N es el limite
practico de diversificacion.

---

## 3) SELECCION POR CALIDAD Y DIVERSIFICACION

Para elegir activos se combinan dos criterios:
1. Calidad: Sharpe Ratio anualizado
   Sharpe_i = (E[Ri] - rf) / sigma_i
2. Diversificacion: baja correlacion promedio con el resto
   puntuacion_diversificacion_i = 1 - corr_promedio_i

Se normalizan ambos criterios a [0, 1] y se combinan:

score_i = w_sharpe * sharpe_norm_i + w_decor * diversif_norm_i

Luego se eligen los N activos con mayor score.

---

## 4) OPTIMIZACION CON SUBCONJUNTO

Una vez seleccionados los activos:
- Se estima μ y Σ solo con ese subconjunto.
- Se optimiza con Markowitz (max Sharpe o min varianza).
- Se reconstruye un vector de pesos completo de 50 posiciones para cumplir el formato.

Esto reduce el impacto del error de estimacion y suele mejorar el Sharpe respecto
de optimizar con todos los activos.

---

## 5) COMPARACION DE ESTRATEGIAS

El modulo compara:
1. Equiponderada 50 activos
2. Markowitz 50 activos
3. Seleccion + Markowitz N activos

La teoria sugiere que la estrategia 3 puede superar a la 2 cuando:
- hay alta correlacion entre activos,
- el estimador de covarianza es ruidoso,
- y el N seleccionado captura la mayor parte de la diversificacion.

---

## 6) LIMITACIONES TEORICAS

- Los retornos esperados son ruidosos; la seleccion puede sobreajustar.
- La correlacion promedio es una medida simple y puede ocultar estructuras por
  clusters.
- El N optimo depende del periodo y del universo de activos.
