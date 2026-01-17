"""
4MULTIFACTORIAL: OPTIMIZACIÓN MULTIFACTORIAL AVANZADA
======================================================

Este módulo implementa optimización Top-Down para construir carteras con
exposiciones objetivo a factores específicos.

FUNCIONALIDADES:
- Optimización Top-Down con tracking de exposiciones
- Control de exposiciones objetivo a factores (momentum, volatilidad, beta, etc.)
- Penalización por riesgo y rotación
- Estrategias alternativas (High Momentum + Low Vol, Quality, Min Variance)

CÓMO FUNCIONA:
1. Define exposiciones objetivo b* a cada factor
2. Calcula pesos W_k para cada factor (inverso de varianza)
3. Optimiza: min ||X^T w - b*||²_W + λ w^T Σ w + τ ||w - w_prev||²
4. Sujeto a restricciones de cartera (long-only, suma=1, RF≤10%)

TEORÍA:
- Exposición de cartera: b(w) = X^T w ∈ ℝ^K
- Tracking error: ||X^T w - b*||²_W = Σ_k W_k ((X^T w)_k - b*_k)²
- Pesos de exposición: W_k = 1 / σ²_k (inverso de varianza)
- Función objetivo: tracking + λ*riesgo + τ*rotación
"""

import numpy as np
import pandas as pd
import cvxpy as cp
import warnings
warnings.filterwarnings('ignore')


def calcular_pesos_exposicion(X, metodo='inverso_varianza'):
    """
    Calcula pesos W_k para cada factor en el tracking de exposiciones.
    
    Parámetros:
    -----------
    X : np.array
        Matriz de características (N activos × K factores)
    metodo : str
        Método de cálculo: 'uniforme' o 'inverso_varianza'
        
    Retorna:
    --------
    np.array
        Vector de pesos W_k (K factores)
        
    Explicación:
    ------------
    Los pesos W_k determinan la importancia de cada factor en el tracking error.
    
    Métodos:
    1. 'uniforme': W_k = 1 para todos (todos los factores igual de importantes)
    2. 'inverso_varianza': W_k = 1 / σ²_k (factores con menor varianza tienen más peso)
    
    El método de inverso de varianza es preferible porque:
    - Factores más estables (baja varianza) son más confiables
    - Factores más volátiles (alta varianza) tienen menos peso
    - Equivale a usar mínimos cuadrados ponderados (WLS)
    """
    K = X.shape[1]
    
    if metodo == 'uniforme':
        W_k = np.ones(K)
    elif metodo == 'inverso_varianza':
        # Varianza de cada factor (columna)
        varianzas = np.var(X, axis=0)
        # Evitar división por cero
        varianzas = np.maximum(varianzas, 1e-8)
        W_k = 1 / varianzas
        # Normalizar para que la suma sea K (mantener escala)
        W_k = W_k / W_k.sum() * K
    else:
        raise ValueError(f"Método desconocido: {metodo}")
    
    return W_k


def optimizar_topdown(mu, Sigma, rf, X, b_star, W_k,
                       lambda_riesgo=1.0, tau_rotacion=0.1, w_prev=None):
    """
    Optimiza cartera usando enfoque Top-Down con tracking de exposiciones.
    
    Parámetros:
    -----------
    mu : np.array
        Vector de rentabilidades esperadas anualizadas (N activos)
    Sigma : np.array
        Matriz de covarianza anualizada (N × N)
    rf : float
        Tasa libre de riesgo anual
    X : np.array
        Matriz de características (N activos × K factores)
    b_star : np.array
        Exposiciones objetivo (K factores)
    W_k : np.array
        Pesos de exposición (K factores)
    lambda_riesgo : float
        Parámetro de penalización por riesgo (mayor = más aversión al riesgo)
    tau_rotacion : float
        Parámetro de penalización por rotación (mayor = menos cambios)
    w_prev : np.array, optional
        Pesos previos de la cartera (para penalizar rotación)
        
    Retorna:
    --------
    dict
        Diccionario con pesos óptimos, métricas y exposiciones reales
        
    Explicación:
    ------------
    Resuelve el problema de optimización:
    
    min ||X^T w - b*||²_W + λ w^T Σ w + τ ||w - w_prev||²
    
    Sujeto a:
    - sum(w) + w_rf = 1
    - w >= 0 (long-only)
    - w_rf >= 0 y w_rf <= 0.1
    
    Donde:
    - ||X^T w - b*||²_W: tracking error de exposiciones (objetivo principal)
    - λ w^T Σ w: penalización por riesgo de la cartera
    - τ ||w - w_prev||²: penalización por rotación (cambios respecto a cartera anterior)
    
    El tracking error mide qué tan bien la cartera logra las exposiciones objetivo.
    Si b*_k > 0, queremos alta exposición al factor k.
    Si b*_k < 0, queremos baja exposición (o exposición negativa si es posible).
    Si b*_k = 0, queremos neutralidad al factor k.
    """
    n, K = X.shape
    
    # Variables de decisión
    w = cp.Variable(n)
    w_rf = cp.Variable()
    
    # Término 1: Tracking de exposiciones
    # b(w) = X^T w es la exposición real de la cartera
    exposicion = X.T @ w  # (K,)
    desviacion = exposicion - b_star  # (K,)
    
    # Matriz diagonal de pesos W
    W_matriz = np.diag(W_k)
    
    # Tracking error: (X^T w - b*)^T W (X^T w - b*)
    tracking = cp.quad_form(desviacion, W_matriz)
    
    # Término 2: Penalización por riesgo
    riesgo = cp.quad_form(w, Sigma)
    
    # Término 3: Penalización por rotación
    if w_prev is None:
        # Si no hay cartera previa, usar equiponderada como referencia
        w_prev = np.ones(n) / n
    rotacion = cp.sum_squares(w - w_prev)
    
    # Función objetivo combinada
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
    problema.solve(solver=cp.ECOS, verbose=False)
    
    if problema.status != 'optimal':
        print(f"ADVERTENCIA: Status del problema: {problema.status}")
        return None
    
    # Extraer resultados
    w_opt = w.value
    w_rf_opt = w_rf.value
    
    # Calcular métricas
    mu_p = w_opt @ mu + w_rf_opt * rf
    sigma_p = np.sqrt(w_opt @ Sigma @ w_opt)
    sharpe_p = (mu_p - rf) / sigma_p if sigma_p > 0 else 0
    
    # Exposiciones reales
    exposiciones_reales = X.T @ w_opt
    
    # Tracking error
    tracking_error = np.sum(W_k * (exposiciones_reales - b_star)**2)
    
    return {
        'w': w_opt,
        'w_rf': w_rf_opt,
        'rentabilidad': mu_p,
        'volatilidad': sigma_p,
        'sharpe': sharpe_p,
        'exposiciones_reales': exposiciones_reales,
        'exposiciones_objetivo': b_star,
        'tracking_error': tracking_error
    }


