"""
5ANALISIS_MULTIPUNTO: ANÁLISIS MULTIPUNTO DE FRONTERA DE DIVERSIFICACIÓN
========================================================================

Este módulo extiende el análisis de diversificación para evaluar múltiples
puntos de interés a lo largo de la frontera, no solo el primero.

FUNCIONALIDADES:
- Detección de puntos relevantes en la frontera de diversificación
- Optimización de carteras para múltiples valores de N
- Consolidación y comparación de resultados
- Visualizaciones comparativas y heatmap de pesos
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# Nota: Las importaciones de módulos 1, 2, 3 y 4 se hacen dentro de funciones
# para evitar problemas de importación circular y permitir ejecución flexible


def detectar_puntos_interes_frontera(df_simulacion, criterios):
    """
    Detecta múltiples puntos de interés en la frontera de diversificación.
    
    Parámetros:
    -----------
    df_simulacion : pd.DataFrame
        DataFrame con columnas: n_activos, volatilidad_media, reduccion_pct,
        riesgo_especifico, riesgo_sistematico
    criterios : dict
        Diccionario de criterios. Claves esperadas:
        - 'umbral_reduccion': float (default: 2.0)
        - 'umbral_cambio_pendiente': float o None (default: None)
        
    Retorna:
    --------
    list
        Lista de valores N considerados puntos de interés, ordenada ascendentemente
    """
    if df_simulacion.empty:
        raise ValueError("El DataFrame de simulación está vacío")
    
    columnas_requeridas = {
        'n_activos', 'volatilidad_media', 'reduccion_pct',
        'riesgo_especifico', 'riesgo_sistematico'
    }
    if not columnas_requeridas.issubset(df_simulacion.columns):
        raise ValueError("El DataFrame de simulación no contiene las columnas requeridas")
    
    if criterios is None:
        criterios = {}
    
    umbral_reduccion = criterios.get('umbral_reduccion', 2.0)
    umbral_cambio_pendiente = criterios.get('umbral_cambio_pendiente', None)
    
    n_vals = df_simulacion['n_activos'].astype(int).values
    vol = df_simulacion['volatilidad_media'].values
    
    puntos_interes = set()
    
    # 1) Mínimos locales de volatilidad_media
    for i in range(1, len(vol) - 1):
        if vol[i] < vol[i - 1] and vol[i] < vol[i + 1]:
            puntos_interes.add(int(n_vals[i]))
    
    # 2) Puntos donde reduccion_pct < umbral
    reduccion = df_simulacion['reduccion_pct'].values
    idx_reduccion = np.where(reduccion < umbral_reduccion)[0]
    for idx in idx_reduccion:
        if not np.isnan(reduccion[idx]):
            puntos_interes.add(int(n_vals[idx]))
    
    # 3) Cambios de pendiente significativos
    if len(vol) >= 3:
        pendientes = np.diff(vol) / np.diff(n_vals)
        cambios_pendiente = np.diff(pendientes)
        
        if umbral_cambio_pendiente is None:
            # Umbral adaptativo basado en la variabilidad de cambios de pendiente
            umbral_cambio_pendiente = np.std(cambios_pendiente) if len(cambios_pendiente) > 0 else 0.0
        
        if umbral_cambio_pendiente > 0:
            idx_cambio = np.where(np.abs(cambios_pendiente) > umbral_cambio_pendiente)[0]
            for idx in idx_cambio:
                # idx corresponde al cambio entre puntos idx y idx+1 en pendientes
                puntos_interes.add(int(n_vals[idx + 1]))
    
    # Asegurar que se incluya el punto detectado por detectar_frontera_optima
    import importlib
    import sys
    if '2equiponderada_diversificacion' in sys.modules:
        modulo2 = sys.modules['2equiponderada_diversificacion']
    else:
        try:
            modulo2 = importlib.import_module('2equiponderada_diversificacion')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo2 = importlib.import_module('2equiponderada_diversificacion')
    
    n_optimo = modulo2.detectar_frontera_optima(df_simulacion, umbral_reduccion=umbral_reduccion)
    puntos_interes.add(int(n_optimo))
    
    return sorted(list(puntos_interes))


def optimizar_multiples_n(retornos, lista_n, rf_anual=0.02, peso_sharpe=0.7):
    """
    Optimiza carteras para múltiples valores de N usando el mismo pipeline
    de selección y optimización del módulo 4.
    
    Parámetros:
    -----------
    retornos : pd.DataFrame
        DataFrame completo de retornos (días × activos)
    lista_n : list
        Lista de valores N a evaluar
    rf_anual : float
        Tasa libre de riesgo anual (default: 0.02)
    peso_sharpe : float
        Peso del Sharpe en la selección (default: 0.7)
        
    Retorna:
    --------
    dict
        Diccionario con clave = N y valor = resultado completo de optimización
    """
    if retornos.empty:
        raise ValueError("El DataFrame de retornos está vacío")
    
    if not lista_n:
        raise ValueError("La lista de valores N está vacía")
    
    # Importar módulos necesarios (dinámicamente)
    import importlib
    import sys
    
    # Módulo 1 (datos)
    if '1datos' in sys.modules:
        modulo1 = sys.modules['1datos']
    else:
        try:
            modulo1 = importlib.import_module('1datos')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo1 = importlib.import_module('1datos')
    
    # Módulo 3 (markowitz)
    if '3markowitz' in sys.modules:
        modulo3 = sys.modules['3markowitz']
    else:
        try:
            modulo3 = importlib.import_module('3markowitz')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo3 = importlib.import_module('3markowitz')
    
    # Módulo 4 (selección)
    if '4seleccion_activos' in sys.modules:
        modulo4 = sys.modules['4seleccion_activos']
    else:
        try:
            modulo4 = importlib.import_module('4seleccion_activos')
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/src')
            modulo4 = importlib.import_module('4seleccion_activos')
    
    resultados = {}
    n_activos_total = retornos.shape[1]
    
    for n in lista_n:
        try:
            print(f"Optimizando cartera con N={n}...")
            
            # PASO 1: Selección de activos (mismo método que módulo 4)
            seleccion = modulo4.seleccionar_activos_por_sharpe_decorrelacion(
                retornos,
                n_activos=n,
                rf_anual=rf_anual,
                peso_sharpe=peso_sharpe,
                peso_decorrelacion=1.0 - peso_sharpe
            )
            
            activos_seleccionados = seleccion['activos_seleccionados']
            indices_seleccionados = seleccion['indices_seleccionados']
            
            # PASO 2: Filtrado de retornos
            retornos_filtrados = modulo4.filtrar_retornos_activos_seleccionados(
                retornos, activos_seleccionados
            )
            
            # PASO 3: Preparación para optimización
            preparador = modulo1.PreparadorDatos(retornos_filtrados, rf_anual=rf_anual)
            preparador.calcular_estadisticas()
            mu, Sigma, rf = preparador.obtener_estadisticas()
            
            # PASO 4: Optimización (máximo Sharpe)
            resultado_opt = modulo3.optimizar_sharpe_maximo(mu, Sigma, rf)
            if resultado_opt is None:
                raise ValueError("La optimización falló. Verifique los datos y parámetros.")
            
            pesos_optimizados = resultado_opt['w']
            peso_rf = resultado_opt.get('w_rf', 0.0)
            
            # PASO 5: Reconstrucción de vector de 50 posiciones
            pesos_completos = np.zeros(n_activos_total)
            for i, idx in enumerate(indices_seleccionados):
                pesos_completos[idx] = pesos_optimizados[i]
            
            suma_pesos = np.sum(pesos_completos)
            suma_objetivo = 1.0 - peso_rf
            if abs(suma_pesos - suma_objetivo) > 1e-6:
                print(
                    f"ADVERTENCIA: La suma de pesos en activos es {suma_pesos:.6f} "
                    f"(objetivo {suma_objetivo:.6f}), renormalizando..."
                )
                if suma_pesos > 0:
                    pesos_completos = pesos_completos * (suma_objetivo / suma_pesos)
            
            # PASO 6: Cálculo de métricas finales
            metricas_cartera = {
                'sharpe': resultado_opt['sharpe'],
                'rentabilidad': resultado_opt['rentabilidad'],
                'volatilidad': resultado_opt['volatilidad'],
                'peso_rf': peso_rf
            }
            
            # Comparación con baseline equiponderada (50 activos)
            pesos_eq_50 = np.ones(n_activos_total) / n_activos_total
            preparador_baseline = modulo1.PreparadorDatos(retornos, rf_anual=rf_anual)
            preparador_baseline.calcular_estadisticas()
            mu_baseline, Sigma_baseline, rf_baseline = preparador_baseline.obtener_estadisticas()
            
            mu_eq_50 = pesos_eq_50 @ mu_baseline
            sigma_eq_50 = np.sqrt(pesos_eq_50 @ Sigma_baseline @ pesos_eq_50)
            sharpe_eq_50 = (mu_eq_50 - rf_anual) / sigma_eq_50 if sigma_eq_50 > 0 else 0
            
            comparacion_baseline = {
                'sharpe_baseline': sharpe_eq_50,
                'rentabilidad_baseline': mu_eq_50,
                'volatilidad_baseline': sigma_eq_50,
                'mejora_sharpe': metricas_cartera['sharpe'] - sharpe_eq_50,
                'mejora_rentabilidad': metricas_cartera['rentabilidad'] - mu_eq_50,
                'reduccion_volatilidad': sigma_eq_50 - metricas_cartera['volatilidad']
            }
            
            detalles_seleccion = {
                'n_optimo_usado': n,
                'resultado_deteccion': None,
                'correlacion_promedio_seleccion': seleccion['correlacion_promedio_seleccion'],
                'sharpe_promedio_seleccion': seleccion['sharpe_promedio_seleccion'],
                'metodo_optimizacion': 'max_sharpe',
                'peso_sharpe': peso_sharpe,
                'peso_decorrelacion': 1.0 - peso_sharpe
            }
            
            resultados[n] = {
                'pesos_completos': pesos_completos,
                'activos_seleccionados': activos_seleccionados,
                'indices_seleccionados': indices_seleccionados,
                'n_activos_usados': n,
                'metricas_cartera': metricas_cartera,
                'comparacion_baseline': comparacion_baseline,
                'detalles_seleccion': detalles_seleccion,
                'peso_rf': peso_rf
            }
        except Exception as exc:
            print(f"ADVERTENCIA: Optimización falló para N={n}. Motivo: {exc}")
            resultados[n] = None
    
    return resultados


def consolidar_resultados_multipunto(resultados_dict):
    """
    Consolida resultados de múltiples optimizaciones en un DataFrame.
    
    Parámetros:
    -----------
    resultados_dict : dict
        Diccionario retornado por optimizar_multiples_n()
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame consolidado con métricas clave de cada cartera
    """
    if resultados_dict is None or len(resultados_dict) == 0:
        raise ValueError("El diccionario de resultados está vacío")
    
    filas = []
    for n, resultado in resultados_dict.items():
        if resultado is None:
            continue
        
        metricas = resultado['metricas_cartera']
        detalles = resultado['detalles_seleccion']
        activos = resultado['activos_seleccionados']
        
        filas.append({
            'n_activos': resultado['n_activos_usados'],
            'sharpe_cartera': metricas['sharpe'],
            'rentabilidad_anual': metricas['rentabilidad'],
            'volatilidad_anual': metricas['volatilidad'],
            'peso_rf': metricas['peso_rf'],
            'n_activos_con_peso': len(activos),
            'correlacion_avg': detalles['correlacion_promedio_seleccion'],
            'sharpe_avg_seleccion': detalles['sharpe_promedio_seleccion']
        })
    
    if not filas:
        raise ValueError("No hay resultados válidos para consolidar")
    
    df_consolidado = pd.DataFrame(filas)
    df_consolidado = df_consolidado.sort_values('sharpe_cartera', ascending=False).reset_index(drop=True)
    
    return df_consolidado


def visualizar_comparacion_multipunto(df_consolidado, resultados_dict, ruta_guardado=None):
    """
    Visualiza comparación de carteras optimizadas en múltiples puntos.
    
    Parámetros:
    -----------
    df_consolidado : pd.DataFrame
        DataFrame consolidado de resultados
    resultados_dict : dict
        Diccionario completo de resultados
    ruta_guardado : str, optional
        Ruta base (sin extensión) para guardar la figura
        
    Retorna:
    --------
    matplotlib.figure.Figure
        Figura con los 4 subplots
    """
    if df_consolidado.empty:
        raise ValueError("El DataFrame consolidado está vacío")
    
    n_vals = df_consolidado['n_activos'].astype(int).values
    sharpe_vals = df_consolidado['sharpe_cartera'].values
    rent_vals = df_consolidado['rentabilidad_anual'].values * 100
    vol_vals = df_consolidado['volatilidad_anual'].values * 100
    peso_rf_vals = df_consolidado['peso_rf'].values * 100
    
    idx_best = int(np.argmax(sharpe_vals))
    n_best = n_vals[idx_best]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    ax1, ax2, ax3, ax4 = axes.flatten()
    
    # Subplot 1: Barras Sharpe
    colores = ['orange' if n == n_best else 'steelblue' for n in n_vals]
    ax1.bar(n_vals, sharpe_vals, color=colores, alpha=0.8, edgecolor='black')
    ax1.set_xlabel('N Activos', fontsize=11)
    ax1.set_ylabel('Sharpe Ratio', fontsize=11)
    ax1.set_title('Comparación de Sharpe Ratio', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Subplot 2: Scatter rentabilidad vs volatilidad
    ax2.scatter(vol_vals, rent_vals, c='gray', s=80, alpha=0.7, edgecolors='black')
    for i, n in enumerate(n_vals):
        ax2.annotate(f'N={n}', (vol_vals[i], rent_vals[i]), textcoords='offset points',
                     xytext=(6, 4), fontsize=9)
    ax2.scatter([vol_vals[idx_best]], [rent_vals[idx_best]], s=200, c='red',
                marker='*', edgecolors='black', linewidths=1.5, label='Mejor Sharpe', zorder=5)
    ax2.set_xlabel('Volatilidad (%)', fontsize=11)
    ax2.set_ylabel('Rentabilidad (%)', fontsize=11)
    ax2.set_title('Rentabilidad vs Volatilidad', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Barras doble rentabilidad y volatilidad
    ancho = 0.35
    posiciones = np.arange(len(n_vals))
    ax3.bar(posiciones - ancho/2, rent_vals, width=ancho, color='blue', alpha=0.7,
            edgecolor='black', label='Rentabilidad (%)')
    ax3.bar(posiciones + ancho/2, vol_vals, width=ancho, color='red', alpha=0.7,
            edgecolor='black', label='Volatilidad (%)')
    ax3.set_xticks(posiciones)
    ax3.set_xticklabels([str(n) for n in n_vals])
    ax3.set_xlabel('N Activos', fontsize=11)
    ax3.set_title('Rentabilidad y Volatilidad por Cartera', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Subplot 4: Peso RF vs N
    ax4.plot(n_vals, peso_rf_vals, marker='o', linestyle='-', color='purple')
    ax4.set_xlabel('N Activos', fontsize=11)
    ax4.set_ylabel('Peso en RF (%)', fontsize=11)
    ax4.set_title('Peso en Renta Fija vs N', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if ruta_guardado:
        ruta = Path(ruta_guardado).with_suffix('.png')
        ruta.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig


def generar_heatmap_pesos(resultados_dict, top_activos=15, ruta_guardado=None):
    """
    Genera heatmap de pesos para los activos más utilizados globalmente.
    
    Parámetros:
    -----------
    resultados_dict : dict
        Diccionario con resultados de optimización
    top_activos : int
        Número de activos top a mostrar (default: 15)
    ruta_guardado : str, optional
        Ruta base (sin extensión) para guardar la figura
        
    Retorna:
    --------
    matplotlib.figure.Figure
        Figura del heatmap
    """
    if resultados_dict is None or len(resultados_dict) == 0:
        raise ValueError("El diccionario de resultados está vacío")
    
    # Filtrar resultados válidos
    resultados_validos = {k: v for k, v in resultados_dict.items() if v is not None}
    if not resultados_validos:
        raise ValueError("No hay resultados válidos para generar el heatmap")
    
    # Determinar activos top por suma de pesos absolutos
    primeros_resultado = next(iter(resultados_validos.values()))
    n_activos_total = len(primeros_resultado['pesos_completos'])
    activos_labels = [f'asset{i+1}' for i in range(n_activos_total)]
    
    suma_pesos = np.zeros(n_activos_total)
    for _, resultado in resultados_validos.items():
        suma_pesos += np.abs(resultado['pesos_completos'])
    
    indices_top = np.argsort(suma_pesos)[::-1][:top_activos]
    activos_top = [activos_labels[i] for i in indices_top]
    
    # Crear matriz de pesos (filas = carteras, columnas = activos top)
    n_sorted = sorted(resultados_validos.keys())
    matriz_pesos = []
    etiquetas_filas = []
    for n in n_sorted:
        resultado = resultados_validos[n]
        pesos = resultado['pesos_completos']
        matriz_pesos.append([pesos[i] for i in indices_top])
        etiquetas_filas.append(f'N={n}')
    
    df_heatmap = pd.DataFrame(matriz_pesos, index=etiquetas_filas, columns=activos_top)
    
    # Visualización con seaborn
    import seaborn as sns
    fig, ax = plt.subplots(figsize=(14, 8))
    vmax = df_heatmap.values.max() if df_heatmap.values.size > 0 else 0
    
    sns.heatmap(
        df_heatmap,
        ax=ax,
        cmap='YlOrRd',
        vmin=0,
        vmax=vmax,
        annot=True,
        fmt='.3f',
        linewidths=0.5,
        cbar_kws={'label': 'Peso'}
    )
    
    ax.set_title('Heatmap de Pesos por Cartera (Top Activos)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Activos', fontsize=11)
    ax.set_ylabel('Carteras', fontsize=11)
    
    plt.tight_layout()
    
    if ruta_guardado:
        ruta = Path(ruta_guardado).with_suffix('.png')
        ruta.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig
