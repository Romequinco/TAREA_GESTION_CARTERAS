# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MÓDULO 3MARKOWITZ

## INTRODUCCIÓN

El módulo `3markowitz.py` implementa las técnicas clásicas de optimización de carteras basadas en la teoría de Markowitz. Su función principal es encontrar las carteras óptimas que maximizan el rendimiento ajustado por riesgo, utilizando optimización convexa con CVXPY.

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1. FUNCIÓN: `_obtener_solver_disponible()`

#### Propósito
Seleccionar el solver de optimización más adecuado disponible en CVXPY para resolver los problemas de optimización de carteras.

#### Proceso Paso a Paso:

**Paso 1.1: Verificación de ECOS**
- Verifica si el solver ECOS está disponible: `'ECOS' in cp.installed_solvers()`
- Si está disponible, retorna `cp.ECOS` inmediatamente
- **Razón**: ECOS es un solver rápido y confiable para problemas cuadráticos convexos

**Paso 1.2: Verificación de CLARABEL**
- Si ECOS no está disponible, verifica CLARABEL: `'CLARABEL' in cp.installed_solvers()`
- Si está disponible, retorna `cp.CLARABEL`
- **Razón**: CLARABEL es un solver moderno y eficiente

**Paso 1.3: Verificación de SCS**
- Si CLARABEL no está disponible, verifica SCS: `'SCS' in cp.installed_solvers()`
- Si está disponible, retorna `cp.SCS`
- **Razón**: SCS es un solver alternativo robusto

**Paso 1.4: Solver por defecto**
- Si ninguno de los anteriores está disponible, retorna `None`
- CVXPY elegirá automáticamente el mejor solver disponible
- **Razón**: Garantiza que el código funcione incluso si no hay solvers específicos instalados

#### Resultado
- Retorna el solver más adecuado disponible, o `None` para usar el solver por defecto de CVXPY

---

### 2. FUNCIÓN: `optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param)`

#### Propósito
Optimizar una cartera usando la función objetivo clásica de Markowitz con un parámetro de aversión al riesgo λ. Esta función resuelve el problema de maximizar el rendimiento esperado menos el riesgo (ponderado por λ).

#### Proceso Paso a Paso:

**Paso 2.1: Definición de variables de optimización**
- Crea variable `w` de dimensión `n` (número de activos): `w = cp.Variable(n)`
- Crea variable `w_rf` escalar para el peso en renta fija: `w_rf = cp.Variable()`
- **Interpretación**: `w` representa los pesos en activos riesgosos, `w_rf` el peso en renta fija

**Paso 2.2: Construcción de función objetivo**
- Calcula rentabilidad esperada: `rentabilidad = w @ mu + w_rf * rf`
  - `w @ mu`: rentabilidad de activos riesgosos (producto punto)
  - `w_rf * rf`: rentabilidad de renta fija
- Calcula riesgo (varianza): `riesgo = cp.quad_form(w, Sigma)`
  - `cp.quad_form(w, Sigma)` es equivalente a `w^T Σ w`
- Construye objetivo: `objetivo = rentabilidad - lambda_param * riesgo`
- **Fórmula matemática**: max w^T μ + w_rf * rf - λ * w^T Σ w

**Paso 2.3: Definición de restricciones**
- Restricción de inversión completa: `cp.sum(w) + w_rf == 1`
  - Todos los pesos deben sumar exactamente 1 (100% de inversión)
- Restricción long-only: `w >= 0`
  - No se permiten posiciones cortas en activos riesgosos
- Restricción renta fija no negativa: `w_rf >= 0`
  - No se puede pedir prestado (no hay w_rf negativo)
- Restricción límite renta fija: `w_rf <= 0.1`
  - Máximo 10% en renta fija según reglas de la competencia

**Paso 2.4: Resolución del problema**
- Crea problema de optimización: `problema = cp.Problem(cp.Maximize(objetivo), restricciones)`
- Obtiene solver disponible: `solver = _obtener_solver_disponible()`
- Resuelve el problema:
  - Si hay solver específico: `problema.solve(solver=solver, verbose=False)`
  - Si no: `problema.solve(verbose=False)`
- **Razón**: CVXPY convierte el problema a formato estándar y lo resuelve numéricamente

**Paso 2.5: Verificación de solución**
- Verifica status: `if problema.status != 'optimal'`
- Si no es óptimo, imprime advertencia y retorna `None`
- **Razón**: Problemas mal formulados o sin solución factible pueden fallar

**Paso 2.6: Extracción de resultados**
- Extrae pesos óptimos: `w_opt = w.value`
- Extrae peso en renta fija: `w_rf_opt = w_rf.value`
- **Interpretación**: Estos son los pesos que maximizan la función objetivo

