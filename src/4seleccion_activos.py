"""
4SELECCION_ACTIVOS: SELECCIÓN ÓPTIMA DE ACTIVOS PARA OPTIMIZACIÓN DE CARTERAS
===============================================================================

Este módulo implementa estrategias de selección de activos basadas en la frontera
de diversificación para mejorar la eficiencia de la optimización de Markowitz.

FUNCIONALIDADES:
- Detección automática del número óptimo de activos (N)
- Selección de activos por Sharpe Ratio + baja correlación
- Filtrado de DataFrame de retornos
- Integración completa con pipeline de optimización
- Reconstrucción de vector de pesos de 50 posiciones

FLUJO DE TRABAJO:
1. Detecta N óptimo usando frontera de diversificación (módulo 2)
2. Selecciona N activos según criterios de calidad + diversificación
3. Filtra retornos a solo esos N activos
4. Optimiza con Markowitz (módulo 3) sobre activos seleccionados
5. Reconstruye vector de 50 posiciones con pesos finales

TEORÍA:
- La diversificación alcanza un límite práctico con N activos (típicamente 15-25)
- Seleccionar los mejores N activos antes de optimizar puede mejorar el Sharpe Ratio
- Criterio de selección: balance entre Sharpe Ratio alto y baja correlación
- Los pesos optimizados sobre N activos se mapean a un vector de 50 posiciones
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

# Nota: Las importaciones de módulos 1, 2 y 3 se harán dentro de las funciones
# para evitar problemas de importación circular y permitir ejecución flexible


def detectar_n_optimo_activos(retornos, umbral_reduccion=2.0, n_simulaciones=100):
    """
    Detecta automáticamente cuántos activos se necesitan para diversificación óptima.
    
    Utiliza las funciones del módulo 2equiponderada_diversificacion para simular
    la frontera de diversificación y detectar el N óptimo según el umbral de reducción.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    umbral_reduccion : float
        Porcentaje mínimo de reducción de riesgo para considerar significativo (default: 2.0%)
    n_simulaciones : int
        Número de simulaciones Monte Carlo por cada N (default: 100)
        
    Retorna:
    --------
    dict
        Diccionario con:
        - 'n_optimo': int, número óptimo de activos detectado
        - 'df_frontera': pd.DataFrame, resultados completos de simulación
        - 'reduccion_en_optimo': float, % de reducción de riesgo en N óptimo
        - 'volatilidad_en_optimo': float, volatilidad anualizada en N óptimo
        
    Explicación:
    ------------
    El proceso realiza:
    1. Simula la frontera de diversificación usando simular_frontera_diversificacion
    2. Detecta N óptimo usando detectar_frontera_optima con el umbral especificado
    3. Extrae métricas en el N óptimo para análisis posterior
    
    El N óptimo es el primer número de activos donde añadir un activo más
    reduce el riesgo en menos del umbral_reduccion%, indicando que se alcanzó
    el límite práctico de diversificación.
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    # Importar funciones del módulo 2 (dinámicamente para evitar problemas)
    import importlib
    import sys
    if '2equiponderada_diversificacion' in sys.modules:
        modulo2 = sys.modules['2equiponderada_diversificacion']
    else:
        # Intentar importar usando diferentes métodos
        try:
            modulo2 = importlib.import_module('2equiponderada_diversificacion')
        except ImportError:
            # Si no funciona, usar importación desde src
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo2 = importlib.import_module('2equiponderada_diversificacion')
    
    # Simular frontera de diversificación
    df_frontera = modulo2.simular_frontera_diversificacion(
        retornos, 
        n_valores=None,  # Usa valores por defecto
        n_simulaciones=n_simulaciones
    )
    
    # Detectar N óptimo
    n_optimo = modulo2.detectar_frontera_optima(df_frontera, umbral_reduccion)
    
    # Extraer métricas en N óptimo
    fila_optima = df_frontera[df_frontera['n_activos'] == n_optimo].iloc[0]
    reduccion_en_optimo = fila_optima['reduccion_pct'] if not np.isnan(fila_optima['reduccion_pct']) else 0.0
    volatilidad_en_optimo = fila_optima['volatilidad_media']
    
    return {
        'n_optimo': n_optimo,
        'df_frontera': df_frontera,
        'reduccion_en_optimo': reduccion_en_optimo,
        'volatilidad_en_optimo': volatilidad_en_optimo
    }


