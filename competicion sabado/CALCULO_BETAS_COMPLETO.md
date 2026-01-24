# CALCULO DE BETAS - COMPETICION SABADO (24 Enero 2026)

## Status: ✓ COMPLETADO

---

## Resumen Ejecutivo

Se ha implementado un **módulo completo de cálculo de betas** para determinar la sensibilidad de cada uno de los 60 activos respecto al índice de mercado.

### Archivos Generados

```
competicion sabado/
├── codigo/
│   └── calcular_betas.py          [14 KB] - Modulo con clase CalculadorBetas
├── notebooks/
│   ├── Calculo_Betas.ipynb        [9 KB]  - Notebook con 12+ celdas ordenadas
│   ├── betas_resultados.csv       [~5 KB] - Tabla con todas las betas (60 filas)
│   └── betas_analisis.png         [534 KB] - Visualizacion: 4 graficos
└── README.md                       - Documentacion actualizada
└── BETAS_RESUMEN.txt              - Resumen tecnico y recomendaciones
```

---

## Metodologia

### Concepto: Beta y Regresion Lineal

Para cada activo se ejecuta una regresion lineal:

```
R_activo = alfa + beta × R_mercado + error
```

Donde:
- **beta** = pendiente de la recta (sensibilidad al mercado)
- **alfa** = intercepto (retorno independiente del mercado)
- **R²** = calidad del ajuste (cuanto explica el mercado la volatilidad)

### Interpretacion de Betas

| Beta | Categoria | Significado | Ejemplos |
|------|-----------|------------|----------|
| > 1.2 | Agresivo | Amplifica movimientos del mercado | Tech, Pharma |
| 0.8-1.2 | Neutral | Replica movimientos del mercado | Industriales |
| 0.5-0.8 | Defensivo | Suaviza movimientos del mercado | Utilities |
| < 0 | Inverso | Se mueve OPUESTO al mercado | Metals/Mining |

---

## Resultados Clave

### Distribucion de Betas

```
Beta promedio:    0.8267
Beta mediana:     0.7639
Rango:           [-0.0668, 1.7960]
Desv. Estandar:   0.4189
```

### Clasificacion por Perfil de Riesgo

```
Defensivos (beta < 0.8):        36 activos (60.0%)
Neutrales (0.8 ≤ beta ≤ 1.2):  17 activos (28.3%)
Agresivos (beta > 1.2):          7 activos (11.7%)
Negativos (beta < 0):            1 activo  (1.7%)
```

### Top Activos

**Mas Agresivos (Mayor Beta):**
1. Activo 42 (Software & IT Services) - Beta = 1.7960
2. Activo 28 (Semiconductors) - Beta = 1.7528
3. Activo 9 (Pharmaceuticals) - Beta = 1.5323
4. Activo 30 (Banking Services) - Beta = 1.4138
5. Activo 13 (Residential & Commercial) - Beta = 1.3399

**Mas Defensivos (Menor Beta):**
1. Activo 39 (Metals & Mining) - Beta = -0.0668 ← NEGATIVA (Hedging)
2. Activo 50 (Electric Utilities & IPPs) - Beta = 0.2894
3. Activo 56 (Residential & Commercial) - Beta = 0.3055
4. Activo 47 (Residential & Commercial) - Beta = 0.3185
5. Activo 46 (Personal & Household Prod) - Beta = 0.3436

### Calidad del Modelo (R²)

```
R² promedio:     0.2074 (mercado explica ~21% de la volatilidad)
R² mediana:      0.1565
% con R² > 0.3:  40.0% (23 activos con buen ajuste)
```

---

## Visualizaciones

### Gráfico 1: Distribución de Betas
- Histograma con 30 bins
- Línea roja en beta=1 (mercado)
- Línea verde en media de betas

### Gráfico 2: Beta vs Calidad de Ajuste
- Scatter: Beta (eje X) vs R² (eje Y)
- Coloreado por volatilidad del activo
- Permite identificar activos "confiables"

### Gráfico 3: Betas Ordenadas
- Barras horizontales ordenadas de menor a mayor beta
- **Rojo**: Defensivos (beta < 0.8)
- **Gris**: Neutrales (0.8 ≤ beta ≤ 1.2)
- **Verde**: Agresivos (beta > 1.2)
- Referencias de corte visibles

### Gráfico 4: Volatilidad
- Scatter: Volatilidad del índice vs Volatilidad del activo
- Línea de referencia para beta=1
- Identifica relacion entre volatilidades

---

## Salidas Generadas

### CSV: betas_resultados.csv

**Columnas:**
- `Activo`: ID del activo (1-60)
- `Beta`: Sensibilidad al mercado (principal)
- `Beta_Alternativa`: Beta calculada como Cov/Var
- `Alfa`: Intercepto de la regresion
- `R_Squared`: Calidad del ajuste (0-1)
- `Correlacion`: Pearson con el índice
- `Volatilidad_Activo`: Vol diaria del activo
- `Volatilidad_Indice`: Vol diaria del índice
- `P_Value`: Significancia estadistica
- `Std_Error`: Error estandar de beta
- `Ticker`: ID del ticker
- `Sector`: Sector del activo

