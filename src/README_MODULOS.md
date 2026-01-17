# MÓDULOS DE OPTIMIZACIÓN DE CARTERAS

Este proyecto contiene 5 módulos Python para la optimización de carteras y una carpeta con notebooks de demostración.

## ESTRUCTURA DEL PROYECTO

```
.
├── src/                           # Módulos de código
│   ├── 1datos.py                 # Exploración y Preparación de Datos
│   ├── 2markowitz.py             # Optimización Clásica de Markowitz
│   ├── 3factores.py              # Construcción de Factores y Señales
│   ├── 4multifactorial.py        # Optimización Multifactorial Avanzada
│   ├── 5validacion.py            # Validación y Selección Final
│   ├── importar_modulos.py       # Script auxiliar para importar módulos
│   └── README_MODULOS.md         # Documentación completa
├── data/                         # Carpeta con datos
│   └── prod_long_sharpe_u50_20260116_v5_train_dataset.csv
├── notebooks_demostracion/       # Notebooks de demostración
│   ├── Modulo1_Exploracion_Datos.ipynb
│   ├── Modulo2_Markowitz.ipynb
│   ├── Modulo3_Factores.ipynb
│   ├── Modulo4_Multifactorial.ipynb
│   └── Modulo5_Validacion.ipynb
└── requirements.txt              # Dependencias del proyecto
```

## 1DATOS: EXPLORACIÓN Y PREPARACIÓN DE DATOS

**Archivo**: `1datos.py`

**Funcionalidades**:
- Carga y validación de datos de retornos diarios
- Cálculo de estadísticas básicas por activo (media, volatilidad, Sharpe histórico)
- Análisis de correlaciones entre activos
- Análisis temporal (retornos acumulados, volatilidad rolling)
- Preparación de vectores μ (rentabilidad esperada) y matriz Σ (covarianza) anualizados

**Clases y Funciones Principales**:
- `cargar_retornos(ruta_csv)`: Carga datos desde CSV
- `calcular_estadisticas_basicas(retornos)`: Calcula estadísticas por activo
- `analizar_correlaciones(retornos)`: Analiza matriz de correlación
- `analizar_temporal(retornos)`: Análisis temporal de retornos
- `PreparadorDatos`: Clase para preparar datos para optimización

**Cómo funciona**:
1. Lee el CSV con retornos diarios (1761 días × 50 activos)
2. Valida que no haya valores faltantes o infinitos
3. Calcula estadísticas descriptivas para cada activo
4. Analiza la estructura de correlaciones entre activos
5. Prepara los datos para optimización (anualiza μ y Σ)

## 2MARKOWITZ: OPTIMIZACIÓN CLÁSICA DE MARKOWITZ

**Archivo**: `2markowitz.py`

**Funcionalidades**:
- Optimización de Markowitz con parámetro de aversión al riesgo (λ)
- Optimización directa del Sharpe Ratio máximo
- Construcción de la frontera eficiente
- Análisis de sensibilidad temporal

**Funciones Principales**:
- `optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param)`: Optimiza con función objetivo de Markowitz
- `optimizar_sharpe_maximo(mu, Sigma, rf)`: Optimiza para máximo Sharpe Ratio
- `construir_frontera_eficiente(mu, Sigma, rf, n_puntos)`: Construye frontera eficiente
- `analizar_sensibilidad_temporal(retornos, rf, ventanas)`: Analiza sensibilidad a ventanas temporales

**Cómo funciona**:
1. Markowitz con λ: Maximiza E(Rp) - λ * Var(Rp) sujeto a restricciones
2. Máximo Sharpe: Minimiza varianza sujeto a rentabilidad objetivo = 1
3. Frontera eficiente: Encuentra carteras de mínima varianza para cada rentabilidad objetivo
4. Análisis de sensibilidad: Evalúa cómo cambian los resultados con diferentes ventanas temporales

## 3FACTORES: CONSTRUCCIÓN DE FACTORES Y SEÑALES

**Archivo**: `3factores.py`

**Funcionalidades**:
- Cálculo de momentum 12-2 (retornos acumulados de 12 meses excluyendo el último mes)
- Cálculo de volatilidad rolling en múltiples ventanas
- Cálculo de betas vs mercado (índice equiponderado)
- Normalización de señales mediante z-scores
- Construcción de matriz de características X (activos × factores)
- Ranking multifactorial combinando señales

**Funciones Principales**:
- `calcular_momentum_12_2(retornos)`: Calcula momentum 12-2
- `calcular_volatilidad_rolling(retornos, ventanas)`: Calcula volatilidad rolling
- `calcular_betas(retornos, ventana)`: Calcula betas vs mercado
- `normalizar_senales(senales_dict)`: Normaliza señales mediante z-scores
- `construir_matriz_caracteristicas(senales_norm)`: Construye matriz X
- `crear_ranking_multifactorial(senales_norm, pesos_factores)`: Crea ranking combinado