def calcular_metricas_seleccion(retornos, rf_anual=0.02):
    """
    Calcula métricas de calidad para cada activo que servirán como criterios de selección.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    rf_anual : float
        Tasa libre de riesgo anual (default: 0.02)
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con columnas:
        - activo: nombre del activo (asset1, asset2, ...)
        - sharpe_ratio: Sharpe anualizado
        - rendimiento_anual: rentabilidad esperada anualizada
        - volatilidad_anual: volatilidad anualizada
        - correlacion_promedio: correlación media con otros activos
        - puntuacion_diversificacion: métrica compuesta (1 - correlacion_promedio)
        
    Explicación:
    ------------
    Para cada activo calcula:
    1. Sharpe Ratio anualizado: (retorno_medio - rf_diario) / volatilidad * sqrt(252)
    2. Volatilidad anualizada: std_diaria * sqrt(252)
    3. Rendimiento esperado anualizado: media_diaria * 252
    4. Correlación promedio: promedio de correlaciones con todos los demás activos
    5. Puntuación de diversificación: 1 - correlacion_promedio (mayor = más diversificador)
    
    Ordena por Sharpe Ratio descendente para identificar los mejores activos.
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    # Convertir tasa anual a diaria
    rf_diario = (1 + rf_anual)**(1/252) - 1
    
    # Calcular estadísticas básicas
    media_diaria = retornos.mean()
    std_diaria = retornos.std()
    
    # Sharpe Ratio anualizado
    sharpe_ratio = (media_diaria - rf_diario) / std_diaria * np.sqrt(252)
    sharpe_ratio = sharpe_ratio.replace([np.inf, -np.inf], 0)
    
    # Anualizar rendimientos y volatilidades
    rendimiento_anual = media_diaria * 252
    volatilidad_anual = std_diaria * np.sqrt(252)
    
    # Calcular matriz de correlación
    correlaciones = retornos.corr()
    
    # Calcular correlación promedio de cada activo con todos los demás
    correlacion_promedio = correlaciones.apply(lambda x: x[x.index != x.name].mean(), axis=0)
    
    # Puntuación de diversificación: 1 - correlación promedio (mayor = más diversificador)
    puntuacion_diversificacion = 1 - correlacion_promedio
    
    # Crear DataFrame
    metricas_df = pd.DataFrame({
        'activo': retornos.columns,
        'sharpe_ratio': sharpe_ratio,
        'rendimiento_anual': rendimiento_anual,
        'volatilidad_anual': volatilidad_anual,
        'correlacion_promedio': correlacion_promedio,
        'puntuacion_diversificacion': puntuacion_diversificacion
    })
    
    # Ordenar por Sharpe descendente
    metricas_df = metricas_df.sort_values('sharpe_ratio', ascending=False).reset_index(drop=True)
    
    return metricas_df


def seleccionar_activos_por_sharpe_decorrelacion(retornos, n_activos, rf_anual=0.02, 
                                                  peso_sharpe=0.7, peso_decorrelacion=0.3):
    """
    Selecciona N activos óptimos balanceando Sharpe Ratio alto y baja correlación.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × activos)
    n_activos : int
        Número de activos a seleccionar
    rf_anual : float
        Tasa libre de riesgo anual
    peso_sharpe : float
        Peso para Sharpe Ratio en score combinado (default: 0.7)
    peso_decorrelacion : float
        Peso para diversificación en score combinado (default: 0.3)
        
    Retorna:
    --------
    dict
        Diccionario con:
        - 'activos_seleccionados': list de nombres de activos
        - 'indices_seleccionados': list de índices de activos en retornos originales
        - 'metricas': DataFrame con métricas de los N activos seleccionados
        - 'correlacion_promedio_seleccion': float, correlación promedio entre seleccionados
        - 'sharpe_promedio_seleccion': float, Sharpe promedio de seleccionados
        
    Explicación:
    ------------
    El proceso realiza:
    1. Calcula métricas de selección para todos los activos
    2. Normaliza Sharpe Ratio y puntuación de diversificación a escala [0, 1]
    3. Calcula score combinado: score = peso_sharpe × sharpe_norm + peso_decorrelacion × diversif_norm
    4. Ordena por score combinado descendente
    5. Selecciona top N activos
    6. Verifica correlación promedio entre seleccionados
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    if n_activos <= 0 or n_activos > retornos.shape[1]:
        raise ValueError(f"n_activos debe estar entre 1 y {retornos.shape[1]}")
    
    if abs(peso_sharpe + peso_decorrelacion - 1.0) > 1e-6:
        raise ValueError("Los pesos deben sumar 1.0")
    
    # Calcular métricas de selección
    metricas = calcular_metricas_seleccion(retornos, rf_anual)
    
    # Normalizar Sharpe Ratio a escala [0, 1]
    sharpe_min = metricas['sharpe_ratio'].min()
    sharpe_max = metricas['sharpe_ratio'].max()
    if sharpe_max > sharpe_min:
        sharpe_norm = (metricas['sharpe_ratio'] - sharpe_min) / (sharpe_max - sharpe_min)
    else:
        sharpe_norm = pd.Series(0.5, index=metricas.index)
    
    # Normalizar puntuación de diversificación a escala [0, 1]
    diversif_min = metricas['puntuacion_diversificacion'].min()
    diversif_max = metricas['puntuacion_diversificacion'].max()
    if diversif_max > diversif_min:
        diversif_norm = (metricas['puntuacion_diversificacion'] - diversif_min) / (diversif_max - diversif_min)
    else:
        diversif_norm = pd.Series(0.5, index=metricas.index)
    
    # Calcular score combinado
    metricas['score_combinado'] = peso_sharpe * sharpe_norm + peso_decorrelacion * diversif_norm
    
    # Ordenar por score combinado descendente
    metricas = metricas.sort_values('score_combinado', ascending=False).reset_index(drop=True)
    
    # Seleccionar top N activos
    metricas_seleccion = metricas.head(n_activos).copy()
    activos_seleccionados = metricas_seleccion['activo'].tolist()
    
    # Obtener índices de activos seleccionados en el DataFrame original
    indices_seleccionados = [list(retornos.columns).index(activo) for activo in activos_seleccionados]
    
    # Calcular correlación promedio entre activos seleccionados
    retornos_seleccion = retornos[activos_seleccionados]
    correlaciones_seleccion = retornos_seleccion.corr()
    # Promedio del triángulo superior (excluyendo diagonal)
    mask = np.triu(np.ones_like(correlaciones_seleccion.values, dtype=bool), k=1)
    correlacion_promedio_seleccion = correlaciones_seleccion.values[mask].mean()
    
    # Sharpe promedio de seleccionados
    sharpe_promedio_seleccion = metricas_seleccion['sharpe_ratio'].mean()
    
    # Advertir si correlación promedio es alta
    if correlacion_promedio_seleccion > 0.8:
        print(f"ADVERTENCIA: Correlación promedio entre activos seleccionados es alta ({correlacion_promedio_seleccion:.3f})")
        print("Esto puede limitar los beneficios de diversificación")
    
    return {
        'activos_seleccionados': activos_seleccionados,
        'indices_seleccionados': indices_seleccionados,
        'metricas': metricas_seleccion,
        'correlacion_promedio_seleccion': correlacion_promedio_seleccion,
        'sharpe_promedio_seleccion': sharpe_promedio_seleccion
    }


