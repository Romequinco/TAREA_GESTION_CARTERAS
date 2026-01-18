"""
2EQUIPONDERADA_DIVERSIFICACION: ANÁLISIS DE CARTERAS EQUIPONDERADAS Y DIVERSIFICACIÓN
=======================================================================================

Este módulo se encarga del análisis de carteras equiponderadas y el efecto de la diversificación.

FUNCIONALIDADES:
- Análisis de cartera equiponderada (descomposición de riesgo)
- Simulación de frontera eficiente de diversificación
- Detección del número óptimo de activos
- Análisis de contribuciones individuales de activos
- Visualización de frontera de diversificación

CÓMO FUNCIONA:
1. Descompone el riesgo de carteras equiponderadas en componentes sistemáticos y específicos
2. Simula el efecto de diversificación variando el número de activos
3. Identifica el número óptimo de activos necesario para alcanzar el límite práctico
4. Analiza la contribución de cada activo al rendimiento y riesgo de la cartera
5. Visualiza los resultados con gráficos informativos
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


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
