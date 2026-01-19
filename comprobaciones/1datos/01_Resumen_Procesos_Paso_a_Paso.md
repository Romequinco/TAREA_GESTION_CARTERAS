# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MODULO 1DATOS

## INTRODUCCION

El modulo `1datos.py` carga, valida, explora y prepara los retornos diarios para que los modulos posteriores puedan optimizar carteras con datos limpios y anualizados.

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1) FUNCION: `cargar_retornos(ruta_csv)`

**Proposito**  
Cargar el CSV de retornos diarios y validar valores faltantes o infinitos.

**Paso a paso**
1. Lee el archivo con `pd.read_csv(ruta_csv)` sin usar `index_col` para preservar todas las columnas (activos).
2. Revisa la primera columna:
   - Si es `"asset1"` o es un numero en texto, mantiene todas las columnas como activos y crea un indice numerico de dias.
   - Si no, deja el indice tal como viene.
3. Valida NaN:
   - Si hay NaN, imprime advertencia y reemplaza por 0 con `fillna(0)`.
4. Valida infinitos:
   - Si hay `inf` o `-inf`, imprime advertencia y reemplaza por 0.
5. Imprime resumen: `"Datos cargados: X dias, Y activos"`.
6. Retorna el DataFrame limpio.

**Salidas**
- DataFrame con filas = dias y columnas = activos.
- Mensajes de advertencia si hay NaN o infinitos.

---

### 2) FUNCION: `calcular_estadisticas_basicas(retornos, rf_anual=0.02)`

**Proposito**  
Calcular media, volatilidad y Sharpe historico para cada activo, y anualizar.

**Paso a paso**
1. Convierte la tasa libre de riesgo anual a diaria:
   - `rf_diario = (1 + rf_anual) ** (1/252) - 1`.
2. Calcula media diaria: `media_diaria = retornos.mean()`.
3. Calcula volatilidad diaria: `std_diaria = retornos.std()`.
4. Calcula Sharpe historico anualizado:
   - `(media_diaria - rf_diario) / std_diaria * sqrt(252)`.
5. Anualiza:
   - `media_anual = media_diaria * 252`.
   - `std_anual = std_diaria * sqrt(252)`.
6. Reemplaza Sharpe infinito por 0.
7. Ordena por `sharpe_historico` descendente y retorna el DataFrame.

**Salidas**
- DataFrame con columnas: `media_diaria`, `std_diaria`, `sharpe_historico`, `media_anual`, `std_anual`.

---

### 3) FUNCION: `analizar_correlaciones(retornos)`

**Proposito**  
Calcular la matriz de correlacion y estadisticas resumen.

**Paso a paso**
1. Calcula `corr_matrix = retornos.corr()` (Pearson).
2. Extrae el triangulo superior sin diagonal con `np.triu(..., k=1)`.
3. Calcula estadisticas sobre los pares unicos:
   - media, min, max y std.
4. Retorna un diccionario con la matriz completa y las estadisticas.

**Salidas**
- `{'matriz', 'media', 'min', 'max', 'std'}`.

---

### 4) FUNCION: `visualizar_correlaciones(corr_matrix, ruta_guardado=None)`

**Proposito**  
Generar un heatmap de la matriz de correlacion.

**Paso a paso**
1. Crea figura de 14x12.
2. Dibuja el heatmap con `sns.heatmap`:
   - `cmap='RdBu_r'`, `center=0`, `vmin=-1`, `vmax=1`, `square=True`.
3. Ajusta titulo y layout.
4. Si `ruta_guardado` existe, guarda PNG con 300 dpi.
5. Retorna la figura (`plt.gcf()`).

---

### 5) FUNCION: `analizar_temporal(retornos)`

**Proposito**  
Analizar el comportamiento temporal de los retornos.

**Paso a paso**
1. Retornos acumulados: `(1 + retornos).cumprod()` (indice de crecimiento, no resta 1).
2. Indice de mercado equiponderado: `retornos.mean(axis=1)`.
3. Volatilidad rolling: `retornos.rolling(63).std() * sqrt(252)`.
4. Retorna diccionario con las tres series.

**Salidas**
- `{'retornos_acumulados', 'indice_mercado', 'volatilidad_rolling'}`.

---

### 6) CLASE: `PreparadorDatos`

**Proposito**  
Preparar μ (rentabilidades esperadas) y Σ (covarianzas) anualizados.

#### 6.1) `__init__(retornos, rf_anual=0.02)`
1. Guarda `retornos` y `rf_anual`.
2. Calcula `rf_diario` y lo almacena.
3. Inicializa `mu_diario`, `cov_matriz`, `mu_anual`, `cov_anual` en `None`.

#### 6.2) `calcular_estadisticas(ventana=None)`
1. Selecciona datos:
   - Todos si `ventana=None`.
   - Ultimos `ventana` dias si se especifica.
2. Calcula μ diario: `datos.mean().values`.
3. Calcula Σ diaria: `datos.cov().values`.
4. Anualiza:
   - `mu_anual = mu_diario * 252`.
   - `cov_anual = cov_matriz * 252`.
5. Retorna `self` para encadenar.

#### 6.3) `obtener_estadisticas()`
1. Si `mu_anual` es `None`, lanza `ValueError`.
2. Retorna `(mu_anual, cov_anual, rf_anual)`.

---

## FLUJO DE TRABAJO TIPICO

1. `retornos = cargar_retornos('ruta.csv')`
2. `stats = calcular_estadisticas_basicas(retornos)`
3. `corr_stats = analizar_correlaciones(retornos)`
4. `visualizar_correlaciones(corr_stats['matriz'])`
5. `temporal = analizar_temporal(retornos)`
6. Preparar para optimizacion:
   ```python
   preparador = PreparadorDatos(retornos, rf_anual=0.02)
   preparador.calcular_estadisticas()
   mu, Sigma, rf = preparador.obtener_estadisticas()
   ```

---

## VALIDACIONES Y SALIDAS EN CONSOLA

- Imprime advertencias si hay NaN o infinitos en `cargar_retornos`.
- Imprime resumen de dimension del DataFrame cargado.
- Lanza error si se pide `obtener_estadisticas` sin calcular antes.

---

## NOTAS IMPORTANTES

- Todo se anualiza con 252 dias de trading.
- El Sharpe se ajusta por la tasa libre de riesgo diaria y se anualiza con `sqrt(252)`.
- Los retornos acumulados representan crecimiento del capital (no se resta 1).