def filtrar_retornos_activos_seleccionados(retornos, activos_seleccionados):
    """
    Crea DataFrame filtrado con solo los activos seleccionados.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        DataFrame completo de retornos (días × 50 activos)
    activos_seleccionados : list
        Lista de nombres de activos a seleccionar
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame filtrado (días × N activos)
        
    Explicación:
    ------------
    Valida que todos los activos seleccionados existan en retornos,
    extrae las columnas correspondientes y retorna un nuevo DataFrame
    con el orden preservado según activos_seleccionados.
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    if not activos_seleccionados:
        raise ValueError("La lista de activos seleccionados está vacía")
    
    # Validar que todos los activos seleccionados existan
    activos_faltantes = [activo for activo in activos_seleccionados if activo not in retornos.columns]
    if activos_faltantes:
        raise ValueError(f"Los siguientes activos no existen en retornos: {activos_faltantes}")
    
    # Filtrar y preservar orden
    retornos_filtrados = retornos[activos_seleccionados].copy()
    
    return retornos_filtrados


def optimizar_cartera_con_seleccion(retornos, rf_anual=0.02, n_optimo=None, 
                                     umbral_reduccion=2.0, metodo_optimizacion='max_sharpe',
                                     **kwargs_seleccion):
    """
    FUNCIÓN PRINCIPAL - Ejecuta pipeline completo de selección + optimización.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × 50 activos)
    rf_anual : float
        Tasa libre de riesgo anual (default: 0.02)
    n_optimo : int, optional
        Número de activos a usar. Si None, detecta automáticamente (default: None)
    umbral_reduccion : float
        Umbral de reducción para detección de N óptimo (default: 2.0%)
    metodo_optimizacion : str
        Método de optimización: 'max_sharpe' o 'min_variance' (default: 'max_sharpe')
    **kwargs_seleccion : dict
        Argumentos adicionales para selección (peso_sharpe, peso_decorrelacion, etc.)
        
    Retorna:
    --------
    dict
        Diccionario con:
        - 'pesos_completos': numpy array de 50 posiciones (orden asset1 a asset50)
        - 'activos_seleccionados': list de nombres de activos con peso > 0
        - 'indices_seleccionados': list de índices de activos seleccionados
        - 'n_activos_usados': int, número de activos seleccionados
        - 'metricas_cartera': dict con sharpe, rentabilidad, volatilidad
        - 'comparacion_baseline': dict con mejora vs equiponderada
        - 'detalles_seleccion': dict con info del proceso de selección
        
    Explicación:
    ------------
    El proceso ejecuta 7 pasos:
    1. Detecta N óptimo usando frontera de diversificación (si n_optimo=None)
    2. Selecciona N activos por Sharpe Ratio + baja correlación
    3. Filtra DataFrame de retornos a solo N activos seleccionados
    4. Prepara datos para optimización (calcula μ y Σ anualizados)
    5. Optimiza con Markowitz sobre N activos seleccionados
    6. Reconstruye vector de 50 posiciones mapeando pesos optimizados
    7. Calcula métricas finales y compara con baseline (equiponderada 50)
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    n_activos_total = retornos.shape[1]
    
    # Importar módulos necesarios (dinámicamente)
    import importlib
    import sys
    
    # Importar módulo 1 (datos)
    if '1datos' in sys.modules:
        modulo1 = sys.modules['1datos']
    else:
        try:
            modulo1 = importlib.import_module('1datos')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo1 = importlib.import_module('1datos')
    
    # Importar módulo 3 (markowitz)
    if '3markowitz' in sys.modules:
        modulo3 = sys.modules['3markowitz']
    else:
        try:
            modulo3 = importlib.import_module('3markowitz')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo3 = importlib.import_module('3markowitz')
    
    # PASO 1: Detección de N óptimo
    if n_optimo is None:
        print("Detectando número óptimo de activos...")
        resultado_n = detectar_n_optimo_activos(retornos, umbral_reduccion=umbral_reduccion)
        n_optimo = resultado_n['n_optimo']
        print(f"Número óptimo detectado: {n_optimo} activos")
    else:
        print(f"Usando número de activos especificado: {n_optimo}")
        resultado_n = None
    
    # PASO 2: Selección de activos
    print("Seleccionando activos óptimos...")
    peso_sharpe = kwargs_seleccion.get('peso_sharpe', 0.7)
    peso_decorrelacion = kwargs_seleccion.get('peso_decorrelacion', 0.3)
    
    seleccion = seleccionar_activos_por_sharpe_decorrelacion(
        retornos,
        n_activos=n_optimo,
        rf_anual=rf_anual,
        peso_sharpe=peso_sharpe,
        peso_decorrelacion=peso_decorrelacion
    )
    
    activos_seleccionados = seleccion['activos_seleccionados']
    indices_seleccionados = seleccion['indices_seleccionados']
    
    print(f"Activos seleccionados: {len(activos_seleccionados)}")
    print(f"Sharpe promedio de seleccionados: {seleccion['sharpe_promedio_seleccion']:.3f}")
    
    # PASO 3: Filtrado de retornos
    print("Filtrando retornos a activos seleccionados...")
    retornos_filtrados = filtrar_retornos_activos_seleccionados(retornos, activos_seleccionados)
    
    # PASO 4: Preparación para optimización
    print("Preparando datos para optimización...")
    preparador = modulo1.PreparadorDatos(retornos_filtrados, rf_anual=rf_anual)
    preparador.calcular_estadisticas()
    mu, Sigma, rf = preparador.obtener_estadisticas()
    
    # PASO 5: Optimización con Markowitz
    print(f"Optimizando cartera con método '{metodo_optimizacion}'...")
    if metodo_optimizacion == 'max_sharpe':
        resultado_opt = modulo3.optimizar_sharpe_maximo(mu, Sigma, rf)
    elif metodo_optimizacion == 'min_variance':
        # Para min_variance, usar lambda alto (máxima aversión al riesgo)
        resultado_opt = modulo3.optimizar_markowitz_lambda(mu, Sigma, rf, lambda_param=100.0)
    else:
        raise ValueError(f"Método de optimización '{metodo_optimizacion}' no reconocido")
    
    if resultado_opt is None:
        raise ValueError("La optimización falló. Verifique los datos y parámetros.")
    
    pesos_optimizados = resultado_opt['w']  # Vector de N posiciones
    
    # PASO 6: Reconstrucción de vector de 50 posiciones
    print("Reconstruyendo vector de pesos de 50 posiciones...")
    pesos_completos = np.zeros(n_activos_total)
    
    # Mapear pesos optimizados a posiciones originales
    for i, idx in enumerate(indices_seleccionados):
        pesos_completos[idx] = pesos_optimizados[i]
    
    # Verificar que la suma sea ≈ 1.0
    suma_pesos = np.sum(pesos_completos)
    if abs(suma_pesos - 1.0) > 1e-6:
        print(f"ADVERTENCIA: La suma de pesos es {suma_pesos:.6f}, renormalizando...")
        pesos_completos = pesos_completos / suma_pesos
    
    # PASO 7: Cálculo de métricas finales
    print("Calculando métricas finales...")
    
    # Métricas de la cartera optimizada
    sharpe_final = resultado_opt['sharpe']
    rentabilidad_final = resultado_opt['rentabilidad']
    volatilidad_final = resultado_opt['volatilidad']
    
    metricas_cartera = {
        'sharpe': sharpe_final,
        'rentabilidad': rentabilidad_final,
        'volatilidad': volatilidad_final
    }
    
    # Comparación con baseline (equiponderada de 50 activos)
    pesos_eq_50 = np.ones(n_activos_total) / n_activos_total
    preparador_baseline = modulo1.PreparadorDatos(retornos, rf_anual=rf_anual)
    preparador_baseline.calcular_estadisticas()
    mu_baseline, Sigma_baseline, rf_baseline = preparador_baseline.obtener_estadisticas()
    
    mu_eq_50 = pesos_eq_50 @ mu_baseline
    sigma_eq_50 = np.sqrt(pesos_eq_50 @ Sigma_baseline @ pesos_eq_50)
    sharpe_eq_50 = (mu_eq_50 - rf_anual) / sigma_eq_50 if sigma_eq_50 > 0 else 0
    
    mejora_sharpe = sharpe_final - sharpe_eq_50
    mejora_rentabilidad = rentabilidad_final - mu_eq_50
    reduccion_volatilidad = sigma_eq_50 - volatilidad_final
    
    comparacion_baseline = {
        'sharpe_baseline': sharpe_eq_50,
        'rentabilidad_baseline': mu_eq_50,
        'volatilidad_baseline': sigma_eq_50,
        'mejora_sharpe': mejora_sharpe,
        'mejora_rentabilidad': mejora_rentabilidad,
        'reduccion_volatilidad': reduccion_volatilidad
    }
    
    # Detalles de selección
    detalles_seleccion = {
        'n_optimo_usado': n_optimo,
        'resultado_deteccion': resultado_n,
        'correlacion_promedio_seleccion': seleccion['correlacion_promedio_seleccion'],
        'sharpe_promedio_seleccion': seleccion['sharpe_promedio_seleccion'],
        'metodo_optimizacion': metodo_optimizacion,
        'peso_sharpe': peso_sharpe,
        'peso_decorrelacion': peso_decorrelacion
    }
    
    print("\nOptimización completada exitosamente")
    print(f"Sharpe Ratio final: {sharpe_final:.4f}")
    print(f"Rentabilidad esperada: {rentabilidad_final*100:.2f}%")
    print(f"Volatilidad: {volatilidad_final*100:.2f}%")
    
    return {
        'pesos_completos': pesos_completos,
        'activos_seleccionados': activos_seleccionados,
        'indices_seleccionados': indices_seleccionados,
        'n_activos_usados': n_optimo,
        'metricas_cartera': metricas_cartera,
        'comparacion_baseline': comparacion_baseline,
        'detalles_seleccion': detalles_seleccion
    }