def crear_estrategia_momentum_lowvol(nombres_factores, b_star_base=None):
    """
    Crea configuración de exposiciones para estrategia High Momentum + Low Vol.
    
    Parámetros:
    -----------
    nombres_factores : list
        Lista de nombres de factores
    b_star_base : np.array, optional
        Exposiciones base (si None, crea desde cero)
        
    Retorna:
    --------
    np.array
        Vector de exposiciones objetivo
        
    Explicación:
    ------------
    Esta estrategia busca:
    - Alta exposición a momentum (activos con buen rendimiento reciente)
    - Baja exposición a volatilidad (activos con bajo riesgo)
    - Neutralidad a otros factores
    
    Es una estrategia de "momentum de calidad": activos con buen rendimiento
    pero bajo riesgo.
    """
    if b_star_base is None:
        b_star = np.zeros(len(nombres_factores))
    else:
        b_star = b_star_base.copy()
    
    # Alta exposición a momentum
    if 'momentum' in nombres_factores:
        idx = nombres_factores.index('momentum')
        b_star[idx] = 0.7
    
    # Baja exposición a volatilidad (negativo porque queremos baja vol)
    if 'vol_63d' in nombres_factores:
        idx = nombres_factores.index('vol_63d')
        b_star[idx] = -0.5
    
    return b_star


def crear_estrategia_quality(nombres_factores):
    """
    Crea configuración de exposiciones para estrategia Quality.
    
    Parámetros:
    -----------
    nombres_factores : list
        Lista de nombres de factores
        
    Retorna:
    --------
    np.array
        Vector de exposiciones objetivo
        
    Explicación:
    ------------
    Estrategia Quality busca activos con alto Sharpe histórico, es decir,
    activos que han ofrecido buena rentabilidad ajustada por riesgo en el pasado.
    
    Esta estrategia asume que el Sharpe histórico es un buen predictor del
    Sharpe futuro (persistencia de calidad).
    """
    b_star = np.zeros(len(nombres_factores))
    
    # Alta exposición a Sharpe histórico
    if 'sharpe_hist' in nombres_factores:
        idx = nombres_factores.index('sharpe_hist')
        b_star[idx] = 0.8
    
    return b_star


def crear_estrategia_min_variance(nombres_factores):
    """
    Crea configuración de exposiciones para estrategia Minimum Variance.
    
    Parámetros:
    -----------
    nombres_factores : list
        Lista de nombres de factores
        
    Retorna:
    --------
    np.array
        Vector de exposiciones objetivo (todos ceros)
        
    Explicación:
    ------------
    Estrategia Minimum Variance ignora las exposiciones a factores y se enfoca
    únicamente en minimizar el riesgo de la cartera.
    
    En la optimización, esto se logra usando:
    - b_star = 0 (sin preferencia por factores)
    - lambda_riesgo alto (máxima penalización por riesgo)
    
    Esta estrategia es útil como benchmark de bajo riesgo.
    """
    return np.zeros(len(nombres_factores))
