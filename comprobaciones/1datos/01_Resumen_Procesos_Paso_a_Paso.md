# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MÓDULO 1DATOS

## INTRODUCCIÓN

El módulo `1datos.py` es el primer paso en el proceso de optimización de carteras. Su función principal es cargar, validar, explorar y preparar los datos de retornos diarios para que puedan ser utilizados por los módulos posteriores de optimización.

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1. FUNCIÓN: `cargar_retornos(ruta_csv)`

#### Propósito
Cargar los datos históricos de retornos diarios desde un archivo CSV y realizar validaciones básicas de calidad de datos.

#### Proceso Paso a Paso:

**Paso 1.1: Lectura del archivo CSV**
- Utiliza `pd.read_csv(ruta_csv)` para leer el archivo
- **IMPORTANTE**: No usa `index_col=0` para preservar todos los activos (asset1 a asset50)
- El DataFrame resultante tiene estructura: filas = días, columnas = activos

**Paso 1.2: Verificación de estructura**
- Comprueba si la primera columna es 'asset1' o un número
- Si es así, crea un índice numérico para los días (0, 1, 2, ..., 1759)
- Esto asegura que todos los 50 activos se preserven como columnas

**Paso 1.3: Validación de valores faltantes (NaN)**
- Verifica si hay valores NaN en cualquier celda: `retornos.isnull().any().any()`
- Si encuentra NaN:
  - Imprime advertencia: "ADVERTENCIA: Se encontraron valores NaN"
  - Reemplaza todos los NaN con 0 usando `fillna(0)`
  - **Razón**: Los NaN pueden causar errores en cálculos posteriores

**Paso 1.4: Validación de valores infinitos**
- Verifica si hay valores infinitos: `np.isinf(retornos.values).any()`
- Si encuentra infinitos:
  - Imprime advertencia: "ADVERTENCIA: Se encontraron valores infinitos"
  - Reemplaza infinitos positivos y negativos con 0 usando `replace([np.inf, -np.inf], 0)`
  - **Razón**: Los infinitos rompen los cálculos matemáticos

**Paso 1.5: Confirmación de carga**
- Imprime resumen: "Datos cargados: X días, Y activos"
- Retorna el DataFrame limpio y validado

#### Resultado
- DataFrame con 1760 filas (días) × 50 columnas (activos)
- Sin valores NaN ni infinitos
- Índice numérico para días
- Columnas nombradas: asset1, asset2, ..., asset50

---

### 2. FUNCIÓN: `calcular_estadisticas_basicas(retornos, rf_anual=0.02)`

#### Propósito
Calcular estadísticas descriptivas fundamentales para cada activo que permiten evaluar su rendimiento histórico y riesgo, incluyendo el Sharpe Ratio ajustado por la tasa libre de riesgo.

#### Proceso Paso a Paso:

**Paso 2.1: Conversión de tasa libre de riesgo**
- Fórmula: `rf_diario = (1 + rf_anual)^(1/252) - 1`
- **Explicación**: Convierte tasa anual compuesta (2% por defecto) a tasa diaria equivalente
- **Ejemplo**: Si rf_anual = 0.02 (2%), entonces rf_diario ≈ 0.000079

**Paso 2.2: Cálculo de media diaria**
- Para cada activo, calcula: `retornos.mean()`
- Resultado: promedio de todos los retornos diarios del activo
- **Interpretación**: Rentabilidad promedio diaria del activo

**Paso 2.3: Cálculo de desviación estándar diaria**
- Para cada activo, calcula: `retornos.std()`
- Resultado: volatilidad diaria (dispersión de retornos)
- **Interpretación**: Medida del riesgo diario del activo

**Paso 2.4: Cálculo de Sharpe Ratio histórico**
- Fórmula: `(media_diaria - rf_diario) / std_diaria * sqrt(252)`
- **Explicación detallada**:
  - `media_diaria - rf_diario`: Exceso de rentabilidad diaria sobre tasa libre de riesgo
  - `(media_diaria - rf_diario) / std_diaria`: Sharpe diario (exceso de rentabilidad por unidad de riesgo)
  - `sqrt(252)`: Factor de anualización (252 días de trading por año)
