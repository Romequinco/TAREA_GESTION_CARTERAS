# MÓDULOS DE OPTIMIZACIÓN DE CARTERAS

Este proyecto contiene 5 módulos Python para la optimización de carteras y una carpeta con notebooks de demostración.

## ESTRUCTURA DEL PROYECTO

```
.
├── src/                           # Módulos de código
│   ├── 1datos.py                 # Exploración y Preparación de Datos
│   ├── 2equiponderada_diversificacion.py  # Análisis de Carteras Equiponderadas y Diversificación
│   ├── 3markowitz.py             # Optimización Clásica de Markowitz
│   ├── 4seleccion_activos.py     # Selección Óptima de Activos
│   ├── 5analisis_multipunto.py   # Análisis multipunto de diversificación
│   ├── validacion.py             # Validación y Exportación Final
│   ├── importar_modulos.py       # Script auxiliar para importar módulos
│   └── README_MODULOS.md         # Documentación completa
├── data/                         # Carpeta con datos
│   └── prod_long_sharpe_u50_20260116_v5_train_dataset.csv
├── notebooks_demostracion/       # Notebooks de demostración
│   ├── Modulo1_Exploracion_Datos.ipynb
│   ├── Modulo2_Equiponderada_Diversificacion.ipynb
│   ├── Modulo3_Markowitz.ipynb
│   ├── Modulo4_Seleccion_Activos.ipynb
│   ├── Modulo5_Comparacion_Multipunto.ipynb
│   ├── Modulo8_Validacion.ipynb
│   └── outputs/                  # Imágenes y archivos generados
├── comprobaciones/               # Documentación detallada por módulo
│   ├── 1datos/
│   ├── 2equiponderada_diversificacion/
│   ├── 3markowitz/
│   ├── 4seleccion_activos/
│   └── 5analisis_multipunto/
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
1. Lee el CSV con retornos diarios (1760 días × 50 activos)
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

## 4SELECCION_ACTIVOS: SELECCIÓN ÓPTIMA DE ACTIVOS

**Archivo**: `4seleccion_activos.py`

**Funcionalidades**:
- Detección automática del número óptimo de activos (N) usando frontera de diversificación
- Selección de activos por Sharpe Ratio + baja correlación
- Filtrado de DataFrame de retornos
- Pipeline completo de selección + optimización
- Reconstrucción de vector de pesos de 50 posiciones
- Visualización del proceso de selección
- Comparación de estrategias (equiponderada, Markowitz 50, Selección+Markowitz N)

**Funciones Principales**:
- `detectar_n_optimo_activos(retornos, umbral_reduccion, n_simulaciones)`: Detecta N óptimo usando módulo 2
- `calcular_metricas_seleccion(retornos, rf_anual)`: Calcula métricas de calidad por activo
- `seleccionar_activos_por_sharpe_decorrelacion(retornos, n_activos, rf_anual, peso_sharpe, peso_decorrelacion)`: Selecciona N activos balanceando Sharpe y diversificación
- `filtrar_retornos_activos_seleccionados(retornos, activos_seleccionados)`: Filtra DataFrame
- `optimizar_cartera_con_seleccion(retornos, rf_anual, n_optimo, umbral_reduccion, metodo_optimizacion)`: **FUNCIÓN PRINCIPAL** - Ejecuta pipeline completo
- `visualizar_seleccion_activos(resultado_seleccion, retornos_completos, ruta_guardado)`: Visualización 2×2 del proceso
- `comparar_estrategias(retornos, rf_anual)`: Compara 3 estrategias diferentes

**Cómo funciona**:
1. Detecta N óptimo usando frontera de diversificación (módulo 2)
2. Selecciona N activos según criterios de calidad + diversificación
3. Filtra retornos a solo esos N activos seleccionados
4. Optimiza con Markowitz (módulo 3) sobre activos seleccionados
5. Reconstruye vector de 50 posiciones con pesos finales
6. Calcula métricas y compara con baseline (equiponderada 50)

## 5VALIDACION: VALIDACIÓN Y EXPORTACIÓN FINAL

**Archivo**: `validacion.py`

**Funcionalidades**:
- Validación de restricciones (long-only, suma=1, RF≤10%, 50 activos)
- Cálculo de métricas de cartera (Sharpe, concentración, diversificación)
- Comparación de estrategias
- Exportación de pesos finales

**Funciones Principales**:
- `validar_cartera(w, w_rf, nombres_activos, tolerancia)`: Valida todas las restricciones
- `calcular_metricas_cartera(w, w_rf, mu, Sigma, rf)`: Calcula métricas completas (rendimiento y estructura)
- `comparar_estrategias(estrategias_dict, nombres_activos)`: Compara múltiples estrategias
- `exportar_pesos(w, nombres_activos, ruta_archivo)`: Exporta pesos a CSV
- `seleccionar_mejor_estrategia(estrategias_dict, criterio)`: Selecciona mejor según criterio

**Cómo funciona**:
1. Valida que la cartera cumpla todas las restricciones
2. Calcula métricas de rendimiento (Sharpe, rentabilidad, volatilidad)
3. Calcula métricas de estructura (concentración Herfindahl, número de activos)
4. Compara múltiples estrategias y selecciona la mejor
5. Exporta los pesos finales en formato requerido

## 6ANALISIS_MULTIPUNTO: ANÁLISIS MULTIPUNTO DE FRONTERA DE DIVERSIFICACIÓN

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
4. **Modulo4_Seleccion_Activos.ipynb**: Demuestra selección de activos y pipeline completo de optimización
5. **Modulo5_Comparacion_Multipunto.ipynb**: Comparación multipunto de la frontera de diversificación
6. **Modulo8_Validacion.ipynb**: Validación de restricciones, cálculo de métricas y exportación

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
seleccion = importlib.import_module('4seleccion_activos')
multipunto = importlib.import_module('5analisis_multipunto')
validacion = importlib.import_module('validacion')

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
