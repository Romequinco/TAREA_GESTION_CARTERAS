# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MÓDULO 2EQUIPONDERADA_DIVERSIFICACION

## INTRODUCCIÓN

El módulo `2equiponderada_diversificacion.py` se encarga del análisis de carteras equiponderadas y el efecto de la diversificación. Su función principal es descomponer el riesgo de carteras equiponderadas en componentes sistemáticos y específicos, simular el efecto de diversificación al variar el número de activos, y analizar las contribuciones individuales de activos al rendimiento y riesgo de la cartera.

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1. FUNCIÓN: `analizar_cartera_equiponderada(retornos)`

#### Propósito
Descompone el riesgo de una cartera equiponderada usando la fórmula teórica de diversificación para separar el riesgo específico (diversificable) del riesgo sistemático (no diversificable).

#### Proceso Paso a Paso:

**Paso 1.1: Validación de entrada**
- Verifica que el DataFrame de retornos no esté vacío
- Si está vacío, lanza error: "El DataFrame de retornos está vacío"
- Obtiene número de activos: `n = retornos.shape[1]`

**Paso 1.2: Cálculo de matriz de covarianza**
- Calcula: `retornos.cov().values` para obtener matriz de covarianzas diarias
- Resultado: Matriz simétrica N×N donde cada elemento σ_ij es la covarianza entre activos i y j

**Paso 1.3: Cálculo de varianza media individual**
- Extrae diagonal de la matriz: `np.diag(cov_matrix)` (varianzas individuales)
- Calcula promedio: `np.mean(diagonal)`
- **Interpretación**: Varianza promedio de activos individuales (V̄) en unidades diarias
- Almacena como `varianza_media_diaria`

**Paso 1.4: Cálculo de covarianza media entre pares**
- Crea máscara: `np.triu(..., k=1)` para excluir diagonal y duplicados
- Extrae triángulo superior: `cov_matrix[mask]`
- Calcula promedio: `np.mean(triangulo_superior)`
- **Interpretación**: Covarianza promedio entre todos los pares de activos (σ̄ᵢⱼ) en unidades diarias
- Almacena como `covarianza_media_diaria`

**Paso 1.5: Anualización de varianzas y covarianzas**
- Fórmula varianza anual: `varianza_media = varianza_media_diaria * 252`
- Fórmula covarianza anual: `covarianza_media = covarianza_media_diaria * 252`
- **Razón**: Convertir estadísticas diarias a anuales para comparación estándar
- **Nota**: Varianzas y covarianzas escalan linealmente con el tiempo (no como volatilidades)

**Paso 1.6: Descomposición del riesgo de cartera**
- Fórmula teórica: `σ²ₚ = (1/n)V̄ + σ̄ᵢⱼ`
- Riesgo específico: `riesgo_especifico = (1/n) * varianza_media` → Disminuye con n
  - **Interpretación**: Componente diversificable del riesgo
  - Cuando n→∞, este término tiende a cero
- Riesgo sistemático: `riesgo_sistematico = covarianza_media` → Permanece constante
  - **Interpretación**: Componente no diversificable del riesgo
  - No se puede eliminar con diversificación
- Varianza total: `varianza_cartera = riesgo_especifico + riesgo_sistematico`

**Paso 1.7: Cálculo de volatilidad**
- Fórmula: `volatilidad_cartera = sqrt(varianza_cartera)`
- **Interpretación**: Volatilidad anualizada de la cartera equiponderada
- **Unidad**: Decimal (0.05 = 5% anual)

**Paso 1.8: Verificación de fórmula teórica**
- Calcula varianza real: `pesos_eq @ cov_diaria @ pesos_eq * 252`
  - Donde `pesos_eq = np.ones(n) / n` (pesos equiponderados)
- Compara con fórmula teórica: `abs(varianza_teorica - varianza_real)`
- Si diferencia > 1e-6: Imprime advertencia
- **Razón**: Validar que la descomposición teórica sea correcta numéricamente

#### Resultado
- Diccionario con:
  - `varianza_media`: Varianza promedio individual (V̄) anualizada
  - `covarianza_media`: Covarianza promedio entre pares (σ̄ᵢⱼ) anualizada
  - `riesgo_especifico`: Componente diversificable (1/n)V̄ anualizada
  - `riesgo_sistematico`: Componente no diversificable σ̄ᵢⱼ anualizada
  - `varianza_cartera`: Varianza total anualizada
  - `volatilidad_cartera`: Volatilidad anualizada (en decimal)

