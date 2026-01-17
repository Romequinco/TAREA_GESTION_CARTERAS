"""
Generador de Archivos de Prompts para Competición de Cartera
=============================================================

Este script genera TODOS los archivos de prompts necesarios.
Ejecuta este código y se crearán automáticamente los archivos .txt

Uso:
    python generar_prompts.py
"""

import os

# Crear directorio
if not os.path.exists('prompts_competicion'):
    os.makedirs('prompts_competicion')

print("📁 Generando archivos de prompts...")
print("=" * 60)

# ==================== PROMPT GENERAL ====================
prompt_general = """
# PROMPT GENERAL - OPTIMIZACIÓN DE CARTERA PARA COMPETICIÓN

## RECURSOS DISPONIBLES

**IMPORTANTE**: Tienes acceso al archivo `Notebook_Ejecutivo_Resumen_Completo.ipynb` que contiene 
TODO el marco teórico necesario para esta tarea. **LEE ESTE NOTEBOOK PRIMERO** antes de empezar 
a implementar cualquier solución. El notebook contiene:

- TEMA 1: Introducción a Carteras (correlación, diversificación, fórmulas básicas)
- TEMA 2: Fundamentos de Gestión de Carteras y Riesgo (Markowitz, CVXPY, Tobin)
- TEMA 3: CAPM y Modelo de Mercado (beta, alpha, SML, regresión)
- TEMA 4: Smart Betas y Modelos Multifactoriales (Fama-French, optimización Top-Down)
- Tabla completa de 41 fórmulas con explicaciones detalladas
- Ejemplos de código y visualizaciones

---

## CONTEXTO DE LA COMPETICIÓN

**Objetivo**: Maximizar el Sharpe Ratio anualizado de una cartera
**Métrica de evaluación**: Sharpe Ratio anualizado sobre retornos futuros no vistos
**Activos disponibles**: 50 activos riesgosos + 1 activo libre de riesgo (renta fija)
**Datos disponibles**: 1761 días de retornos logarítmicos diarios para los 50 activos
**Periodo de competición**: 7 días (16-23 enero 2026) donde puedo enviar 1 solución por día
**Tasa libre de riesgo**: 2.00% anual

**Restricciones**:
- Long-only: todos los pesos wi ≥ 0 (no posiciones cortas)
- Suma de pesos = 1 (inversión completa)
- Peso máximo en renta fija: 10% (0.1)
- Sin límites individuales por activo riesgoso

**Formato de entrega**: Vector de 50 pesos para los activos riesgosos

---

## MARCO TEÓRICO (Consulta el Notebook)

### TEMA 1: Fundamentos
- Rentabilidad: E(R̃_p) = Σ wᵢE(R̃ᵢ)
- Varianza: σ²_p = wᵀΣw
- Efecto correlación y diversificación

### TEMA 2: Markowitz y Tobin
- max f(w) = wᵀμ - λwᵀΣw
- CML: μₚ = rf + [(μₘ - rf)/σₘ]σₚ
- Implementación CVXPY

### TEMA 3: CAPM
- E[r̃ᵢ] - rf = βᵢ(E[r̃ₘ] - rf)
- β = Cov(r̃ᵢ, r̃ₘ)/σ²ₘ

### TEMA 4: Multifactorial
- Fama-French (MKT, SMB, HML, MOM)
- Momentum 12-2
- Optimización Top-Down

---

## MÓDULOS DE TRABAJO

**MÓDULO 1**: Exploración y Preparación de Datos
**MÓDULO 2**: Optimización Clásica de Markowitz  
**MÓDULO 3**: Construcción de Factores y Señales
**MÓDULO 4**: Optimización Multifactorial Avanzada
**MÓDULO 5**: Validación y Selección Final

Consulta los prompts específicos de cada módulo.

---

## PRINCIPIOS FUNDAMENTALES

1. **Lee el Notebook Teórico**: Todas las fórmulas están ahí
2. **Prioriza Robustez**: Evaluación en retornos futuros desconocidos
3. **Librerías**: cvxpy, numpy, pandas, matplotlib, seaborn
4. **Anualización**: μ_anual = μ_diario × 252, Σ_anual = Σ_diario × 252
5. **Código Modular**: Funciones claras con docstrings

---

## VALIDACIONES OBLIGATORIAS

```python
assert all(w >= 0), "Long-only"
assert abs(sum(w) + w_rf - 1.0) < 1e-6, "Suma = 1"
assert 0 <= w_rf <= 0.1, "RF ≤ 10%"
assert len(w) == 50, "50 activos"
```

---

## MÉTRICAS A REPORTAR

1. Rentabilidad Esperada Anualizada
2. Volatilidad Esperada Anualizada
3. Sharpe Ratio Anualizado
4. Peso en Renta Fija
5. Índice de Concentración (Herfindahl)
6. Número de activos con peso >1%

---

**SIGUIENTE PASO**: Lee los prompts modulares específicos y el notebook teórico.
"""

