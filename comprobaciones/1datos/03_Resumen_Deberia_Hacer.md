# RESUMEN: LO QUE EL MÓDULO 1DATOS DEBERÍA HACER

## INTRODUCCIÓN

Este documento analiza las funcionalidades actuales del módulo `1datos.py` y propone mejoras, extensiones y funcionalidades adicionales que debería implementar para ser más completo, robusto y útil en un contexto de optimización de carteras profesional.

---

## FUNCIONALIDADES ACTUALES (YA IMPLEMENTADAS)

### ✅ Implementado Correctamente

1. **Carga de datos con validación básica**
   - Lectura de CSV preservando todos los activos
   - Detección y tratamiento de NaN e infinitos
   - Validación de estructura de datos

2. **Cálculo de estadísticas básicas**
   - Media y volatilidad diarias y anualizadas
   - Sharpe Ratio histórico
   - Ordenamiento por Sharpe

3. **Análisis de correlaciones**
   - Matriz de correlaciones completa
   - Estadísticas resumen (media, min, max, std)
   - Visualización con heatmap

4. **Análisis temporal**
   - Retornos acumulados
   - Índice de mercado equiponderado
   - Volatilidad rolling

5. **Preparación para optimización**
   - Clase `PreparadorDatos` con anualización
   - Generación de μ y Σ en formato numpy
   - Soporte para ventanas temporales

---

## FUNCIONALIDADES QUE DEBERÍA AGREGAR

### 1. VALIDACIONES Y CALIDAD DE DATOS MEJORADAS

#### 1.1 Detección de Outliers
**Qué debería hacer:**
- Detectar retornos anómalos (outliers) usando métodos estadísticos:
  - Método de Z-score: identificar retornos con |z| > 3
  - Método de IQR (Interquartile Range): identificar valores fuera de Q1-1.5×IQR y Q3+1.5×IQR
  - Método de desviación estándar: identificar retornos fuera de μ ± 3σ

**Por qué es importante:**
- Los outliers pueden distorsionar significativamente las estimaciones de μ y Σ
- Pueden indicar errores de datos o eventos extremos que deben tratarse de forma especial
- Mejora la robustez de las estimaciones

**Implementación sugerida:**
```python
def detectar_outliers(retornos, metodo='zscore', umbral=3):
    """
    Detecta retornos anómalos usando diferentes métodos.
    Retorna máscara booleana y estadísticas de outliers.
    """
```

#### 1.2 Análisis de Estacionariedad
**Qué debería hacer:**
- Realizar tests de estacionariedad (ADF, KPSS) para verificar si las series de retornos son estacionarias
- Detectar cambios estructurales en las series (test de Chow, CUSUM)
- Identificar períodos con diferentes regímenes de volatilidad

**Por qué es importante:**
- La optimización asume que las estadísticas (μ, Σ) son estables en el tiempo
- Si hay cambios estructurales, las estimaciones históricas pueden no ser válidas para el futuro
- Permite identificar ventanas temporales más apropiadas para estimación

#### 1.3 Validación de Normalidad
**Qué debería hacer:**
- Tests de normalidad (Jarque-Bera, Shapiro-Wilk, Kolmogorov-Smirnov)
- Visualización de distribuciones (histogramas, Q-Q plots)
- Medidas de asimetría (skewness) y curtosis (kurtosis)

**Por qué es importante:**
- Muchos modelos asumen normalidad de retornos
- La no-normalidad afecta la validez del Sharpe Ratio y otras métricas
- Permite decidir si se necesitan modelos más robustos

#### 1.4 Detección de Autocorrelación
**Qué debería hacer:**
- Tests de autocorrelación (Ljung-Box, Durbin-Watson)
- Análisis de autocorrelación parcial (PACF)
- Detección de efectos ARCH/GARCH (heterocedasticidad)

**Por qué es importante:**
- Los retornos deberían ser independientes en el tiempo (hipótesis de mercado eficiente)
- La autocorrelación indica dependencia temporal que puede explotarse
- La heterocedasticidad requiere modelos más sofisticados (GARCH)

---

### 2. ESTIMADORES ROBUSTOS DE μ Y Σ

#### 2.1 Estimadores Robustos de Media
**Qué debería hacer:**
- Implementar estimadores robustos alternativos a la media muestral:
  - **Media recortada (trimmed mean)**: Elimina los X% de valores extremos
  - **Mediana**: Más robusta a outliers
  - **Media de Huber**: Combina media y mediana según distancia
  - **Media exponencialmente ponderada (EWMA)**: Da más peso a observaciones recientes

