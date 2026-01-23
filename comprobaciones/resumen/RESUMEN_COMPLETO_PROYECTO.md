# RESUMEN COMPLETO: PROYECTO DE OPTIMIZACIÓN DE CARTERAS

## INTRODUCCIÓN

Este proyecto implementa un sistema completo de optimización de carteras para maximizar el Sharpe Ratio anualizado. El sistema procesa datos históricos de 50 activos durante 1760 días, aplica teoría moderna de carteras (Markowitz), análisis de diversificación, selección inteligente de activos y validación final.

---

## ARQUITECTURA DEL PROYECTO

El proyecto está organizado en 5 módulos principales que se ejecutan secuencialmente:

1. **1datos.py**: Exploración y preparación de datos
2. **2equiponderada_diversificacion.py**: Análisis de diversificación y carteras equiponderadas
3. **3markowitz.py**: Optimización clásica de Markowitz
4. **4seleccion_activos.py**: Selección inteligente de activos
5. **5analisis_multipunto.py**: Análisis comparativo de múltiples puntos en la frontera
6. **validacion.py**: Validación y exportación final

---

## MÓDULO 1: EXPLORACIÓN Y PREPARACIÓN DE DATOS (1datos.py)

### Funciones Principales

#### `cargar_retornos(ruta_csv)`
**Teoría**: Carga datos históricos preservando integridad de todos los activos.

**Proceso**:
1. Lee CSV con `pd.read_csv()` sin usar primera columna como índice
2. Valida estructura: 1760 días × 50 activos
3. Detecta y reemplaza valores NaN por 0
4. Detecta y reemplaza infinitos por 0
5. Retorna DataFrame limpio

**Resultado**: DataFrame con retornos diarios listo para análisis.

---

#### `calcular_estadisticas_basicas(retornos, rf_anual=0.02)`
**Teoría**: Calcula estadísticas descriptivas anualizadas usando 252 días de trading.

**Proceso**:
1. Convierte tasa libre de riesgo anual a diaria: `rf_diario = (1 + rf_anual)^(1/252) - 1`
2. Calcula media diaria: `media_diaria = retornos.mean()`
3. Calcula volatilidad diaria: `std_diaria = retornos.std()`
4. Calcula Sharpe histórico anualizado: `(media_diaria - rf_diario) / std_diaria * sqrt(252)`
5. Anualiza rentabilidad: `media_anual = media_diaria * 252`
6. Anualiza volatilidad: `std_anual = std_diaria * sqrt(252)`
7. Reemplaza Sharpe infinito por 0
8. Ordena por Sharpe descendente

**Resultado**: DataFrame con estadísticas por activo ordenadas por Sharpe Ratio.

---

#### `analizar_correlaciones(retornos)`
**Teoría**: La correlación mide dependencia lineal entre activos. Correlación baja permite diversificación.

**Proceso**:
1. Calcula matriz de correlación de Pearson: `corr_matrix = retornos.corr()`
2. Extrae triángulo superior (sin diagonal) para evitar duplicados
3. Calcula estadísticas: media, min, max, std de correlaciones
4. Retorna diccionario con matriz y estadísticas

**Resultado**: Matriz de correlación y estadísticas resumen para análisis de diversificación.

---

#### `analizar_temporal(retornos)`
**Teoría**: Análisis temporal identifica patrones, volatilidad dinámica y evolución del mercado.

**Proceso**:
1. Calcula retornos acumulados: `(1 + retornos).cumprod()` (valor de inversión unitaria)
2. Calcula índice de mercado equiponderado: `retornos.mean(axis=1)`
3. Calcula volatilidad rolling 63 días anualizada: `retornos.rolling(63).std() * sqrt(252)`
4. Retorna diccionario con las tres series

**Resultado**: Series temporales para visualización y análisis de evolución.

---

#### Clase `PreparadorDatos`
**Teoría**: Prepara vectores μ (rentabilidades esperadas) y matrices Σ (covarianzas) anualizados para optimización.

**Métodos**:

**`__init__(retornos, rf_anual=0.02)`**:
- Almacena retornos y tasa libre de riesgo
- Calcula `rf_diario` para uso interno