---

## Recomendaciones para Construccion de Carteras

### Estrategia 1: Cartera Defensiva (Bajo Riesgo)
- **Seleccionar:** Activos con beta < 0.8 (36 disponibles)
- **Sectores:** Utilities, Consumer Staples, Beverages
- **Beneficio:** Menor volatilidad, menor correlation con movimientos del mercado
- **Ejemplos:** Activos 50, 56, 47, 46, 44

### Estrategia 2: Cartera Neutral (Riesgo Medio)
- **Seleccionar:** Activos con 0.8 ≤ beta ≤ 1.2 (17 disponibles)
- **Beneficio:** Replican el mercado, baja complejidad
- **Ejemplos:** Activos 59, 24, 6, 21, 55

### Estrategia 3: Cartera Agresiva (Alto Riesgo)
- **Seleccionar:** Activos con beta > 1.2 (7 disponibles)
- **Sectores:** Tech, Semiconductors, Pharma, Finance
- **Beneficio:** Mayor potencial de retorno en mercados alcistas
- **Ejemplos:** Activos 42, 28, 9, 30, 13

### Estrategia 4: Cartera con Hedging
- **Incluir:** Activo 39 (Metals & Mining, beta = -0.0668)
- **Proporcion:** 5-10% del portafolio
- **Beneficio:** Cubre movimientos del mercado (beta negativa)
- **Efecto:** Reduce volatilidad total

### Combinacion Equilibrada (Ejemplo)
- 50% Activos defensivos (beta promedio ~0.5)
- 30% Activos neutrales (beta promedio ~1.0)
- 15% Activos agresivos (beta promedio ~1.5)
- 5% Activo 39 hedging (beta = -0.067)

Beta promedio cartera = 0.5×0.5 + 0.3×1.0 + 0.15×1.5 + 0.05×(-0.067) = 0.7745

---

## Integracion con Otros Modulos

### Con Análisis de Número Óptimo
- Usar betas para seleccionar N activos con perfiles complementarios
- Ejemplo: N=4 activos con betas [0.4, 0.8, 1.2, 1.6] para diversificacion de riesgo

### Con Optimizacion Markowitz
- Usar betas para restricciones en la optimizacion
- Limitar beta promedio de la cartera (ej: beta_cartera ≤ 1.0)
- Combinar activos con diferentes betas para control de riesgo

### Con CAPM
- Usar beta para estimar retorno esperado: E[R] = Rf + beta × (E[Rm] - Rf)
- Calcular costo de capital
- Valuar activos individuales

---

## Consideraciones Tecnicas

### Limitaciones del Modelo
- **R² bajo (0.21 promedio)**: El mercado explica solo ~21% de la volatilidad
- **Implica:** Hay otros factores importantes (sectores, tamaño, estilo)
- **Solucion:** Modelos multifactoriales (Fama-French, APT)

### Estabilidad de Betas
- Betas cambian a lo largo del tiempo
- Recomendacion: Recalcular cada trimestre
- Usar ventanas de 3-5 años para mayor estabilidad

### Sesgo de Periodo
- Betas calculadas durante 1,758 dias (~7 años)
- Puede no ser representativo de periodos futuros
- Especialmente importante en cambios de regimen de mercado

---

## Reproducibilidad y Uso

### Ejecutar Calculo Completo

```python
import sys
sys.path.insert(0, 'competicion sabado/codigo')
from calcular_betas import CalculadorBetas

# Inicializar
calc = CalculadorBetas('data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv')

# Calcular
betas_df = calc.calcular_betas()

# Clasificar
clasificacion = calc.clasificar_activos()

# Visualizar
calc.visualizar_betas(figsize=(16, 12))

# Exportar
calc.exportar_resultados('competicion sabado/notebooks/betas_resultados.csv')

# Analizar por sector
sectores = calc.obtener_betas_por_sector()
```

### En Jupyter Notebook

Ver `competicion sabado/notebooks/Calculo_Betas.ipynb` para ejecucion paso a paso.

---

## Proximos Pasos Recomendados

1. **Backtesting**: Validar predicciones de beta en periodos futuros
2. **Modelos Multifactoriales**: Incorporar sector, tamaño, momentum
3. **Analisis Dinamico**: Detectar cambios en betas (estabilidad)
4. **Integracion**: Usar betas en optimizacion de carteras
5. **Cobertura**: Implementar estrategias de hedging con activo 39

---

## Metadata

**Archivo**: `competicion sabado/BETAS_RESUMEN.txt` (este documento)
**Dataset**: `data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv`
- Sheet1: 1,758 obs × 60 activos
- Hoja2: 60 características (sector, ticker, etc)
- Indice: 1,758 obs índice de mercado

**Periodo**: ~7 años (1,758 días de retornos diarios)
**Fecha Calculo**: 24 Enero 2026
**Autor**: Oscar Romero
**Contacto**: romequinco@gmail.com
**Repositorio**: https://github.com/Romequinco/TAREA_GESTION_CARTERAS.git

---

**STATUS**: ✓ COMPLETO Y OPERACIONAL
