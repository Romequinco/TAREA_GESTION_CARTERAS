# MÓDULOS DE OPTIMIZACIÓN DE CARTERAS

Este proyecto contiene 5 módulos Python para la optimización de carteras y una carpeta con notebooks de demostración.

## ESTRUCTURA DEL PROYECTO

```
.
├── src/                           # Módulos de código
│   ├── 1datos.py                 # Exploración y Preparación de Datos
│   ├── 2equiponderada_diversificacion.py  # Análisis de Carteras Equiponderadas y Diversificación
│   ├── 3markowitz.py             # Optimización Clásica de Markowitz
│   ├── validacion.py             # Validación y Selección Final (en desarrollo)
│   ├── 5analisis_multipunto.py   # Análisis multipunto de diversificación
│   ├── importar_modulos.py       # Script auxiliar para importar módulos
│   └── README_MODULOS.md         # Documentación completa
├── data/                         # Carpeta con datos
│   └── prod_long_sharpe_u50_20260116_v5_train_dataset.csv
├── notebooks_demostracion/       # Notebooks de demostración
│   ├── Modulo1_Exploracion_Datos.ipynb
│   ├── Modulo2_Equiponderada_Diversificacion.ipynb
│   ├── Modulo3_Markowitz.ipynb
│   ├── Modulo4_Validacion.ipynb  (en desarrollo)
│   └── Modulo5_Comparacion_Multipunto.ipynb
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
- `calcular_estadisticas_basicas(retornos, rf_anual=0.02)`: Calcula estadísticas por activo
  - Calcula Sharpe histórico restando la tasa libre de riesgo (2% anual por defecto)
  - Fórmula: (retorno_medio - rf_diario) / volatilidad * sqrt(252)
- `analizar_correlaciones(retornos)`: Analiza matriz de correlación
- `analizar_temporal(retornos)`: Análisis temporal de retornos
- `PreparadorDatos`: Clase para preparar datos para optimización

**Cómo funciona**:
1. Lee el CSV con retornos diarios (1761 días × 50 activos)
2. Valida que no haya valores faltantes o infinitos
3. Calcula estadísticas descriptivas para cada activo
4. Analiza la estructura de correlaciones entre activos
5. Prepara los datos para optimización (anualiza μ y Σ)

## 2EQUIPONDERADA_DIVERSIFICACION: ANÁLISIS DE CARTERAS EQUIPONDERADAS Y DIVERSIFICACIÓN

**Archivo**: `2equiponderada_diversificacion.py`

**Funcionalidades**:
- Análisis de cartera equiponderada (descomposición de riesgo)
- Simulación de frontera eficiente de diversificación
- Detección del número óptimo de activos
- Análisis de contribuciones individuales de activos
- Visualización de frontera de diversificación

**Funciones Principales**:
- `analizar_cartera_equiponderada(retornos)`: Descompone el riesgo de cartera equiponderada
  - Implementa fórmula teórica: σ²ₚ = (1/n)V̄ + (1-1/n)σ̄ᵢⱼ
  - Separa riesgo específico (diversificable) y sistemático (no diversificable)
- `simular_frontera_diversificacion(retornos, n_valores, n_simulaciones)`: Simula efecto de diversificación
  - Evalúa cuántos activos se necesitan para alcanzar límite práctico
  - Realiza múltiples simulaciones aleatorias por cada N
  - Genera tabla resumen con estadísticas de diversificación
- `detectar_frontera_optima(df_simulacion, umbral_reduccion)`: Identifica el número óptimo de activos
  - Detecta el punto donde la reducción marginal de riesgo es menor al umbral
- `analizar_contribuciones(retornos, pesos)`: Calcula contribución de cada activo
  - Contribución al rendimiento: wᵢ × E(Rᵢ)
  - Contribución al riesgo: wᵢ × Cov(Rᵢ, Rₚ)
  - Identifica activos diversificadores ideales
- `visualizar_frontera_diversificacion(df_simulacion)`: Visualiza frontera de diversificación
  - Gráfico de evolución del riesgo vs número de activos
  - Descomposición riesgo sistemático vs específico

**Cómo funciona**:
1. Descompone el riesgo de carteras equiponderadas en componentes sistemáticos y específicos
2. Simula el efecto de diversificación variando el número de activos
3. Identifica el número óptimo de activos necesario para alcanzar el límite práctico
4. Analiza la contribución de cada activo al rendimiento y riesgo de la cartera
5. Visualiza los resultados de la simulación y la descomposición del riesgo

## 3MARKOWITZ: OPTIMIZACIÓN CLÁSICA DE MARKOWITZ

**Archivo**: `3markowitz.py`

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

## 4VALIDACION: VALIDACIÓN Y SELECCIÓN FINAL

**Archivo**: `validacion.py`

**Estado**: ⏳ **EN PROCESO DE DESARROLLO**

**Funcionalidades planificadas**:
- Validación de restricciones (long-only, suma=1, RF≤10%)
- Cálculo de métricas de cartera (Sharpe, concentración, diversificación)
- Comparación de estrategias
- Exportación de pesos finales

**Funciones planificadas**:
- `validar_cartera(w, w_rf, nombres_activos)`: Valida restricciones
- `calcular_metricas_cartera(w, w_rf, mu, Sigma, rf)`: Calcula métricas
- `comparar_estrategias(estrategias_dict, nombres_activos)`: Compara estrategias
- `exportar_pesos(w, nombres_activos, ruta_archivo)`: Exporta pesos
- `seleccionar_mejor_estrategia(estrategias_dict, criterio)`: Selecciona mejor

**Cómo funcionará**:
1. Valida que la cartera cumpla todas las restricciones
2. Calcula métricas de rendimiento (Sharpe, rentabilidad, volatilidad)
3. Calcula métricas de estructura (concentración, número de activos)
4. Compara múltiples estrategias y selecciona la mejor
5. Exporta los pesos finales en formato requerido

## 5ANALISIS_MULTIPUNTO: ANÁLISIS MULTIPUNTO DE FRONTERA DE DIVERSIFICACIÓN

**Archivo**: `5analisis_multipunto.py`

**Funcionalidades**:
- Detección de puntos de interés en la frontera de diversificación
- Optimización de carteras para múltiples valores de N
- Consolidación y comparación de resultados
- Visualización comparativa multipanel
- Heatmap de pesos de activos relevantes

**Funciones Principales**:
- `detectar_puntos_interes_frontera(df_simulacion, criterios)`: Identifica mínimos locales, cambios de pendiente y puntos con baja reducción marginal
- `optimizar_multiples_n(retornos, lista_n, rf_anual, peso_sharpe)`: Ejecuta el pipeline de selección+optimización para múltiples N
- `consolidar_resultados_multipunto(resultados_dict)`: Consolida métricas clave de cada cartera
- `visualizar_comparacion_multipunto(df_consolidado, resultados_dict, ruta_guardado)`: Comparación gráfica en 4 subplots
- `generar_heatmap_pesos(resultados_dict, top_activos, ruta_guardado)`: Heatmap de pesos de activos top

**Cómo funciona**:
1. Detecta los puntos relevantes sobre la frontera de diversificación
2. Optimiza carteras usando exactamente el pipeline del módulo 4
3. Consolida y compara métricas de cada cartera resultante
4. Visualiza resultados para facilitar la selección del N óptimo

## NOTEBOOKS DE DEMOSTRACIÓN

Cada notebook en `notebooks_demostracion/` demuestra el funcionamiento de su módulo correspondiente:

1. **Modulo1_Exploracion_Datos.ipynb**: Muestra carga de datos, estadísticas, correlaciones y preparación
2. **Modulo2_Equiponderada_Diversificacion.ipynb**: Demuestra análisis de diversificación y carteras equiponderadas
3. **Modulo3_Markowitz.ipynb**: Demuestra optimización Markowitz, máximo Sharpe y frontera eficiente
4. **Modulo4_Validacion.ipynb**: Validación y selección final (en desarrollo)
5. **Modulo5_Comparacion_Multipunto.ipynb**: Comparación multipunto de la frontera de diversificación

## USO

### Ejecutar un módulo individualmente:

```python
import importlib
import sys
sys.path.append('src')  # O '../src' desde notebooks_demostracion

# Importar módulos (los nombres que empiezan con números requieren importlib)
datos = importlib.import_module('1datos')
equiponderada = importlib.import_module('2equiponderada_diversificacion')
markowitz = importlib.import_module('3markowitz')
validacion = importlib.import_module('validacion')  # (en desarrollo)
multipunto = importlib.import_module('5analisis_multipunto')

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
