import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')


def cargar_datos(ruta_retornos=None, ruta_benchmark=None, df_retornos=None, df_benchmark=None):
    """
    Carga datos de retornos y benchmark desde archivo CSV o DataFrames.
    
    Parámetros:
    -----------
    ruta_retornos : str, opcional
        Ruta del archivo CSV con retornos de activos.
    ruta_benchmark : str, opcional
        Ruta del archivo CSV con retornos del benchmark.
    df_retornos : pd.DataFrame, opcional
        DataFrame con retornos de activos (alternativa a CSV).
    df_benchmark : pd.DataFrame, opcional
        DataFrame con retornos del benchmark (alternativa a CSV).
    
    Retorna:
    --------
    datos_retornos : pd.DataFrame
        Retornos de los N activos (N x T).
    benchmark_retornos : pd.Series
        Retornos del benchmark (T,).
    """
    if df_retornos is not None:
        datos_retornos = df_retornos
    elif ruta_retornos is not None:
        datos_retornos = pd.read_csv(ruta_retornos, index_col=0)
    else:
        raise ValueError("Debe proporcionar ruta_retornos o df_retornos")
    
    if df_benchmark is not None:
        benchmark_retornos = df_benchmark.iloc[:, 0] if isinstance(df_benchmark, pd.DataFrame) else df_benchmark
    elif ruta_benchmark is not None:
        benchmark_df = pd.read_csv(ruta_benchmark, index_col=0)
        benchmark_retornos = benchmark_df.iloc[:, 0] if isinstance(benchmark_df, pd.DataFrame) else benchmark_df
    else:
        raise ValueError("Debe proporcionar ruta_benchmark o df_benchmark")
    
    if len(datos_retornos) != len(benchmark_retornos):
        raise ValueError("Retornos y benchmark deben tener el mismo número de observaciones")
    
    return datos_retornos, benchmark_retornos


def calcular_estadisticas(datos_retornos, benchmark_retornos):
    """
    Calcula medias, covarianzas y correlaciones necesarias para optimización.
    
    Parámetros:
    -----------
    datos_retornos : pd.DataFrame
        Retornos de activos (filas: períodos, columnas: activos).
    benchmark_retornos : pd.Series
        Retornos del benchmark (índice: períodos).
    
    Retorna:
    --------
    stats : dict
        Diccionario con:
        - mu : media de retornos (N,)
        - cov_matrix : matriz covarianza activos (N x N)
        - mu_benchmark : retorno promedio benchmark (escalar)
        - var_benchmark : varianza benchmark (escalar)
        - cov_activos_benchmark : covarianza activos-benchmark (N,)
    """
    mu = datos_retornos.mean().values
    cov_matrix = datos_retornos.cov().values
    mu_benchmark = benchmark_retornos.mean()
    var_benchmark = benchmark_retornos.var()
    
    cov_activos_benchmark = np.array([
        datos_retornos.iloc[:, i].cov(benchmark_retornos) 
        for i in range(datos_retornos.shape[1])
    ])
    
    stats = {
        'mu': mu,
        'cov_matrix': cov_matrix,
        'mu_benchmark': mu_benchmark,
        'var_benchmark': var_benchmark,
        'cov_activos_benchmark': cov_activos_benchmark
    }
    
    return stats


def calcular_excess_return(pesos, stats):
    """
    Calcula el retorno en exceso del portafolio vs benchmark.
    
    Parámetros:
    -----------
    pesos : np.array
        Vector de pesos (N,).
    stats : dict
        Diccionario con estadísticas (de calcular_estadisticas).
    
    Retorna:
    --------
    excess_return : float
        E[R_p - R_m].
    """
    mu = stats['mu']
    mu_benchmark = stats['mu_benchmark']
    return np.sum(pesos * mu) - mu_benchmark


def calcular_tracking_error(pesos, stats):
    """
    Calcula el tracking error anualizado del portafolio.
    
    Parámetros:
    -----------
    pesos : np.array
        Vector de pesos (N,).
    stats : dict
        Diccionario con estadísticas.
    
    Retorna:
    --------
    tracking_error : float
        sqrt(Var(R_p - R_m)) anualizado.
    """
    cov_matrix = stats['cov_matrix']
    cov_activos_benchmark = stats['cov_activos_benchmark']
    var_benchmark = stats['var_benchmark']
    
    var_excess = (np.dot(pesos, np.dot(cov_matrix, pesos)) - 
                  2 * np.dot(pesos, cov_activos_benchmark) + 
                  var_benchmark)
    
    tracking_error = np.sqrt(max(var_excess, 0))
    
    return tracking_error * np.sqrt(252)


def calcular_sharpe_relativo(pesos, stats):
    """
    Calcula el Sharpe ratio relativo del portafolio.
    
    Parámetros:
    -----------
    pesos : np.array
        Vector de pesos (N,).
    stats : dict
        Diccionario con estadísticas.
    
    Retorna:
    --------
    sharpe_relativo : float
        (E[R_p - R_m] / TE_anualizado).
    """
    excess_return = calcular_excess_return(pesos, stats)
    tracking_error = calcular_tracking_error(pesos, stats)
    
    if tracking_error == 0:
        return 0
    
    return (excess_return * 252) / tracking_error