- **Interpretación**: Mide el rendimiento ajustado por riesgo anualizado
- **Fórmula teórica**: Sharpe = (E(Rp) - rf) / σp
- Sharpe alto = mejor rendimiento excedente por unidad de riesgo

**Paso 2.5: Anualización de media**
- Fórmula: `media_anual = media_diaria * 252`
- **Razón**: Convierte rentabilidad diaria a anual para comparación estándar
- **Interpretación**: Rentabilidad esperada anual si el activo mantiene su promedio diario

**Paso 2.6: Anualización de volatilidad**
- Fórmula: `std_anual = std_diaria * sqrt(252)`
- **Razón**: La volatilidad escala con la raíz cuadrada del tiempo (propiedad de procesos estocásticos)
- **Interpretación**: Volatilidad anualizada del activo

**Paso 2.7: Manejo de infinitos en Sharpe**
- Reemplaza valores infinitos en Sharpe con 0
- **Razón**: Ocurre cuando std_diaria = 0 (activo sin variabilidad)
- **Razón**: También puede ocurrir si media_diaria = rf_diario y std_diaria = 0

**Paso 2.8: Ordenamiento**
- Ordena el DataFrame por Sharpe histórico descendente
- **Razón**: Identificar los mejores activos (mayor Sharpe = mejor rendimiento/riesgo ajustado)

#### Resultado
- DataFrame con 5 columnas por activo:
  - `media_diaria`: Rentabilidad promedio diaria
  - `std_diaria`: Volatilidad diaria
  - `sharpe_historico`: Sharpe Ratio anualizado (ajustado por rf)
  - `media_anual`: Rentabilidad anualizada
  - `std_anual`: Volatilidad anualizada
- Ordenado por Sharpe descendente

---

### 3. FUNCIÓN: `analizar_correlaciones(retornos)`

#### Propósito
Analizar la estructura de correlaciones entre todos los pares de activos para entender las relaciones de dependencia.

#### Proceso Paso a Paso:

**Paso 3.1: Cálculo de matriz de correlación**
- Calcula: `retornos.corr()`
- **Método**: Correlación de Pearson (coeficiente lineal)
- Resultado: Matriz simétrica N×N donde cada elemento ρ_ij ∈ [-1, 1]
- **Interpretación**:
  - ρ = 1: Correlación perfecta positiva (mueven juntos)
  - ρ = -1: Correlación perfecta negativa (mueven opuestos)
  - ρ = 0: Sin correlación lineal

**Paso 3.2: Extracción de triángulo superior**
- Crea máscara: `np.triu(..., k=1)` para excluir diagonal y duplicados
- Extrae solo pares únicos: `corr_matrix.where(mask).stack()`
- **Razón**: La matriz es simétrica (ρ_ij = ρ_ji), solo necesitamos pares únicos

**Paso 3.3: Cálculo de estadísticas de correlación**
- **Media**: Promedio de todas las correlaciones
  - **Interpretación**: Correlación promedio del mercado
  - Valor típico: 0.3-0.6 (activos financieros suelen estar correlacionados)
- **Mínimo**: Correlación más negativa
  - **Interpretación**: Par de activos más diversificante
- **Máximo**: Correlación más positiva
  - **Interpretación**: Par de activos más similares
- **Desviación estándar**: Dispersión de correlaciones
  - **Interpretación**: Heterogeneidad en relaciones entre activos

#### Resultado
- Diccionario con:
  - `matriz`: DataFrame completo de correlaciones (N×N)
  - `media`: Correlación promedio
  - `min`: Correlación mínima
  - `max`: Correlación máxima
  - `std`: Desviación estándar de correlaciones

---

### 4. FUNCIÓN: `visualizar_correlaciones(corr_matrix, ruta_guardado)`

#### Propósito
Crear una visualización gráfica (heatmap) de la matriz de correlaciones para análisis visual.

#### Proceso Paso a Paso:

**Paso 4.1: Configuración de figura**
- Crea figura de tamaño 14×12 pulgadas
- **Razón**: Matriz grande (50×50) necesita espacio