**`calcular_estadisticas(ventana=None)`**:
1. Selecciona datos (todos o últimos N días si `ventana` especificada)
2. Calcula μ diario: `datos.mean().values` (vector N×1)
3. Calcula Σ diaria: `datos.cov().values` (matriz N×N)
4. Anualiza: `mu_anual = mu_diario * 252`, `cov_anual = cov_matriz * 252`
5. Retorna `self` para encadenamiento

**`obtener_estadisticas()`**:
- Valida que se hayan calculado estadísticas
- Retorna tupla: `(mu_anual, cov_anual, rf_anual)`

**Resultado**: Datos preparados en formato numpy para optimización convexa.

---

## MÓDULO 2: ANÁLISIS DE DIVERSIFICACIÓN (2equiponderada_diversificacion.py)

### Funciones Principales

#### `analizar_cartera_equiponderada(retornos)`
**Teoría**: Descompone riesgo de cartera equiponderada en riesgo específico (diversificable) y sistemático (no diversificable).

**Fórmula teórica**: `σ²ₚ = (1/n)V̄ + (1-1/n)σ̄ᵢⱼ`

**Proceso**:
1. Calcula matriz de covarianza diaria
2. Calcula varianza media (promedio de diagonal)
3. Calcula covarianza media (promedio de triángulo superior)
4. Anualiza multiplicando por 252
5. Calcula riesgo específico: `(1/n) * varianza_media`
6. Calcula riesgo sistemático: `covarianza_media`
7. Calcula varianza total: `riesgo_especifico + riesgo_sistematico`
8. Verifica con cálculo real de cartera equiponderada

**Resultado**: Diccionario con descomposición de riesgo y volatilidad de cartera.

---

#### `simular_frontera_diversificacion(retornos, n_valores=None, n_simulaciones=100)`
**Teoría**: Simula efecto de diversificación variando número de activos. Identifica número óptimo donde beneficios marginales se reducen.

**Proceso**:
1. Para cada N en `n_valores` (default: [2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50]):
   - Realiza `n_simulaciones` selecciones aleatorias de N activos
   - Para cada selección:
     - Calcula matriz de covarianza del subconjunto
     - Calcula varianza y covarianza media
     - Anualiza
     - Calcula componentes de riesgo según fórmula teórica
     - Calcula volatilidad total
   - Promedia resultados de todas las simulaciones
   - Calcula reducción porcentual vs N-1
2. Construye DataFrame con resultados
3. Imprime tabla resumen formateada

**Resultado**: DataFrame con volatilidad media, std, riesgo específico, riesgo sistemático y reducción porcentual por cada N.

---

#### `detectar_frontera_optima(df_simulacion, umbral_reduccion=2.0)`
**Teoría**: Identifica número óptimo de activos donde reducción marginal de riesgo es menor al umbral.

**Proceso**:
1. Busca primer N donde `reduccion_pct < umbral_reduccion`
2. Si no se alcanza, retorna máximo N disponible
3. Retorna número óptimo detectado

**Resultado**: Entero con número óptimo de activos para diversificación.

---

#### `analizar_contribuciones(retornos, pesos=None)`
**Teoría**: Calcula contribución de cada activo al rendimiento y riesgo de la cartera.

**Fórmulas**:
- Contribución al Rendimiento: `wᵢ × E(Rᵢ)`
- Contribución al Riesgo: `wᵢ × Cov(Rᵢ, Rₚ)`

**Proceso**:
1. Si no hay pesos, usa equiponderada (1/N)
2. Calcula rendimientos esperados anualizados
3. Calcula contribuciones al rendimiento: `pesos * rendimientos_esperados`
4. Calcula covarianzas con cartera: `Σ @ pesos` (álgebra matricial)
5. Anualiza covarianzas
6. Calcula contribuciones al riesgo: `pesos * covarianzas_cartera`
7. Identifica activos diversificadores ideales: `E(Rᵢ) > 0` y `Cov(Rᵢ, Rₚ) < 0`
8. Ordena por contribución al riesgo descendente

**Resultado**: DataFrame con contribuciones y flag de diversificador ideal por activo.

---

#### `visualizar_frontera_diversificacion(df_simulacion, ruta_guardado=None)`
**Teoría**: Visualiza evolución del riesgo con diversificación y descomposición sistemático vs específico.

