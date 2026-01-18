# RESUMEN TEÓRICO COMPLETO: OPTIMIZACIÓN DE CARTERAS DE MARKOWITZ

## INTRODUCCIÓN

Este documento presenta la teoría completa sobre optimización de carteras basada en la teoría de Markowitz (1952), incluyendo la optimización media-varianza, el Ratio de Sharpe, la frontera eficiente, y la incorporación del activo libre de riesgo. La teoría está basada en los notebooks teóricos de `teoria`.

**Conexión con módulos anteriores**: Este módulo utiliza los insights de diversificación del módulo `2equiponderada_diversificacion` para optimizar carteras. Mientras que el módulo 2 demuestra que la diversificación reduce el riesgo específico pero no el sistemático, este módulo encuentra las ponderaciones exactas que optimizan el trade-off riesgo-rendimiento, utilizando la misma matriz de covarianza (Σ) y principios teóricos de diversificación.

---

## 1. FUNDAMENTOS DE LA TEORÍA DE MARKOWITZ

### 1.1 El Problema Fundamental

Harry Markowitz (1952) revolucionó la teoría de inversiones al proponer que los inversores no solo se preocupan por la rentabilidad esperada, sino también por el riesgo (medido como varianza o volatilidad).

**Hipótesis Fundamentales:**
- Los inversores son **aversos al riesgo**: Prefieren mayor rentabilidad para un nivel dado de riesgo, o menor riesgo para un nivel dado de rentabilidad
- Los retornos de los activos son **variables aleatorias** con distribución conocida (o estimable)
- Los inversores toman decisiones en un **horizonte de un período**
- Existen **expectativas homogéneas**: Todos los inversores tienen las mismas estimaciones de μ y Σ

### 1.2 Función Objetivo de Markowitz

La función objetivo que Markowitz propone maximizar es:

$$\boxed{\max_w \quad f(w) = w^T \mu - \lambda \cdot w^T \Sigma w}$$

Donde:
- $w = [w_1, w_2, ..., w_N]^T$ es el vector de pesos (ponderaciones) de los activos
- $\mu = [\mu_1, \mu_2, ..., \mu_N]^T$ es el vector de rentabilidades esperadas
- $\Sigma$ es la matriz de covarianzas (N × N)
- $\lambda \geq 0$ es el **parámetro de aversión al riesgo**

**Interpretación:**
- **Primer término** ($w^T \mu$): Rentabilidad esperada de la cartera
- **Segundo término** ($\lambda \cdot w^T \Sigma w$): Penalización por riesgo (varianza)
- **Parámetro λ**: Controla el trade-off entre rentabilidad y riesgo
  - $\lambda$ pequeño: Prioriza rentabilidad (inversor menos averso al riesgo)
  - $\lambda$ grande: Prioriza reducir riesgo (inversor más averso al riesgo)

### 1.3 Solución Analítica (Sin Restricciones)

Si no hay restricciones (excepto que los pesos sumen 1), la solución analítica es:

$$\frac{\partial f(w)}{\partial w} = \mu - 2\lambda \Sigma w = 0$$

Resolviendo:

$$\boxed{w^* = \frac{1}{2\lambda} \Sigma^{-1} \mu}$$

**Propiedades:**
- La función $f(w)$ es **cóncava** (porque $\Sigma$ es semidefinida positiva)
- La condición de primer orden define un **único máximo global**
- La solución depende críticamente de $\Sigma^{-1}$ (inversa de la matriz de covarianzas)

**Problema Práctico:**
- La inversión de $\Sigma$ puede ser numéricamente inestable si la matriz está mal condicionada
- Con restricciones adicionales (long-only, límites, etc.), no hay solución analítica → se requiere optimización numérica

---

## 2. RESTRICCIONES COMUNES EN OPTIMIZACIÓN DE CARTERAS

### 2.1 Restricción de Inversión Completa

