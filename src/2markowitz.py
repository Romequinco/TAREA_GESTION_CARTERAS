"""
2MARKOWITZ: OPTIMIZACIÓN CLÁSICA DE MARKOWITZ
==============================================

Este módulo implementa las técnicas clásicas de optimización de carteras
basadas en la teoría de Markowitz.

FUNCIONALIDADES:
- Optimización de Markowitz con parámetro de aversión al riesgo (λ)
- Optimización directa del Sharpe Ratio máximo
- Construcción de la frontera eficiente
- Análisis de sensibilidad temporal

CÓMO FUNCIONA:
1. Markowitz con λ: Maximiza E(Rp) - λ * Var(Rp) sujeto a restricciones
2. Máximo Sharpe: Minimiza varianza sujeto a rentabilidad objetivo = 1
3. Frontera eficiente: Encuentra carteras de mínima varianza para cada rentabilidad objetivo
4. Análisis de sensibilidad: Evalúa cómo cambian los resultados con diferentes ventanas temporales

TEORÍA:
- Función objetivo Markowitz: max w^T μ - λ w^T Σ w
- Sharpe Ratio: (μp - rf) / σp
- Frontera eficiente: conjunto de carteras con máxima rentabilidad para cada nivel de riesgo
"""

import numpy as np
import pandas as pd
import cvxpy as cp
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


def optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param):
    """
    Optimiza cartera usando función objetivo de Markowitz con parámetro λ.
    
    Parámetros:
    -----------
    mu : np.array
        Vector de rentabilidades esperadas anualizadas (N activos)
    Sigma : np.array
        Matriz de covarianza anualizada (N × N)
    rf : float
        Tasa libre de riesgo anual
    lambda_param : float
        Parámetro de aversión al riesgo (mayor λ = más aversión)
        
    Retorna:
    --------
    dict
        Diccionario con pesos óptimos, peso en RF, Sharpe, rentabilidad y volatilidad
        
    Explicación:
    ------------
    Resuelve: max w^T μ + w_rf * rf - λ * w^T Σ w
    
    Sujeto a:
    - sum(w) + w_rf = 1 (inversión completa)
    - w >= 0 (long-only)
    - w_rf >= 0 y w_rf <= 0.1 (RF máximo 10%)
    
    El parámetro λ controla el trade-off entre rentabilidad y riesgo:
    - λ pequeño: prioriza rentabilidad (cartera más riesgosa)
    - λ grande: prioriza reducir riesgo (cartera más conservadora)
    """
    n = len(mu)
    w = cp.Variable(n)
    w_rf = cp.Variable()
    
    # Función objetivo: rentabilidad - λ * riesgo
    rentabilidad = w @ mu + w_rf * rf
    riesgo = cp.quad_form(w, Sigma)
    objetivo = rentabilidad - lambda_param * riesgo
    
    # Restricciones
    restricciones = [
        cp.sum(w) + w_rf == 1,
        w >= 0,
        w_rf >= 0,
        w_rf <= 0.1
    ]
    
    # Resolver
    problema = cp.Problem(cp.Maximize(objetivo), restricciones)
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
    sharpe = (mu_p - rf) / sigma_p if sigma_p > 0 else 0
    
    return {
        'w': w_opt,
        'w_rf': w_rf_opt,
        'sharpe': sharpe,
        'rentabilidad': mu_p,
        'volatilidad': sigma_p
    }