**Proceso**:
1. Subplot 1: Evolución riesgo total
   - Línea de volatilidad media vs N
   - Banda de confianza ±1 std
   - Línea horizontal de límite teórico (riesgo sistemático)
   - Marca punto de frontera práctica (reducción < 2%)
2. Subplot 2: Descomposición del riesgo
   - Área de riesgo específico (diversificable)
   - Línea de riesgo total: `√(σ²_esp + σ²_sis)`
   - Línea horizontal de límite sistemático
3. Guarda figura si se especifica ruta

**Resultado**: Figura con dos subplots mostrando frontera de diversificación.

---

## MÓDULO 3: OPTIMIZACIÓN DE MARKOWITZ (3markowitz.py)

### Funciones Principales

#### `_obtener_solver_disponible()`
**Proceso**:
1. Intenta ECOS (preferido)
2. Si no, intenta CLARABEL
3. Si no, intenta SCS
4. Si ninguno, retorna None (CVXPY elige por defecto)

**Resultado**: Solver disponible para optimización convexa.

---

#### `optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param)`
**Teoría**: Optimización de Markowitz con función objetivo `max w^T μ + w_rf * rf - λ * w^T Σ w`.

**Proceso**:
1. Define variables de decisión: `w` (N activos), `w_rf` (renta fija)
2. Define rentabilidad: `w @ mu + w_rf * rf`
3. Define riesgo: `cp.quad_form(w, Sigma)`
4. Define objetivo: `rentabilidad - lambda_param * riesgo`
5. Define restricciones:
   - `sum(w) + w_rf == 1` (inversión completa)
   - `w >= 0` (long-only)
   - `w_rf >= 0` y `w_rf <= 0.1` (RF máximo 10%)
6. Resuelve problema con solver disponible
7. Si status no es 'optimal', imprime advertencia y retorna None
8. Extrae pesos óptimos
9. Calcula métricas:
   - Rentabilidad: `w_opt @ mu + w_rf_opt * rf`
   - Volatilidad: `sqrt(w_opt @ Sigma @ w_opt)`
   - Sharpe: `(mu_p - rf) / sigma_p`
10. Retorna diccionario con pesos y métricas

**Resultado**: Cartera óptima con pesos, Sharpe, rentabilidad y volatilidad.

---

#### `optimizar_sharpe_maximo(mu, Sigma, rf)`
**Teoría**: Maximiza Sharpe Ratio reformulando como problema convexo. Sharpe = `(μp - rf) / σp`.

**Reformulación**: Minimiza `y^T Σ y` sujeto a `y^T μ + y_rf * rf == 1`, luego normaliza.

**Proceso**:
1. Define variables auxiliares: `y` (N activos), `y_rf` (renta fija)
2. Define objetivo: minimizar `cp.quad_form(y, Sigma)`
3. Define restricción de rentabilidad normalizada: `y @ mu + y_rf * rf == 1`
4. Restricciones: `y >= 0`, `y_rf >= 0`
5. Resuelve problema
6. Normaliza: `w = y / sum(y + y_rf)`, `w_rf = y_rf / sum(y + y_rf)`
7. Si `w_rf > 0.1`, ajusta al límite y renormaliza `w`
8. Calcula métricas finales
9. Retorna diccionario con resultados

**Resultado**: Cartera de máximo Sharpe Ratio con pesos optimizados.

---

#### `construir_frontera_eficiente(mu, Sigma, rf, n_puntos=50)`
**Teoría**: Frontera eficiente = conjunto de carteras con máxima rentabilidad para cada nivel de riesgo.

**Proceso**:
1. Define rango de rentabilidades objetivo: `[rf, mu.max() * 0.95]`
2. Genera `n_puntos` rentabilidades objetivo equiespaciadas
3. Para cada rentabilidad objetivo `mu_t`:
   - Define variables `w`, `w_rf`
   - Minimiza `w^T Σ w`
   - Restricciones:
     - `w @ mu + w_rf * rf == mu_t` (rentabilidad objetivo)
     - `sum(w) + w_rf == 1`
     - `w >= 0`, `w_rf >= 0`, `w_rf <= 0.1`
   - Resuelve problema
   - Si es óptimo, calcula volatilidad y Sharpe
   - Guarda punto en lista
4. Retorna DataFrame con puntos válidos