**Por qué es importante:**
- La media muestral es muy sensible a outliers
- Los estimadores robustos proporcionan estimaciones más estables
- EWMA captura cambios recientes en el mercado

**Implementación sugerida:**
```python
def estimar_mu_robusto(retornos, metodo='trimmed', alpha=0.1):
    """
    Estima rentabilidades esperadas usando métodos robustos.
    """
```

#### 2.2 Estimadores Robustos de Covarianza
**Qué debería hacer:**
- Implementar estimadores alternativos de matriz de covarianza:
  - **Covarianza muestral estándar**: Ya implementada
  - **Covarianza de Ledoit-Wolf**: Shrinkage hacia matriz objetivo
  - **Covarianza de OAS (Oracle Approximating Shrinkage)**: Mejora de Ledoit-Wolf
  - **Covarianza exponencialmente ponderada**: Da más peso a datos recientes
  - **Covarianza usando factor models**: Reduce dimensionalidad

**Por qué es importante:**
- La matriz de covarianza muestral es muy inestable con pocos datos
- Los estimadores de shrinkage mejoran la estabilidad numérica
- Los modelos factoriales reducen el ruido en estimaciones

**Implementación sugerida:**
```python
def estimar_sigma_robusto(retornos, metodo='ledoit_wolf'):
    """
    Estima matriz de covarianza usando métodos robustos.
    """
```

#### 2.3 Regularización de Matriz de Covarianza
**Qué debería hacer:**
- Detectar y corregir problemas numéricos:
  - Verificar si la matriz es semidefinida positiva
  - Aplicar regularización si hay autovalores negativos
  - Aplicar shrinkage si la matriz está mal condicionada
  - Usar factorización de Cholesky con corrección si es necesario

**Por qué es importante:**
- Matrices mal condicionadas causan errores en optimización
- La regularización mejora la estabilidad numérica
- Es esencial para problemas con muchos activos y pocos datos

---

### 3. ANÁLISIS DE RIESGO MEJORADO

#### 3.1 Medidas de Riesgo Alternativas
**Qué debería hacer:**
- Calcular medidas de riesgo más sofisticadas:
  - **Value at Risk (VaR)**: Pérdida máxima esperada con cierto nivel de confianza
  - **Conditional VaR (CVaR)**: Pérdida esperada dado que se excede el VaR
  - **Maximum Drawdown**: Mayor caída desde un máximo histórico
  - **Semivarianza**: Varianza solo de retornos negativos
  - **Riesgo a la baja (Downside Risk)**: Medidas que solo penalizan pérdidas

**Por qué es importante:**
- La volatilidad (varianza) trata igual ganancias y pérdidas
- Los inversores suelen ser más aversos a pérdidas que amantes de ganancias
- Estas medidas capturan mejor la percepción de riesgo

**Implementación sugerida:**
```python
def calcular_medidas_riesgo(retornos, confianza=0.05):
    """
    Calcula VaR, CVaR, Maximum Drawdown, etc.
    """
```

#### 3.2 Análisis de Stress Testing
**Qué debería hacer:**
- Simular escenarios extremos:
  - Escenarios históricos: aplicar correlaciones de crisis pasadas
  - Escenarios hipotéticos: shocks a factores específicos
  - Monte Carlo: simular miles de escenarios posibles
  - Análisis de sensibilidad: cómo cambia la cartera ante cambios en μ o Σ

**Por qué es importante:**
- Evalúa la robustez de las carteras en condiciones extremas
- Identifica vulnerabilidades antes de que ocurran
- Cumple con requisitos regulatorios (stress testing)

#### 3.3 Análisis de Dependencias No Lineales
**Qué debería hacer:**
- Ir más allá de la correlación lineal:
  - **Correlación de rangos (Spearman)**: Captura dependencias no lineales
  - **Correlación de colas**: Dependencia en eventos extremos
  - **Cópulas**: Modelar dependencias complejas entre activos
  - **Análisis de dependencia condicional**: Cómo cambian las relaciones en diferentes regímenes

**Por qué es importante:**
- La correlación de Pearson solo captura relaciones lineales
- En crisis, las dependencias pueden cambiar drásticamente
- Permite mejor modelado de riesgo de cola (tail risk)