$$\sum_{i=1}^{N} w_i + w_{rf} = 1$$

**Interpretación:** Todo el capital disponible debe estar invertido (no hay efectivo ocioso).

### 2.2 Restricción Long-Only

$$w_i \geq 0 \quad \forall i$$

**Interpretación:** No se permiten posiciones cortas. Solo se puede comprar activos, no venderlos en corto.

**Razón:** 
- Simplifica la gestión operativa
- Reduce el riesgo de pérdidas ilimitadas
- Es común en fondos de inversión retail

### 2.3 Restricción de Límite en Renta Fija

$$0 \leq w_{rf} \leq w_{rf}^{max}$$

En nuestro caso: $w_{rf} \leq 0.1$ (máximo 10% en renta fija).

**Razón:** 
- Limita la exposición al activo libre de riesgo
- Fuerza a invertir en activos riesgosos (objetivo de la competencia)

### 2.4 Restricciones Adicionales (No Implementadas en el Módulo)

Otras restricciones comunes que podrían agregarse:
- **Límites por activo**: $w_i^{min} \leq w_i \leq w_i^{max}$
- **Límites por sector**: $\sum_{i \in S} w_i \leq w_S^{max}$
- **Restricciones de tracking error**: $\|w - w_{benchmark}\| \leq \epsilon$
- **Restricciones de liquidez**: Solo activos con volumen mínimo

---

## 3. OPTIMIZACIÓN CON ACTIVO LIBRE DE RIESGO

### 3.1 Incorporación del Activo Libre de Riesgo

Cuando se introduce un activo libre de riesgo con rentabilidad garantizada $r_f$:

**Características del Activo Libre de Riesgo:**
- **Rentabilidad garantizada**: $E(R_f) = r_f$ (constante, no aleatoria)
- **Varianza cero**: $\sigma_f^2 = 0$
- **Covarianza cero**: $Cov(R_f, R_i) = 0$ para cualquier activo riesgoso $i$

**Función Objetivo Extendida:**

$$\max_{w, w_{rf}} \quad w^T \mu + w_{rf} \cdot r_f - \lambda \cdot w^T \Sigma w$$

Sujeto a:
- $\sum_{i=1}^{N} w_i + w_{rf} = 1$
- $w_i \geq 0$ (long-only)
- $0 \leq w_{rf} \leq 0.1$ (límite renta fija)

### 3.2 Teorema de Separación de Tobin

**Enunciado:** Cuando existe un activo libre de riesgo, todos los inversores deberían mantener la **misma cartera de activos riesgosos** (llamada "cartera de mercado" o "cartera tangente", denotada $M$). Las diferencias en aversión al riesgo solo se reflejan en la proporción entre esta cartera y el activo libre de riesgo.

**Implicaciones:**
- La cartera óptima de activos riesgosos es **independiente** de la aversión al riesgo del inversor
- Todos los inversores deberían tener la misma cartera de activos riesgosos
- Solo cambia la proporción entre activos riesgosos y renta fija

**Nota:** Este teorema asume que se puede pedir prestado al tipo libre de riesgo sin límites. En nuestro caso, con el límite $w_{rf} \leq 0.1$, el teorema se modifica ligeramente.

### 3.3 Capital Market Line (CML)

La **Capital Market Line** es la línea recta que conecta el activo libre de riesgo con la cartera de mercado $M$ en el espacio riesgo-retorno.

**Ecuación de la CML:**

$$\boxed{\mu_p = r_f + \left(\frac{\mu_M - r_f}{\sigma_M}\right) \sigma_p}$$

Donde:
- $\mu_M$ y $\sigma_M$ son la rentabilidad y volatilidad de la cartera de mercado $M$
- El término $\frac{\mu_M - r_f}{\sigma_M}$ es el **Ratio de Sharpe de la cartera de mercado** (pendiente de la CML)