def visualizar_seleccion_activos(resultado_seleccion, retornos_completos, ruta_guardado=None):
    """
    Crea visualización completa del proceso de selección y optimización.
    
    Genera figura con 4 subplots (2×2):
    1. Distribución de Pesos: barras con los 50 activos (seleccionados en azul, resto en gris)
    2. Métricas de Activos Seleccionados: scatter plot rendimiento vs volatilidad
    3. Matriz de Correlación de Seleccionados: heatmap de correlaciones
    4. Comparación de Fronteras: frontera de diversificación con puntos de carteras
    
    Parámetros:
    -----------
    resultado_seleccion : dict
        Diccionario retornado por optimizar_cartera_con_seleccion
    retornos_completos : pd.DataFrame
        DataFrame original de 50 activos
    ruta_guardado : str, optional
        Ruta para guardar la figura (opcional)
        
    Retorna:
    --------
    matplotlib.figure.Figure
        Figura con los gráficos
    """
    if resultado_seleccion is None:
        raise ValueError("El resultado de selección está vacío")
    
    pesos_completos = resultado_seleccion['pesos_completos']
    activos_seleccionados = resultado_seleccion['activos_seleccionados']
    indices_seleccionados = resultado_seleccion['indices_seleccionados']
    metricas_cartera = resultado_seleccion['metricas_cartera']
    
    # Crear figura con 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    ax1, ax2, ax3, ax4 = axes.flatten()
    
    # SUBPLOT 1: Distribución de Pesos
    n_activos_total = len(pesos_completos)
    activos_labels = [f'asset{i+1}' for i in range(n_activos_total)]
    
    # Colores: azul para seleccionados (peso > 0), gris para no seleccionados
    colores = ['blue' if i in indices_seleccionados else 'gray' for i in range(n_activos_total)]
    
    ax1.bar(range(n_activos_total), pesos_completos * 100, color=colores, alpha=0.7, edgecolor='black', linewidth=0.5)
    ax1.set_xlabel('Activos (asset1 a asset50)', fontsize=11)
    ax1.set_ylabel('Peso (%)', fontsize=11)
    ax1.set_title(f'Distribución de Pesos Finales (N={len(activos_seleccionados)} activos con peso > 0)', 
                  fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_xticks(range(0, n_activos_total, 5))
    ax1.set_xticklabels([activos_labels[i] for i in range(0, n_activos_total, 5)], rotation=45, ha='right')
    
    # SUBPLOT 2: Métricas de Activos Seleccionados (scatter plot)
    # Calcular métricas de todos los activos
    rf_anual = 0.02
    rf_diario = (1 + rf_anual)**(1/252) - 1
    media_diaria = retornos_completos.mean()
    std_diaria = retornos_completos.std()
    sharpe_individual = (media_diaria - rf_diario) / std_diaria * np.sqrt(252)
    
    rendimiento_anual = media_diaria * 252
    volatilidad_anual = std_diaria * np.sqrt(252)
    
    # Todos los activos (gris)
    ax2.scatter(volatilidad_anual * 100, rendimiento_anual * 100, 
               c='gray', alpha=0.3, s=50, label='Activos no seleccionados')
    
    # Activos seleccionados (rojo, tamaño proporcional al peso)
    volatilidades_seleccion = volatilidad_anual[activos_seleccionados] * 100
    rendimientos_seleccion = rendimiento_anual[activos_seleccionados] * 100
    pesos_seleccion = pesos_completos[indices_seleccionados] * 100
    
    ax2.scatter(volatilidades_seleccion, rendimientos_seleccion, 
               c='red', s=pesos_seleccion*5, alpha=0.7, edgecolors='black', linewidths=1.5,
               label='Activos seleccionados (tamaño = peso)')
    
    # Anotar nombres de activos seleccionados
    for i, activo in enumerate(activos_seleccionados):
        ax2.annotate(activo, (volatilidades_seleccion.iloc[i], rendimientos_seleccion.iloc[i]),
                    fontsize=8, alpha=0.7)
    
    ax2.set_xlabel('Volatilidad Anualizada (%)', fontsize=11)
    ax2.set_ylabel('Rendimiento Esperado Anualizado (%)', fontsize=11)
    ax2.set_title('Métricas de Activos: Rendimiento vs Volatilidad', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # SUBPLOT 3: Matriz de Correlación de Seleccionados
    retornos_seleccion = retornos_completos[activos_seleccionados]
    correlaciones_seleccion = retornos_seleccion.corr()
    
    im = ax3.imshow(correlaciones_seleccion.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    ax3.set_xticks(range(len(activos_seleccionados)))
    ax3.set_yticks(range(len(activos_seleccionados)))
    ax3.set_xticklabels(activos_seleccionados, rotation=45, ha='right', fontsize=8)
    ax3.set_yticklabels(activos_seleccionados, fontsize=8)
    ax3.set_title('Matriz de Correlación de Activos Seleccionados', fontsize=12, fontweight='bold')
    
    # Añadir valores numéricos
    for i in range(len(activos_seleccionados)):
        for j in range(len(activos_seleccionados)):
            texto = f'{correlaciones_seleccion.iloc[i, j]:.2f}'
            ax3.text(j, i, texto, ha='center', va='center', fontsize=7,
                    color='white' if abs(correlaciones_seleccion.iloc[i, j]) > 0.5 else 'black')
    
    plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    
    # SUBPLOT 4: Comparación de Fronteras (simplificado - mostrar puntos clave)
    # Punto verde: Cartera equiponderada de 50 activos
    pesos_eq_50 = np.ones(n_activos_total) / n_activos_total
    preparador_baseline = resultado_seleccion.get('detalles_seleccion', {}).get('comparacion_baseline', {})
    
    # Extraer métricas del baseline
    comparacion = resultado_seleccion['comparacion_baseline']
    vol_eq_50 = comparacion['volatilidad_baseline'] * 100
    rend_eq_50 = comparacion['rentabilidad_baseline'] * 100
    
    # Punto rojo: Cartera optimizada de N activos
    vol_opt = metricas_cartera['volatilidad'] * 100
    rend_opt = metricas_cartera['rentabilidad'] * 100
    
    ax4.scatter([vol_eq_50], [rend_eq_50], s=300, c='green', marker='o', 
               edgecolors='black', linewidths=2, label='Equiponderada 50 activos', zorder=5)
    ax4.scatter([vol_opt], [rend_opt], s=300, c='red', marker='*', 
               edgecolors='black', linewidths=2, label='Optimizada N activos', zorder=5)
    
    # Anotar métricas
    ax4.annotate(f'Sharpe: {comparacion["sharpe_baseline"]:.3f}', 
                xy=(vol_eq_50, rend_eq_50), xytext=(10, 10), 
                textcoords='offset points', fontsize=9, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    ax4.annotate(f'Sharpe: {metricas_cartera["sharpe"]:.3f}', 
                xy=(vol_opt, rend_opt), xytext=(10, -20), 
                textcoords='offset points', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
    
    ax4.set_xlabel('Volatilidad Anualizada (%)', fontsize=11)
    ax4.set_ylabel('Rendimiento Esperado Anualizado (%)', fontsize=11)
    ax4.set_title('Comparación de Carteras: Equiponderada vs Optimizada', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if ruta_guardado:
        plt.savefig(ruta_guardado, dpi=300, bbox_inches='tight')
        print(f"Figura guardada en: {ruta_guardado}")
    
    return fig


def comparar_estrategias(retornos, rf_anual=0.02):
    """
    Compara 3 estrategias: equiponderada 50, Markowitz 50, Selección+Markowitz N.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        Retornos diarios (días × 50 activos)
    rf_anual : float
        Tasa libre de riesgo anual (default: 0.02)
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con comparación de métricas de las 3 estrategias
    matplotlib.figure.Figure
        Figura con gráficos comparativos
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    # Importar módulos necesarios
    import importlib
    import sys
    
    # Importar módulo 1
    if '1datos' in sys.modules:
        modulo1 = sys.modules['1datos']
    else:
        try:
            modulo1 = importlib.import_module('1datos')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo1 = importlib.import_module('1datos')
    
    # Importar módulo 3
    if '3markowitz' in sys.modules:
        modulo3 = sys.modules['3markowitz']
    else:
        try:
            modulo3 = importlib.import_module('3markowitz')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo3 = importlib.import_module('3markowitz')
    
    resultados = {}
    
    # ESTRATEGIA 1: Equiponderada de 50 activos
    print("Estrategia 1: Cartera equiponderada de 50 activos...")
    n_activos_total = retornos.shape[1]
    pesos_eq_50 = np.ones(n_activos_total) / n_activos_total
    
    preparador = modulo1.PreparadorDatos(retornos, rf_anual=rf_anual)
    preparador.calcular_estadisticas()
    mu_total, Sigma_total, rf = preparador.obtener_estadisticas()
    
    mu_eq_50 = pesos_eq_50 @ mu_total
    sigma_eq_50 = np.sqrt(pesos_eq_50 @ Sigma_total @ pesos_eq_50)
    sharpe_eq_50 = (mu_eq_50 - rf_anual) / sigma_eq_50 if sigma_eq_50 > 0 else 0
    
    resultados['Equiponderada_50'] = {
        'sharpe': sharpe_eq_50,
        'rentabilidad': mu_eq_50,
        'volatilidad': sigma_eq_50,
        'n_activos': n_activos_total
    }
    
    # ESTRATEGIA 2: Markowitz sobre 50 activos
    print("Estrategia 2: Markowitz sobre 50 activos...")
    resultado_markowitz_50 = modulo3.optimizar_sharpe_maximo(mu_total, Sigma_total, rf)
    
    if resultado_markowitz_50 is not None:
        resultados['Markowitz_50'] = {
            'sharpe': resultado_markowitz_50['sharpe'],
            'rentabilidad': resultado_markowitz_50['rentabilidad'],
            'volatilidad': resultado_markowitz_50['volatilidad'],
            'n_activos': n_activos_total
        }
    else:
        print("ADVERTENCIA: Optimización Markowitz sobre 50 activos falló")
        resultados['Markowitz_50'] = {
            'sharpe': 0,
            'rentabilidad': 0,
            'volatilidad': 0,
            'n_activos': n_activos_total
        }
    
    # ESTRATEGIA 3: Selección + Markowitz sobre N activos
    print("Estrategia 3: Selección + Markowitz sobre N activos...")
    resultado_seleccion = optimizar_cartera_con_seleccion(
        retornos,
        rf_anual=rf_anual,
        n_optimo=None,  # Auto-detectar
        umbral_reduccion=2.0,
        metodo_optimizacion='max_sharpe'
    )
    
    resultados['Seleccion_Markowitz_N'] = {
        'sharpe': resultado_seleccion['metricas_cartera']['sharpe'],
        'rentabilidad': resultado_seleccion['metricas_cartera']['rentabilidad'],
        'volatilidad': resultado_seleccion['metricas_cartera']['volatilidad'],
        'n_activos': resultado_seleccion['n_activos_usados']
    }
    
    # Crear DataFrame comparativo
    df_comparacion = pd.DataFrame(resultados).T
    df_comparacion.columns = ['Sharpe Ratio', 'Rentabilidad (%)', 'Volatilidad (%)', 'N Activos']
    df_comparacion['Rentabilidad (%)'] = df_comparacion['Rentabilidad (%)'] * 100
    df_comparacion['Volatilidad (%)'] = df_comparacion['Volatilidad (%)'] * 100
    
    # Crear visualización comparativa
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    estrategias = df_comparacion.index.tolist()
    colores = ['green', 'blue', 'red']
    
    # Gráfico 1: Sharpe Ratio
    axes[0].bar(estrategias, df_comparacion['Sharpe Ratio'], color=colores, alpha=0.7, edgecolor='black')
    axes[0].set_ylabel('Sharpe Ratio', fontsize=11)
    axes[0].set_title('Comparación: Sharpe Ratio', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].tick_params(axis='x', rotation=15)
    
    # Gráfico 2: Rentabilidad
    axes[1].bar(estrategias, df_comparacion['Rentabilidad (%)'], color=colores, alpha=0.7, edgecolor='black')
    axes[1].set_ylabel('Rentabilidad Esperada (%)', fontsize=11)
    axes[1].set_title('Comparación: Rentabilidad', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].tick_params(axis='x', rotation=15)
    
    # Gráfico 3: Volatilidad
    axes[2].bar(estrategias, df_comparacion['Volatilidad (%)'], color=colores, alpha=0.7, edgecolor='black')
    axes[2].set_ylabel('Volatilidad (%)', fontsize=11)
    axes[2].set_title('Comparación: Volatilidad', fontsize=12, fontweight='bold')
    axes[2].grid(True, alpha=0.3, axis='y')
    axes[2].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    
    return df_comparacion, fig