---

### 4. ANÁLISIS TEMPORAL AVANZADO

#### 4.1 Análisis de Regímenes
**Qué debería hacer:**
- Identificar diferentes regímenes de mercado:
  - **Alta volatilidad vs. baja volatilidad**: Usar modelos de cambio de régimen (Markov Switching)
  - **Mercado alcista vs. bajista**: Identificar tendencias
  - **Períodos de crisis vs. normalidad**: Detectar cambios estructurales

**Por qué es importante:**
- Las estadísticas (μ, Σ) pueden variar significativamente entre regímenes
- Permite usar estimaciones específicas por régimen
- Mejora la precisión de las predicciones

#### 4.2 Análisis de Estacionalidad
**Qué debería hacer:**
- Detectar patrones estacionales:
  - **Efecto día de la semana**: ¿Hay días con mejor/peor rendimiento?
  - **Efecto mes**: ¿Hay meses con patrones consistentes?
  - **Efecto año**: ¿Hay ciclos anuales?

**Por qué es importante:**
- Puede explotarse para timing de inversión
- Ajusta las estimaciones si hay estacionalidad significativa
- Útil para estrategias de trading de corto plazo

#### 4.3 Análisis de Persistencia y Reversión a la Media
**Qué debería hacer:**
- Analizar si los retornos muestran:
  - **Momentum**: Los retornos pasados predicen retornos futuros (positivos)
  - **Reversión a la media**: Los retornos extremos tienden a revertirse
  - **Tests de rachas (runs test)**: Verificar aleatoriedad

**Por qué es importante:**
- Informa sobre la eficiencia del mercado
- Puede usarse para construir señales de trading
- Afecta la validez de modelos que asumen independencia

---

### 5. ANÁLISIS DE FACTORES Y CARACTERÍSTICAS

#### 5.1 Análisis de Exposición a Factores
**Qué debería hacer:**
- Calcular exposiciones a factores comunes:
  - **Beta vs. mercado**: Sensibilidad a movimientos del mercado
  - **Exposición a sectores**: Análisis de concentración sectorial
  - **Exposición a factores de estilo**: Value, Growth, Size, Momentum
  - **Análisis de componentes principales (PCA)**: Identificar factores latentes

**Por qué es importante:**
- Los módulos posteriores (3factores, 4multifactorial) necesitan estas exposiciones
- Permite entender las fuentes de riesgo y rendimiento
- Facilita la construcción de carteras con exposiciones objetivo

#### 5.2 Análisis de Características Fundamentales
**Qué debería hacer:**
- Si hay datos disponibles, calcular características:
  - **Ratios financieros**: P/E, P/B, ROE, etc.
  - **Métricas de calidad**: Deuda, liquidez, rentabilidad
  - **Métricas de momentum**: Retornos pasados a diferentes horizontes
  - **Métricas de volatilidad**: Volatilidad histórica, volatilidad implícita

**Por qué es importante:**
- Estas características son la base para modelos multifactoriales
- Permiten construir señales de inversión
- Son necesarias para el módulo 3factores

---

### 6. VISUALIZACIONES ADICIONALES

#### 6.1 Visualizaciones de Distribución
**Qué debería hacer:**
- Crear visualizaciones más informativas:
  - **Histogramas con curvas normales**: Comparar con normalidad
  - **Q-Q plots**: Verificar normalidad cuantil por cuantil
  - **Box plots**: Visualizar outliers y distribuciones
  - **Violin plots**: Mostrar forma completa de distribuciones

#### 6.2 Visualizaciones de Dependencias
**Qué debería hacer:**
- Mejorar visualización de correlaciones:
  - **Network graphs**: Mostrar activos como nodos, correlaciones como aristas
  - **Clustering de correlaciones**: Agrupar activos similares
  - **Heatmaps interactivos**: Permitir zoom y filtrado
  - **Gráficos de dispersión de pares**: Mostrar relaciones bivariadas

#### 6.3 Visualizaciones Temporales Avanzadas
**Qué debería hacer:**
- Visualizaciones temporales más ricas:
  - **Gráficos de retornos acumulados con bandas de confianza**
  - **Heatmaps temporales de correlaciones**: Ver cómo cambian las correlaciones en el tiempo
  - **Gráficos de volatilidad rolling con percentiles**
  - **Análisis de drawdowns visual**: Mostrar períodos de pérdidas

---