**Interpretación:**
- **Segmento $R_f$ a $M$**: Inversiones mixtas (combinaciones de $R_f$ y $M$)
- **Punto $M$**: Cartera de mercado (100% en activos riesgosos)
- **Más allá de $M$**: Carteras apalancadas (endeudamiento en $R_f$ para invertir más en $M$)
- **Por debajo de la CML**: Carteras ineficientes (siempre hay una mejor en la CML)

---

## 4. RATIO DE SHARPE Y OPTIMIZACIÓN DE MÁXIMO SHARPE

### 4.1 Definición del Ratio de Sharpe

El **Ratio de Sharpe** mide el rendimiento ajustado por riesgo:

$$\boxed{Sharpe = \frac{E(\tilde{R_p}) - r_f}{\sigma_p}}$$

Donde:
- $E(\tilde{R_p})$ es la rentabilidad esperada de la cartera
- $r_f$ es la tasa libre de riesgo
- $\sigma_p$ es la volatilidad (riesgo) de la cartera

**Versión con Datos Históricos:**

$$Sharpe_{historico} = \frac{\bar{R} - r_f}{\sigma} \times \sqrt{252}$$

Donde el factor $\sqrt{252}$ anualiza el ratio (252 días de trading por año).

### 4.2 Interpretación del Ratio de Sharpe

- **Sharpe alto**: Mayor rentabilidad por unidad de riesgo asumido
- **Sharpe bajo**: Menor rentabilidad ajustada por riesgo
- **Sharpe negativo**: La cartera tiene peor rendimiento que el activo libre de riesgo

**Benchmarks Típicos:**
- Sharpe < 0.5: Pobre
- Sharpe 0.5-1.0: Aceptable
- Sharpe 1.0-2.0: Bueno
- Sharpe > 2.0: Excelente

### 4.3 Problema de Optimización de Máximo Sharpe

**Formulación Directa (No-Lineal):**

$$\max_{w, w_{rf}} \quad \frac{w^T \mu + w_{rf} \cdot r_f - r_f}{\sqrt{w^T \Sigma w}}$$

Sujeto a restricciones.

**Problema:** Esta formulación es **no-lineal** y puede ser difícil de resolver numéricamente.

### 4.4 Reformulación como Problema Cuadrático Convexo

**Truco:** Reformular el problema para convertirlo en un problema cuadrático convexo (más fácil de resolver).

**Paso 1:** Introducir variables auxiliares $y$ y $y_{rf}$:

$$\min_{y, y_{rf}} \quad y^T \Sigma y$$

Sujeto a:
- $y^T \mu + y_{rf} \cdot r_f = 1$ (rentabilidad normalizada a 1)
- $y \geq 0$, $y_{rf} \geq 0$

**Paso 2:** Normalizar para obtener los pesos reales:

$$w = \frac{y}{\sum y + y_{rf}}, \quad w_{rf} = \frac{y_{rf}}{\sum y + y_{rf}}$$

**Ventajas:**
- Problema **cuadrático convexo** (eficiente de resolver)
- Más **numéricamente estable** que optimización no-lineal
- **Garantías de convergencia** si hay solución factible

**Justificación Matemática:**
- El problema original es equivalente a maximizar el Sharpe
- La normalización preserva las proporciones relativas
- El solver encuentra la solución óptima de forma eficiente

---

## 5. FRONTERA EFICIENTE

### 5.1 Definición de Frontera Eficiente

La **frontera eficiente** es el conjunto de carteras que:
- **Maximizan la rentabilidad esperada** para cada nivel dado de riesgo (volatilidad), O
- **Minimizan el riesgo** para cada nivel dado de rentabilidad esperada

**Propiedad Fundamental:** No existe ninguna cartera que tenga:
- Mayor rentabilidad con el mismo riesgo, O
- Menor riesgo con la misma rentabilidad

### 5.2 Construcción de la Frontera Eficiente

