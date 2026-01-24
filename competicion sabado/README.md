# 📊 Competición Sábado - Proyecto Independiente

## Descripción General

Este es un **proyecto independiente y autónomo** para exploración, análisis y optimización de un dataset de retornos de 60 activos durante ~7 años de histórico.

## 📂 Estructura de la Carpeta

```
competicion sabado/
├── codigo/
│   └── extractor_datos.py       # Módulo de extracción y análisis
├── notebooks/
│   ├── Exploracion_Datos.ipynb  # Análisis exploratorio interactivo
│   └── *.png                     # Gráficos generados
└── README.md                      # Este archivo
```

## 🎯 Objetivos

1. **Exploración Completa**: Entender la estructura y características del dataset
2. **Análisis Estadístico**: Calcular métricas financieras relevantes
3. **Visualización**: Crear gráficos informativos de rentabilidad, riesgo y correlación
4. **Preparación**: Base para posteriores análisis de optimización

## 📊 Dataset

- **Activos**: 60
- **Observaciones**: 1,758 días (aproximadamente 7 años)
- **Tipo de Datos**: Retornos diarios (log-retornos)
- **Formato**: Excel oculto en .csv

## 🚀 Uso Rápido

### Opción 1: Ejecutar el Notebook (Recomendado)

```bash
# Abrir Jupyter
jupyter notebook competicion\ sabado/notebooks/Exploracion_Datos.ipynb

# Ejecutar todas las celdas (Kernel → Restart & Run All)
```

### Opción 2: Usar el módulo de extracción directamente

```python
import sys
sys.path.insert(0, './competicion sabado/codigo')

from extractor_datos import ExtractorDatos

extractor = ExtractorDatos("data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv")
stats = extractor.resumen_completo()
```

## 📈 Contenido del Notebook

El notebook `Exploracion_Datos.ipynb` incluye:

### Paso 1: Carga y Validación
- Carga de datos desde CSV/Excel
- Validación de integridad
- Información básica del dataset

### Paso 2: Estadísticas Descriptivas
- Retornos diarios/acumulados
- Volatilidad diaria y anualizada
- Sharpe Ratio
- Correlaciones
- Asimetría (Skewness) y Curtosis

### Paso 3: Análisis de Activos Extremos
- Top 5 mejores/peores activos
- Activos más/menos volátiles
- Activos con mejor Sharpe Ratio

### Paso 4: Distribución de Retornos (Gráfico 1)
- Histograma de retornos
- Boxplots por activo
- Evolución de retornos acumulados
- Q-Q Plot de normalidad

### Paso 5: Matriz de Correlaciones (Gráfico 2)
- Heatmap completo 60×60
- Heatmap detallado primeros 15 activos
- Estadísticas de correlación

### Paso 6: Métricas por Activo
- Tabla con Sharpe Ratio, volatilidad, retornos
- Ranking de activos

### Paso 7: Visualizaciones de Métricas (Gráfico 3)
- Sharpe Ratio por activo
- Retorno vs Volatilidad
- Volatilidad anualizada
- Retorno acumulado

### Paso 8: Análisis Rentabilidad vs Riesgo (Gráfico 4)
- Scatter: Rentabilidad anualizada vs Volatilidad
- Identificación de top 5 activos
- Distribución de Sharpe Ratio

### Paso 9: Resumen Ejecutivo
- Conclusiones clave
- Recomendaciones para optimización

## Análisis del Número Óptimo de Activos

El notebook `Analisis_Numero_Optimo.ipynb` implementa:

### Paso 1: Carga de Datos
- Carga desde el archivo CSV

### Paso 2: Simulación de Frontera de Diversificación
- Simulación Monte Carlo para N = {2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50,60}
- 150 simulaciones por cada N
- Cálculo de volatilidad media y desviación estándar
- Descomposición de riesgo específico vs sistemático

### Paso 3: Detección de N Óptimo
- Automática mediante análisis de reducción marginal
- Umbral: reducción de volatilidad < 2%
- Identificación del punto de rendimientos decrecientes

