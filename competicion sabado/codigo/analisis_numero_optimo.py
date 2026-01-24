"""
================================================================================
ANÁLISIS DE NÚMERO ÓPTIMO DE ACTIVOS - COMPETICIÓN SÁBADO
================================================================================

Módulo para detectar el número óptimo de activos mediante análisis de 
diversificación. Implementa frontera de diversificación y detección de punto 
de rendimientos decrecientes.

Características:
- Simulación de frontera de diversificación
- Detección de N óptimo automática
- Análisis de reducción marginal de volatilidad
- Visualizaciones de frontera

Autor: Oscar Romero
Fecha: Enero 2026

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, List
import warnings

warnings.filterwarnings('ignore')


class AnalisisNumeroOptimo:
    """
    Clase para analizar y determinar el número óptimo de activos.
    
    Attributes:
    -----------
    retornos : pd.DataFrame
        DataFrame con retornos de activos
    _frontera : pd.DataFrame
        Frontera de diversificación calculada
    """
    
    def __init__(self, retornos: pd.DataFrame):
        """
        Inicializa el análisis.
        
        Parameters:
        -----------
        retornos : pd.DataFrame
            DataFrame con retornos diarios de activos
        """
        self.retornos = retornos
        self._frontera = None
        
        print("\n[OK] Análisis de número óptimo inicializado")
        print(f"  Activos disponibles: {retornos.shape[1]}")
        print(f"  Observaciones: {retornos.shape[0]}")
    
    
    def simular_frontera_diversificacion(self, 
                                          n_valores: List[int] = None,
                                          n_simulaciones: int = 100) -> pd.DataFrame:
        """
        Simula la frontera de diversificación mediante Monte Carlo.
        
        Para cada N, se generan carteras equiponderadas aleatorias y se 
        calcula la volatilidad promedio.
        
        Parameters:
        -----------
        n_valores : List[int]
            Valores de N a probar. Default: [2,3,4,5,6,7,8,9,10,12,15,20,25,30,40,50]
        n_simulaciones : int
            Número de simulaciones por cada N
            
        Returns:
        --------
        pd.DataFrame
            Frontera de diversificación con estadísticas
        """
        if n_valores is None:
            n_valores = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50]
        
        # Limitar N a activos disponibles
        n_valores = [n for n in n_valores if n <= self.retornos.shape[1]]
        
        print("\n" + "="*80)
        print("SIMULACIÓN: FRONTERA DE DIVERSIFICACIÓN")
        print("="*80)
        print(f"Valores de N a probar: {n_valores}")
        print(f"Simulaciones por N: {n_simulaciones}")
        print(f"Total de simulaciones: {len(n_valores) * n_simulaciones}")
        print("-"*80)
        
        # Calcular matriz de covarianza
        cov_matrix = self.retornos.cov().values
        std_activos = self.retornos.std().values
        
        # Descomposición media de volatilidades y correlaciones
        vol_media = np.mean(std_activos)
        corr_matrix = self.retornos.corr().values
        
        # Extraer correlaciones fuera de diagonal
        corr_pares = corr_matrix[np.triu_indices_from(corr_matrix, k=1)]
        corr_media = np.mean(corr_pares)
        
        resultados = []
        
        for n in n_valores:
            print(f"\nProcesando N={n}...")
            
            vols_simuladas = []
            
            for sim in range(n_simulaciones):
                # Seleccionar N activos aleatorios
                indices = np.random.choice(self.retornos.shape[1], size=n, replace=False)
                
                # Cartera equiponderada
                pesos = np.ones(n) / n
                
                # Submatriz de covarianza
                cov_sub = cov_matrix[np.ix_(indices, indices)]
                
                # Volatilidad de cartera
                vol = np.sqrt(pesos @ cov_sub @ pesos)
                vols_simuladas.append(vol)
            
            # Estadísticas
            vol_media_n = np.mean(vols_simuladas)
            vol_std_n = np.std(vols_simuladas)
            
            # Descomposición de riesgo
            # σ²_p = (1/n)V̄ + (1-1/n)ρ̄ * σ̄
            var_especifico = (1/n) * (vol_media ** 2)
            var_sistematico = (1 - 1/n) * (corr_media * vol_media ** 2)
            
            # Reducción marginal respecto al anterior
            if resultados:
                reduccion = (resultados[-1]['volatilidad_media'] - vol_media_n) / resultados[-1]['volatilidad_media'] * 100
            else:
                reduccion = np.nan
            
            resultados.append({
                'n_activos': n,
                'volatilidad_media': vol_media_n,
                'volatilidad_std': vol_std_n,
                'riesgo_especifico_pct': np.sqrt(var_especifico) / vol_media_n * 100,
                'riesgo_sistematico_pct': np.sqrt(var_sistematico) / vol_media_n * 100,
                'reduccion_marginal_pct': reduccion
            })
        
        self._frontera = pd.DataFrame(resultados)
        
        print("\n" + "="*80)
        print("TABLA RESUMEN: FRONTERA DE DIVERSIFICACIÓN")
        print("="*80)
        print(f"{'N':>3} | {'Vol(%)':>7} | {'±Std':>6} | {'Esp(%)':>7} | {'Sis(%)':>7} | {'Reduc':>6}")
        print("-"*80)
        
        for _, row in self._frontera.iterrows():
            print(f"{int(row['n_activos']):3} | "
                  f"{row['volatilidad_media']*100:7.2f} | "
                  f"{row['volatilidad_std']*100:6.2f} | "
                  f"{row['riesgo_especifico_pct']:7.2f} | "
                  f"{row['riesgo_sistematico_pct']:7.2f} | "
                  f"{row['reduccion_marginal_pct']:6.2f}%")
        
        print("-"*80)
        
        return self._frontera
    
    
    def detectar_n_optimo(self, umbral_reduccion: float = 2.0) -> int:
        """
        Detecta automáticamente el N óptimo.
        
        El N óptimo es el punto donde la reducción marginal de volatilidad 
        cae por debajo del umbral especificado.
        
        Parameters:
        -----------
        umbral_reduccion : float
            Umbral de reducción marginal (%) bajo el cual N es considerado óptimo
            
        Returns:
        --------
        int
            Número óptimo de activos
        """
        if self._frontera is None:
            raise ValueError("Debe ejecutar simular_frontera_diversificacion() primero")
        
        print("\n" + "="*80)
        print("DETECCIÓN DE N ÓPTIMO")
        print("="*80)
        print(f"Umbral de reducción marginal: {umbral_reduccion:.1f}%\n")
        
        # Buscar primera N donde reducción < umbral
        frontera_util = self._frontera[self._frontera['reduccion_marginal_pct'].notna()]
        
        for _, row in frontera_util.iterrows():
            n = int(row['n_activos'])
            reduc = row['reduccion_marginal_pct']
            
            if reduc < umbral_reduccion:
                print(f"[OK] N={n} es optimo (reduccion: {reduc:.2f}% < {umbral_reduccion:.1f}%)")
                
                # Mostrar contexto
                print(f"\nContexto:")
                print(f"  - Volatilidad en N={n}: {row['volatilidad_media']*100:.2f}%")
                print(f"  - Riesgo específico: {row['riesgo_especifico_pct']:.2f}%")
                print(f"  - Riesgo sistemático: {row['riesgo_sistematico_pct']:.2f}%")
                
                # Comparación con N+1
                siguiente = frontera_util[frontera_util['n_activos'] > n]
                if not siguiente.empty:
                    siguiente_row = siguiente.iloc[0]
                    mejora = (row['volatilidad_media'] - siguiente_row['volatilidad_media']) / row['volatilidad_media'] * 100
                    print(f"  - Mejora posible sumando activos: {mejora:.2f}%")
                
                return n
        
        # Si no se encuentra umbral, retornar el máximo
        n_optimo = int(self._frontera.iloc[-1]['n_activos'])
        print(f"Ningún N supera el umbral. Retornando máximo: N={n_optimo}")
        return n_optimo
    
    
    def visualizar_frontera(self, figsize: Tuple[int, int] = (14, 5)):
        """
        Visualiza la frontera de diversificación.
        
        Parameters:
        -----------
        figsize : Tuple
            Tamaño de la figura
        """
        if self._frontera is None:
            raise ValueError("Debe ejecutar simular_frontera_diversificacion() primero")
        
        print("\nGenerando visualizaciones...")
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Gráfico 1: Volatilidad vs N
        ax1 = axes[0]
        ax1.plot(self._frontera['n_activos'], self._frontera['volatilidad_media']*100,
                'o-', linewidth=2, markersize=8, color='#1f77b4', label='Volatilidad Media')
        ax1.fill_between(self._frontera['n_activos'], 
                         (self._frontera['volatilidad_media'] - self._frontera['volatilidad_std'])*100,
                         (self._frontera['volatilidad_media'] + self._frontera['volatilidad_std'])*100,
                         alpha=0.2, color='#1f77b4')
        ax1.set_xlabel('Número de Activos (N)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Volatilidad (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Frontera de Diversificación: Volatilidad vs N', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Gráfico 2: Reducción marginal vs N
        ax2 = axes[1]
        reduccion_no_nan = self._frontera[self._frontera['reduccion_marginal_pct'].notna()]
        ax2.plot(reduccion_no_nan['n_activos'], reduccion_no_nan['reduccion_marginal_pct'],
                'o-', linewidth=2, markersize=8, color='#ff7f0e', label='Reducción Marginal')
        ax2.axhline(y=2, color='r', linestyle='--', linewidth=2, label='Umbral 2%')
        ax2.set_xlabel('Número de Activos (N)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Reducción Marginal (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Reducción Marginal de Volatilidad', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('analisis_numero_optimo.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ Visualizaciones guardadas: analisis_numero_optimo.png")
    
    
    def resumen_analisis(self):
        """
        Imprime un resumen completo del análisis.
        """
        if self._frontera is None:
            raise ValueError("Debe ejecutar simular_frontera_diversificacion() primero")
        
        print("\n" + "="*80)
        print("RESUMEN DEL ANÁLISIS DE NÚMERO ÓPTIMO")
        print("="*80)
        
        n_optimo = self.detectar_n_optimo()
        
        row_optima = self._frontera[self._frontera['n_activos'] == n_optimo].iloc[0]
        row_maxima = self._frontera.iloc[-1]
        
        print(f"\n📊 HALLAZGOS PRINCIPALES:")
        print(f"  • N óptimo: {n_optimo} activos")
        print(f"  • Volatilidad óptima: {row_optima['volatilidad_media']*100:.2f}%")
        print(f"  • Riesgo específico: {row_optima['riesgo_especifico_pct']:.2f}%")
        print(f"  • Riesgo sistemático: {row_optima['riesgo_sistematico_pct']:.2f}%")
        
        mejora_total = (row_maxima['volatilidad_media'] - row_optima['volatilidad_media']) / row_maxima['volatilidad_media'] * 100
        print(f"\n💡 IMPLICACIONES:")
        print(f"  • Complejidad adicional para N>{n_optimo}: NO JUSTIFICADA")
        print(f"  • Mejora adicional añadiendo hasta N=50: {mejora_total:.2f}%")
        print(f"  • Conclusión: {n_optimo} activos es prácticamente óptimo")
        
        print(f"\n🎯 RECOMENDACIÓN:")
        print(f"  Usar {n_optimo} activos para optimización posterior")
        print(f"  (Más activos aumentan complejidad sin beneficio significativo)")
        
        print("="*80 + "\n")
        
        return n_optimo


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("Módulo de Análisis de Número Óptimo")
    print("Uso: analizador = AnalisisNumeroOptimo(retornos)")
    print("     analizador.simular_frontera_diversificacion()")
    print("     n_optimo = analizador.detectar_n_optimo()")