**Resultado**: DataFrame con rentabilidad, volatilidad y Sharpe de cada punto de la frontera.

---

#### `visualizar_frontera_eficiente(frontera_df, cartera_max_sharpe=None, ruta_guardado=None)`
**Proceso**:
1. Grafica volatilidad vs rentabilidad (ambas en porcentaje)
2. Si se pasa `cartera_max_sharpe`, marca punto con estrella roja
3. Configura etiquetas, título, leyenda y grid
4. Guarda figura si se especifica ruta

**Resultado**: Gráfico de frontera eficiente con cartera de máximo Sharpe destacada.

---

#### `analizar_sensibilidad_temporal(retornos, rf, ventanas=[252, 504, 756, None])`
**Teoría**: Evalúa robustez de estrategia usando diferentes ventanas temporales para estimar μ y Σ.

**Proceso**:
1. Para cada ventana:
   - Si `None`, usa todos los datos
   - Si es número, usa últimos N días
   - Calcula `mu` y `Sigma` anualizados con esa ventana
   - Optimiza con `optimizar_sharpe_maximo`
   - Calcula métricas adicionales:
     - Índice de Herfindahl: `sum(w²)` (concentración)
     - Número de activos con peso > 1%
   - Guarda resultados
2. Retorna DataFrame con resultados por ventana

**Resultado**: Tabla comparativa mostrando estabilidad de la estrategia ante cambios temporales.

---

## MÓDULO 4: SELECCIÓN DE ACTIVOS (4seleccion_activos.py)

### Funciones Principales

#### `detectar_n_optimo_activos(retornos, umbral_reduccion=2.0, n_simulaciones=100)`
**Proceso**:
1. Importa dinámicamente módulo 2 (`2equiponderada_diversificacion`)
2. Simula frontera de diversificación con `simular_frontera_diversificacion`
3. Detecta N óptimo con `detectar_frontera_optima`
4. Extrae métricas en N óptimo
5. Retorna diccionario con N óptimo y detalles

**Resultado**: Número óptimo de activos detectado automáticamente.

---

#### `calcular_metricas_seleccion(retornos, rf_anual=0.02)`
**Proceso**:
1. Calcula Sharpe Ratio anualizado por activo
2. Calcula rendimiento y volatilidad anualizados
3. Calcula matriz de correlación
4. Calcula correlación promedio de cada activo con el resto
5. Calcula puntuación de diversificación: `1 - correlacion_promedio`
6. Ordena por Sharpe descendente

**Resultado**: DataFrame con métricas de calidad por activo para selección.

---

#### `seleccionar_activos_por_sharpe_decorrelacion(retornos, n_activos, rf_anual=0.02, peso_sharpe=0.7, peso_decorrelacion=0.3)`
**Teoría**: Selecciona activos balanceando Sharpe Ratio alto (rentabilidad/riesgo) y baja correlación (diversificación).

**Proceso**:
1. Calcula métricas de selección para todos los activos
2. Normaliza Sharpe Ratio a escala [0, 1]
3. Normaliza puntuación de diversificación a escala [0, 1]
4. Calcula score combinado: `peso_sharpe * sharpe_norm + peso_decorrelacion * diversif_norm`
5. Ordena por score combinado descendente
6. Selecciona top N activos
7. Calcula correlación promedio entre seleccionados
8. Calcula Sharpe promedio de seleccionados
9. Si correlación promedio > 0.8, imprime advertencia
10. Retorna diccionario con activos seleccionados y métricas

**Resultado**: Lista de N activos óptimos con métricas de calidad.

---

#### `filtrar_retornos_activos_seleccionados(retornos, activos_seleccionados)`
**Proceso**:
1. Valida que todos los activos seleccionados existan
2. Filtra DataFrame preservando orden
3. Retorna DataFrame filtrado

**Resultado**: DataFrame con solo los N activos seleccionados.

---

#### `optimizar_cartera_con_seleccion(retornos, rf_anual=0.02, n_optimo=None, umbral_reduccion=2.0, metodo_optimizacion='max_sharpe', **kwargs_seleccion)`
**FUNCIÓN PRINCIPAL**: Ejecuta pipeline completo de selección + optimización.

**Proceso** (7 pasos):

