"""
1DATOS: EXPLORACIÓN Y PREPARACIÓN DE DATOS
===========================================

Este módulo se encarga de cargar, explorar y preparar los datos de retornos
diarios para la optimización de carteras.

FUNCIONALIDADES:
- Carga y validación de datos de retornos
- Cálculo de estadísticas básicas (media, volatilidad, Sharpe histórico)
  El Sharpe se calcula restando la tasa libre de riesgo (rf_anual=0.02 por defecto)
- Análisis de correlaciones entre activos
- Análisis temporal (retornos acumulados, volatilidad rolling)
- Análisis de diversificación (cartera equiponderada, frontera eficiente, contribuciones)
- Preparación de vectores de rentabilidad esperada (μ) y matriz de covarianza (Σ)
- Anualización de estadísticas (252 días de trading por año)

CÓMO FUNCIONA:
1. Carga el CSV con retornos diarios (1760 días × 50 activos)
2. Valida que no haya valores faltantes o infinitos
3. Calcula estadísticas descriptivas para cada activo
   - Sharpe histórico: (retorno_medio - rf_diario) / volatilidad * sqrt(252)
   - Donde rf_diario se calcula desde rf_anual=0.02 (2% anual)
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
    # Leer CSV sin usar la primera columna como índice para preservar todos los activos
    retornos = pd.read_csv(ruta_csv)
    
    # Si la primera columna es el índice (números), usarla como índice
    # Si no, crear un índice numérico
    if retornos.columns[0] == 'asset1' or retornos.columns[0].isdigit():
        # La primera columna es asset1, usarla como datos, no como índice
        # Crear índice numérico para los días
        retornos.index = range(len(retornos))
    else:
        # Ya tiene un índice apropiado
        pass
    
    # Validaciones
    if retornos.isnull().any().any():
        print("ADVERTENCIA: Se encontraron valores NaN")
        retornos = retornos.fillna(0)
    
    if np.isinf(retornos.values).any():
        print("ADVERTENCIA: Se encontraron valores infinitos")
        retornos = retornos.replace([np.inf, -np.inf], 0)
    
    print(f"Datos cargados: {retornos.shape[0]} días, {retornos.shape[1]} activos")
    return retornos


def calcular_estadisticas_basicas(retornos, rf_anual=0.02):
    """
    Calcula estadísticas básicas para cada activo.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    rf_anual : float, optional
        Tasa libre de riesgo anual (default: 0.02 = 2%)
        
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
    - Sharpe histórico: (media_diaria - rf_diario) / std_diaria * sqrt(252)
      donde rf_diario es la tasa libre de riesgo diaria convertida desde rf_anual
    - Media anual: media_diaria * 252 (asumiendo 252 días de trading)
    - Volatilidad anual: std_diaria * sqrt(252)
    
    Ordena por Sharpe histórico descendente para identificar los mejores activos.
    """
    # Convertir tasa libre de riesgo anual a diaria: (1 + rf_anual)^(1/252) - 1
    rf_diario = (1 + rf_anual)**(1/252) - 1
    
    # Calcular estadísticas
    media_diaria = retornos.mean()
    std_diaria = retornos.std()
    
    # Sharpe histórico: (retorno_medio - rf_diario) / volatilidad * sqrt(252)
    sharpe_historico = (media_diaria - rf_diario) / std_diaria * np.sqrt(252)
    
    stats_df = pd.DataFrame({
        'media_diaria': media_diaria,
        'std_diaria': std_diaria,
        'sharpe_historico': sharpe_historico,
        'media_anual': media_diaria * 252,
        'std_anual': std_diaria * np.sqrt(252)
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


def analizar_cartera_equiponderada(retornos):
    """
    Analiza la composición del riesgo de una cartera equiponderada.
    
    Implementa la descomposición teórica:
    σ²ₚ = (1/n)V̄ + (1 - 1/n)σ̄ᵢⱼ
    
    Donde:
    - V̄: Varianza media de activos individuales
    - σ̄ᵢⱼ: Covarianza media entre activos
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
        
    Retorna:
    --------
    dict
        Diccionario con:
        - varianza_media: V̄ (varianza promedio individual, anualizada)
        - covarianza_media: σ̄ᵢⱼ (covarianza promedio entre pares, anualizada)
        - riesgo_especifico: (1/n)V̄ (riesgo diversificable, anualizada)
        - riesgo_sistematico: σ̄ᵢⱼ (riesgo no diversificable, anualizada)
        - varianza_cartera: σ²ₚ total (anualizada)
        - volatilidad_cartera: σₚ (anualizada, en decimal)
        
    Explicación:
    ------------
    Para una cartera equiponderada con n activos:
    - Cada activo tiene peso w_i = 1/n
    - La varianza de la cartera se descompone en:
      * Riesgo específico: (1/n) × V̄ → se reduce con más activos
      * Riesgo sistemático: σ̄ᵢⱼ → no se puede diversificar
    - El límite cuando n→∞ es σ̄ᵢⱼ (riesgo sistemático)
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    n = retornos.shape[1]  # Número de activos
    
    # Calcular matriz de covarianza diaria
    cov_diaria = retornos.cov().values
    
    # Varianza media (promedio de la diagonal)
    varianza_media_diaria = np.mean(np.diag(cov_diaria))
    
    # Covarianza media (promedio del triángulo superior, excluyendo diagonal)
    mask = np.triu(np.ones_like(cov_diaria, dtype=bool), k=1)
    covarianzas_pares = cov_diaria[mask]
    covarianza_media_diaria = np.mean(covarianzas_pares)
    
    # Anualizar (varianzas y covarianzas se multiplican por 252)
    varianza_media = varianza_media_diaria * 252
    covarianza_media = covarianza_media_diaria * 252
    
    # Calcular componentes del riesgo según fórmula teórica
    riesgo_especifico = (1 / n) * varianza_media
    riesgo_sistematico = covarianza_media
    
    # Varianza total de cartera (fórmula teórica)
    varianza_cartera = riesgo_especifico + riesgo_sistematico
    
    # Volatilidad (raíz cuadrada de varianza)
    volatilidad_cartera = np.sqrt(varianza_cartera)
    
    # Verificación: calcular varianza real de cartera equiponderada
    pesos_eq = np.ones(n) / n
    varianza_real = pesos_eq @ cov_diaria @ pesos_eq * 252
    
    # Verificar que la diferencia sea pequeña (tolerancia numérica)
    diferencia = abs(varianza_cartera - varianza_real)
    if diferencia > 1e-6:
        print(f"ADVERTENCIA: Diferencia entre fórmula teórica y cálculo real: {diferencia:.2e}")
    
    return {
        'varianza_media': varianza_media,
        'covarianza_media': covarianza_media,
        'riesgo_especifico': riesgo_especifico,
        'riesgo_sistematico': riesgo_sistematico,
        'varianza_cartera': varianza_cartera,
        'volatilidad_cartera': volatilidad_cartera
    }


