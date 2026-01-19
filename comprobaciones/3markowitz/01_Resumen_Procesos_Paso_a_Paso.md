# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MODULO 3MARKOWITZ

## INTRODUCCION

El modulo `3markowitz.py` resuelve problemas de optimizacion de carteras con CVXPY: Markowitz con lambda, maximo Sharpe y frontera eficiente, ademas de sensibilidad temporal.

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1) FUNCION: `_obtener_solver_disponible()`

**Proposito**  
Elegir un solver disponible en CVXPY.

**Paso a paso**
1. Si ECOS esta instalado, retorna `cp.ECOS`.
2. Si no, prueba CLARABEL.
3. Si no, prueba SCS.
4. Si ninguno existe, retorna `None` (CVXPY elige por defecto).

---

### 2) FUNCION: `optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param)`

**Proposito**  
Maximizar rentabilidad menos riesgo con aversion `lambda_param`.

**Paso a paso**
1. Define variables `w` (N activos) y `w_rf` (renta fija).
2. Define rentabilidad: `w @ mu + w_rf * rf`.
3. Define riesgo: `quad_form(w, Sigma)`.
4. Objetivo: `rentabilidad - lambda_param * riesgo`.
5. Restricciones:
   - `sum(w) + w_rf == 1`
   - `w >= 0`
   - `w_rf >= 0`
   - `w_rf <= 0.1`
6. Resuelve con el solver disponible.
7. Si el status no es `optimal`, imprime advertencia y retorna `None`.
8. Extrae pesos y calcula:
   - rentabilidad, volatilidad, Sharpe.
9. Retorna diccionario con pesos y metricas.

**Salidas**
- Diccionario con `w`, `w_rf`, `sharpe`, `rentabilidad`, `volatilidad`.
- Advertencia en consola si el problema no es optimo.

---

### 3) FUNCION: `optimizar_sharpe_maximo(mu, Sigma, rf)`

**Proposito**  
Maximizar Sharpe Ratio via reformulacion convexa.

**Paso a paso**
1. Define variables auxiliares `y` y `y_rf`.
2. Objetivo: minimizar `y^T Sigma y`.
3. Restriccion de rentabilidad normalizada: `y @ mu + y_rf * rf == 1`.
4. Long-only: `y >= 0`, `y_rf >= 0`.
5. Resuelve el problema.
6. Si no es `optimal`, imprime advertencia y retorna `None`.
7. Normaliza:
   - `suma = sum(y) + y_rf`
   - Si `suma <= 0`, imprime error y retorna `None`.
   - `w = y / suma`, `w_rf = y_rf / suma`.
8. Si `w_rf > 0.1`, fija `w_rf = 0.1` y renormaliza `w`.
9. Calcula rentabilidad, volatilidad y Sharpe.
10. Retorna diccionario con resultados.

---

### 4) FUNCION: `construir_frontera_eficiente(mu, Sigma, rf, n_puntos=50)`

**Proposito**  
Construir la frontera eficiente resolviendo multiples problemas de minima varianza.

**Paso a paso**
1. Define rango de rentabilidades objetivo:
   - `mu_min = rf`
   - `mu_max = mu.max() * 0.95`
2. Genera `mu_targets` con `n_puntos`.
3. Para cada `mu_t`:
   - Define `w` y `w_rf`.
   - Minimiza `w^T Sigma w`.
   - Restricciones:
     - `w @ mu + w_rf * rf == mu_t`
     - `sum(w) + w_rf == 1`
     - `w >= 0`
     - `w_rf >= 0` y `w_rf <= 0.1`
   - Si es optimo, guarda rentabilidad, volatilidad y Sharpe.
4. Retorna DataFrame con los puntos validos.

---

### 5) FUNCION: `visualizar_frontera_eficiente(frontera_df, cartera_max_sharpe=None, ruta_guardado=None)`

**Proposito**  
Graficar frontera eficiente y marcar la cartera de maximo Sharpe (si se pasa).

**Paso a paso**
1. Crea figura.
2. Grafica `volatilidad` vs `rentabilidad` (ambas en porcentaje).
3. Si se pasa `cartera_max_sharpe`, dibuja un punto estrella con su Sharpe.
4. Configura etiquetas, titulo y grid.
5. Guarda si hay `ruta_guardado`.
6. Retorna la figura.

---

### 6) FUNCION: `analizar_sensibilidad_temporal(retornos, rf, ventanas=[252, 504, 756, None])`

**Proposito**  
Evaluar como cambian los resultados al usar diferentes ventanas de datos.

**Paso a paso**
1. Itera sobre cada `ventana`:
   - Si `None`, usa todos los datos.
   - Si es numero, usa los ultimos `ventana` dias.
2. Calcula `mu` y `Sigma` anualizados con esa ventana.
3. Optimiza con `optimizar_sharpe_maximo`.
4. Si hay solucion:
   - Calcula Herfindahl: `sum(w**2)`.
   - Cuenta activos con peso > 1%.
   - Guarda metricas (sharpe, rentabilidad, volatilidad, concentracion, n_activos, peso_rf).
5. Retorna DataFrame con resultados por ventana.

---

## FLUJO DE TRABAJO TIPICO

1. Calcular `mu` y `Sigma` con el modulo 1datos.
2. Optimizar con `optimizar_sharpe_maximo` o `optimizar_markowitz_lambda`.
3. Construir y graficar frontera eficiente.
4. Analizar sensibilidad temporal.

---

## VALIDACIONES Y SALIDAS EN CONSOLA

- Advertencias si el status no es `optimal`.
- Error si la suma para normalizar es no positiva.
- Limite de renta fija aplicado en ambos metodos.

---

## NOTAS IMPORTANTES

- Las dimensiones dependen de `len(mu)` (no se asume un numero fijo de activos).
- La frontera solo incluye puntos con solucion optima.
- El Sharpe se calcula como `(mu_p - rf) / sigma_p`.