**Paso 2.7: Cálculo de métricas**
- Rentabilidad esperada: `mu_p = w_opt @ mu + w_rf_opt * rf`
- Volatilidad: `sigma_p = np.sqrt(w_opt @ Sigma @ w_opt)`
- Sharpe Ratio: `sharpe = (mu_p - rf) / sigma_p if sigma_p > 0 else 0`
- **Fórmula Sharpe**: (μp - rf) / σp

**Paso 2.8: Retorno de resultados**
- Retorna diccionario con:
  - `'w'`: pesos en activos riesgosos
  - `'w_rf'`: peso en renta fija
  - `'sharpe'`: Sharpe Ratio
  - `'rentabilidad'`: rentabilidad esperada anualizada
  - `'volatilidad'`: volatilidad anualizada

#### Resultado
- Diccionario con cartera óptima y sus métricas, o `None` si el problema no tiene solución

#### Interpretación del parámetro λ
- **λ pequeño (ej: 0.1)**: Prioriza rentabilidad → cartera más riesgosa y rentable
- **λ medio (ej: 1.0)**: Balance entre rentabilidad y riesgo
- **λ grande (ej: 10.0)**: Prioriza reducir riesgo → cartera más conservadora

---

### 3. FUNCIÓN: `optimizar_sharpe_maximo(mu, Sigma, rf)`

#### Propósito
Optimizar una cartera para maximizar directamente el Sharpe Ratio. Esta es la estrategia más común en optimización de carteras, ya que maximiza el rendimiento ajustado por riesgo.

#### Proceso Paso a Paso:

**Paso 3.1: Reformulación del problema**
- El problema original es no-lineal: max (μp - rf) / σp
- Se reformula como problema cuadrático convexo:
  - Variables auxiliares: `y` (activos riesgosos) y `y_rf` (renta fija)
  - Objetivo: `min y^T Σ y` (minimizar varianza)
  - Restricción: `y^T μ + y_rf * rf == 1` (rentabilidad normalizada a 1)
- **Razón**: Esta reformulación permite usar optimización cuadrática convexa (más eficiente)

**Paso 3.2: Definición de variables**
- Crea `y = cp.Variable(n)` para activos riesgosos
- Crea `y_rf = cp.Variable()` para renta fija
- **Nota**: Estas son variables auxiliares, no los pesos finales

**Paso 3.3: Construcción del problema reformulado**
- Objetivo: `objetivo = cp.quad_form(y, Sigma)` (minimizar varianza)
- Restricciones:
  - `y @ mu + y_rf * rf == 1`: Rentabilidad normalizada
  - `y >= 0`: Long-only
  - `y_rf >= 0`: Renta fija no negativa

**Paso 3.4: Resolución**
- Crea y resuelve el problema de optimización
- Verifica que el status sea 'optimal'

**Paso 3.5: Normalización de pesos**
- Calcula suma: `suma = np.sum(y.value) + y_rf.value`
- Normaliza: `w_opt = y.value / suma` y `w_rf_opt = y_rf.value / suma`
- **Razón**: Las variables auxiliares `y` no suman 1, necesitan normalización

**Paso 3.6: Ajuste de límite de renta fija**
- Verifica: `if w_rf_opt > 0.1`
- Si excede el límite:
  - Fija `w_rf_opt = 0.1`
  - Renormaliza activos riesgosos: `w_opt = w_opt * (1 - w_rf_opt) / np.sum(w_opt)`
- **Razón**: Respeta la restricción de máximo 10% en renta fija

**Paso 3.7: Cálculo de métricas finales**
- Calcula rentabilidad, volatilidad y Sharpe Ratio con los pesos finales
- Retorna diccionario con resultados

#### Resultado
- Diccionario con cartera de máximo Sharpe Ratio y sus métricas

#### Ventajas de esta formulación
- **Eficiencia**: Problema cuadrático convexo (rápido de resolver)
- **Estabilidad**: Más numéricamente estable que optimización no-lineal directa
- **Garantías**: Si hay solución factible, el solver la encontrará

---

### 4. FUNCIÓN: `construir_frontera_eficiente(mu, Sigma, rf, n_puntos=50)`

#### Propósito
Construir la frontera eficiente de carteras, que muestra el trade-off óptimo entre riesgo y rentabilidad. La frontera eficiente contiene todas las carteras que maximizan la rentabilidad para cada nivel de riesgo dado.

#### Proceso Paso a Paso:

