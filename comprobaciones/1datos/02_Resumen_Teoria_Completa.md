# RESUMEN TEÓRICO COMPLETO: FUNDAMENTOS DE DATOS Y ESTADÍSTICAS PARA CARTERAS

## INTRODUCCIÓN

Este documento presenta la teoría completa sobre el análisis de datos, estadísticas y preparación de información para la optimización de carteras, basado en los notebooks teóricos de `teoria`.

---

## 1. FUNDAMENTOS DE RENTABILIDAD Y RIESGO

### 1.1 Rentabilidad de un Activo

En un contexto de riesgo, la rentabilidad de un activo es una variable aleatoria $\tilde{R_i}$ que puede tomar diferentes valores $R_{ij}$ con probabilidades $P_j$.

**Fórmula de Rentabilidad Esperada:**
$$E(\tilde{R_i}) = \sum_{j=1}^{m} R_{ij} P_j$$

**Interpretación:**
- $E(\tilde{R_i})$ es el valor esperado (promedio ponderado por probabilidades)
- En la práctica, con datos históricos, se estima como la media muestral: $\bar{R_i} = \frac{1}{T}\sum_{t=1}^{T} R_{it}$
- Representa la rentabilidad promedio que se espera obtener del activo

### 1.2 Varianza y Volatilidad de un Activo

**Varianza:**
$$\sigma_i^2 = Var(\tilde{R_i}) = \sum_{j=1}^{m} (R_{ij} - E(\tilde{R_i}))^2 P_j$$

**Desviación Típica (Volatilidad):**
$$\sigma_i = \sqrt{\sigma_i^2} = \sqrt{\sum_{j=1}^{m} (R_{ij} - E(\tilde{R_i}))^2 P_j}$$

**Interpretación:**
- La varianza mide la dispersión de los retornos alrededor de la media
- La volatilidad (desviación estándar) es la medida más común de riesgo
- Mayor volatilidad = mayor incertidumbre sobre el resultado futuro
- Con datos históricos: $\sigma_i^2 = \frac{1}{T-1}\sum_{t=1}^{T} (R_{it} - \bar{R_i})^2$

### 1.3 Semivarianza (Medida de Riesgo a la Baja)

**Fórmula:**
$$SV_i = \sum_{j=1}^{m} (R_{ij}^* - E(\tilde{R_i}))^2 P_j$$

Donde $R_{ij}^*$ son solo los rendimientos por debajo de la media.

**Interpretación:**
- Mide únicamente el riesgo de pérdidas (downside risk)
- Útil para inversores que solo se preocupan por pérdidas, no por ganancias excesivas
- Alternativa a la varianza cuando la distribución no es simétrica

---

## 2. CARTERAS DE ACTIVOS

### 2.1 Rentabilidad de una Cartera

Para una cartera con $N$ activos y ponderaciones $w_i$ (donde $\sum_{i=1}^{N} w_i = 1$):

**Fórmula General:**
$$E(\tilde{R_p}) = \sum_{i=1}^{N} w_i E(\tilde{R_i})$$

**Propiedades Importantes:**
- La rentabilidad de la cartera es una **combinación lineal** de las rentabilidades individuales
- **NO depende de las relaciones entre activos** (correlaciones/covarianzas)
- Es simplemente el promedio ponderado de las rentabilidades esperadas

**Caso Especial - Dos Activos:**
$$E(\tilde{R_P}) = w_1 E(\tilde{R_1}) + w_2 E(\tilde{R_2})$$

Donde $w_2 = 1 - w_1$ (inversión completa).

### 2.2 Varianza de una Cartera

La varianza de una cartera es más compleja porque debe considerar las relaciones entre activos.

**Fórmula Expandida:**
$$\sigma_p^2 = \sum_{i=1}^{N} w_i^2 \sigma_i^2 + \sum_{i=1}^{N}\sum_{j=1}^{N} w_i w_j \sigma_{ij} \quad \forall i \neq j$$

**Descomposición:**
1. **Primer término**: $\sum_{i=1}^{N} w_i^2 \sigma_i^2$ - Contribución de las varianzas individuales
2. **Segundo término**: $\sum_{i=1}^{N}\sum_{j=1}^{N} w_i w_j \sigma_{ij}$ - Contribución de las covarianzas entre activos

**Forma Matricial (Más Compacta):**
$$\sigma_p^2 = \mathbf{w}^T \mathbf{C} \mathbf{w}$$