def simular_frontera_diversificacion(retornos, n_valores=None, n_simulaciones=100):
    """
    Simula el efecto de la diversificación al variar el número de activos.
    
    Para cada N en n_valores:
    1. Selecciona N activos aleatorios (n_simulaciones veces)
    2. Calcula riesgo de cartera equiponderada
    3. Descompone en riesgo sistemático y específico
    4. Promedia resultados
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    n_valores : list, optional
        Lista de N activos a probar. 
        Si None, usa: [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
    n_simulaciones : int
        Número de carteras aleatorias por cada N (default: 100)
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con columnas:
        - n_activos: Número de activos en la cartera
        - volatilidad_media: σₚ promedio (anualizada, en decimal)
        - volatilidad_std: Desviación estándar entre simulaciones (anualizada)
        - riesgo_especifico: (1/n)V̄ promedio (anualizada)
        - riesgo_sistematico: σ̄ᵢⱼ promedio (anualizada)
        - reduccion_pct: % reducción de riesgo vs N-1 (NaN para N=2)
        
    Explicación:
    ------------
    Esta función permite identificar cuántos activos se necesitan para alcanzar
    el límite práctico de diversificación. Cuando la reducción porcentual de riesgo
    al añadir un activo más es menor al 2%, se considera que se ha alcanzado la
    frontera eficiente de diversificación.
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    n_total = retornos.shape[1]  # Número total de activos disponibles
    
    # Valores por defecto de N a probar
    if n_valores is None:
        n_valores = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
    
    # Filtrar valores que exceden el número de activos disponibles
    n_valores = [n for n in n_valores if n <= n_total]
    
    if not n_valores:
        raise ValueError(f"No hay valores válidos de N. Máximo disponible: {n_total}")
    
    # Semilla para reproducibilidad
    np.random.seed(42)
    
    resultados = []
    
    for n in n_valores:
        volatilidades = []
        riesgos_especificos = []
        riesgos_sistematicos = []
        
        # Realizar n_simulaciones selecciones aleatorias
        for _ in range(n_simulaciones):
            # Seleccionar n activos aleatorios
            activos_seleccionados = np.random.choice(retornos.columns, size=n, replace=False)
            retornos_subset = retornos[activos_seleccionados]
            
            # Calcular matriz de covarianza
            cov_diaria = retornos_subset.cov().values
            
            # Varianza media (diagonal)
            varianza_media_diaria = np.mean(np.diag(cov_diaria))
            
            # Covarianza media (triángulo superior)
            mask = np.triu(np.ones_like(cov_diaria, dtype=bool), k=1)
            covarianzas_pares = cov_diaria[mask]
            if len(covarianzas_pares) > 0:
                covarianza_media_diaria = np.mean(covarianzas_pares)
            else:
                covarianza_media_diaria = 0.0
            
            # Anualizar
            varianza_media = varianza_media_diaria * 252
            covarianza_media = covarianza_media_diaria * 252
            
            # Componentes del riesgo
            riesgo_especifico = (1 / n) * varianza_media
            riesgo_sistematico = covarianza_media
            
            # Varianza total
            varianza_total = riesgo_especifico + riesgo_sistematico
            volatilidad = np.sqrt(varianza_total)
            
            volatilidades.append(volatilidad)
            riesgos_especificos.append(riesgo_especifico)
            riesgos_sistematicos.append(riesgo_sistematico)
        
        # Promediar resultados
        volatilidad_media = np.mean(volatilidades)
        volatilidad_std = np.std(volatilidades)
        riesgo_especifico_medio = np.mean(riesgos_especificos)
        riesgo_sistematico_medio = np.mean(riesgos_sistematicos)
        
        # Calcular reducción porcentual vs N-1
        if len(resultados) > 0:
            vol_anterior = resultados[-1]['volatilidad_media']
            reduccion_pct = ((vol_anterior - volatilidad_media) / vol_anterior) * 100
        else:
            reduccion_pct = np.nan
        
        resultados.append({
            'n_activos': n,
            'volatilidad_media': volatilidad_media,
            'volatilidad_std': volatilidad_std,
            'riesgo_especifico': riesgo_especifico_medio,
            'riesgo_sistematico': riesgo_sistematico_medio,
            'reduccion_pct': reduccion_pct
        })
    
    df_resultado = pd.DataFrame(resultados)
    
    # Imprimir tabla resumen con formato mejorado
    print("\n" + "="*80)
    print("TABLA RESUMEN: FRONTERA DE DIVERSIFICACIÓN")
    print("="*80)
    print(f"{'N':>3} | {'Vol(%)':>7} | {'±Std':>6} | {'Esp(%)':>7} | {'Sis(%)':>7} | {'Reduc':>6}")
    print("-"*80)
    for _, row in df_resultado.iterrows():
        vol_esp = np.sqrt(row['riesgo_especifico']) * 100
        vol_sis = np.sqrt(row['riesgo_sistematico']) * 100
        reduc_str = f"{row['reduccion_pct']:.2f}%" if not np.isnan(row['reduccion_pct']) else "  N/A"
        print(f"{row['n_activos']:3.0f} | {row['volatilidad_media']*100:7.2f} | "
              f"{row['volatilidad_std']*100:6.2f} | "
              f"{vol_esp:7.2f} | "
              f"{vol_sis:7.2f} | {reduc_str:>6}")
    print("="*80)
    
    return df_resultado


def detectar_frontera_optima(df_simulacion, umbral_reduccion=2.0):
    """
    Detecta automáticamente el número óptimo de activos para diversificación.
    
    Criterio: Primer N donde la reducción de riesgo al añadir un activo más
    es menor que umbral_reduccion%.
    
    Parámetros:
    -----------
    df_simulacion : pd.DataFrame
        DataFrame retornado por simular_frontera_diversificacion()
    umbral_reduccion : float
        Umbral de reducción porcentual (default: 2.0%)
        
    Retorna:
    --------
    int
        Número óptimo de activos. Si no se alcanza el umbral, retorna el máximo N disponible.
        
    Explicación:
    ------------
    Cuando la reducción de riesgo al añadir un activo más es menor que el umbral,
    se considera que se ha alcanzado el límite práctico de diversificación.
    Añadir más activos no aporta beneficios significativos adicionales.
    """
    if df_simulacion.empty:
        raise ValueError("El DataFrame de simulación está vacío")
    
    # Buscar primer N donde reducción < umbral
    idx = df_simulacion[df_simulacion['reduccion_pct'] < umbral_reduccion].index
    
    if len(idx) > 0:
        n_optimo = int(df_simulacion.loc[idx[0], 'n_activos'])
    else:
        # Si no se alcanza el umbral, retornar el máximo N disponible
        n_optimo = int(df_simulacion['n_activos'].iloc[-1])
    
    return n_optimo


def analizar_contribuciones(retornos, pesos=None):
    """
    Calcula la contribución de cada activo al rendimiento y riesgo de la cartera.
    
    Fórmulas:
    - Contribución al Rendimiento: wᵢ × E(Rᵢ)
    - Contribución al Riesgo: wᵢ × Cov(Rᵢ, Rₚ)
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    pesos : np.array, optional
        Array de pesos (debe sumar 1.0). Si None, usa equiponderada (1/N)
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con índice = nombres de activos y columnas:
        - peso: Peso del activo en cartera
        - rendimiento_esperado: E(Rᵢ) anualizado (en decimal)
        - contribucion_rendimiento: wᵢ × E(Rᵢ) anualizado
        - covarianza_cartera: Cov(Rᵢ, Rₚ) anualizada
        - contribucion_riesgo: wᵢ × Cov(Rᵢ, Rₚ) anualizada
        - es_diversificador: True si E(Rᵢ)>0 y Cov(Rᵢ, Rₚ)<0 (activo ideal)
        
        Ordenado por contribución al riesgo descendente
        
    Explicación:
    ------------
    Un activo es "diversificador ideal" si:
    - Tiene rendimiento esperado positivo (aportará rentabilidad)
    - Tiene covarianza negativa con la cartera (reducirá el riesgo total)
    
    Estos activos son especialmente valiosos porque aumentan el rendimiento
    mientras reducen el riesgo de la cartera.
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    n_activos = retornos.shape[1]
    
    # Si no se proporcionan pesos, usar equiponderada
    if pesos is None:
        pesos = np.ones(n_activos) / n_activos
    else:
        pesos = np.array(pesos)
        if len(pesos) != n_activos:
            raise ValueError(f"El número de pesos ({len(pesos)}) no coincide con el número de activos ({n_activos})")
    
    # Validar que los pesos sumen aproximadamente 1
    suma_pesos = np.sum(pesos)
    if abs(suma_pesos - 1.0) > 1e-6:
        raise ValueError(f"Los pesos deben sumar 1.0, pero suman {suma_pesos:.6f}")
    
    # Calcular retorno de cartera diario
    retorno_cartera_diario = (retornos * pesos).sum(axis=1)
    
    # Calcular rendimientos esperados anualizados
    rendimientos_esperados = retornos.mean() * 252
    
    # Calcular contribuciones al rendimiento
    contribuciones_rendimiento = pesos * rendimientos_esperados
    
    # Calcular covarianzas con la cartera (anualizadas)
    covarianzas_cartera = []
    contribuciones_riesgo = []
    
    for i, activo in enumerate(retornos.columns):
        # Covarianza entre activo i y cartera
        cov_diaria = np.cov(retornos[activo], retorno_cartera_diario)[0, 1]
        cov_anual = cov_diaria * 252
        covarianzas_cartera.append(cov_anual)
        
        # Contribución al riesgo: peso × covarianza
        contrib_riesgo = pesos[i] * cov_anual
        contribuciones_riesgo.append(contrib_riesgo)
    
    # Identificar activos diversificadores ideales
    es_diversificador = (rendimientos_esperados > 0) & (np.array(covarianzas_cartera) < 0)
    
    # Construir DataFrame
    df_resultado = pd.DataFrame({
        'peso': pesos,
        'rendimiento_esperado': rendimientos_esperados,
        'contribucion_rendimiento': contribuciones_rendimiento,
        'covarianza_cartera': covarianzas_cartera,
        'contribucion_riesgo': contribuciones_riesgo,
        'es_diversificador': es_diversificador
    }, index=retornos.columns)
    
    # Ordenar por contribución al riesgo descendente
    df_resultado = df_resultado.sort_values('contribucion_riesgo', ascending=False)
    
    return df_resultado