---

### 2. FUNCIÓN: `simular_frontera_diversificacion(retornos, n_valores=None, n_simulaciones=100)`

#### Propósito
Simula el efecto de la diversificación al variar el número de activos mediante múltiples simulaciones aleatorias de carteras equiponderadas para identificar cuántos activos se necesitan para alcanzar el límite práctico de diversificación.

#### Proceso Paso a Paso:

**Paso 2.1: Configuración inicial**
- Obtiene número total de activos: `retornos.shape[1]`
- Si `n_valores=None`: Usa valores por defecto `[2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]`
- Filtra valores que exceden el número de activos disponibles
- Establece semilla aleatoria: `np.random.seed(42)` para reproducibilidad
- **Razón**: Asegurar resultados reproducibles en múltiples ejecuciones

**Paso 2.2: Bucle principal para cada N**
- Para cada valor de N en `n_valores`:

**Paso 2.3: Simulaciones aleatorias**
- Realiza `n_simulaciones` iteraciones (default: 100):
  - Selecciona N activos aleatorios: `np.random.choice(columnas, size=N, replace=False)`
  - Extrae subconjunto de retornos: `retornos[activos_seleccionados]`
  - Calcula matriz de covarianza del subconjunto
  - Calcula varianza media y covarianza media (como en `analizar_cartera_equiponderada`)
  - Calcula componentes de riesgo: 
    - `riesgo_especifico = (1/N) * varianza_media`
    - `riesgo_sistematico = covarianza_media`
  - Calcula volatilidad: `sqrt(riesgo_especifico + riesgo_sistematico)`
  - Almacena resultados en listas (`volatilidades`, `riesgos_especificos`, `riesgos_sistematicos`)

**Paso 2.4: Promedio de resultados**
- Promedia todas las simulaciones:
  - `volatilidad_media = np.mean(volatilidades)`
  - `volatilidad_std = np.std(volatilidades)` (desviación estándar entre simulaciones)
  - `riesgo_especifico_medio = np.mean(riesgos_especificos)`
  - `riesgo_sistematico_medio = np.mean(riesgos_sistematicos)`

**Paso 2.5: Cálculo de reducción porcentual**
- Compara con N-1: `reduccion_pct = ((vol_anterior - vol_actual) / vol_anterior) * 100`
- Para N=2: `reduccion_pct = NaN` (no hay punto de referencia anterior)
- **Interpretación**: Mide el beneficio marginal de añadir un activo más

**Paso 2.6: Impresión de tabla resumen**
- Imprime tabla formateada con:
  - Número de activos (N)
  - Volatilidad media (%) convertida a porcentaje
  - Desviación estándar entre simulaciones (%)
  - Volatilidad de riesgo específico (%) = `sqrt(riesgo_especifico) * 100`
  - Volatilidad de riesgo sistemático (%) = `sqrt(riesgo_sistematico) * 100`
  - Reducción porcentual vs N-1

**Paso 2.7: Construcción de DataFrame**
- Crea DataFrame con todos los resultados
- Columnas: `n_activos`, `volatilidad_media`, `volatilidad_std`, `riesgo_especifico`, `riesgo_sistematico`, `reduccion_pct`

#### Resultado
- DataFrame con resultados para cada N
- Tabla impresa en consola con formato mejorado
- Permite identificar el N óptimo donde reducción < 2%

---

### 3. FUNCIÓN: `detectar_frontera_optima(df_simulacion, umbral_reduccion=2.0)`

#### Propósito
Detecta automáticamente el número óptimo de activos para diversificación usando el criterio de reducción porcentual de riesgo.

#### Proceso Paso a Paso:

**Paso 3.1: Validación de entrada**
- Verifica que `df_simulacion` no esté vacío
- Si está vacío, lanza error: "El DataFrame de simulación está vacío"

**Paso 3.2: Búsqueda de frontera**
- Busca primer N donde `reduccion_pct < umbral_reduccion` (default: 2.0%)
- Usa: `df_simulacion[df_simulacion['reduccion_pct'] < umbral].index[0]`
- **Interpretación**: Cuando la reducción marginal es menor al umbral, se ha alcanzado el límite práctico