### Paso 4: Visualización
- Gráfico 1: Volatilidad vs N (con intervalo de confianza)
- Gráfico 2: Reducción marginal vs N (con umbral de corte)

### Paso 5: Resumen Ejecutivo
- Interpretación de resultados
- Recomendaciones para optimización posterior

## Cálculo de Betas de Activos

El notebook `Calculo_Betas.ipynb` calcula la sensibilidad de cada activo al mercado:

### Concepto de Beta
- Beta = pendiente de la regresión lineal: R_activo = alfa + beta × R_mercado + error
- Interpretación:
  - **beta > 1**: Activo agresivo (más volátil que el mercado)
  - **beta = 1**: Activo neutral (volatilidad igual al mercado)
  - **beta < 1**: Activo defensivo (menos volátil que el mercado)
  - **beta < 0**: Activo con movimiento inverso al mercado

### Paso 1: Carga de Datos
- Importa las 3 hojas del Excel:
  - Sheet1: Retornos diarios de los 60 activos
  - Hoja2: Características (ticker, sector, capitalización, P/B)
  - Indice: Retornos del índice de mercado

### Paso 2: Cálculo mediante Regresión Lineal
- Para cada activo:
  - Regresión con scipy.stats.linregress
  - Cálculo de beta, alfa, R², correlación
  - Volatilidades

### Paso 3: Clasificación de Activos
- **Defensivos (beta < 0.8)**: 36 activos - indicados para carteras conservadoras
- **Neutrales (0.8 ≤ beta ≤ 1.2)**: 17 activos - movimiento similar al mercado
- **Agresivos (beta > 1.2)**: 7 activos - para carteras dinámicas
- **Negativos (beta < 0)**: 1 activo - útil para hedging

### Paso 4: Visualizaciones
- **Gráfico 1**: Distribución de betas con media y línea de mercado (beta=1)
- **Gráfico 2**: Beta vs R² (calidad de ajuste), coloreado por volatilidad
- **Gráfico 3**: Betas ordenadas con clasificación por color (rojo/gris/verde)
- **Gráfico 4**: Volatilidad de activos vs volatilidad del índice

### Paso 5: Exportación de Resultados
- Tabla CSV con todas las betas calculadas
- Formato: Activo, Beta, Alfa, R², Correlación, Volatilidades, Sector

### Paso 6: Resumen Ejecutivo
- Estadísticas globales
- Distribución por categoría
- Top 5 activos más agresivos/defensivos
- Sectores con mayor exposición al mercado
- Recomendaciones para construcción de carteras

### Salidas Generadas
- `betas_resultados.csv`: Tabla completa de betas
- `betas_analisis.png`: Visualización de 4 gráficos

## 🔧 Módulo extractor_datos.py

### Clase: `ExtractorDatos`

Funcionalidades principales:

```python
# Crear instancia
extractor = ExtractorDatos(ruta_datos)

# Cargar datos
datos = extractor.cargar_datos()

# Validar datos
extractor.validar_datos()

# Estadísticas descriptivas
stats = extractor.estadisticas_descriptivas()

# Activos extremos
extractor.activos_extremos(n=5)

# Ejecutar todo de una vez
stats = extractor.resumen_completo()

# Obtener datos
datos = extractor.obtener_datos()
```

### Métricas Calculadas

- **Retornos**: Diarios, acumulados, anualizados
- **Volatilidad**: Diaria, anualizada (√252)
- **Sharpe Ratio**: (Retorno anual) / (Volatilidad anual)
- **Correlación**: Matriz completa de correlaciones
- **Distribución**: Asimetría (Skewness), Curtosis

## 📊 Gráficos Generados