def optimizar_sharpe_maximo(mu, Sigma, rf):
    """
    Optimiza cartera para maximizar el Sharpe Ratio directamente.
    
    Parámetros:
    -----------
    mu : np.array
        Vector de rentabilidades esperadas anualizadas (N activos)
    Sigma : np.array
        Matriz de covarianza anualizada (N × N)
    rf : float
        Tasa libre de riesgo anual
        
    Retorna:
    --------
    dict
        Diccionario con pesos óptimos, peso en RF, Sharpe, rentabilidad y volatilidad
        
    Explicación:
    ------------
    El problema de máximo Sharpe es no-lineal, pero se puede reformular como:
    min y^T Σ y  sujeto a y^T μ + y_rf * rf = 1, y >= 0, y_rf >= 0
    
    Luego normalizamos: w = y / sum(y + y_rf)
    
    Esta formulación evita la no-linealidad del Sharpe Ratio (μp - rf) / σp
    y permite usar optimización cuadrática convexa.
    
    Si después de normalizar w_rf > 0.1, se ajusta al límite y se renormaliza.
    """
    n = len(mu)
    y = cp.Variable(n)
    y_rf = cp.Variable()
    
    # Reformulación: minimizar varianza sujeto a rentabilidad = 1
    objetivo = cp.quad_form(y, Sigma)
    restricciones = [
        y @ mu + y_rf * rf == 1,
        y >= 0,
        y_rf >= 0
    ]
    
    problema = cp.Problem(cp.Minimize(objetivo), restricciones)
    problema.solve(solver=cp.ECOS, verbose=False)
    
    if problema.status != 'optimal':
        print(f"ADVERTENCIA: Status del problema: {problema.status}")
        return None
    
    # Normalizar para que sumen 1
    suma = np.sum(y.value) + y_rf.value
    if suma <= 0:
        print("ERROR: Suma de pesos no positiva")
        return None
    
    w_opt = y.value / suma
    w_rf_opt = y_rf.value / suma
    
    # Ajustar si w_rf > 0.1
    if w_rf_opt > 0.1:
        w_rf_opt = 0.1
        w_opt = w_opt * (1 - w_rf_opt) / np.sum(w_opt)
    
    # Calcular métricas
    mu_p = w_opt @ mu + w_rf_opt * rf
    sigma_p = np.sqrt(w_opt @ Sigma @ w_opt)
    sharpe = (mu_p - rf) / sigma_p if sigma_p > 0 else 0
    
    return {
        'w': w_opt,
        'w_rf': w_rf_opt,
        'sharpe': sharpe,
        'rentabilidad': mu_p,
        'volatilidad': sigma_p
    }


def construir_frontera_eficiente(mu, Sigma, rf, n_puntos=50):
    """
    Construye la frontera eficiente de carteras.
    
    Parámetros:
    -----------
    mu : np.array
        Vector de rentabilidades esperadas anualizadas (N activos)
    Sigma : np.array
        Matriz de covarianza anualizada (N × N)
    rf : float
        Tasa libre de riesgo anual
    n_puntos : int
        Número de puntos en la frontera
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con rentabilidad, volatilidad y Sharpe de cada punto
        
    Explicación:
    ------------
    Para cada rentabilidad objetivo μ_target en un rango [rf, μ_max]:
    1. Resuelve: min w^T Σ w  sujeto a w^T μ + w_rf * rf = μ_target
    2. Obtiene la volatilidad mínima σ_min para esa rentabilidad
    3. Calcula el Sharpe: (μ_target - rf) / σ_min
    
    La frontera eficiente muestra el trade-off óptimo entre riesgo y rentabilidad.
    Todas las carteras en la frontera son eficientes (máxima rentabilidad para su nivel de riesgo).
    """
    mu_min = rf
    mu_max = mu.max() * 0.95  # Evitar extremos
    mu_targets = np.linspace(mu_min, mu_max, n_puntos)
    
    fronteras = []
    
    for mu_t in mu_targets:
        n = len(mu)
        w = cp.Variable(n)
        w_rf = cp.Variable()
        
        # Minimizar varianza sujeto a rentabilidad objetivo
        objetivo = cp.quad_form(w, Sigma)
        restricciones = [
            w @ mu + w_rf * rf == mu_t,
            cp.sum(w) + w_rf == 1,
            w >= 0,
            w_rf >= 0,
            w_rf <= 0.1
        ]
        
        problema = cp.Problem(cp.Minimize(objetivo), restricciones)
        problema.solve(solver=cp.ECOS, verbose=False)
        
        if problema.status == 'optimal':
            sigma_p = np.sqrt(objetivo.value)
            sharpe = (mu_t - rf) / sigma_p if sigma_p > 0 else 0
            
            fronteras.append({
                'rentabilidad': mu_t,
                'volatilidad': sigma_p,
                'sharpe': sharpe
            })
    
    return pd.DataFrame(fronteras)