**Cómo funciona**:
1. Momentum 12-2: Acumula retornos de t-252 a t-21 (evita reversión a corto plazo)
2. Volatilidad rolling: Calcula desviación estándar móvil anualizada
3. Beta: Covarianza con mercado / Varianza del mercado
4. Normalización: z = (señal - μ) / σ (cross-sectional)
5. Matriz X: Cada fila es un activo, cada columna es un factor normalizado
6. Ranking: Combina señales con pesos para crear score único

## 4MULTIFACTORIAL: OPTIMIZACIÓN MULTIFACTORIAL AVANZADA

**Archivo**: `4multifactorial.py`

**Funcionalidades**:
- Optimización Top-Down con tracking de exposiciones
- Control de exposiciones objetivo a factores (momentum, volatilidad, beta, etc.)
- Penalización por riesgo y rotación
- Estrategias alternativas (High Momentum + Low Vol, Quality, Min Variance)

**Funciones Principales**:
- `calcular_pesos_exposicion(X, metodo)`: Calcula pesos W_k para factores
- `optimizar_topdown(mu, Sigma, rf, X, b_star, W_k, ...)`: Optimización Top-Down
- `crear_estrategia_momentum_lowvol(nombres_factores)`: Estrategia Momentum+LowVol
- `crear_estrategia_quality(nombres_factores)`: Estrategia Quality
- `crear_estrategia_min_variance(nombres_factores)`: Estrategia Min Variance

**Cómo funciona**:
1. Define exposiciones objetivo b* a cada factor
2. Calcula pesos W_k para cada factor (inverso de varianza)
3. Optimiza: min ||X^T w - b*||²_W + λ w^T Σ w + τ ||w - w_prev||²
4. Sujeto a restricciones de cartera (long-only, suma=1, RF≤10%)

## 5VALIDACION: VALIDACIÓN Y SELECCIÓN FINAL

**Archivo**: `5validacion.py`

**Funcionalidades**:
- Validación de restricciones (long-only, suma=1, RF≤10%)
- Cálculo de métricas de cartera (Sharpe, concentración, diversificación)
- Comparación de estrategias
- Exportación de pesos finales

**Funciones Principales**:
- `validar_cartera(w, w_rf, nombres_activos)`: Valida restricciones
- `calcular_metricas_cartera(w, w_rf, mu, Sigma, rf)`: Calcula métricas
- `comparar_estrategias(estrategias_dict, nombres_activos)`: Compara estrategias
- `exportar_pesos(w, nombres_activos, ruta_archivo)`: Exporta pesos
- `seleccionar_mejor_estrategia(estrategias_dict, criterio)`: Selecciona mejor

**Cómo funciona**:
1. Valida que la cartera cumpla todas las restricciones
2. Calcula métricas de rendimiento (Sharpe, rentabilidad, volatilidad)
3. Calcula métricas de estructura (concentración, número de activos)
4. Compara múltiples estrategias y selecciona la mejor
5. Exporta los pesos finales en formato requerido

## NOTEBOOKS DE DEMOSTRACIÓN

Cada notebook en `notebooks_demostracion/` demuestra el funcionamiento de su módulo correspondiente:

1. **Modulo1_Exploracion_Datos.ipynb**: Muestra carga de datos, estadísticas, correlaciones y preparación
2. **Modulo2_Markowitz.ipynb**: Demuestra optimización Markowitz, máximo Sharpe y frontera eficiente
3. **Modulo3_Factores.ipynb**: Muestra cálculo de momentum, volatilidad, betas y construcción de señales
4. **Modulo4_Multifactorial.ipynb**: Demuestra optimización Top-Down y comparación de estrategias
5. **Modulo5_Validacion.ipynb**: Muestra validación, comparación y selección final

## USO

### Ejecutar un módulo individualmente:

```python
import importlib
import sys
sys.path.append('src')  # O '../src' desde notebooks_demostracion

# Importar módulos (los nombres que empiezan con números requieren importlib)
datos = importlib.import_module('1datos')

retornos = datos.cargar_retornos('data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv')
preparador = datos.PreparadorDatos(retornos, rf_anual=0.02)
preparador.calcular_estadisticas()
mu, Sigma, rf = preparador.obtener_estadisticas()
```

**Nota**: Los módulos con nombres que empiezan con números requieren usar `importlib.import_module()` en lugar de `import` directo. Los notebooks de demostración ya incluyen esta solución y apuntan a `../src`.

### Ejecutar notebooks de demostración:

1. Abrir Jupyter Notebook o JupyterLab
2. Navegar a la carpeta `notebooks_demostracion/`
3. Ejecutar las celdas de cada notebook en orden

## DEPENDENCIAS

- numpy
- pandas
- matplotlib
- seaborn
- cvxpy

## NOTAS

- Todos los módulos incluyen documentación detallada en docstrings
- Cada función explica qué hace y cómo funciona
- Los notebooks incluyen visualizaciones paso a paso
- Las carteras optimizadas cumplen todas las restricciones de la competencia
