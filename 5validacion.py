"""
5VALIDACION: VALIDACIÓN Y SELECCIÓN FINAL
==========================================

Este módulo valida las carteras optimizadas y calcula métricas finales
para seleccionar la mejor estrategia.

FUNCIONALIDADES:
- Validación de restricciones (long-only, suma=1, RF≤10%)
- Cálculo de métricas de cartera (Sharpe, concentración, diversificación)
- Comparación de estrategias
- Exportación de pesos finales

CÓMO FUNCIONA:
1. Valida que la cartera cumpla todas las restricciones
2. Calcula métricas de rendimiento (Sharpe, rentabilidad, volatilidad)
3. Calcula métricas de estructura (concentración, número de activos)
4. Compara múltiples estrategias y selecciona la mejor
5. Exporta los pesos finales en formato requerido

MÉTRICAS:
- Sharpe Ratio: (μp - rf) / σp
- Índice de Herfindahl: Σ w_i² (mide concentración)
- Número de activos: activos con peso > 1%
- Tracking error: error en exposiciones objetivo
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def validar_cartera(w, w_rf, nombres_activos=None, tolerancia=1e-6):
    """
    Valida que una cartera cumpla todas las restricciones.
    
    Parámetros:
    -----------
    w : np.array
        Pesos de activos riesgosos (N activos)
    w_rf : float
        Peso en renta fija
    nombres_activos : list, optional
        Nombres de activos (para mensajes de error)
    tolerancia : float
        Tolerancia numérica para validaciones
        
    Retorna:
    --------
    dict
        Diccionario con resultados de validación
        
    Explicación:
    ------------
    Valida las siguientes restricciones:
    1. Long-only: todos los pesos w_i >= 0
    2. Suma de pesos: sum(w) + w_rf = 1 (dentro de tolerancia)
    3. Renta fija: 0 <= w_rf <= 0.1
    4. Número de activos: len(w) == 50
    
    Si alguna validación falla, se reporta en el diccionario de resultados.
    """
    resultados = {
        'valida': True,
        'errores': [],
        'advertencias': []
    }
    
    # Validar long-only
    if np.any(w < -tolerancia):
        idx_negativos = np.where(w < -tolerancia)[0]
        resultados['valida'] = False
        if nombres_activos:
            activos_neg = [nombres_activos[i] for i in idx_negativos]
            resultados['errores'].append(f"Pesos negativos en: {activos_neg}")
        else:
            resultados['errores'].append(f"Pesos negativos en índices: {idx_negativos}")
    
    # Validar suma de pesos
    suma_total = np.sum(w) + w_rf
    if abs(suma_total - 1.0) > tolerancia:
        resultados['valida'] = False
        resultados['errores'].append(f"Suma de pesos = {suma_total:.8f} (debe ser 1.0)")
    
    # Validar renta fija
    if w_rf < -tolerancia or w_rf > 0.1 + tolerancia:
        resultados['valida'] = False
        resultados['errores'].append(f"Peso en RF = {w_rf:.8f} (debe estar en [0, 0.1])")
    
    # Validar número de activos
    if len(w) != 50:
        resultados['valida'] = False
        resultados['errores'].append(f"Número de activos = {len(w)} (debe ser 50)")
    
    # Advertencias (no críticas)
    if w_rf < 0:
        resultados['advertencias'].append(f"Peso en RF negativo: {w_rf:.8f}")
    
    if np.any(w > 0.5):
        idx_alto = np.where(w > 0.5)[0]
        resultados['advertencias'].append(f"Pesos muy altos (>50%) en índices: {idx_alto}")
    
    return resultados


def calcular_metricas_cartera(w, w_rf, mu, Sigma, rf):
    """
    Calcula métricas de rendimiento y estructura de la cartera.
    
    Parámetros:
    -----------
    w : np.array
        Pesos de activos riesgosos (N activos)
    w_rf : float
        Peso en renta fija
    mu : np.array
        Vector de rentabilidades esperadas anualizadas (N activos)
    Sigma : np.array
        Matriz de covarianza anualizada (N × N)
    rf : float
        Tasa libre de riesgo anual
        
    Retorna:
    --------
    dict
        Diccionario con todas las métricas
        
    Explicación:
    ------------
    Métricas de rendimiento:
    - Rentabilidad esperada: μp = w^T μ + w_rf * rf
    - Volatilidad: σp = sqrt(w^T Σ w)
    - Sharpe Ratio: (μp - rf) / σp
    
    Métricas de estructura:
    - Índice de Herfindahl: Σ w_i² (mide concentración, 0=diversificado, 1=concentrado)
    - Número de activos: activos con peso > 1%
    - Peso máximo: max(w_i)
    - Peso en RF: w_rf
    """
    # Métricas de rendimiento
    mu_p = w @ mu + w_rf * rf
    sigma_p = np.sqrt(w @ Sigma @ w)
    sharpe = (mu_p - rf) / sigma_p if sigma_p > 0 else 0
    
    # Métricas de estructura
    herfindahl = np.sum(w**2)  # Índice de concentración
    n_activos = np.sum(w > 0.01)  # Activos con peso > 1%
    peso_maximo = np.max(w)
    
    return {
        'rentabilidad': mu_p,
        'volatilidad': sigma_p,
        'sharpe': sharpe,
        'herfindahl': herfindahl,
        'n_activos': n_activos,
        'peso_maximo': peso_maximo,
        'peso_rf': w_rf
    }


def comparar_estrategias(estrategias_dict, nombres_activos=None):
    """
    Compara múltiples estrategias y genera tabla comparativa.
    
    Parámetros:
    -----------
    estrategias_dict : dict
        Diccionario {nombre_estrategia: dict_cartera}
        Cada dict_cartera debe tener 'w', 'w_rf', y opcionalmente 'mu', 'Sigma', 'rf'
    nombres_activos : list, optional
        Nombres de activos para exportación
        
    Retorna:
    --------
    pd.DataFrame
        Tabla comparativa de estrategias
        
    Explicación:
    ------------
    Compara todas las estrategias en:
    - Sharpe Ratio (métrica principal)
    - Rentabilidad esperada
    - Volatilidad
    - Concentración (Herfindahl)
    - Número de activos
    - Peso en RF
    
    Si las estrategias tienen 'mu', 'Sigma', 'rf', calcula métricas completas.
    Si no, solo reporta métricas básicas disponibles.
    """
    resultados = []
    
    for nombre, cartera in estrategias_dict.items():
        w = cartera['w']
        w_rf = cartera.get('w_rf', 0.0)
        
        # Calcular métricas básicas
        herfindahl = np.sum(w**2)
        n_activos = np.sum(w > 0.01)
        peso_maximo = np.max(w)
        
        resultado = {
            'estrategia': nombre,
            'sharpe': cartera.get('sharpe', np.nan),
            'rentabilidad': cartera.get('rentabilidad', np.nan),
            'volatilidad': cartera.get('volatilidad', np.nan),
            'herfindahl': herfindahl,
            'n_activos': n_activos,
            'peso_maximo': peso_maximo,
            'peso_rf': w_rf
        }
        
        # Si hay tracking error, agregarlo
        if 'tracking_error' in cartera:
            resultado['tracking_error'] = cartera['tracking_error']
        
        resultados.append(resultado)
    
    df_comparacion = pd.DataFrame(resultados)
    
    # Ordenar por Sharpe descendente
    if 'sharpe' in df_comparacion.columns:
        df_comparacion = df_comparacion.sort_values('sharpe', ascending=False)
    
    return df_comparacion


def exportar_pesos(w, nombres_activos=None, ruta_archivo=None):
    """
    Exporta los pesos de la cartera en formato requerido.
    
    Parámetros:
    -----------
    w : np.array
        Pesos de activos riesgosos (N activos)
    nombres_activos : list, optional
        Nombres de activos. Si None, usa 'asset1', 'asset2', ...
    ruta_archivo : str, optional
        Ruta para guardar CSV. Si None, solo retorna DataFrame.
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con pesos por activo
        
    Explicación:
    ------------
    Crea un DataFrame con los pesos de cada activo, ordenado por peso descendente.
    Este formato es el requerido para la entrega de la competencia.
    """
    if nombres_activos is None:
        nombres_activos = [f'asset{i+1}' for i in range(len(w))]
    
    df_pesos = pd.DataFrame({
        'activo': nombres_activos,
        'peso': w
    })
    
    # Ordenar por peso descendente
    df_pesos = df_pesos.sort_values('peso', ascending=False)
    
    # Guardar si se especifica ruta
    if ruta_archivo:
        df_pesos.to_csv(ruta_archivo, index=False)
        print(f"Pesos exportados a: {ruta_archivo}")
    
    return df_pesos


def seleccionar_mejor_estrategia(estrategias_dict, criterio='sharpe'):
    """
    Selecciona la mejor estrategia según un criterio.
    
    Parámetros:
    -----------
    estrategias_dict : dict
        Diccionario {nombre_estrategia: dict_cartera}
    criterio : str
        Criterio de selección: 'sharpe', 'rentabilidad', 'volatilidad'
        
    Retorna:
    --------
    tuple
        (nombre_mejor, dict_cartera_mejor)
        
    Explicación:
    ------------
    Selecciona la estrategia con mejor valor según el criterio:
    - 'sharpe': máximo Sharpe Ratio
    - 'rentabilidad': máxima rentabilidad
    - 'volatilidad': mínima volatilidad (menor riesgo)
    """
    mejor_nombre = None
    mejor_valor = None
    mejor_cartera = None
    
    for nombre, cartera in estrategias_dict.items():
        if criterio not in cartera:
            continue
        
        valor = cartera[criterio]
        
        if mejor_valor is None:
            mejor_nombre = nombre
            mejor_valor = valor
            mejor_cartera = cartera
        else:
            if criterio == 'volatilidad':
                # Para volatilidad, queremos mínimo
                if valor < mejor_valor:
                    mejor_nombre = nombre
                    mejor_valor = valor
                    mejor_cartera = cartera
            else:
                # Para Sharpe y rentabilidad, queremos máximo
                if valor > mejor_valor:
                    mejor_nombre = nombre
                    mejor_valor = valor
                    mejor_cartera = cartera
    
    return mejor_nombre, mejor_cartera