**PASO 1: Detección de N óptimo** (si `n_optimo=None`):
- Llama `detectar_n_optimo_activos`
- Imprime N detectado

**PASO 2: Selección de activos**:
- Llama `seleccionar_activos_por_sharpe_decorrelacion` con N óptimo
- Imprime cantidad y Sharpe promedio de seleccionados

**PASO 3: Filtrado de retornos**:
- Llama `filtrar_retornos_activos_seleccionados`
- Obtiene DataFrame con solo N activos

**PASO 4: Preparación para optimización**:
- Usa `PreparadorDatos` del módulo 1
- Calcula `mu`, `Sigma`, `rf` anualizados sobre N activos

**PASO 5: Optimización con Markowitz**:
- Si `metodo_optimizacion='max_sharpe'`: llama `optimizar_sharpe_maximo`
- Si `metodo_optimizacion='min_variance'`: llama `optimizar_markowitz_lambda` con lambda alto
- Obtiene pesos optimizados sobre N activos

**PASO 6: Reconstrucción de vector de 50 posiciones**:
- Crea vector de ceros de 50 posiciones
- Mapea pesos optimizados a índices originales de activos seleccionados
- Verifica suma y renormaliza si es necesario

**PASO 7: Cálculo de métricas finales**:
- Calcula Sharpe, rentabilidad, volatilidad de cartera optimizada
- Calcula baseline: cartera equiponderada de 50 activos
- Calcula mejoras vs baseline
- Imprime resultados finales

**Resultado**: Diccionario con:
- `pesos_completos`: vector de 50 posiciones
- `activos_seleccionados`: lista de nombres
- `metricas_cartera`: Sharpe, rentabilidad, volatilidad
- `comparacion_baseline`: mejoras vs equiponderada
- `detalles_seleccion`: información del proceso

---

#### `visualizar_seleccion_activos(resultado_seleccion, retornos_completos, ruta_guardado=None)`
**Proceso**:
1. Subplot 1: Barras de pesos de 50 activos (azul seleccionados, gris resto)
2. Subplot 2: Scatter rendimiento vs volatilidad (tamaño = peso)
3. Subplot 3: Heatmap de correlaciones de activos seleccionados
4. Subplot 4: Comparación equiponderada vs optimizada (puntos con anotaciones)
5. Guarda figura si se especifica ruta

**Resultado**: Figura 2×2 con visualizaciones completas del proceso.

---

#### `comparar_estrategias(retornos, rf_anual=0.02)`
**Proceso**:
1. Estrategia 1: Equiponderada de 50 activos
2. Estrategia 2: Markowitz máximo Sharpe sobre 50 activos
3. Estrategia 3: Selección + Markowitz sobre N activos detectados
4. Calcula métricas para cada estrategia
5. Crea DataFrame comparativo
6. Genera gráficos de barras comparativos (Sharpe, rentabilidad, volatilidad)
7. Retorna DataFrame y figura

**Resultado**: Comparación cuantitativa y visual de las tres estrategias.

---

## MÓDULO 5: ANÁLISIS MULTIPUNTO (5analisis_multipunto.py)

### Funciones Principales

#### `detectar_puntos_interes_frontera(df_simulacion, criterios)`
**Teoría**: Detecta múltiples puntos relevantes en la frontera de diversificación, no solo el primero.

**Proceso**:
1. Detecta mínimos locales de volatilidad
2. Agrega puntos donde `reduccion_pct < umbral_reduccion`
3. Calcula cambios de pendiente y agrega puntos con cambio significativo
4. Asegura incluir punto detectado por `detectar_frontera_optima`
5. Retorna lista ordenada de valores N

**Resultado**: Lista de N valores considerados puntos de interés.

---

#### `optimizar_multiples_n(retornos, lista_n, rf_anual=0.02, peso_sharpe=0.7)`
**Proceso**:
1. Para cada N en `lista_n`:
   - Selecciona N activos con `seleccionar_activos_por_sharpe_decorrelacion`
   - Filtra retornos
   - Prepara datos con `PreparadorDatos`
   - Optimiza con `optimizar_sharpe_maximo`
   - Reconstruye vector de 50 posiciones
   - Calcula métricas y baseline
   - Guarda resultado en diccionario
2. Maneja errores por N y continúa
3. Retorna diccionario con resultados por N