**Paso 4.1: Definición del rango de rentabilidades objetivo**
- Calcula rentabilidad mínima: `mu_min = rf` (tasa libre de riesgo)
- Calcula rentabilidad máxima: `mu_max = mu.max() * 0.95` (95% del máximo, evita extremos)
- Genera puntos: `mu_targets = np.linspace(mu_min, mu_max, n_puntos)`
- **Razón**: Crea un rango uniforme de rentabilidades objetivo para evaluar

**Paso 4.2: Inicialización de lista de resultados**
- Crea lista vacía: `fronteras = []`
- Esta lista almacenará los resultados de cada punto de la frontera

**Paso 4.3: Bucle sobre rentabilidades objetivo**
- Para cada `mu_t` en `mu_targets`:
  
  **Paso 4.3.1: Definición de variables**
  - Crea `w = cp.Variable(n)` y `w_rf = cp.Variable()`
  
  **Paso 4.3.2: Problema de optimización**
  - Objetivo: `min cp.quad_form(w, Sigma)` (minimizar varianza)
  - Restricciones:
    - `w @ mu + w_rf * rf == mu_t`: Rentabilidad objetivo
    - `cp.sum(w) + w_rf == 1`: Inversión completa
    - `w >= 0`: Long-only
    - `w_rf >= 0` y `w_rf <= 0.1`: Límites renta fija
  
  **Paso 4.3.3: Resolución**
  - Resuelve el problema de optimización
  - Verifica que el status sea 'optimal'
  
  **Paso 4.3.4: Cálculo de métricas**
  - Volatilidad: `sigma_p = np.sqrt(objetivo.value)`
  - Sharpe Ratio: `sharpe = (mu_t - rf) / sigma_p if sigma_p > 0 else 0`
  
  **Paso 4.3.5: Almacenamiento**
  - Añade diccionario a `fronteras` con rentabilidad, volatilidad y Sharpe

**Paso 4.4: Construcción de DataFrame**
- Convierte lista a DataFrame: `return pd.DataFrame(fronteras)`
- Columnas: 'rentabilidad', 'volatilidad', 'sharpe'

#### Resultado
- DataFrame con `n_puntos` filas, cada una representando un punto en la frontera eficiente

#### Interpretación de la Frontera Eficiente
- **Forma típica**: Curva cóncava hacia arriba en el espacio riesgo-rentabilidad
- **Punto más a la izquierda**: Cartera de mínima varianza (menor riesgo)
- **Punto más a la derecha**: Cartera de máxima rentabilidad (mayor riesgo)
- **Punto óptimo**: Intersección con la línea de máximo Sharpe (si se incluye renta fija)

---

### 5. FUNCIÓN: `visualizar_frontera_eficiente(frontera_df, cartera_max_sharpe=None, ruta_guardado=None)`

#### Propósito
Crear una visualización gráfica de la frontera eficiente y, opcionalmente, destacar la cartera de máximo Sharpe Ratio.

#### Proceso Paso a Paso:

**Paso 5.1: Creación de figura**
- Crea figura: `plt.figure(figsize=(12, 8))`
- **Razón**: Tamaño adecuado para visualización clara

**Paso 5.2: Gráfico de frontera eficiente**
- Dibuja línea: `plt.plot(frontera_df['volatilidad'] * 100, frontera_df['rentabilidad'] * 100, ...)`
- Convierte a porcentaje multiplicando por 100
- Estilo: línea azul continua, grosor 2
- Etiqueta: 'Frontera Eficiente'

**Paso 5.3: Destacado de cartera máximo Sharpe (opcional)**
- Si se proporciona `cartera_max_sharpe`:
  - Dibuja punto: `plt.scatter(...)`
  - Estilo: estrella roja grande (s=300), borde negro
  - Etiqueta: muestra el Sharpe Ratio en la leyenda
  - `zorder=5`: Asegura que esté por encima de la línea

**Paso 5.4: Configuración de ejes y etiquetas**
- Eje X: 'Volatilidad Anualizada (%)'
- Eje Y: 'Rentabilidad Esperada Anualizada (%)'
- Título: 'Frontera Eficiente de Carteras'
- Leyenda: muestra frontera y cartera máximo Sharpe
- Grid: activado con transparencia

**Paso 5.5: Guardado (opcional)**
- Si se proporciona `ruta_guardado`:
  - Guarda figura: `plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')`
  - **Razón**: Permite guardar gráficos para reportes

**Paso 5.6: Retorno**
- Retorna: `plt.gcf()` (get current figure)
- Permite modificar la figura después si es necesario

#### Resultado
- Figura de matplotlib con la frontera eficiente visualizada

---