**Paso 3.3: Manejo de casos**
- Si encuentra N: Retorna ese valor (convierte a int)
- Si no encuentra (reducción > umbral para todos): Retorna el máximo N disponible
- **Razón**: Asegurar que siempre retorne un valor válido

#### Resultado
- `int`: Número óptimo de activos
- Si no se alcanza umbral, retorna el máximo N disponible

---

### 4. FUNCIÓN: `analizar_contribuciones(retornos, pesos=None)`

#### Propósito
Calcula la contribución de cada activo al rendimiento y riesgo de la cartera, identificando activos diversificadores ideales.

#### Proceso Paso a Paso:

**Paso 4.1: Configuración de pesos**
- Si `pesos=None`: Crea cartera equiponderada: `np.ones(n_activos) / n_activos`
- Si se proporcionan pesos: Convierte a array numpy
- Valida que número de pesos coincida con número de activos
- Valida que los pesos sumen 1.0 (tolerancia 1e-6)

**Paso 4.2: Cálculo de retorno de cartera**
- Fórmula: `retorno_cartera_diario = (retornos * pesos).sum(axis=1)`
- **Interpretación**: Retorno diario de la cartera ponderada

**Paso 4.3: Cálculo de rendimientos esperados**
- Fórmula: `rendimientos_esperados = retornos.mean() * 252`
- **Interpretación**: Rentabilidad esperada anualizada de cada activo
- **Resultado**: Series de pandas con rendimientos anuales

**Paso 4.4: Contribución al rendimiento**
- Fórmula: `contribucion_rendimiento = pesos * rendimientos_esperados`
- **Propiedad**: Suma de contribuciones = rendimiento total de cartera
- **Interpretación**: Aporte de cada activo al rendimiento esperado de la cartera

**Paso 4.5: Cálculo de covarianzas con cartera**
- Para cada activo i:
  - Calcula covarianza: `np.cov(retornos[i], retorno_cartera_diario)[0,1]`
  - Anualiza: `cov_diaria * 252`
  - **Interpretación**: Mide cómo el activo i se mueve con respecto a la cartera
  - Covarianza positiva: activo se mueve en la misma dirección que la cartera
  - Covarianza negativa: activo se mueve en dirección opuesta (diversificador)

**Paso 4.6: Contribución al riesgo**
- Fórmula: `contribucion_riesgo = peso[i] * covarianza_cartera[i]`
- **Propiedad**: Suma de contribuciones = varianza total de cartera
- **Interpretación**: Aporte de cada activo al riesgo total de la cartera

**Paso 4.7: Identificación de diversificadores ideales**
- Criterio: `rendimiento_esperado > 0 AND covarianza_cartera < 0`
- **Interpretación**: Activos que aumentan rendimiento y reducen riesgo simultáneamente
- **Valor**: Estos activos son especialmente valiosos para diversificación

**Paso 4.8: Construcción de DataFrame**
- Crea DataFrame con:
  - `peso`: Peso del activo
  - `rendimiento_esperado`: E(Rᵢ) anualizado
  - `contribucion_rendimiento`: wᵢ × E(Rᵢ)
  - `covarianza_cartera`: Cov(Rᵢ, Rₚ) anualizada
  - `contribucion_riesgo`: wᵢ × Cov(Rᵢ, Rₚ)
  - `es_diversificador`: True si es activo ideal
- Ordena por `contribucion_riesgo` descendente
- **Razón**: Identificar activos que más aportan al riesgo primero

#### Resultado
- DataFrame con contribuciones de cada activo
- Ordenado por contribución al riesgo (mayores contribuyentes primero)
- Identifica activos diversificadores ideales (bandera `es_diversificador`)

---

### 5. FUNCIÓN: `visualizar_frontera_diversificacion(df_simulacion, ruta_guardado=None)`

#### Propósito
Crea visualización gráfica de la frontera eficiente de diversificación mostrando la evolución del riesgo total y la descomposición sistemático vs específico.

#### Proceso Paso a Paso:

**Paso 5.1: Configuración de figura**
- Crea figura con 2 subplots: `fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))`
- **Razón**: Dos visualizaciones complementarias en una sola figura