# ==================== MÓDULO 1 ====================
modulo1 = """
# MÓDULO 1: EXPLORACIÓN Y PREPARACIÓN DE DATOS

## PREREQUISITO
Lee `Notebook_Ejecutivo_Resumen_Completo.ipynb`:
- ApÃ©ndice (fórmulas ID 1-4)
- TEMA 1.1, 1.2, 1.3

## OBJETIVO
Cargar, explorar y preparar datos de 1761 días × 50 activos

## PASO 1.1: CARGA
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def cargar_retornos(ruta):
    # Cargar CSV (1761 × 50)
    # Verificar dimensiones, NaNs, infinitos
    pass

retornos = cargar_retornos('retornos_diarios.csv')
```

## PASO 1.2: ESTADÍSTICAS
```python
def calcular_estadisticas_basicas(retornos):
    stats_df = pd.DataFrame({
        'media_diaria': retornos.mean(),
        'std_diaria': retornos.std(),
        'sharpe_historico': retornos.mean() / retornos.std() * np.sqrt(252),
        'media_anual': retornos.mean() * 252,
        'std_anual': retornos.std() * np.sqrt(252)
    })
    return stats_df.sort_values('sharpe_historico', ascending=False)

stats = calcular_estadisticas_basicas(retornos)
print(stats.head(10))
```

## PASO 1.3: CORRELACIONES
```python
corr_matrix = retornos.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
correlaciones = corr_matrix.where(mask).stack()

print(f"Correlación media: {correlaciones.mean():.4f}")
print(f"Correlación min/max: {correlaciones.min():.4f} / {correlaciones.max():.4f}")

# Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, cmap='RdBu_r', center=0, vmin=-1, vmax=1)
plt.title('Matriz de Correlación')
plt.savefig('correlaciones.png', dpi=300)
```

## PASO 1.4: ANÁLISIS TEMPORAL
```python
# Retornos acumulados
retornos_acum = (1 + retornos).cumprod()
indice_mercado = retornos.mean(axis=1)

# Volatilidad rolling 63 días
vol_rolling = retornos.rolling(63).std() * np.sqrt(252)
```

## PASO 1.5: PREPARACIÓN FINAL
```python
class PreparadorDatos:
    def __init__(self, retornos, rf_anual=0.02):
        self.retornos = retornos
        self.rf_anual = rf_anual
        self.rf_diario = (1 + rf_anual)**(1/252) - 1
    
    def calcular_estadisticas(self, ventana=None):
        datos = self.retornos if ventana is None else self.retornos.iloc[-ventana:]
        self.mu_diario = datos.mean().values
        self.cov_matriz = datos.cov().values
        self.mu_anual = self.mu_diario * 252
        self.cov_anual = self.cov_matriz * 252
        return self

preparador = PreparadorDatos(retornos)
preparador.calcular_estadisticas()
mu, Sigma = preparador.mu_anual, preparador.cov_anual
```

## SALIDAS
✅ DataFrame retornos cargado
✅ Estadísticas completas
✅ Matriz correlaciones
✅ Vectores μ y Σ anualizados
✅ Gráficos guardados

**SIGUIENTE**: Módulo 2 - Markowitz
"""