Donde:
- $\mathbf{w} = [w_1, w_2, ..., w_N]^T$ es el vector de ponderaciones
- $\mathbf{C}$ es la matriz de covarianzas (N×N) con elementos:
  - Diagonal: $\mathbf{C}_{ii} = \sigma_i^2$ (varianzas)
  - Fuera de diagonal: $\mathbf{C}_{ij} = \sigma_{ij}$ (covarianzas)

**Caso Especial - Dos Activos:**
$$\sigma_p^2 = w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2w_1 w_2 \rho_{12} \sigma_1 \sigma_2$$

Donde $\rho_{12}$ es el coeficiente de correlación entre los activos.

### 2.3 Covarianza y Correlación

**Covarianza entre dos activos:**
$$\sigma_{ij} = Cov(\tilde{R_i}, \tilde{R_j}) = E[(\tilde{R_i} - E(\tilde{R_i}))(\tilde{R_j} - E(\tilde{R_j}))]$$

**Coeficiente de Correlación:**
$$\rho_{ij} = \frac{\sigma_{ij}}{\sigma_i \sigma_j}$$

**Propiedades:**
- $\rho_{ij} \in [-1, 1]$ (normalizado)
- $\rho_{ij} = 1$: Correlación perfecta positiva
- $\rho_{ij} = -1$: Correlación perfecta negativa
- $\rho_{ij} = 0$: Sin correlación lineal
- $\rho_{ij} = \rho_{ji}$ (simetría)

**Interpretación de la Correlación:**
- **Correlación positiva alta ($\rho \approx 1$)**: Los activos tienden a moverse juntos
  - **Implicación**: Poca diversificación, el riesgo de la cartera es aproximadamente la suma ponderada de riesgos individuales
- **Correlación negativa ($\rho < 0$)**: Los activos tienden a moverse en direcciones opuestas
  - **Implicación**: Mayor diversificación, el riesgo de la cartera puede ser menor que el promedio de riesgos individuales
- **Correlación cercana a cero ($\rho \approx 0$)**: Los activos son independientes
  - **Implicación**: Diversificación moderada

---

## 3. EL EFECTO DE LA DIVERSIFICACIÓN

### 3.1 Cartera Equiponderada

Para una cartera donde cada activo tiene el mismo peso $w_i = \frac{1}{n}$:

**Varianza de la Cartera:**
$$\sigma_p^2 = \frac{1}{n^2}\sum_{i=1}^{n} \sigma_i^2 + \frac{1}{n^2}\sum_{i=1}^{n}\sum_{j=1}^{n}\sigma_{ij} \quad \forall i \neq j$$

**Reformulación usando promedios:**
Definiendo:
- Varianza media: $\bar{V} = \frac{1}{n}\sum_{i=1}^{n} \sigma_i^2$
- Covarianza media: $\bar{\sigma_{ij}} = \frac{1}{n(n-1)}\sum_{i=1}^{n}\sum_{j=1}^{n}\sigma_{ij}$

La varianza se puede expresar como:
$$\sigma_p^2 = \frac{1}{n}\bar{V} + \left(1 - \frac{1}{n}\right) \bar{\sigma_{ij}}$$

### 3.2 Límite de la Diversificación

**Cuando $n \to \infty$:**
$$\lim_{n \to \infty} \sigma_p^2 = \bar{\sigma_{ij}}$$

**Interpretación Fundamental:**
- El primer término $\frac{1}{n}\bar{V}$ tiende a cero cuando aumenta el número de activos
- El segundo término $\bar{\sigma_{ij}}$ permanece constante
- **Conclusión**: La diversificación puede eliminar el riesgo específico, pero NO el riesgo sistemático

### 3.3 Riesgo Sistemático vs. Riesgo Específico

**Riesgo Específico (Diversificable):**
- Representado por: $\frac{1}{n}\bar{V}$ (varianza promedio de activos individuales)
- **Características**:
  - Disminuye a medida que aumenta el número de activos
  - Puede eliminarse completamente con diversificación suficiente
  - Es único de cada activo (riesgo idiosincrático)
- **Ejemplos**: Problemas específicos de una empresa, eventos que afectan solo a un sector

**Riesgo Sistemático (No Diversificable):**
- Representado por: $\bar{\sigma_{ij}}$ (covarianza promedio entre activos)
- **Características**:
  - Permanece constante independientemente del número de activos
  - NO puede eliminarse mediante diversificación
  - Afecta a todos los activos del mercado
- **Ejemplos**: Recesiones económicas, cambios en tipos de interés, crisis financieras globales

