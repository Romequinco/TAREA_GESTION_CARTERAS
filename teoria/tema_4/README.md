# TEMA 4: SMART BETAS Y MODELOS MULTIFACTORIALES

Esta carpeta contiene los notebooks del TEMA 4 sobre Smart Betas, modelos multifactoriales y su aplicación práctica.

## Archivos en esta carpeta:

- **`APT_analisis.ipynb`** (Sección 4.1):
  - Análisis de Arbitrage Pricing Theory (APT)
  - Modelo de Fama-French de 3 y 4 factores
  - Análisis de factores SMB (tamaño), HML (valor) y MOM (momentum)
  - Análisis estadístico con regresión HAC/Newey-West
  - Rolling t-statistics para evaluar estabilidad temporal
  - Análisis de subperíodos (pre/post 1980, pre/post 2007, etc.)

- **`APT_fondo.ipynb`** (Sección 4.2):
  - Análisis de fondos de inversión usando factores de Fama-French
  - Uso de Style Box de Morningstar para clasificar fondos
  - Regresión lineal entre rendimientos del fondo y factores de mercado
  - Regresión con factores por industria
  - Regresión con activos individuales del fondo
  - Descomposición del alpha y beta del fondo

- **`APT_Cartera.ipynb`** (Sección 4.3):
  - Construcción de carteras multifactoriales usando aproximación Top-Down
  - Optimización con exposiciones objetivo a factores (Value, Momentum, Beta)
  - Matriz X con características de activos normalizadas (z-scores)
  - Tracking de exposiciones: minimización de ||X^T w - b*||^2_W
  - Penalización por riesgo y rotación en función objetivo
  - Restricciones de neutralidad a mercado (beta target)
  - Implementación práctica con CVXPY para carteras del IBEX35

- **`APT_MIAX.pdf`**: Documento sobre APT (Arbitrage Pricing Theory) y Smart Betas relacionado con MIAX

- **`CUESTI_1.PDF`**: Documento con cuestiones o ejercicios del TEMA 4

## Contenido del TEMA 4:

- **4.1**: Análisis de los factores de Fama-French
  - Modelo de Fama-French de 4 factores (MKT, SMB, HML, MOM)
  - Análisis temporal de factores con rolling t-statistics
  - Estabilidad temporal y limitaciones empíricas

- **4.2**: Análisis de fondos de inversión
  - Uso de Style Box para clasificación de fondos
  - Regresiones multifactoriales para descomponer rendimientos
  - Análisis de exposiciones sectoriales e industriales

- **4.3**: Diseño de carteras con factores
  - Aproximación Top-Down para construcción de carteras factor-based
  - Optimización con tracking de exposiciones objetivo
  - Neutralidad a mercado y control de rotación

## Conceptos relacionados:

- Modelos multifactoriales (APT, Fama-French)
- Factores de riesgo (tamaño SMB, valor HML, momentum MOM)
- Smart Betas y Factor-Based Investing
- Análisis de fondos de inversión (Style Box, regresiones multifactoriales)
- Construcción de carteras con exposiciones objetivo a factores
- Optimización con CVXPY para carteras multifactoriales
- Tracking de exposiciones y neutralidad a mercado

## Fórmulas principales:

### Modelo de Fama-French (4 factores):
$$E(r_i) = r_f + \beta_{i,MKT} E(r_m - r_f) + \beta_{i,SMB} E(SMB) + \beta_{i,HML} E(HML) + \beta_{i,MOM} E(MOM)$$

### Momentum 12-2:
$$MOM_{i,t} = \prod_{j=2}^{12}(1+r_{i,t-j})-1$$

### Matriz de características normalizadas:
$$z_{i,k} = \frac{señal_{i,k} - \mu_k}{\sigma_k}$$

### Exposición de cartera a factores:
$$b(w) = X^T w \in \mathbb{R}^K$$

### Tracking de exposiciones:
$$\|X^T w - b^*\|^2_W = (X^T w - b^*)^T W (X^T w - b^*) = \sum_{k=1}^K W_k ((X^T w)_k - b^*_k)^2$$

### Pesos de exposición:
$$W_k = \frac{1}{\sigma^2_k}$$

---

*TEMA 4 completo: Análisis de factores, fondos de inversión y diseño de carteras multifactoriales.*