### 7. EXPORTACIÓN Y REPORTING

#### 7.1 Generación de Reportes
**Qué debería hacer:**
- Crear reportes automáticos:
  - **Reporte PDF/HTML**: Resumen ejecutivo de análisis
  - **Tablas formateadas**: Estadísticas en formato profesional
  - **Dashboards interactivos**: Usando Plotly o similar
  - **Exportación a Excel**: Múltiples hojas con diferentes análisis

**Por qué es importante:**
- Facilita la comunicación de resultados
- Permite documentación automática
- Útil para presentaciones y auditorías

#### 7.2 Exportación de Datos Procesados
**Qué debería hacer:**
- Exportar datos en múltiples formatos:
  - **CSV**: Para análisis externos
  - **Parquet**: Formato eficiente para grandes volúmenes
  - **HDF5**: Para datos numéricos complejos
  - **JSON**: Para integración con APIs

---

### 8. OPTIMIZACIÓN Y EFICIENCIA

#### 8.1 Caching de Resultados
**Qué debería hacer:**
- Implementar caché para cálculos costosos:
  - Guardar resultados de cálculos de μ y Σ
  - Invalidar caché cuando cambian los datos
  - Usar decoradores de memoización

**Por qué es importante:**
- Acelera iteraciones durante desarrollo
- Reduce tiempo de ejecución en análisis repetitivos

#### 8.2 Procesamiento Paralelo
**Qué debería hacer:**
- Paralelizar cálculos cuando sea posible:
  - Cálculo de correlaciones por bloques
  - Procesamiento de múltiples ventanas temporales en paralelo
  - Uso de multiprocessing o joblib

**Por qué es importante:**
- Con 50 activos y 1760 días, algunos cálculos pueden ser lentos
- La paralelización acelera significativamente el procesamiento

---

### 9. VALIDACIÓN Y TESTING

#### 9.1 Tests Unitarios
**Qué debería hacer:**
- Crear suite de tests:
  - Tests de funciones individuales
  - Tests de casos extremos (datos vacíos, un solo activo, etc.)
  - Tests de propiedades matemáticas (simetría de matrices, etc.)
  - Tests de regresión (verificar que cambios no rompan funcionalidad)

#### 9.2 Validación Cruzada Temporal
**Qué debería hacer:**
- Implementar validación temporal:
  - Dividir datos en train/validation/test
  - Evaluar estabilidad de estimaciones en diferentes períodos
  - Detectar overfitting temporal

---

### 10. DOCUMENTACIÓN Y USABILIDAD

#### 10.1 Documentación Mejorada
**Qué debería hacer:**
- Mejorar documentación:
  - Ejemplos de uso para cada función
  - Guías de mejores prácticas
  - Troubleshooting común
  - Referencias a papers y teoría relevante

#### 10.2 Manejo de Errores Mejorado
**Qué debería hacer:**
- Mensajes de error más informativos:
  - Explicar qué salió mal y por qué
  - Sugerir soluciones
  - Validar inputs antes de procesar
  - Logging detallado para debugging

---

## PRIORIZACIÓN DE MEJORAS

### Alta Prioridad (Implementar Primero)
1. **Estimadores robustos de Σ** (Ledoit-Wolf, OAS) - Crítico para estabilidad
2. **Validación de matriz de covarianza** - Evita errores en optimización
3. **Detección de outliers** - Mejora calidad de estimaciones
4. **Medidas de riesgo alternativas** (VaR, CVaR) - Más relevantes que solo volatilidad

### Media Prioridad
5. **Análisis de estacionariedad y cambios estructurales**
6. **Análisis de regímenes de mercado**
7. **Visualizaciones mejoradas**
8. **Tests de normalidad y autocorrelación**

### Baja Prioridad (Nice to Have)
9. **Análisis de estacionalidad**
10. **Caching y optimización**
11. **Reportes automáticos**
12. **Procesamiento paralelo**

---

## CONCLUSIÓN

El módulo `1datos.py` actual es una base sólida, pero puede mejorarse significativamente agregando:

1. **Robustez**: Estimadores más estables y validaciones más completas
2. **Profundidad**: Análisis más sofisticados de riesgo y dependencias
3. **Usabilidad**: Mejor documentación, visualizaciones y manejo de errores
4. **Eficiencia**: Caching, paralelización y optimización

Estas mejoras harían el módulo más profesional, robusto y útil en un contexto de gestión de carteras real.