**Paso 5.2: Subplot 1 - Evolución del Riesgo Total**
- Extrae datos: `n_activos`, `volatilidad_media`, `volatilidad_std` (convierte a %)
- Dibuja línea principal: `ax1.plot(n_activos, vol_media)` - evolución de volatilidad
- Dibuja banda de confianza: `ax1.fill_between(n_activos, vol_media - vol_std, vol_media + vol_std)` - ±1 desviación estándar
- Dibuja línea horizontal: Límite teórico (último valor de `riesgo_sistematico` convertido a volatilidad)
- Marca punto de frontera práctica: `ax1.scatter([n_frontera], [vol_frontera])` si `reduccion_pct < 2%`
- Configura labels, título y leyenda

**Paso 5.3: Subplot 2 - Descomposición del Riesgo**
- **IMPORTANTE**: No suma volatilidades directamente
- Fórmula correcta: `σ_total = sqrt(σ_especifico² + σ_sistematico²)`
- Convierte varianzas a volatilidades: 
  - `riesgo_especifico_vol = np.sqrt(riesgo_especifico) * 100`
  - `riesgo_sistematico_vol = np.sqrt(riesgo_sistematico) * 100`
- Calcula riesgo total: `np.sqrt(riesgo_especifico + riesgo_sistematico) * 100`
- Dibuja área de riesgo específico: `ax2.fill_between(n_activos, 0, riesgo_especifico_vol)` - área naranja
- Dibuja línea de riesgo total: `ax2.plot(n_activos, riesgo_total_vol)` - línea azul
- Dibuja línea horizontal de límite sistemático: `ax2.axhline(y=riesgo_sistematico_vol[-1])` - línea verde punteada
- Configura labels, título y leyenda

**Paso 5.4: Guardado (opcional)**
- Si `ruta_guardado` está definida: `plt.savefig(ruta_guardado, dpi=300)`
- Resolución: 300 DPI para calidad de impresión

#### Resultado
- Figura matplotlib con 2 subplots
- Subplot 1: Evolución del riesgo total con bandas de confianza y frontera práctica marcada
- Subplot 2: Descomposición visual de riesgo sistemático vs específico
- Guardada en archivo si se especifica ruta

---

## FLUJO DE TRABAJO TÍPICO

1. **Análisis de cartera equiponderada completa**: 
   ```python
   resultado_eq = analizar_cartera_equiponderada(retornos)
   ```
   - Obtiene descomposición de riesgo para todos los activos

2. **Simulación de frontera de diversificación**: 
   ```python
   df_frontera = simular_frontera_diversificacion(retornos, n_valores=None, n_simulaciones=100)
   ```
   - Evalúa cuántos activos se necesitan para diversificar efectivamente

3. **Detección del número óptimo**: 
   ```python
   n_optimo = detectar_frontera_optima(df_frontera, umbral_reduccion=2.0)
   ```
   - Identifica automáticamente el punto óptimo

4. **Análisis de contribuciones**: 
   ```python
   df_contrib = analizar_contribuciones(retornos, pesos=None)
   ```
   - Evalúa qué aporta cada activo a la cartera

5. **Visualización**: 
   ```python
   visualizar_frontera_diversificacion(df_frontera, ruta_guardado='output.png')
   ```
   - Genera gráficos informativos de los resultados

---

## VALIDACIONES Y TRATAMIENTO DE ERRORES

- **DataFrame vacío**: Todas las funciones validan que el DataFrame no esté vacío antes de procesar
- **Pesos inválidos**: `analizar_contribuciones` valida que los pesos sumen 1.0 con tolerancia 1e-6
- **Valores de N inválidos**: `simular_frontera_diversificacion` filtra valores que exceden el número de activos disponibles
- **Verificación numérica**: `analizar_cartera_equiponderada` verifica que la fórmula teórica coincida con el cálculo directo

---

## NOTAS IMPORTANTES

1. **Fórmula teórica de descomposición**: σ²ₚ = (1/n)V̄ + σ̄ᵢⱼ para carteras equiponderadas
2. **Anualización**: Todos los cálculos finales están anualizados (252 días de trading)
3. **Riesgo específico vs sistemático**: El riesgo específico se puede diversificar, el sistemático no
4. **Límite de diversificación**: Cuando n→∞, solo queda el riesgo sistemático (σ̄ᵢⱼ)
5. **Reproducibilidad**: Se usa `np.random.seed(42)` para asegurar resultados reproducibles
6. **Covarianza con cartera**: La contribución al riesgo se calcula como peso × covarianza con la cartera, no con otros activos individuales
7. **Visualización correcta**: Las volatilidades NO se suman directamente; se suman varianzas y luego se toma la raíz cuadrada