# ==================== MÓDULO 2 ====================
modulo2 = """
# MÓDULO 2: OPTIMIZACIÓN DE MARKOWITZ

## PREREQUISITO
Lee Notebook: TEMA 2.1, 2.3, 2.4, 2.6
Fórmulas ID 14-16, 28

## OBJETIVO
Optimización clásica + máximo Sharpe + frontera eficiente

## PASO 2.1: MARKOWITZ CON λ
```python
import cvxpy as cp

def optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param):
    n = len(mu)
    w = cp.Variable(n)
    w_rf = cp.Variable()
    
    rentabilidad = w @ mu + w_rf * rf
    riesgo = cp.quad_form(w, Sigma)
    objetivo = rentabilidad - lambda_param * riesgo
    
    restricciones = [
        cp.sum(w) + w_rf == 1,
        w >= 0,
        w_rf >= 0,
        w_rf <= 0.1
    ]
    
    problema = cp.Problem(cp.Maximize(objetivo), restricciones)
    problema.solve(solver=cp.ECOS)
    
    w_opt = w.value
    w_rf_opt = w_rf.value
    mu_p = w_opt @ mu + w_rf_opt * rf
    sigma_p = np.sqrt(w_opt @ Sigma @ w_opt)
    sharpe = (mu_p - rf) / sigma_p
    
    return {'w': w_opt, 'w_rf': w_rf_opt, 'sharpe': sharpe}

# Probar diferentes λ
for lam in [0.5, 1.0, 2.0, 5.0]:
    res = optimizar_markowitz_lambda(mu, Sigma, rf, lam)
    print(f"λ={lam}: Sharpe={res['sharpe']:.4f}")
```

## PASO 2.2: MÁXIMO SHARPE DIRECTO
```python
def optimizar_sharpe_maximo(mu, Sigma, rf):
    n = len(mu)
    y = cp.Variable(n)
    y_rf = cp.Variable()
    
    objetivo = cp.quad_form(y, Sigma)
    restricciones = [
        y @ mu + y_rf * rf == 1,
        y >= 0,
        y_rf >= 0
    ]
    
    problema = cp.Problem(cp.Minimize(objetivo), restricciones)
    problema.solve()
    
    suma = np.sum(y.value) + y_rf.value
    w_opt = y.value / suma
    w_rf_opt = y_rf.value / suma
    
    # Ajustar si w_rf > 0.1
    if w_rf_opt > 0.1:
        w_rf_opt = 0.1
        w_opt = w_opt * (1 - w_rf_opt) / np.sum(w_opt)
    
    mu_p = w_opt @ mu + w_rf_opt * rf
    sigma_p = np.sqrt(w_opt @ Sigma @ w_opt)
    sharpe = (mu_p - rf) / sigma_p
    
    return {'w': w_opt, 'w_rf': w_rf_opt, 'sharpe': sharpe,
            'rentabilidad': mu_p, 'volatilidad': sigma_p}

cartera_max_sharpe = optimizar_sharpe_maximo(mu, Sigma, rf)
print(f"Máximo Sharpe: {cartera_max_sharpe['sharpe']:.4f}")
```

## PASO 2.3: FRONTERA EFICIENTE
```python
def construir_frontera(mu, Sigma, rf, n_puntos=50):
    mu_min = rf
    mu_max = mu.max() * 0.95
    mu_targets = np.linspace(mu_min, mu_max, n_puntos)
    
    fronteras = []
    for mu_t in mu_targets:
        w = cp.Variable(len(mu))
        w_rf = cp.Variable()
        
        objetivo = cp.quad_form(w, Sigma)
        restricciones = [
            w @ mu + w_rf * rf == mu_t,
            cp.sum(w) + w_rf == 1,
            w >= 0,
            w_rf >= 0,
            w_rf <= 0.1
        ]
        
        problema = cp.Problem(cp.Minimize(objetivo), restricciones)
        problema.solve(verbose=False)
        
        if problema.status == 'optimal':
            sigma_p = np.sqrt(objetivo.value)
            fronteras.append({
                'rentabilidad': mu_t,
                'volatilidad': sigma_p,
                'sharpe': (mu_t - rf) / sigma_p
            })
    
    return pd.DataFrame(fronteras)

frontera_df = construir_frontera(mu, Sigma, rf)

# Graficar
plt.figure(figsize=(12, 8))
plt.plot(frontera_df['volatilidad']*100, frontera_df['rentabilidad']*100, 'b-', lw=2)
plt.scatter(cartera_max_sharpe['volatilidad']*100, 
            cartera_max_sharpe['rentabilidad']*100,
            s=200, c='red', marker='*', label='Max Sharpe')
plt.xlabel('Volatilidad (%)')
plt.ylabel('Rentabilidad (%)')
plt.title('Frontera Eficiente')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('frontera_eficiente.png', dpi=300)
```

## PASO 2.4: ANÁLISIS DE SENSIBILIDAD
```python
# Ventanas temporales
ventanas = [252, 504, 756, None]
resultados = []

for ventana in ventanas:
    if ventana:
        mu_v = retornos.iloc[-ventana:].mean().values * 252
        Sigma_v = retornos.iloc[-ventana:].cov().values * 252
    else:
        mu_v, Sigma_v = mu, Sigma
    
    cartera = optimizar_sharpe_maximo(mu_v, Sigma_v, rf)
    resultados.append({
        'ventana': ventana or 'Completa',
        'sharpe': cartera['sharpe'],
        'concentracion': np.sum(cartera['w']**2)
    })

pd.DataFrame(resultados)
```

## SALIDAS
✅ Cartera óptima con diferentes λ
✅ Cartera máximo Sharpe
✅ Frontera eficiente completa
✅ Análisis de sensibilidad
✅ CML visualizada

**SIGUIENTE**: Módulo 3 - Factores
"""