| Nombre | Contenido |
|--------|----------|
| 01_Distribucion_Retornos.png | Histogramas, boxplots, evolución, Q-Q plot |
| 02_Matriz_Correlaciones.png | Heatmaps de correlación |
| 03_Metricas_Activos.png | Sharpe, volatilidad, retornos por activo |
| 04_Rentabilidad_vs_Riesgo.png | Scatter rentabilidad/volatilidad, distribución Sharpe |

## 💡 Hallazgos Clave

### Rentabilidad
- Retorno promedio muy bajo (~0.036% diario)
- Amplia disparidad entre activos
- Algunos activos con retornos negativos

### Riesgo
- Volatilidad diaria promedio: ~1.76%
- Volatilidad anualizada: ~28% aprox.
- Amplitud significativa de volatilidades

### Sharpe Ratio
- Promedio bajo (alrededor de 0.03-0.04)
- Relación riesgo-rendimiento pobre en promedio
- Gran variabilidad entre activos

### Correlaciones
- Correlación promedio: ~0.36-0.40
- Rango: Desde -0.3 hasta 1.0
- Activos moderadamente correlacionados (oportunidad de diversificación)

### Distribuciones
- No son perfectamente normales
- Evidencia de colas pesadas (riesgo extremo)
- Asimetría presente en la mayoría

## 🎯 Recomendaciones para Optimización

1. **Selección de Activos**
   - Enfocarse en activos con Sharpe Ratio > percentil 75%
   - Considerar correlaciones bajas para diversificación

2. **Estrategias de Cartera**
   - Optimización de Markowitz (minimizar riesgo dado retorno)
   - Risk Parity (igual contribución al riesgo)
   - Máximo Sharpe Ratio

3. **Gestión de Riesgo**
   - Considerar colas pesadas en modelos
   - Posibles coberturas para eventos extremos
   - Análisis de máxima pérdida

4. **Validación**
   - Backtesting en ventanas móviles
   - Análisis de estabilidad de pesos
   - Comparación de estrategias

## 📝 Tecnologías Utilizadas

- **Python 3.8+**
- **Pandas**: Manipulación de datos
- **NumPy**: Cálculos numéricos
- **Matplotlib & Seaborn**: Visualización
- **SciPy**: Análisis estadístico

## 📦 Dependencias

```
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
scipy>=1.7.0
openpyxl>=3.0.0
```

Instalar con:
```bash
pip install -r ../../requirements.txt
```

## 🔗 Relación con Otros Proyectos

Este proyecto es **completamente independiente** del sistema de configuración paramétrica de datos. Utiliza solo los datos del CSV nuevo (U60) sin necesidad del módulo `config_datos.py`.

## 📞 Estructura de Archivos

```
TAREA_GESTION_CARTERAS/
├── competicion sabado/              ← PROYECTO NUEVO (INDEPENDIENTE)
│   ├── codigo/
│   │   └── extractor_datos.py
│   ├── notebooks/
│   │   ├── Exploracion_Datos.ipynb
│   │   └── *.png
│   └── README.md
├── data/
│   ├── prod_long_sharpe_u50_20260116_v5_train_dataset.csv
│   └── prod_long_sharpe_u60_20260125_v1_train_dataset.csv
├── config_datos.py                  ← Sistema anterior (No usado)
└── ...otros archivos...
```

## ✅ Checklist de Ejecución

- [ ] Navegar a la carpeta del proyecto
- [ ] Ejecutar `jupyter notebook notebooks/Exploracion_Datos.ipynb`
- [ ] Ejecutar todos los pasos secuencialmente
- [ ] Revisar gráficos generados
- [ ] Leer conclusiones y recomendaciones
- [ ] Usar estadísticas para próximos análisis de optimización

## 📅 Próximos Pasos

1. **Optimización de Carteras**: Aplicar estrategias de Markowitz y Risk Parity
2. **Validación Out-of-Sample**: Backtesting en períodos de prueba
3. **Análisis de Sensibilidad**: Robustez de pesos ante cambios
4. **Implementación de Restricciones**: Long-only, límites de posición, etc.

---

**Proyecto Independiente | Competición Sábado | Enero 2026**