**Método:** Para cada rentabilidad objetivo $\mu_{target}$ en un rango $[r_f, \mu_{max}]$:

1. Resolver el problema de **mínima varianza**:

$$\min_{w, w_{rf}} \quad w^T \Sigma w$$

Sujeto a:
- $w^T \mu + w_{rf} \cdot r_f = \mu_{target}$ (rentabilidad objetivo)
- $\sum w + w_{rf} = 1$ (inversión completa)
- $w \geq 0$, $0 \leq w_{rf} \leq 0.1$ (restricciones)

2. Obtener la volatilidad mínima $\sigma_{min}$ para esa rentabilidad

3. Calcular el Sharpe Ratio: $Sharpe = \frac{\mu_{target} - r_f}{\sigma_{min}}$

4. Almacenar el punto $(\sigma_{min}, \mu_{target}, Sharpe)$

### 5.3 Propiedades de la Frontera Eficiente

**Forma Típica:**
- Curva **cóncava hacia arriba** en el espacio riesgo-rentabilidad
- **Monótona creciente**: Mayor riesgo implica mayor rentabilidad esperada
- **Suave**: Sin discontinuidades (siempre que $\Sigma$ sea definida positiva)

**Puntos Característicos:**
- **Punto más a la izquierda**: Cartera de **mínima varianza global** (GMV - Global Minimum Variance)
  - Menor riesgo posible
  - Rentabilidad correspondiente a ese riesgo mínimo
- **Punto más a la derecha**: Cartera de **máxima rentabilidad**
  - Máxima rentabilidad posible (típicamente 100% en el activo con mayor $\mu_i$)
  - Riesgo correspondiente
- **Punto de máximo Sharpe**: Intersección con la línea de máximo Sharpe
  - Mejor relación riesgo-retorno
  - Es la cartera óptima si se puede combinar con renta fija

### 5.4 Visualización de la Frontera Eficiente

**Ejes del Gráfico:**
- **Eje X**: Volatilidad (riesgo) en porcentaje
- **Eje Y**: Rentabilidad esperada en porcentaje

**Elementos del Gráfico:**
- **Curva de frontera eficiente**: Línea que muestra todas las carteras eficientes
- **Punto de máximo Sharpe**: Destacado con marcador especial (ej: estrella roja)
- **Línea de renta fija**: Punto en el eje Y correspondiente a $r_f$ con riesgo cero

**Interpretación:**
- Cualquier punto **por encima** de la frontera es inalcanzable
- Cualquier punto **por debajo** de la frontera es ineficiente (hay una mejor cartera en la frontera)

---

## 6. OPTIMIZACIÓN NUMÉRICA CON CVXPY

### 6.1 ¿Por qué CVXPY?

**CVXPY** es una librería de Python para optimización convexa que:
- Permite formular problemas de optimización de forma intuitiva
- Detecta automáticamente si el problema es convexo
- Selecciona el solver apropiado automáticamente
- Maneja problemas de optimización cuadrática de forma eficiente

### 6.2 Tipos de Problemas que Resuelve

**Problemas Cuadráticos Convexos (QP):**
- Función objetivo: cuadrática (o lineal)
- Restricciones: lineales (o cuadráticas convexas)
- Ejemplo: Optimización de Markowitz, máximo Sharpe reformulado

**Ventajas:**
- **Eficiencia**: Algoritmos especializados muy rápidos
- **Convergencia garantizada**: Si hay solución factible, la encuentra
- **Estabilidad numérica**: Manejo robusto de problemas mal condicionados

### 6.3 Solvers Disponibles

**ECOS (Embedded Conic Solver):**
- Rápido y confiable para problemas de tamaño medio
- Especializado en problemas cónicos

**CLARABEL:**
- Solver moderno y eficiente
- Buen rendimiento en problemas grandes

**SCS (Splitting Conic Solver):**
- Alternativa robusta
- Puede ser más lento pero más estable