**Implicación Teórica:**
Este resultado justifica por qué los inversores exigen un premio por asumir riesgo: el riesgo sistemático no puede evitarse, por lo que debe ser compensado con mayor rentabilidad esperada.

---

## 4. CONTRIBUCIÓN DE ACTIVOS A LA CARTERA

### 4.1 Contribución al Rendimiento

**Fórmula:**
$$Contribución_i^{Rendimiento} = w_i E(\tilde{R_i})$$

**Propiedades:**
- Depende **solo del peso** $w_i$ y la rentabilidad esperada del activo
- **NO depende de la composición de la cartera**
- Es aditiva: $E(\tilde{R_p}) = \sum_{i=1}^{N} w_i E(\tilde{R_i})$

### 4.2 Contribución al Riesgo

**Fórmula:**
$$Contribución_i^{Riesgo} = w_i^2 cov(\tilde{R_i}, \tilde{R_P}) = w_i^2 \sigma_{i,P}$$

Donde $\sigma_{i,P}$ es la covarianza del activo $i$ con la cartera $P$.

**Propiedades:**
- Depende **tanto del peso** $w_i$ **como de la composición de la cartera**
- Un mismo activo puede aportar diferente riesgo a diferentes carteras
- La contribución total al riesgo es: $\sigma_p^2 = \sum_{i=1}^{N} w_i^2 \sigma_{i,P}$

**Caso Especial - Activo Deseable:**
Si un activo tiene:
- Rentabilidad esperada positiva: $E(\tilde{R_i}) > 0$
- Covarianza negativa con la cartera: $cov(\tilde{R_i}, \tilde{R_P}) < 0$

Entonces:
- **Aumenta el rendimiento** de la cartera
- **Disminuye el riesgo** de la cartera

Este es el activo ideal para diversificación.

---

## 5. ANUALIZACIÓN DE ESTADÍSTICAS

### 5.1 Anualización de Rentabilidades

**Rentabilidad Diaria a Anual:**
$$\mu_{anual} = \mu_{diaria} \times 252$$

**Razón:**
- Asumiendo 252 días de trading por año
- La rentabilidad es aditiva en el tiempo (compuesta simple)
- Si un activo tiene rentabilidad diaria promedio de 0.1%, la anual es aproximadamente 25.2%

### 5.2 Anualización de Volatilidad

**Volatilidad Diaria a Anual:**
$$\sigma_{anual} = \sigma_{diaria} \times \sqrt{252}$$

**Razón:**
- La volatilidad escala con la raíz cuadrada del tiempo (propiedad de procesos estocásticos)
- Viene de la teoría de procesos de Wiener/Browniano
- Si un activo tiene volatilidad diaria de 1%, la anual es aproximadamente 15.87%

**Matemáticamente:**
Si los retornos son independientes e idénticamente distribuidos (i.i.d.):
$$Var(R_{anual}) = Var\left(\sum_{t=1}^{252} R_{diaria,t}\right) = 252 \times Var(R_{diaria})$$

Por lo tanto:
$$\sigma_{anual} = \sqrt{252 \times \sigma_{diaria}^2} = \sqrt{252} \times \sigma_{diaria}$$

### 5.3 Anualización de Covarianzas

**Covarianza Diaria a Anual:**
$$\sigma_{ij,anual} = \sigma_{ij,diaria} \times 252$$

**Razón:**
- La covarianza escala linealmente con el tiempo (similar a la varianza)
- Mantiene la estructura de correlaciones (el coeficiente de correlación no cambia)

---

## 6. RATIO DE SHARPE

### 6.1 Definición

**Fórmula:**
$$Sharpe = \frac{E(\tilde{R_p}) - r_f}{\sigma_p}$$

Donde:
- $E(\tilde{R_p})$ es la rentabilidad esperada de la cartera
- $r_f$ es la tasa libre de riesgo (2% anual por defecto)
- $\sigma_p$ es la volatilidad (riesgo) de la cartera

**Versión con Datos Históricos:**
$$Sharpe_{historico} = \frac{\bar{R} - r_{f,diario}}{\sigma_{diaria}} \times \sqrt{252}$$

Donde:
- $\bar{R}$ es la rentabilidad promedio diaria
- $r_{f,diario}$ es la tasa libre de riesgo diaria: $r_{f,diario} = (1 + r_{f,anual})^{1/252} - 1$
- $\sigma_{diaria}$ es la volatilidad diaria
- El factor $\sqrt{252}$ anualiza el ratio