**Paso 4.2: Generación de heatmap**
- Usa `sns.heatmap()` con:
  - `cmap='RdBu_r'`: Colormap rojo-azul invertido
  - `center=0`: Centro en correlación cero
  - `vmin=-1, vmax=1`: Rango completo de correlaciones
  - `square=True`: Celdas cuadradas
  - `linewidths=0.5`: Separación entre celdas
- **Interpretación visual**:
  - Rojo intenso: Correlación positiva fuerte
  - Azul intenso: Correlación negativa fuerte
  - Blanco: Correlación cercana a cero

**Paso 4.3: Guardado (opcional)**
- Si se proporciona `ruta_guardado`, guarda la figura en PNG
- Resolución: 300 DPI para calidad de impresión

#### Resultado
- Figura matplotlib con heatmap de correlaciones
- Guardada en archivo si se especifica ruta

---

### 5. FUNCIÓN: `analizar_temporal(retornos)`

#### Propósito
Realizar análisis temporal de los retornos para entender la evolución histórica y el riesgo dinámico.

#### Proceso Paso a Paso:

**Paso 5.1: Cálculo de retornos acumulados**
- Fórmula: `(1 + retornos).cumprod()`
- **Explicación matemática**:
  - Para cada activo: Valor_t = Valor_0 × (1+r_1) × (1+r_2) × ... × (1+r_t)
  - Representa el valor de una inversión unitaria (1€) a lo largo del tiempo
- **Interpretación**: Evolución del valor de inversión si se reinvierten los retornos

**Paso 5.2: Cálculo de índice de mercado**
- Fórmula: `retornos.mean(axis=1)`
- **Explicación**: Promedio simple de todos los activos en cada día
- **Interpretación**: Índice equiponderado del mercado (benchmark simple)
- **Uso**: Comparar rendimiento de carteras individuales vs. mercado

**Paso 5.3: Cálculo de volatilidad rolling**
- Fórmula: `retornos.rolling(63).std() * sqrt(252)`
- **Explicación**:
  - `rolling(63)`: Ventana móvil de 63 días (≈ 3 meses)
  - `.std()`: Desviación estándar en cada ventana
  - `* sqrt(252)`: Anualización
- **Interpretación**: Volatilidad dinámica del activo (cambia con el tiempo)
- **Uso**: Identificar períodos de alta/baja volatilidad

#### Resultado
- Diccionario con:
  - `retornos_acumulados`: DataFrame con evolución de valor (días × activos)
  - `indice_mercado`: Series con retorno promedio diario del mercado
  - `volatilidad_rolling`: DataFrame con volatilidad móvil anualizada (días × activos)

---

### 6. CLASE: `PreparadorDatos`

#### Propósito
Encapsular la lógica de preparación de datos necesarios para optimización: vectores μ (rentabilidades esperadas) y matrices Σ (covarianzas), ambos anualizados.

#### Proceso Paso a Paso:

**6.1. INICIALIZACIÓN (`__init__`)**

**Paso 6.1.1: Almacenamiento de datos**
- Guarda `retornos` (DataFrame) y `rf_anual` (tasa libre de riesgo, default: 0.02)
- **Razón**: Necesarios para todos los cálculos posteriores

**Paso 6.1.2: Conversión de tasa libre de riesgo**
- Fórmula: `rf_diario = (1 + rf_anual)^(1/252) - 1`
- **Explicación**: Convierte tasa anual compuesta a tasa diaria equivalente
- **Ejemplo**: Si rf_anual = 0.02 (2%), entonces rf_diario ≈ 0.000079
- **Razón**: Necesaria para cálculos diarios (aunque no se usa directamente en la preparación final)

**Paso 6.1.3: Inicialización de atributos**
- Inicializa `mu_diario`, `cov_matriz`, `mu_anual`, `cov_anual` como None
- **Razón**: Se calcularán cuando se llame a `calcular_estadisticas()`

---

**6.2. MÉTODO: `calcular_estadisticas(ventana=None)`**

**Paso 6.2.1: Selección de datos**
- Si `ventana=None`: Usa todos los datos históricos
- Si `ventana` es un número: Usa solo los últimos N días (`iloc[-ventana:]`)
- **Razón**: Permite análisis de sensibilidad temporal