**Resultado**: Diccionario `{N: resultado}` con formato del módulo 4.

---

#### `consolidar_resultados_multipunto(resultados_dict)`
**Proceso**:
1. Recorre resultados válidos
2. Extrae métricas clave: Sharpe, rentabilidad, volatilidad, peso_rf, correlación promedio, Sharpe promedio de selección
3. Construye DataFrame consolidado
4. Ordena por Sharpe descendente

**Resultado**: DataFrame con métricas estandarizadas de todas las carteras.

---

#### `visualizar_comparacion_multipunto(df_consolidado, resultados_dict, ruta_guardado=None)`
**Proceso**:
1. Subplot 1: Barras de Sharpe Ratio (mejor en color distinto)
2. Subplot 2: Scatter rentabilidad vs volatilidad con etiquetas N
3. Subplot 3: Barras dobles rentabilidad y volatilidad
4. Subplot 4: Línea peso_rf vs N
5. Guarda figura si se especifica ruta

**Resultado**: Figura 2×2 comparando todas las carteras optimizadas.

---

#### `generar_heatmap_pesos(resultados_dict, top_activos=15, ruta_guardado=None)`
**Proceso**:
1. Determina activos top por suma de pesos absolutos
2. Construye matriz: filas = carteras (N), columnas = activos top
3. Genera heatmap con seaborn
4. Guarda figura si se especifica ruta

**Resultado**: Heatmap mostrando distribución de pesos por cartera y activo.

---

## MÓDULO 6: VALIDACIÓN (validacion.py)

### Funciones Principales

#### `validar_cartera(w, w_rf, nombres_activos=None, tolerancia=1e-6)`
**Proceso**:
1. Valida long-only: `w >= 0`
2. Valida suma de pesos: `sum(w) + w_rf == 1`
3. Valida renta fija: `0 <= w_rf <= 0.1`
4. Valida número de activos: `len(w) == 50`
5. Advertencias para pesos muy altos (>50%)
6. Retorna diccionario con resultados de validación

**Resultado**: Diccionario indicando si la cartera cumple todas las restricciones.

---

#### `calcular_metricas_cartera(w, w_rf, mu, Sigma, rf)`
**Proceso**:
1. Calcula rentabilidad: `w @ mu + w_rf * rf`
2. Calcula volatilidad: `sqrt(w @ Sigma @ w)`
3. Calcula Sharpe: `(mu_p - rf) / sigma_p`
4. Calcula índice de Herfindahl: `sum(w²)` (concentración)
5. Cuenta activos con peso > 1%
6. Calcula peso máximo
7. Retorna diccionario con todas las métricas

**Resultado**: Métricas completas de rendimiento y estructura de la cartera.

---

#### `comparar_estrategias(estrategias_dict, nombres_activos=None)`
**Proceso**:
1. Para cada estrategia en diccionario:
   - Calcula métricas básicas (Herfindahl, n_activos, peso_maximo)
   - Extrae métricas de rendimiento si disponibles
   - Construye fila de resultados
2. Construye DataFrame comparativo
3. Ordena por Sharpe descendente

**Resultado**: Tabla comparativa de todas las estrategias.

---

#### `exportar_pesos(w, nombres_activos=None, ruta_archivo=None)`
**Proceso**:
1. Crea DataFrame con activos y pesos
2. Ordena por peso descendente
3. Guarda CSV si se especifica ruta
4. Retorna DataFrame

**Resultado**: CSV con pesos finales listo para entrega.

---

#### `seleccionar_mejor_estrategia(estrategias_dict, criterio='sharpe')`
**Proceso**:
1. Recorre todas las estrategias
2. Selecciona según criterio:
   - 'sharpe': máximo Sharpe
   - 'rentabilidad': máxima rentabilidad
   - 'volatilidad': mínima volatilidad
3. Retorna nombre y diccionario de mejor estrategia

**Resultado**: Mejor estrategia según criterio especificado.

---

## FLUJO DE TRABAJO COMPLETO DEL PROYECTO

### Pipeline Principal

1. **Carga de Datos** (`1datos.cargar_retornos`):
   - Lee CSV: 1760 días × 50 activos
   - Valida y limpia datos

