"""
1DATOS: EXPLORACIÓN Y PREPARACIÓN DE DATOS
===========================================

Este módulo se encarga de cargar, explorar y preparar los datos de retornos
diarios para la optimización de carteras.

FUNCIONALIDADES:
- Carga y validación de datos de retornos
- Cálculo de estadísticas básicas (media, volatilidad, Sharpe histórico)
- Análisis de correlaciones entre activos
- Análisis temporal (retornos acumulados, volatilidad rolling)
- Preparación de vectores de rentabilidad esperada (μ) y matriz de covarianza (Σ)
- Anualización de estadísticas (252 días de trading por año)

CÓMO FUNCIONA:
1. Carga el CSV con retornos diarios (1761 días × 50 activos)
2. Valida que no haya valores faltantes o infinitos
3. Calcula estadísticas descriptivas para cada activo
4. Analiza la estructura de correlaciones entre activos
5. Prepara los datos para optimización (anualiza μ y Σ)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


def cargar_retornos(ruta_csv):
    """
    Carga los retornos diarios desde un archivo CSV.
    
    Parámetros:
    -----------
    ruta_csv : str
        Ruta al archivo CSV con retornos diarios
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con retornos diarios (días × activos)
        
    Explicación:
    ------------
    Lee el CSV donde cada fila es un día y cada columna es un activo.
    Los valores son retornos logarítmicos diarios. Valida que no haya
    valores faltantes o infinitos que puedan afectar la optimización.
    """
    retornos = pd.read_csv(ruta_csv, index_col=0)
    
    # Validaciones
    if retornos.isnull().any().any():
        print("ADVERTENCIA: Se encontraron valores NaN")
        retornos = retornos.fillna(0)
    
    if np.isinf(retornos.values).any():
        print("ADVERTENCIA: Se encontraron valores infinitos")
        retornos = retornos.replace([np.inf, -np.inf], 0)
    
    print(f"Datos cargados: {retornos.shape[0]} días, {retornos.shape[1]} activos")
    return retornos


def calcular_estadisticas_basicas(retornos):
    """
    Calcula estadísticas básicas para cada activo.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
        
    Retorna:
    --------
    pd.DataFrame
        Estadísticas por activo: media diaria, std diaria, Sharpe histórico,
        media anual, std anual
        
    Explicación:
    ------------
    Para cada activo calcula:
    - Media diaria: promedio de retornos diarios
    - Volatilidad diaria: desviación estándar de retornos diarios
    - Sharpe histórico: (media_diaria / std_diaria) * sqrt(252)
    - Media anual: media_diaria * 252 (asumiendo 252 días de trading)
    - Volatilidad anual: std_diaria * sqrt(252)
    
    Ordena por Sharpe histórico descendente para identificar los mejores activos.
    """
    stats_df = pd.DataFrame({
        'media_diaria': retornos.mean(),
        'std_diaria': retornos.std(),
        'sharpe_historico': retornos.mean() / retornos.std() * np.sqrt(252),
        'media_anual': retornos.mean() * 252,
        'std_anual': retornos.std() * np.sqrt(252)
    })
    
    # Reemplazar infinitos en Sharpe
    stats_df['sharpe_historico'] = stats_df['sharpe_historico'].replace([np.inf, -np.inf], 0)
    
    return stats_df.sort_values('sharpe_historico', ascending=False)


def analizar_correlaciones(retornos):
    """
    Analiza la matriz de correlaciones entre activos.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
        
    Retorna:
    --------
    dict
        Diccionario con matriz de correlación, estadísticas y visualización
        
    Explicación:
    ------------
    Calcula la matriz de correlación de Pearson entre todos los pares de activos.
    Extrae solo la parte triangular superior (sin diagonal) para evitar duplicados.
    Proporciona estadísticas resumen (media, min, max) de las correlaciones.
    """
    corr_matrix = retornos.corr()
    
    # Extraer solo triángulo superior (sin diagonal)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    correlaciones = corr_matrix.where(mask).stack()
    
    stats_corr = {
        'matriz': corr_matrix,
        'media': correlaciones.mean(),
        'min': correlaciones.min(),
        'max': correlaciones.max(),
        'std': correlaciones.std()
    }
    
    return stats_corr


def visualizar_correlaciones(corr_matrix, ruta_guardado=None):
    """
    Genera un heatmap de la matriz de correlaciones.
    
    Parámetros:
    -----------
    corr_matrix : pd.DataFrame
        Matriz de correlación
    ruta_guardado : str, optional
        Ruta para guardar la figura
        
    Explicación:
    ------------
    Crea un mapa de calor donde los colores representan la fuerza de correlación:
    - Rojo: correlación positiva fuerte
    - Azul: correlación negativa fuerte
    - Blanco: correlación cercana a cero
    """
    plt.figure(figsize=(14, 12))
    sns.heatmap(corr_matrix, cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title('Matriz de Correlación entre Activos', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if ruta_guardado:
        plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
    
    return plt.gcf()


def analizar_temporal(retornos):
    """
    Realiza análisis temporal de los retornos.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
        
    Retorna:
    --------
    dict
        Diccionario con retornos acumulados, índice de mercado, volatilidad rolling
        
    Explicación:
    ------------
    - Retornos acumulados: (1 + r1) * (1 + r2) * ... * (1 + rn) - 1
      Muestra la evolución del valor de una inversión unitaria
    - Índice de mercado: promedio simple de todos los activos (equiponderado)
    - Volatilidad rolling: desviación estándar móvil de 63 días (≈ 3 meses)
      anualizada para medir el riesgo dinámico
    """
    # Retornos acumulados (valor de inversión unitaria)
    retornos_acum = (1 + retornos).cumprod()
    
    # Índice de mercado equiponderado
    indice_mercado = retornos.mean(axis=1)
    
    # Volatilidad rolling 63 días (≈ 3 meses) anualizada
    vol_rolling = retornos.rolling(63).std() * np.sqrt(252)
    
    return {
        'retornos_acumulados': retornos_acum,
        'indice_mercado': indice_mercado,
        'volatilidad_rolling': vol_rolling
    }


class PreparadorDatos:
    """
    Clase para preparar datos para optimización de carteras.
    
    Esta clase encapsula la lógica de preparación de datos necesarios
    para la optimización: vectores de rentabilidad esperada (μ) y
    matrices de covarianza (Σ), ambos anualizados.
    
    CÓMO FUNCIONA:
    1. Recibe retornos diarios y tasa libre de riesgo anual
    2. Calcula μ diario (media de retornos) y Σ diario (covarianza)
    3. Anualiza multiplicando μ por 252 y Σ por 252
    4. Permite usar ventanas temporales específicas para estimación
    """
    
    def __init__(self, retornos, rf_anual=0.02):
        """
        Inicializa el preparador de datos.
        
        Parámetros:
        -----------
        retornos : pd.DataFrame
            Retornos diarios (días × activos)
        rf_anual : float
            Tasa libre de riesgo anual (default: 2% = 0.02)
        """
        self.retornos = retornos
        self.rf_anual = rf_anual
        # Convertir tasa anual a diaria: (1 + rf_anual)^(1/252) - 1
        self.rf_diario = (1 + rf_anual)**(1/252) - 1
        
        # Inicializar atributos
        self.mu_diario = None
        self.cov_matriz = None
        self.mu_anual = None
        self.cov_anual = None
    
    def calcular_estadisticas(self, ventana=None):
        """
        Calcula estadísticas necesarias para optimización.
        
        Parámetros:
        -----------
        ventana : int, optional
            Número de días más recientes a usar. Si None, usa todos los datos.
            
        Retorna:
        --------
        self
            Para permitir encadenamiento de métodos
            
        Explicación:
        ------------
        Calcula:
        - μ diario: vector de medias de retornos (1 × N activos)
        - Σ diario: matriz de covarianza (N × N)
        - μ anual: μ diario × 252
        - Σ anual: Σ diario × 252
        
        La anualización asume 252 días de trading por año. Si se especifica
        una ventana, solo usa los últimos N días para estimar las estadísticas,
        lo cual es útil para análisis de sensibilidad temporal.
        """
        # Seleccionar datos
        if ventana is None:
            datos = self.retornos
        else:
            datos = self.retornos.iloc[-ventana:]
        
        # Calcular estadísticas diarias
        self.mu_diario = datos.mean().values  # Vector (N,)
        self.cov_matriz = datos.cov().values   # Matriz (N × N)
        
        # Anualizar (252 días de trading por año)
        self.mu_anual = self.mu_diario * 252
        self.cov_anual = self.cov_matriz * 252
        
        return self
    
    def obtener_estadisticas(self):
        """
        Retorna las estadísticas calculadas.
        
        Retorna:
        --------
        tuple
            (mu_anual, cov_anual, rf_anual)
        """
        if self.mu_anual is None:
            raise ValueError("Debe llamar a calcular_estadisticas() primero")
        
        return self.mu_anual, self.cov_anual, self.rf_anual