# ==================== MÓDULO 3 ====================
modulo3 = """
# MÓDULO 3: CONSTRUCCIÓN DE FACTORES Y SEÑALES

## PREREQUISITO
Lee Notebook: TEMA 4.1, 4.3
Fórmulas ID 35-40

## OBJETIVO
Construir señales de momentum, volatilidad, beta

## PASO 3.1: MOMENTUM 12-2
```python
def calcular_momentum_12_2(retornos):
    \"\"\"
    MOM = ∏(j=2 to 12)(1 + r_{t-j}) - 1
    En días: retornos acumulados desde t-252 hasta t-21
    \"\"\"
    momentum = pd.DataFrame(index=retornos.index, columns=retornos.columns)
    
    for i in range(252, len(retornos)):
        # Retornos de t-252 a t-21 (evitar t-1 por reversión)
        ret_periodo = retornos.iloc[i-252:i-21]
        mom = (1 + ret_periodo).prod() - 1
        momentum.iloc[i] = mom
    
    return momentum

momentum = calcular_momentum_12_2(retornos)

# Momentum más reciente (última fila válida)
mom_actual = momentum.iloc[-1]
print("Top 10 por Momentum:")
print(mom_actual.sort_values(ascending=False).head(10))
```

## PASO 3.2: VOLATILIDAD ROLLING
```python
def calcular_volatilidad_rolling(retornos, ventanas=[21, 63, 252]):
    \"\"\"
    Calcular volatilidad en múltiples ventanas
    \"\"\"
    vols = {}
    for v in ventanas:
        vols[f'vol_{v}d'] = retornos.rolling(v).std() * np.sqrt(252)
    
    return pd.DataFrame(vols, index=retornos.index)

volatilidades = calcular_volatilidad_rolling(retornos)

# Volatilidad más reciente
vol_actual_63d = volatilidades['vol_63d'].iloc[-1]
print("Top 10 Menor Volatilidad (63d):")
print(vol_actual_63d.sort_values().head(10))
```

## PASO 3.3: BETA VS MERCADO
```python
def calcular_betas(retornos, ventana=252):
    \"\"\"
    β = Cov(r_i, r_M) / Var(r_M)
    Mercado = índice equiponderado de 50 activos
    \"\"\"
    # Índice mercado equiponderado
    indice_mercado = retornos.mean(axis=1)
    
    betas = {}
    for col in retornos.columns:
        # Usar últimos 'ventana' días
        datos = retornos[[col]].iloc[-ventana:]
        mercado = indice_mercado.iloc[-ventana:]
        
        cov = np.cov(datos[col], mercado)[0, 1]
        var_m = np.var(mercado)
        beta = cov / var_m if var_m > 0 else 1.0
        betas[col] = beta
    
    return pd.Series(betas)

betas = calcular_betas(retornos, ventana=252)
print("Top 10 Menor Beta:")
print(betas.sort_values().head(10))
```

## PASO 3.4: NORMALIZACIÓN Z-SCORE
```python
def normalizar_senales(senales_dict):
    \"\"\"
    z = (señal - μ) / σ
    Normalización cross-sectional
    \"\"\"
    senales_norm = {}
    
    for nombre, senal in senales_dict.items():
        if isinstance(senal, pd.Series):
            # Última observación válida
            valores = senal.dropna()
        else:
            valores = senal
        
        mu = valores.mean()
        sigma = valores.std()
        z = (valores - mu) / sigma if sigma > 0 else valores * 0
        senales_norm[nombre] = z
    
    return pd.DataFrame(senales_norm)

# Señales actuales
senales = {
    'momentum': mom_actual,
    'vol_63d': -vol_actual_63d,  # Negativo porque queremos baja vol
    'beta': -betas,  # Negativo para favorecer baja beta
    'sharpe_hist': stats['sharpe_historico']
}

senales_norm = normalizar_senales(senales)
print(senales_norm.head())
```

## PASO 3.5: CONSTRUCCIÓN MATRIZ X
```python
def construir_matriz_caracteristicas(senales_norm):
    \"\"\"
    Matriz X (50 × K) de características normalizadas
    Cada fila = activo, cada columna = factor
    \"\"\"
    X = senales_norm.values  # (50, K)
    nombres_factores = senales_norm.columns.tolist()
    
    print(f"Matriz X shape: {X.shape}")
    print(f"Factores: {nombres_factores}")
    
    return X, nombres_factores

X, nombres_factores = construir_matriz_caracteristicas(senales_norm)

# Verificar
print(f"\\nCaracterísticas de X:")
print(f"  Media por columna: {X.mean(axis=0)}")  # Debe ser ~0
print(f"  Std por columna: {X.std(axis=0)}")     # Debe ser ~1
```

## PASO 3.6: RANKING MULTIFACTORIAL
```python
def crear_ranking_multifactorial(senales_norm, pesos_factores=None):
    \"\"\"
    Combinar señales en ranking único
    Score = Σ peso_k × z_k
    \"\"\"
    if pesos_factores is None:
        # Pesos iguales por defecto
        pesos_factores = {col: 1.0 for col in senales_norm.columns}
    
    score_total = pd.Series(0, index=senales_norm.index)
    for factor, peso in pesos_factores.items():
        if factor in senales_norm.columns:
            score_total += peso * senales_norm[factor]
    
    # Normalizar score total
    score_total = (score_total - score_total.mean()) / score_total.std()
    
    return score_total.sort_values(ascending=False)

# Ranking con pesos iguales
ranking = crear_ranking_multifactorial(senales_norm)
print("Top 20 por Ranking Multifactorial:")
print(ranking.head(20))
```

## SALIDAS
✅ Señales de momentum calculadas
✅ Volatilidades rolling
✅ Betas vs mercado
✅ Señales normalizadas (z-scores)
✅ Matriz X (50 × K)
✅ Ranking multifactorial

**SIGUIENTE**: Módulo 4 - Optimización Avanzada
"""