**Paso 6.2.2: Cálculo de μ diario (vector de medias)**
- Fórmula: `datos.mean().values`
- Resultado: Vector numpy de forma (N,) donde N = número de activos
- **Contenido**: Rentabilidad esperada diaria de cada activo
- **Ejemplo**: μ_diario = [0.0005, 0.0007, ..., 0.0003] para 50 activos

**Paso 6.2.3: Cálculo de Σ diario (matriz de covarianza)**
- Fórmula: `datos.cov().values`
- Resultado: Matriz numpy de forma (N×N)
- **Contenido**: Covarianzas entre todos los pares de activos
- **Propiedades**:
  - Simétrica: Σ_ij = Σ_ji
  - Diagonal: Σ_ii = varianza del activo i
  - Fuera de diagonal: Σ_ij = covarianza entre activos i y j

**Paso 6.2.4: Anualización de μ**
- Fórmula: `mu_anual = mu_diario * 252`
- **Razón**: Multiplicación simple porque la media es aditiva en el tiempo
- **Resultado**: Rentabilidades esperadas anuales

**Paso 6.2.5: Anualización de Σ**
- Fórmula: `cov_anual = cov_matriz * 252`
- **Razón**: La covarianza escala linealmente con el tiempo
- **Resultado**: Matriz de covarianza anualizada
- **Nota**: La varianza anual = varianza diaria × 252, pero la volatilidad anual = volatilidad diaria × √252

**Paso 6.2.6: Retorno de self**
- Retorna `self` para permitir encadenamiento: `preparador.calcular_estadisticas().obtener_estadisticas()`

---

**6.3. MÉTODO: `obtener_estadisticas()`**

**Paso 6.3.1: Validación**
- Verifica que `mu_anual` no sea None
- Si es None, lanza error: "Debe llamar a calcular_estadisticas() primero"

**Paso 6.3.2: Retorno de estadísticas**
- Retorna tupla: `(mu_anual, cov_anual, rf_anual)`
- **Formato**:
  - `mu_anual`: numpy array shape (50,) - vector de rentabilidades esperadas anualizadas
  - `cov_anual`: numpy array shape (50, 50) - matriz de covarianza anualizada
  - `rf_anual`: float - tasa libre de riesgo anual (default: 0.02)

---

## FLUJO DE TRABAJO TÍPICO

1. **Cargar datos**: `retornos = cargar_retornos('ruta.csv')`
2. **Explorar estadísticas**: `stats = calcular_estadisticas_basicas(retornos)`
3. **Analizar correlaciones**: `corr_stats = analizar_correlaciones(retornos)`
4. **Visualizar correlaciones**: `visualizar_correlaciones(corr_stats['matriz'])`
5. **Análisis temporal**: `temporal = analizar_temporal(retornos)`
6. **Preparar para optimización**:
   ```python
   preparador = PreparadorDatos(retornos, rf_anual=0.02)
   preparador.calcular_estadisticas()
   mu, Sigma, rf = preparador.obtener_estadisticas()
   ```

---

## VALIDACIONES Y TRATAMIENTO DE ERRORES

- **NaN**: Reemplazados por 0 (asumiendo que son errores de datos)
- **Infinitos**: Reemplazados por 0 (evitan errores matemáticos)
- **Sharpe infinito**: Reemplazado por 0 (ocurre cuando volatilidad = 0)
- **Validación de llamadas**: `obtener_estadisticas()` verifica que se hayan calculado las estadísticas
- **Validación de estructura**: Verifica que la primera columna sea 'asset1' para preservar todos los activos

---

## NOTAS IMPORTANTES

1. **Tasa libre de riesgo**: Se usa `rf_anual=0.02` (2% anual) por defecto en todos los cálculos
2. **Anualización**: Todos los cálculos finales están anualizados (252 días de trading)
3. **Preservación de activos**: El código asegura que se carguen los 50 activos completos
4. **Eficiencia**: Los cálculos usan operaciones vectorizadas de NumPy/Pandas
5. **Compatibilidad**: Los outputs están en formato numpy para compatibilidad con módulos de optimización
6. **Sharpe Ratio**: Se calcula restando la tasa libre de riesgo (ajuste por riesgo) y se anualiza multiplicando por √252