**Solver por defecto:**
- CVXPY elige automáticamente el mejor disponible

### 6.4 Estructura de un Problema en CVXPY

```python
# 1. Definir variables
w = cp.Variable(n)  # Vector de pesos
w_rf = cp.Variable()  # Peso en renta fija

# 2. Construir función objetivo
objetivo = w @ mu + w_rf * rf - lambda_param * cp.quad_form(w, Sigma)

# 3. Definir restricciones
restricciones = [
    cp.sum(w) + w_rf == 1,  # Inversión completa
    w >= 0,  # Long-only
    w_rf >= 0,
    w_rf <= 0.1  # Límite renta fija
]

# 4. Crear y resolver problema
problema = cp.Problem(cp.Maximize(objetivo), restricciones)
problema.solve(solver=solver)

# 5. Extraer resultados
w_opt = w.value
w_rf_opt = w_rf.value
```

---

## 7. ANÁLISIS DE SENSIBILIDAD TEMPORAL

### 7.1 ¿Por qué Analizar Sensibilidad Temporal?

**Problema Fundamental:** Las estimaciones de $\mu$ y $\Sigma$ dependen de los datos históricos utilizados. Diferentes ventanas temporales pueden producir estimaciones muy diferentes.

**Objetivos del Análisis:**
- **Robustez**: ¿Los resultados son estables ante cambios en la ventana temporal?
- **Estabilidad**: ¿La cartera óptima cambia mucho con diferentes períodos?
- **Confiabilidad**: ¿Podemos confiar en las estimaciones históricas?

### 7.2 Metodología

**Proceso:**
1. Seleccionar diferentes ventanas temporales (ej: 252, 504, 756 días, y todos los datos)
2. Para cada ventana:
   - Calcular $\mu$ y $\Sigma$ usando solo los últimos N días
   - Optimizar cartera de máximo Sharpe
   - Calcular métricas (Sharpe, concentración, número de activos)
3. Comparar resultados entre ventanas

**Métricas a Analizar:**
- **Sharpe Ratio**: ¿Cambia mucho?
- **Concentración (Herfindahl)**: ¿La cartera se concentra en pocos activos?
- **Número de activos**: ¿Cuántos activos tienen peso significativo?
- **Peso en renta fija**: ¿Cuánto se invierte en renta fija?

### 7.3 Interpretación de Resultados

**Cartera Robusta:**
- Las métricas cambian poco entre ventanas
- La composición de la cartera es similar
- **Conclusión**: La estrategia es estable y confiable

**Cartera Inestable:**
- Las métricas cambian mucho entre ventanas
- La composición de la cartera varía significativamente
- **Conclusión**: La estrategia es sensible a los datos históricos, puede ser poco confiable

**Recomendaciones:**
- Si la cartera es inestable, considerar:
  - Usar estimadores más robustos de $\mu$ y $\Sigma$
  - Aplicar regularización (shrinkage)
  - Usar ventanas más largas (más datos)
  - Implementar restricciones adicionales (límites por activo)

---

## 8. LIMITACIONES Y CRÍTICAS A LA TEORÍA DE MARKOWITZ

### 8.1 Limitaciones Teóricas

**Hipótesis Irrealistas:**
- **Expectativas homogéneas**: En la práctica, los inversores tienen estimaciones diferentes
- **Sin costes de transacción**: Los rebalanceos tienen costes
- **Sin impuestos**: La fiscalidad afecta las decisiones
- **Horizonte de un período**: No considera rebalanceo dinámico

**Asunciones sobre Distribuciones:**
- **Normalidad**: Asume que los retornos son normales (en la práctica, hay colas pesadas)
- **Estacionariedad**: Asume que $\mu$ y $\Sigma$ son constantes (pueden cambiar en el tiempo)
- **Independencia temporal**: Asume que los retornos son independientes (puede haber autocorrelación)

### 8.2 Problemas Prácticos

