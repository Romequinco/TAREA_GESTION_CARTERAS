"""
3FACTORES: CONSTRUCCIÓN DE FACTORES Y SEÑALES
==============================================

Este módulo construye señales de inversión basadas en factores como momentum,
volatilidad y beta para usar en estrategias multifactoriales.

FUNCIONALIDADES:
- Cálculo de momentum 12-2 (retornos acumulados de 12 meses excluyendo el último mes)
- Cálculo de volatilidad rolling en múltiples ventanas
- Cálculo de betas vs mercado (índice equiponderado)
- Normalización de señales mediante z-scores
- Construcción de matriz de características X (activos × factores)
- Ranking multifactorial combinando señales

CÓMO FUNCIONA:
1. Momentum 12-2: Acumula retornos de t-252 a t-21 (evita reversión a corto plazo)
2. Volatilidad rolling: Calcula desviación estándar móvil anualizada
3. Beta: Covarianza con mercado / Varianza del mercado
4. Normalización: z = (señal - μ) / σ (cross-sectional)
5. Matriz X: Cada fila es un activo, cada columna es un factor normalizado
6. Ranking: Combina señales con pesos para crear score único

TEORÍA:
- Momentum: MOM_{i,t} = ∏(j=2 to 12)(1 + r_{i,t-j}) - 1
- Beta: β_i = Cov(r_i, r_M) / Var(r_M)
- Z-score: z_{i,k} = (señal_{i,k} - μ_k) / σ_k
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def calcular_momentum_12_2(retornos):
    """
    Calcula el momentum 12-2 para cada activo.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
        
    Retorna:
    --------
    pd.DataFrame
        Momentum 12-2 para cada activo en cada fecha
        
    Explicación:
    ------------
    Momentum 12-2 acumula retornos de los últimos 12 meses excluyendo el último mes.
    En días: desde t-252 hasta t-21 (231 días ≈ 12 meses menos 1 mes).
    
    Fórmula: MOM_{i,t} = ∏(j=2 to 12)(1 + r_{i,t-j}) - 1
    
    Se excluye el último mes (t-21 a t-1) para evitar el efecto de reversión
    a corto plazo (short-term reversal), que es un fenómeno empírico donde
    los activos con muy buenos retornos recientes tienden a revertir.
    
    El momentum es una señal de continuación de tendencia.
    """
    momentum = pd.DataFrame(index=retornos.index, columns=retornos.columns)
    
    # Necesitamos al menos 252 días de historia
    for i in range(252, len(retornos)):
        # Retornos de t-252 a t-21 (evitar t-1 por reversión)
        ret_periodo = retornos.iloc[i-252:i-21]
        
        # Acumular retornos: (1 + r1) * (1 + r2) * ... * (1 + rn) - 1
        mom = (1 + ret_periodo).prod() - 1
        momentum.iloc[i] = mom
    
    return momentum


def calcular_volatilidad_rolling(retornos, ventanas=[21, 63, 252]):
    """
    Calcula volatilidad rolling en múltiples ventanas.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    ventanas : list
        Lista de ventanas en días (default: [21, 63, 252] = 1 mes, 3 meses, 1 año)
        
    Retorna:
    --------
    pd.DataFrame
        Volatilidades anualizadas para cada ventana
        
    Explicación:
    ------------
    Para cada ventana, calcula la desviación estándar móvil de los retornos
    y la anualiza multiplicando por sqrt(252).
    
    Ventanas comunes:
    - 21 días: volatilidad de corto plazo (1 mes)
    - 63 días: volatilidad de medio plazo (3 meses)
    - 252 días: volatilidad de largo plazo (1 año)
    
    La volatilidad es una medida de riesgo: activos con menor volatilidad
    son preferibles (ceteris paribus) porque ofrecen mejor ratio riesgo/rentabilidad.
    """
    vols = {}
    for v in ventanas:
        # Desviación estándar rolling anualizada
        vols[f'vol_{v}d'] = retornos.rolling(v).std() * np.sqrt(252)
    
    return pd.DataFrame(vols, index=retornos.index)


def calcular_betas(retornos, ventana=252):
    """
    Calcula betas de cada activo respecto al mercado.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    ventana : int
        Ventana en días para calcular beta (default: 252 = 1 año)
        
    Retorna:
    --------
    pd.Series
        Beta de cada activo
        
    Explicación:
    ------------
    Beta mide la sensibilidad del activo al mercado:
    β_i = Cov(r_i, r_M) / Var(r_M)
    
    Donde el mercado es un índice equiponderado de todos los activos:
    r_M = (1/N) * Σ r_i
    
    Interpretación:
    - β > 1: Activo más volátil que el mercado (amplifica movimientos)
    - β = 1: Activo se mueve igual que el mercado
    - β < 1: Activo menos volátil que el mercado (amortigua movimientos)
    - β < 0: Activo se mueve en dirección opuesta al mercado (raro)
    
    Para estrategias de bajo riesgo, preferimos activos con β < 1.
    """
    # Índice mercado equiponderado
    indice_mercado = retornos.mean(axis=1)
    
    betas = {}
    
    for col in retornos.columns:
        # Usar últimos 'ventana' días
        datos = retornos[[col]].iloc[-ventana:]
        mercado = indice_mercado.iloc[-ventana:]
        
        # Calcular covarianza y varianza
        cov = np.cov(datos[col], mercado)[0, 1]
        var_m = np.var(mercado)
        
        # Beta = Cov / Var
        beta = cov / var_m if var_m > 0 else 1.0
        betas[col] = beta
    
    return pd.Series(betas)


def normalizar_senales(senales_dict):
    """
    Normaliza señales mediante z-scores cross-sectional.
    
    Parámetros:
    -----------
    senales_dict : dict
        Diccionario {nombre_señal: valores} donde valores es pd.Series o np.array
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con señales normalizadas (activos × señales)
        
    Explicación:
    ------------
    Normalización z-score: z_{i,k} = (señal_{i,k} - μ_k) / σ_k
    
    Donde:
    - μ_k: media de la señal k entre todos los activos
    - σ_k: desviación estándar de la señal k entre todos los activos
    
    Esta normalización:
    1. Centra las señales en 0 (media = 0)
    2. Escala a desviación estándar = 1
    3. Permite combinar señales de diferentes escalas (momentum %, volatilidad %, etc.)
    4. Facilita la interpretación: valores positivos = por encima de la media
    
    Si la señal es una Serie temporal, usa la última observación válida.
    """
    senales_norm = {}
    
    for nombre, senal in senales_dict.items():
        if isinstance(senal, pd.Series):
            # Si es Serie temporal, usar última observación válida
            valores = senal.dropna()
            if len(valores) == 0:
                # Si no hay valores válidos, usar todos
                valores = senal
            else:
                # Usar último valor no-nulo
                valores = valores.iloc[-1:] if hasattr(valores, 'iloc') else valores
        else:
            valores = senal
        
        # Convertir a array si es necesario
        if isinstance(valores, pd.Series):
            valores = valores.values
        
        # Calcular media y desviación estándar
        mu = np.mean(valores)
        sigma = np.std(valores)
        
        # Normalizar
        if sigma > 0:
            z = (valores - mu) / sigma
        else:
            z = valores * 0  # Si no hay variación, z = 0
        
        # Guardar como Serie para mantener índices
        if isinstance(senal, pd.Series):
            senales_norm[nombre] = pd.Series(z, index=senal.index)
        else:
            senales_norm[nombre] = z
    
    return pd.DataFrame(senales_norm)


def construir_matriz_caracteristicas(senales_norm):
    """
    Construye la matriz de características X para optimización multifactorial.
    
    Parámetros:
    -----------
    senales_norm : pd.DataFrame
        DataFrame con señales normalizadas (activos × factores)
        
    Retorna:
    --------
    tuple
        (X, nombres_factores) donde X es np.array (N × K) y nombres_factores es list
        
    Explicación:
    ------------
    La matriz X tiene:
    - Filas: activos (N = 50)
    - Columnas: factores (K = número de señales)
    - Valores: z-scores normalizados
    
    Esta matriz se usa en optimización Top-Down para controlar las exposiciones
    de la cartera a cada factor. La exposición de la cartera al factor k es:
    b_k(w) = (X^T w)_k = Σ_i w_i * X_{i,k}
    
    Verificar que:
    - Media por columna ≈ 0 (normalización correcta)
    - Std por columna ≈ 1 (escalado correcto)
    """
    X = senales_norm.values  # (N activos, K factores)
    nombres_factores = senales_norm.columns.tolist()
    
    return X, nombres_factores


def crear_ranking_multifactorial(senales_norm, pesos_factores=None):
    """
    Crea un ranking multifactorial combinando señales.
    
    Parámetros:
    -----------
    senales_norm : pd.DataFrame
        DataFrame con señales normalizadas (activos × factores)
    pesos_factores : dict, optional
        Diccionario {nombre_factor: peso}. Si None, usa pesos iguales.
        
    Retorna:
    --------
    pd.Series
        Score total por activo, ordenado descendente
        
    Explicación:
    ------------
    Combina señales normalizadas en un score único:
    Score_i = Σ_k peso_k * z_{i,k}
    
    Luego normaliza el score total para que tenga media 0 y std 1.
    
    El ranking resultante ordena activos de mejor a peor según el score combinado.
    Activos con mayor score son mejores candidatos para la cartera.
    
    Ejemplo de uso:
    - Momentum positivo: favorece activos con buen rendimiento reciente
    - Volatilidad negativa: favorece activos con bajo riesgo
    - Beta negativa: favorece activos con baja sensibilidad al mercado
    """
    if pesos_factores is None:
        # Pesos iguales por defecto
        pesos_factores = {col: 1.0 for col in senales_norm.columns}
    
    # Inicializar score total
    score_total = pd.Series(0.0, index=senales_norm.index)
    
    # Combinar señales ponderadas
    for factor, peso in pesos_factores.items():
        if factor in senales_norm.columns:
            score_total += peso * senales_norm[factor]
    
    # Normalizar score total (opcional, para mejor interpretación)
    mu_score = score_total.mean()
    sigma_score = score_total.std()
    if sigma_score > 0:
        score_total = (score_total - mu_score) / sigma_score
    
    return score_total.sort_values(ascending=False)