# ==================== MÓDULO 4 ====================
modulo4 = """
# MÓDULO 4: OPTIMIZACIÓN MULTIFACTORIAL AVANZADA

## PREREQUISITO
Lee Notebook: TEMA 4.3 (Optimización Top-Down)
Fórmulas ID 37-41

## OBJETIVO
Optimización Top-Down con tracking de exposiciones

## PASO 4.1: DEFINIR EXPOSICIONES OBJETIVO
```python
# Exposiciones objetivo b*
exposiciones_objetivo = {
    'momentum': 0.5,      # Alta exposición a momentum
    'vol_63d': -0.3,      # Baja volatilidad
    'beta': 0.0,          # Neutral a beta (market neutral)
    'sharpe_hist': 0.4    # Alta exposición a Sharpe histórico
}

b_star = np.array([exposiciones_objetivo[f] for f in nombres_factores])
print("Exposiciones objetivo b*:", b_star)
```

## PASO 4.2: PESOS DE EXPOSICIÓN
```python
# Pesos W_k para cada factor
# Opción 1: Pesos iguales
W_k_uniform = np.ones(len(nombres_factores))

# Opción 2: Inverso de varianza
W_k_invvar = 1 / X.std(axis=0)**2
W_k_invvar = W_k_invvar / W_k_invvar.sum() * len(nombres_factores)  # Normalizar

print("Pesos de factores (inv-var):", dict(zip(nombres_factores, W_k_invvar)))
```

## PASO 4.3: OPTIMIZACIÓN TOP-DOWN
```python
def optimizar_topdown(mu, Sigma, rf, X, b_star, W_k,
                       lambda_riesgo=1.0, tau_rotacion=0.1, w_prev=None):
    \"\"\"
    min ||X^T w - b*||²_W + λ w^T Σ w + τ ||w - w_prev||²
    
    s.t. sum(w) + w_rf = 1
         w ≥ 0
         0 ≤ w_rf ≤ 0.1
    \"\"\"
    n, K = X.shape
    
    # Variables
    w = cp.Variable(n)
    w_rf = cp.Variable()
    
    # Término 1: Tracking de exposiciones
    # (X^T w - b*)^T W (X^T w - b*)
    exposicion = X.T @ w  # (K,)
    desviacion = exposicion - b_star
    W_matriz = np.diag(W_k)
    tracking = cp.quad_form(desviacion, W_matriz)
    
    # Término 2: Penalización por riesgo
    riesgo = cp.quad_form(w, Sigma)
    
    # Término 3: Penalización por rotación
    if w_prev is None:
        w_prev = np.ones(n) / n  # Equiponderada inicial
    rotacion = cp.sum_squares(w - w_prev)
    
    # Función objetivo
    objetivo = tracking + lambda_riesgo * riesgo + tau_rotacion * rotacion
    
    # Restricciones
    restricciones = [
        cp.sum(w) + w_rf == 1,
        w >= 0,
        w_rf >= 0,
        w_rf <= 0.1
    ]
    
    # Resolver
    problema = cp.Problem(cp.Minimize(objetivo), restricciones)
    problema.solve(solver=cp.ECOS)
    
    if problema.status != 'optimal':
        print(f"⚠️ Status: {problema.status}")
        return None
    
    # Calcular métricas
    w_opt = w.value
    w_rf_opt = w_rf.value
    mu_p = w_opt @ mu + w_rf_opt * rf
    sigma_p = np.sqrt(w_opt @ Sigma @ w_opt)
    sharpe_p = (mu_p - rf) / sigma_p
    
    # Exposiciones reales
    exposiciones_reales = X.T @ w_opt
    
    return {
        'w': w_opt,
        'w_rf': w_rf_opt,
        'rentabilidad': mu_p,
        'volatilidad': sigma_p,
        'sharpe': sharpe_p,
        'exposiciones_reales': exposiciones_reales,
        'exposiciones_objetivo': b_star,
        'tracking_error': np.sum((exposiciones_reales - b_star)**2)
    }

# Optimizar
cartera_topdown = optimizar_topdown(
    mu, Sigma, rf, X, b_star, W_k_invvar,
    lambda_riesgo=2.0, tau_rotacion=0.5
)

print(f"\\nCartera Top-Down:")
print(f"  Sharpe: {cartera_topdown['sharpe']:.4f}")
print(f"  Tracking Error: {cartera_topdown['tracking_error']:.4f}")
print(f"\\n  Exposiciones:")
for i, nombre in enumerate(nombres_factores):
    print(f"    {nombre:15s}: objetivo={b_star[i]:6.2f}, real={cartera_topdown['exposiciones_reales'][i]:6.2f}")
```

## PASO 4.4: ESTRATEGIAS ALTERNATIVAS
```python
# Estrategia 1: High Momentum + Low Vol
exp_mom_lowvol = b_star.copy()
exp_mom_lowvol[nombres_factores.index('momentum')] = 0.7
exp_mom_lowvol[nombres_factores.index('vol_63d')] = -0.5

cart_mom_lowvol = optimizar_topdown(mu, Sigma, rf, X, exp_mom_lowvol, W_k_invvar)

# Estrategia 2: Quality (high Sharpe)
exp_quality = np.zeros(len(nombres_factores))
exp_quality[nombres_factores.index('sharpe_hist')] = 0.8

cart_quality = optimizar_topdown(mu, Sigma, rf, X, exp_quality, W_k_invvar)

# Estrategia 3: Minimum Variance (solo penalizar riesgo)
cart_minvar = optimizar_topdown(mu, Sigma, rf, X, 
                                  np.zeros(len(nombres_factores)), W_k_invvar,
                                  lambda_riesgo=10.0, tau_rotacion=0.1)

# Comparar
print("\\n=== COMPARACIÓN DE ESTRATEGIAS ===")
estrategias = {
    'Max Sharpe (Markowitz)': cartera_max_sharpe,
    'Top-Down Multifactorial': cartera_topdown,
    'High Mom + Low Vol': cart_mom_lowvol,
    'Quality': cart_quality,
    'Min Variance': cart_minvar
}

for nombre, cart in estrategias.items():
    print(f"\\n{nombre}:")
    print(f"  Sharpe: {cart['sharpe']:.4f}")
    print(f"  Ret: {cart['rentabilidad'