**Estimación de Parámetros:**
- **Error en $\mu$**: Las rentabilidades esperadas son muy difíciles de estimar
- **Error en $\Sigma$**: La matriz de covarianza puede estar mal estimada, especialmente con pocos datos
- **Inestabilidad**: Pequeños cambios en $\mu$ o $\Sigma$ pueden causar grandes cambios en los pesos óptimos

**Problemas Numéricos:**
- **Matriz mal condicionada**: Si $\Sigma$ está mal condicionada, la inversión es inestable
- **Dimensionalidad**: Con muchos activos y pocos datos, $\Sigma$ puede ser singular o casi singular

**Concentración:**
- Las carteras óptimas pueden ser muy concentradas (pocos activos con peso alto)
- Esto va contra el principio de diversificación

### 8.3 Mejoras y Extensiones

**Estimadores Robustos:**
- **Shrinkage de Ledoit-Wolf**: Mejora la estimación de $\Sigma$
- **Media recortada**: Reduce el impacto de outliers en $\mu$
- **Covarianza exponencialmente ponderada**: Da más peso a datos recientes

**Regularización:**
- **Límites por activo**: Evita concentración excesiva
- **Penalización L1/L2**: Fuerza diversificación
- **Tracking error**: Limita desviación de un benchmark

**Modelos Alternativos:**
- **Black-Litterman**: Incorpora views del inversor
- **Risk Parity**: Equipara contribuciones al riesgo
- **Factor Models**: Reduce dimensionalidad usando factores

---

## 9. RESUMEN DE FÓRMULAS CLAVE

### 9.1 Función Objetivo de Markowitz

$$\max_w \quad w^T \mu - \lambda \cdot w^T \Sigma w$$

### 9.2 Rentabilidad de Cartera

$$\mu_p = w^T \mu + w_{rf} \cdot r_f$$

### 9.3 Varianza de Cartera

$$\sigma_p^2 = w^T \Sigma w$$

### 9.4 Volatilidad de Cartera

$$\sigma_p = \sqrt{w^T \Sigma w}$$

### 9.5 Ratio de Sharpe

$$Sharpe = \frac{\mu_p - r_f}{\sigma_p}$$

### 9.6 Capital Market Line

$$\mu_p = r_f + \left(\frac{\mu_M - r_f}{\sigma_M}\right) \sigma_p$$

### 9.7 Solución Analítica (Sin Restricciones)

$$w^* = \frac{1}{2\lambda} \Sigma^{-1} \mu$$

---

## 10. REFERENCIAS Y LECTURAS ADICIONALES

### 10.1 Papers Fundamentales

- **Markowitz, H. (1952)**: "Portfolio Selection". Journal of Finance, 7(1), 77-91.
- **Sharpe, W. F. (1966)**: "Mutual Fund Performance". Journal of Business, 39(1), 119-138.
- **Tobin, J. (1958)**: "Liquidity Preference as Behavior Towards Risk". Review of Economic Studies, 25(2), 65-86.

### 10.2 Libros Recomendados

- **Elton, E. J., Gruber, M. J., Brown, S. J., & Goetzmann, W. N. (2014)**: "Modern Portfolio Theory and Investment Analysis". Wiley.
- **Bodie, Z., Kane, A., & Marcus, A. J. (2020)**: "Investments". McGraw-Hill Education.

### 10.3 Recursos Online

- Documentación de CVXPY: https://www.cvxpy.org/
- Notebooks teóricos en `teoria/`

---

## CONCLUSIÓN

La teoría de Markowitz proporciona un marco sólido para la optimización de carteras, pero debe aplicarse con cuidado considerando sus limitaciones. El módulo `3markowitz.py` implementa las técnicas fundamentales de manera eficiente usando optimización convexa, permitiendo encontrar carteras óptimas que maximizan el rendimiento ajustado por riesgo bajo restricciones realistas.