**Conversión de Tasa Libre de Riesgo:**
Para convertir tasa anual a diaria: $r_{f,diario} = (1 + r_{f,anual})^{1/252} - 1$

Ejemplo: Si $r_{f,anual} = 0.02$ (2%), entonces $r_{f,diario} \approx 0.000079$

### 6.2 Interpretación

- **Sharpe alto**: Mayor rentabilidad por unidad de riesgo asumido
- **Sharpe bajo**: Menor rentabilidad ajustada por riesgo
- **Sharpe negativo**: La cartera tiene peor rendimiento que el activo libre de riesgo

**Benchmarks Típicos:**
- Sharpe < 0.5: Pobre
- Sharpe 0.5-1.0: Aceptable
- Sharpe 1.0-2.0: Bueno
- Sharpe > 2.0: Excelente

### 6.3 Uso en Selección de Activos

El Sharpe Ratio permite comparar activos con diferentes niveles de riesgo:
- Un activo con mayor Sharpe es preferible (mejor rendimiento/riesgo)
- Es la base para identificar "mejores activos" en el análisis exploratorio

---

## 7. ANÁLISIS TEMPORAL Y RETORNOS ACUMULADOS

### 7.1 Retornos Acumulados

**Fórmula:**
$$Valor_t = Valor_0 \times \prod_{s=1}^{t} (1 + R_s)$$

**Interpretación:**
- Representa el valor de una inversión unitaria (1€) a lo largo del tiempo
- Asume reinversión de todos los retornos (compuesto)
- Permite visualizar la evolución del valor de la inversión

**En términos logarítmicos:**
Si $R_t$ son retornos logarítmicos:
$$Valor_t = Valor_0 \times e^{\sum_{s=1}^{t} R_s}$$

### 7.2 Índice de Mercado

**Definición:**
Un índice de mercado es una cartera de referencia que representa el comportamiento promedio del mercado.

**Índice Equiponderado:**
$$R_{mercado,t} = \frac{1}{N}\sum_{i=1}^{N} R_{i,t}$$

**Uso:**
- Benchmark para comparar rendimiento de carteras individuales
- Representa el "mercado promedio"
- Útil para análisis de alpha (rendimiento excedente)

### 7.3 Volatilidad Rolling (Dinámica)

**Definición:**
La volatilidad rolling calcula la volatilidad en una ventana móvil de tiempo.

**Fórmula:**
$$\sigma_{rolling,t}(w) = \sqrt{\frac{1}{w-1}\sum_{s=t-w+1}^{t} (R_s - \bar{R}_w)^2} \times \sqrt{252}$$

Donde $w$ es el tamaño de la ventana (ej: 63 días).

**Interpretación:**
- Muestra cómo cambia el riesgo del activo con el tiempo
- Permite identificar períodos de alta/baja volatilidad
- Útil para estrategias de gestión de riesgo dinámico

---

## 8. MATRIZ DE COVARIANZAS: PROPIEDADES Y ESTRUCTURA

### 8.1 Estructura de la Matriz

Para $N$ activos, la matriz de covarianzas $\mathbf{C}$ es de tamaño $N \times N$:

$$\mathbf{C} = \begin{pmatrix}
\sigma_1^2 & \sigma_{12} & \cdots & \sigma_{1N} \\
\sigma_{21} & \sigma_2^2 & \cdots & \sigma_{2N} \\
\vdots & \vdots & \ddots & \vdots \\
\sigma_{N1} & \sigma_{N2} & \cdots & \sigma_N^2
\end{pmatrix}$$

**Propiedades:**
1. **Simétrica**: $\sigma_{ij} = \sigma_{ji}$ (solo $N(N+1)/2$ elementos únicos)
2. **Semidefinida positiva**: Todos los autovalores son no negativos
3. **Diagonal**: Contiene las varianzas individuales $\sigma_i^2$
4. **Fuera de diagonal**: Contiene las covarianzas entre pares de activos

### 8.2 Cálculo con Datos Históricos

**Estimador de Covarianza:**
$$\hat{\sigma}_{ij} = \frac{1}{T-1}\sum_{t=1}^{T} (R_{i,t} - \bar{R_i})(R_{j,t} - \bar{R_j})$$

**En forma matricial:**
Si $\mathbf{R}$ es la matriz de retornos (T×N), entonces:
$$\mathbf{C} = \frac{1}{T-1} (\mathbf{R} - \mathbf{1}\bar{\mathbf{R}}^T)^T (\mathbf{R} - \mathbf{1}\bar{\mathbf{R}}^T)$$