def optimizar_tracking_error(datos_retornos, benchmark_retornos, verbose=True):
    """
    Optimiza un portafolio maximizando el Sharpe ratio relativo (tracking error).
    
    Parámetros:
    -----------
    datos_retornos : pd.DataFrame
        Retornos de activos.
    benchmark_retornos : pd.Series
        Retornos del benchmark.
    verbose : bool
        Si True, imprime información de optimización.
    
    Retorna:
    --------
    resultado : dict
        Diccionario con:
        - pesos : vector de pesos óptimos
        - retorno_esperado : retorno anual esperado del portafolio
        - tracking_error : tracking error anualizado
        - sharpe_relativo : Sharpe ratio relativo anualizado
        - excess_return : retorno en exceso anual
        - status : estado de la optimización
    """
    stats = calcular_estadisticas(datos_retornos, benchmark_retornos)
    n_activos = datos_retornos.shape[1]
    
    def funcion_objetivo_negativa(w):
        return -calcular_sharpe_relativo(w, stats)
    
    restricciones = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    limites = tuple((0, 1) for _ in range(n_activos))
    x0 = np.array([1.0 / n_activos] * n_activos)
    
    resultado_opt = minimize(
        funcion_objetivo_negativa,
        x0,
        method='SLSQP',
        bounds=limites,
        constraints=restricciones,
        options={'maxiter': 1000}
    )
    
    pesos_optimos = resultado_opt.x
    
    retorno_cartera = np.sum(pesos_optimos * stats['mu']) * 252
    tracking_error = calcular_tracking_error(pesos_optimos, stats)
    sharpe_relativo = calcular_sharpe_relativo(pesos_optimos, stats)
    excess_return = calcular_excess_return(pesos_optimos, stats) * 252
    
    if verbose:
        print('[OK] Optimizacion completada')
        print(f'Retorno esperado portafolio: {retorno_cartera:.4f} ({retorno_cartera*100:.2f}%)')
        print(f'Tracking error anualizado: {tracking_error:.4f} ({tracking_error*100:.2f}%)')
        print(f'Sharpe relativo: {sharpe_relativo:.4f}')
        print(f'Excess return: {excess_return:.4f} ({excess_return*100:.2f}%)')
        print(f'Retorno benchmark: {stats["mu_benchmark"]*252:.4f} ({stats["mu_benchmark"]*252*100:.2f}%)')
    
    return {
        'pesos': pesos_optimos,
        'retorno_esperado': retorno_cartera,
        'tracking_error': tracking_error,
        'sharpe_relativo': sharpe_relativo,
        'excess_return': excess_return,
        'status': 'success' if resultado_opt.success else 'failed',
        'stats': stats
    }


def calcular_performance_portafolio(datos_retornos, benchmark_retornos, pesos):
    """
    Calcula la serie temporal de retornos del portafolio y benchmark.
    
    Parámetros:
    -----------
    datos_retornos : pd.DataFrame
        Retornos diarios de activos.
    benchmark_retornos : pd.Series
        Retornos diarios del benchmark.
    pesos : np.array
        Pesos óptimos del portafolio.
    
    Retorna:
    --------
    performance : dict
        Diccionario con:
        - retornos_portafolio : Serie temporal de retornos portafolio
        - retornos_benchmark : Serie temporal de retornos benchmark
        - tracking_error_dinamico : Serie temporal de tracking error
        - valor_portafolio : Valor acumulado portafolio (normalizado a 1)
        - valor_benchmark : Valor acumulado benchmark (normalizado a 1)
    """
    retornos_portafolio = np.dot(datos_retornos, pesos)
    retornos_benchmark = benchmark_retornos.values
    
    tracking_error_dinamico = retornos_portafolio - retornos_benchmark
    
    valor_portafolio = (1 + retornos_portafolio).cumprod()
    valor_benchmark = (1 + retornos_benchmark).cumprod()
    
    performance = {
        'retornos_portafolio': retornos_portafolio,
        'retornos_benchmark': retornos_benchmark,
        'tracking_error_dinamico': tracking_error_dinamico,
        'valor_portafolio': valor_portafolio,
        'valor_benchmark': valor_benchmark
    }
    
    return performance


def resumen_portafolio(datos_retornos, pesos, nombres_activos=None):
    """
    Genera un resumen de los pesos del portafolio.
    
    Parámetros:
    -----------
    datos_retornos : pd.DataFrame
        Retornos de activos (para acceder a nombres de columnas).
    pesos : np.array
        Pesos del portafolio.
    nombres_activos : list, opcional
        Nombres de los activos (usa índice de datos_retornos si no se proporciona).
    
    Retorna:
    --------
    resumen_df : pd.DataFrame
        DataFrame con activos, pesos y orden.
    """
    if nombres_activos is None:
        nombres_activos = datos_retornos.columns.tolist()
    
    df_resumen = pd.DataFrame({
        'Activo': nombres_activos,
        'Peso': pesos,
        'Peso_Porcentaje': pesos * 100
    })
    
    df_resumen = df_resumen[df_resumen['Peso'] > 0.001].sort_values('Peso', ascending=False)
    
    return df_resumen