### 6. FUNCIÓN: `analizar_sensibilidad_temporal(retornos, rf, ventanas=[252, 504, 756, None])`

#### Propósito
Analizar cómo cambian los resultados de optimización cuando se usan diferentes ventanas temporales para estimar μ y Σ. Esto evalúa la robustez y estabilidad de la estrategia.

#### Proceso Paso a Paso:

**Paso 6.1: Inicialización de resultados**
- Crea lista vacía: `resultados = []`

**Paso 6.2: Bucle sobre ventanas temporales**
- Para cada `ventana` en la lista:
  
  **Paso 6.2.1: Selección de datos**
  - Si `ventana is None`: usa todos los datos (`datos = retornos`)
  - Si `ventana` es un número: usa últimos N días (`datos = retornos.iloc[-ventana:]`)
  - Asigna nombre: `nombre_ventana = 'Completa'` o `f'{ventana}d'`
  
  **Paso 6.2.2: Cálculo de estadísticas**
  - Media anualizada: `mu_v = datos.mean().values * 252`
  - Covarianza anualizada: `Sigma_v = datos.cov().values * 252`
  - **Razón**: Anualiza las estadísticas para comparación estándar
  
  **Paso 6.2.3: Optimización**
  - Optimiza cartera máximo Sharpe: `cartera = optimizar_sharpe_maximo(mu_v, Sigma_v, rf)`
  - Verifica que haya solución: `if cartera:`
  
  **Paso 6.2.4: Cálculo de métricas adicionales**
  - Índice de concentración (Herfindahl): `concentracion = np.sum(cartera['w']**2)`
    - **Interpretación**: 0 = diversificado, 1 = concentrado en un activo
  - Número de activos: `n_activos = np.sum(cartera['w'] > 0.01)`
    - Activos con peso > 1%
  
  **Paso 6.2.5: Almacenamiento**
  - Añade diccionario a `resultados` con:
    - 'ventana': nombre de la ventana
    - 'sharpe', 'rentabilidad', 'volatilidad': métricas de rendimiento
    - 'concentracion', 'n_activos', 'peso_rf': métricas de estructura

**Paso 6.3: Construcción de DataFrame**
- Convierte lista a DataFrame: `return pd.DataFrame(resultados)`

#### Resultado
- DataFrame con una fila por ventana temporal, mostrando cómo cambian las métricas

#### Interpretación de Resultados
- **Estabilidad**: Si las métricas cambian poco entre ventanas → estrategia robusta
- **Inestabilidad**: Si las métricas cambian mucho → estrategia sensible a datos históricos
- **Concentración**: Si la concentración es alta → cartera poco diversificada
- **Número de activos**: Si es bajo → cartera concentrada en pocos activos

---

## RESUMEN DE FLUJO DE TRABAJO TÍPICO

1. **Cargar y preparar datos** (módulo 1datos):
   - Cargar retornos diarios
   - Calcular μ y Σ anualizados usando `PreparadorDatos`

2. **Optimizar cartera**:
   - Usar `optimizar_sharpe_maximo()` para obtener cartera óptima
   - O usar `optimizar_markowitz_lambda()` con diferentes valores de λ

3. **Analizar frontera eficiente**:
   - Construir frontera con `construir_frontera_eficiente()`
   - Visualizar con `visualizar_frontera_eficiente()`

4. **Evaluar robustez**:
   - Analizar sensibilidad temporal con `analizar_sensibilidad_temporal()`
   - Verificar que los resultados sean estables

5. **Validar y reportar**:
   - Verificar que los pesos cumplan restricciones
   - Calcular métricas finales
   - Generar reportes y visualizaciones

---

## NOTAS IMPORTANTES

### Restricciones del Problema
- **Long-only**: No se permiten posiciones cortas (w >= 0)
- **Inversión completa**: Todos los pesos suman 1 (incluyendo renta fija)
- **Límite renta fija**: Máximo 10% en renta fija (w_rf <= 0.1)
- **50 activos**: El vector w tiene dimensión 50

### Consideraciones Numéricas
- La matriz Σ debe ser semidefinida positiva (siempre lo es si viene de covarianza)
- Si el problema no tiene solución factible, retorna `None`
- Los solvers pueden tener problemas con matrices mal condicionadas

### Interpretación de Resultados
- **Sharpe Ratio**: Mide rendimiento ajustado por riesgo (mayor es mejor)
- **Rentabilidad**: Rentabilidad esperada anualizada (en decimal, ej: 0.15 = 15%)
- **Volatilidad**: Riesgo anualizado (en decimal, ej: 0.20 = 20%)
- **Pesos**: Fracciones que suman 1 (ej: 0.05 = 5% del capital)