2. **Exploración Inicial** (`1datos`):
   - Calcula estadísticas básicas por activo
   - Analiza correlaciones
   - Analiza comportamiento temporal
   - Prepara μ y Σ anualizados

3. **Análisis de Diversificación** (`2equiponderada_diversificacion`):
   - Simula frontera de diversificación
   - Detecta número óptimo de activos (N)
   - Analiza contribuciones de activos

4. **Selección de Activos** (`4seleccion_activos`):
   - Detecta N óptimo (si no se especifica)
   - Selecciona N activos por Sharpe + baja correlación
   - Filtra retornos a activos seleccionados

5. **Optimización** (`3markowitz` o `4seleccion_activos`):
   - Prepara μ y Σ sobre N activos seleccionados
   - Optimiza para máximo Sharpe Ratio
   - Reconstruye vector de 50 posiciones

6. **Análisis Comparativo** (`5analisis_multipunto`, opcional):
   - Detecta múltiples puntos de interés
   - Optimiza para cada N
   - Compara resultados

7. **Validación Final** (`validacion`):
   - Valida restricciones
   - Calcula métricas finales
   - Exporta pesos

---

## RESULTADOS Y OUTPUTS

### Datos Intermedios
- Estadísticas por activo (Sharpe, rentabilidad, volatilidad)
- Matriz de correlación
- Frontera de diversificación (volatilidad vs N activos)
- Frontera eficiente (volatilidad vs rentabilidad)

### Resultados Finales
- **Vector de pesos**: 50 posiciones (una por activo) + peso en renta fija
- **Métricas de cartera**:
  - Sharpe Ratio anualizado
  - Rentabilidad esperada anualizada
  - Volatilidad anualizada
  - Índice de Herfindahl (concentración)
  - Número de activos con peso significativo
- **Comparación con baseline**: Mejoras vs cartera equiponderada

### Visualizaciones
- Heatmap de correlaciones
- Frontera de diversificación
- Frontera eficiente
- Distribución de pesos
- Comparaciones multipanel

### Archivos Exportados
- CSV con pesos finales ordenados
- PNG con visualizaciones

---

## TEORÍA MATEMÁTICA APLICADA

### Fundamentos
1. **Rentabilidad de Cartera**: `E(Rp) = w^T μ + w_rf * rf`
2. **Riesgo de Cartera**: `σ²p = w^T Σ w`
3. **Sharpe Ratio**: `(μp - rf) / σp`
4. **Diversificación**: `σ²p = (1/n)V̄ + (1-1/n)σ̄ᵢⱼ` (equiponderada)

### Optimización
1. **Markowitz con λ**: `max w^T μ - λ * w^T Σ w`
2. **Máximo Sharpe**: Reformulación convexa minimizando varianza sujeto a rentabilidad normalizada
3. **Frontera Eficiente**: Mínima varianza para cada rentabilidad objetivo

### Restricciones
- Long-only: `w >= 0`
- Inversión completa: `sum(w) + w_rf == 1`
- Renta fija limitada: `0 <= w_rf <= 0.1`
- 50 activos: `len(w) == 50`

---

## DEPENDENCIAS Y TECNOLOGÍAS

### Librerías Python
- `numpy`: Cálculos numéricos y álgebra matricial
- `pandas`: Manipulación de datos
- `matplotlib` / `seaborn`: Visualizaciones
- `cvxpy`: Optimización convexa
- `scipy`: Funciones científicas adicionales

### Solvers de Optimización
- ECOS (preferido)
- CLARABEL (alternativa moderna)
- SCS (fallback)
- Solver por defecto de CVXPY

---

## CONCLUSIÓN

Este proyecto implementa un sistema completo de optimización de carteras que:

1. **Carga y prepara datos** históricos de 50 activos
2. **Analiza diversificación** para identificar número óptimo de activos
3. **Selecciona activos** balanceando Sharpe Ratio y baja correlación
4. **Optimiza carteras** usando teoría de Markowitz para maximizar Sharpe Ratio
5. **Compara estrategias** en múltiples puntos de la frontera
6. **Valida y exporta** resultados finales

El sistema produce carteras optimizadas que cumplen todas las restricciones (long-only, suma=1, RF≤10%, 50 activos) y maximizan el Sharpe Ratio anualizado, proporcionando una solución completa para gestión profesional de carteras.