Donde $\bar{\mathbf{R}}$ es el vector de medias.

### 8.3 Problemas Numéricos

**Matriz Singular o Mal Condicionada:**
- Ocurre cuando hay activos perfectamente correlacionados o datos insuficientes
- Puede causar problemas en la optimización (inversión de matriz)
- **Soluciones**: Regularización, reducción de dimensionalidad, uso de estimadores robustos

---

## 9. CORRELACIÓN Y DIVERSIFICACIÓN

### 9.1 Efecto de la Correlación en el Riesgo de la Cartera

**Caso de Dos Activos:**
$$\sigma_p^2 = w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2w_1 w_2 \rho_{12} \sigma_1 \sigma_2$$

**Análisis de Casos Extremos:**

1. **$\rho_{12} = 1$ (Correlación Perfecta Positiva):**
   - $\sigma_p^2 = (w_1 \sigma_1 + w_2 \sigma_2)^2$
   - $\sigma_p = w_1 \sigma_1 + w_2 \sigma_2$ (combinación lineal)
   - **No hay diversificación**: El riesgo es simplemente la suma ponderada

2. **$\rho_{12} = -1$ (Correlación Perfecta Negativa):**
   - Es posible encontrar $w_1, w_2$ tal que $\sigma_p = 0$
   - **Máxima diversificación**: Puede eliminarse completamente el riesgo

3. **$-1 < \rho_{12} < 1$ (Correlación Intermedia):**
   - El riesgo está entre los dos extremos
   - **Diversificación parcial**: Reduce el riesgo pero no lo elimina

### 9.2 Correlación Promedio del Mercado

**Interpretación:**
- Correlación promedio alta ($\bar{\rho} > 0.5$): Mercado muy integrado, poca diversificación posible
- Correlación promedio baja ($\bar{\rho} < 0.3$): Mercado fragmentado, mayor potencial de diversificación
- Correlación promedio muy alta en crisis: "Correlación va a 1" - todos los activos caen juntos

---

## 10. PREPARACIÓN DE DATOS PARA OPTIMIZACIÓN

### 10.1 Requisitos de los Datos

Para la optimización de carteras (módulos posteriores) se necesitan:

1. **Vector de Rentabilidades Esperadas ($\mu$):**
   - Forma: (N,) - vector unidimensional
   - Contenido: Rentabilidades anualizadas de cada activo
   - Origen: Media muestral de retornos históricos anualizada

2. **Matriz de Covarianzas ($\Sigma$):**
   - Forma: (N×N) - matriz cuadrada
   - Contenido: Covarianzas anualizadas entre todos los pares de activos
   - Origen: Matriz de covarianza muestral anualizada

3. **Tasa Libre de Riesgo ($r_f$):**
   - Forma: Escalar (float)
   - Contenido: Tasa anual (ej: 0.02 = 2%)
   - Uso: Para cálculo de Sharpe Ratio y optimización con activo libre de riesgo

### 10.2 Proceso de Preparación

**Paso 1: Cálculo de Estadísticas Diarias**
- $\mu_{diaria} = \frac{1}{T}\sum_{t=1}^{T} R_t$ (vector de medias)
- $\Sigma_{diaria} = \frac{1}{T-1}\sum_{t=1}^{T} (R_t - \mu_{diaria})(R_t - \mu_{diaria})^T$ (matriz de covarianza)

**Paso 2: Anualización**
- $\mu_{anual} = \mu_{diaria} \times 252$
- $\Sigma_{anual} = \Sigma_{diaria} \times 252$

**Paso 3: Validación**
- Verificar que $\Sigma$ sea semidefinida positiva
- Verificar que no haya valores NaN o infinitos
- Verificar dimensiones correctas

---

## CONCLUSIONES TEÓRICAS

1. **La rentabilidad de la cartera** es una combinación lineal simple de rentabilidades individuales, independiente de correlaciones.

2. **El riesgo de la cartera** depende crucialmente de las correlaciones entre activos, lo que permite la diversificación.

3. **La diversificación** puede eliminar el riesgo específico pero nunca el riesgo sistemático.

4. **La correlación** es el factor clave que determina el beneficio de la diversificación.

5. **La anualización** es esencial para comparar activos y realizar optimizaciones con horizontes temporales consistentes.

6. **La preparación correcta de datos** (μ y Σ anualizados) es fundamental para que los algoritmos de optimización funcionen correctamente.