def visualizar_frontera_eficiente(frontera_df, cartera_max_sharpe=None, ruta_guardado=None):
    """
    Visualiza la frontera eficiente.
    
    Parámetros:
    -----------
    frontera_df : pd.DataFrame
        DataFrame con puntos de la frontera eficiente
    cartera_max_sharpe : dict, optional
        Diccionario con información de la cartera de máximo Sharpe
    ruta_guardado : str, optional
        Ruta para guardar la figura
        
    Explicación:
    ------------
    Crea un gráfico riesgo-rentabilidad mostrando:
    - La frontera eficiente (curva)
    - La cartera de máximo Sharpe (punto destacado)
    - Ejes en porcentaje para mejor interpretación
    """
    plt.figure(figsize=(12, 8))
    
    # Frontera eficiente
    plt.plot(frontera_df['volatilidad'] * 100, 
             frontera_df['rentabilidad'] * 100, 
             'b-', linewidth=2, label='Frontera Eficiente')
    
    # Cartera máximo Sharpe
    if cartera_max_sharpe:
        plt.scatter(cartera_max_sharpe['volatilidad'] * 100,
                   cartera_max_sharpe['rentabilidad'] * 100,
                   s=300, c='red', marker='*', 
                   label=f"Max Sharpe ({cartera_max_sharpe['sharpe']:.3f})",
                   zorder=5, edgecolors='black', linewidths=1.5)
    
    plt.xlabel('Volatilidad Anualizada (%)', fontsize=12)
    plt.ylabel('Rentabilidad Esperada Anualizada (%)', fontsize=12)
    plt.title('Frontera Eficiente de Carteras', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if ruta_guardado:
        plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
    
    return plt.gcf()


def analizar_sensibilidad_temporal(retornos, rf, ventanas=[252, 504, 756, None]):
    """
    Analiza la sensibilidad de la cartera óptima a diferentes ventanas temporales.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    rf : float
        Tasa libre de riesgo anual
    ventanas : list
        Lista de ventanas en días (None = todos los datos)
        
    Retorna:
    --------
    pd.DataFrame
        Resultados de optimización para cada ventana
        
    Explicación:
    ------------
    Para cada ventana temporal:
    1. Calcula μ y Σ usando solo los últimos N días
    2. Optimiza cartera de máximo Sharpe
    3. Calcula métricas (Sharpe, concentración)
    
    Esto permite evaluar la robustez de la estrategia: si los resultados
    cambian mucho con la ventana, la estrategia puede ser inestable.
    """
    resultados = []
    
    for ventana in ventanas:
        # Calcular estadísticas para esta ventana
        if ventana is None:
            datos = retornos
            nombre_ventana = 'Completa'
        else:
            datos = retornos.iloc[-ventana:]
            nombre_ventana = f'{ventana}d'
        
        mu_v = datos.mean().values * 252
        Sigma_v = datos.cov().values * 252
        
        # Optimizar
        cartera = optimizar_sharpe_maximo(mu_v, Sigma_v, rf)
        
        if cartera:
            # Índice de concentración (Herfindahl)
            concentracion = np.sum(cartera['w']**2)
            
            # Número de activos con peso > 1%
            n_activos = np.sum(cartera['w'] > 0.01)
            
            resultados.append({
                'ventana': nombre_ventana,
                'sharpe': cartera['sharpe'],
                'rentabilidad': cartera['rentabilidad'],
                'volatilidad': cartera['volatilidad'],
                'concentracion': concentracion,
                'n_activos': n_activos,
                'peso_rf': cartera['w_rf']
            })
    
    return pd.DataFrame(resultados)