def visualizar_frontera_diversificacion(df_simulacion, ruta_guardado=None):
    """
    Crea visualización de la frontera eficiente de diversificación.
    
    Genera figura con 2 subplots:
    1. Evolución del riesgo total vs N activos (con bandas de confianza)
    2. Descomposición: riesgo sistemático vs específico
    
    Parámetros:
    -----------
    df_simulacion : pd.DataFrame
        DataFrame retornado por simular_frontera_diversificacion()
    ruta_guardado : str, optional
        Ruta para guardar la figura (opcional)
        
    Retorna:
    --------
    matplotlib.figure.Figure
        Figura con los gráficos
    """
    if df_simulacion.empty:
        raise ValueError("El DataFrame de simulación está vacío")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Subplot 1: Evolución del riesgo total
    n_activos = df_simulacion['n_activos'].values
    vol_media = df_simulacion['volatilidad_media'].values * 100  # Convertir a porcentaje
    vol_std = df_simulacion['volatilidad_std'].values * 100
    
    # Línea principal
    ax1.plot(n_activos, vol_media, 'b-', linewidth=2, label='Volatilidad Media')
    
    # Banda de confianza (±1 std)
    ax1.fill_between(n_activos, 
                     vol_media - vol_std, 
                     vol_media + vol_std, 
                     alpha=0.3, color='blue', label='±1 Desviación Estándar')
    
    # Línea horizontal: límite teórico (último valor de riesgo sistemático)
    limite_teorico = np.sqrt(df_simulacion['riesgo_sistematico'].iloc[-1]) * 100
    ax1.axhline(y=limite_teorico, color='r', linestyle='--', linewidth=1.5, 
                label=f'Límite Teórico ({limite_teorico:.2f}%)')
    
    # Marcar punto donde reducción < 2% (frontera práctica)
    idx_frontera = df_simulacion[df_simulacion['reduccion_pct'] < 2.0].index
    if len(idx_frontera) > 0:
        n_frontera = df_simulacion.loc[idx_frontera[0], 'n_activos']
        vol_frontera = df_simulacion.loc[idx_frontera[0], 'volatilidad_media'] * 100
        ax1.scatter([n_frontera], [vol_frontera], s=200, c='red', marker='*', 
                   zorder=5, edgecolors='black', linewidths=1.5,
                   label=f'Frontera Práctica (N={int(n_frontera)})')
    
    ax1.set_xlabel('Número de Activos', fontsize=12)
    ax1.set_ylabel('Volatilidad Anualizada (%)', fontsize=12)
    ax1.set_title('Evolución del Riesgo Total con Diversificación', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Descomposición del riesgo
    # NOTA: No se pueden sumar volatilidades directamente.
    # La relación correcta es: σ_total = sqrt(σ_especifico² + σ_sistematico²)
    # Las varianzas están en df_simulacion en decimal (anualizadas)
    
    # Convertir varianzas a volatilidades (raíz cuadrada) y luego a porcentaje
    riesgo_especifico_vol = np.sqrt(df_simulacion['riesgo_especifico'].values) * 100
    riesgo_sistematico_vol = np.sqrt(df_simulacion['riesgo_sistematico'].values) * 100
    # Riesgo total = raíz cuadrada de suma de varianzas
    riesgo_total_vol = np.sqrt(df_simulacion['riesgo_especifico'].values + 
                               df_simulacion['riesgo_sistematico'].values) * 100
    
    # Visualización correcta: área para específico, línea para total, línea horizontal para límite
    ax2.fill_between(n_activos, 0, riesgo_especifico_vol, alpha=0.6, color='orange', 
                     label='Riesgo Específico (Diversificable)')
    ax2.plot(n_activos, riesgo_total_vol, 'b-', linewidth=2, 
             label='Riesgo Total', zorder=10)
    ax2.axhline(y=riesgo_sistematico_vol[-1], color='green', 
                linestyle='--', linewidth=2, 
                label=f'Límite Sistemático ({riesgo_sistematico_vol[-1]:.2f}%)')
    
    ax2.set_xlabel('Número de Activos', fontsize=12)
    ax2.set_ylabel('Volatilidad Anualizada (%)', fontsize=12)
    ax2.set_title('Descomposición del Riesgo', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if ruta_guardado:
        plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
    
    return fig
