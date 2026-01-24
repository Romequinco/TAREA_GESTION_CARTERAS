"""
================================================================================
CALCULO DE BETAS - COMPETICION SABADO
================================================================================

Modulo para calcular las betas de cada activo con respecto al indice del mercado.

Beta mide la sensibilidad de un activo respecto a los movimientos del mercado:
- Beta > 1: Activo mas volatil que el mercado
- Beta = 1: Activo con volatilidad igual al mercado
- Beta < 1: Activo menos volatil que el mercado
- Beta < 0: Activo se mueve en direccion opuesta al mercado

Caracteristicas:
- Calculo de beta mediante regresion lineal
- Analisis de R-squared
- Identificacion de activos defensivos vs agresivos
- Visualizaciones

Autor: Oscar Romero
Fecha: Enero 2026

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


class CalculadorBetas:
    """
    Clase para calcular y analizar betas de activos.
    
    La beta es la pendiente de la regresion lineal:
    R_activo = alfa + beta * R_mercado + error
    
    Attributes:
    -----------
    retornos_activos : pd.DataFrame
        Retornos diarios de los 60 activos
    retornos_indice : pd.Series
        Retornos diarios del indice de mercado
    caracteristicas : pd.DataFrame
        Informacion adicional de los activos (sector, capitalizacion, etc)
    betas : pd.DataFrame
        Betas calculadas con estadisticas
    """
    
    def __init__(self, archivo_excel: str):
        """
        Inicializa el calculador cargando datos del Excel.
        
        Parameters:
        -----------
        archivo_excel : str
            Ruta al archivo Excel con 3 hojas:
            - Sheet1: Retornos diarios de activos
            - Hoja2: Caracteristicas de activos
            - Indice: Retornos del indice de mercado
        """
        print("[OK] Cargando datos del Excel...")
        
        # Cargar las 3 hojas
        self.retornos_activos = pd.read_excel(archivo_excel, sheet_name='Sheet1')
        self.caracteristicas = pd.read_excel(archivo_excel, sheet_name='Hoja2')
        self.retornos_indice = pd.read_excel(archivo_excel, sheet_name='Indice')['INDICE']
        
        # Renombrar columnas para claridad
        self.retornos_activos.columns = [f"Activo_{i}" for i in range(1, 61)]
        
        self.betas = None
        
        print(f"  Retornos activos: {self.retornos_activos.shape}")
        print(f"  Caracteristicas: {self.caracteristicas.shape}")
        print(f"  Retornos indice: {self.retornos_indice.shape}")
    
    
    def calcular_betas(self) -> pd.DataFrame:
        """
        Calcula la beta de cada activo mediante regresion lineal.
        
        Para cada activo:
        R_activo = alfa + beta * R_mercado + error
        
        Returns:
        --------
        pd.DataFrame
            DataFrame con betas y estadisticas de regresion
        """
        print("\n" + "="*80)
        print("CALCULO DE BETAS")
        print("="*80)
        
        resultados = []
        
        for i in range(1, 61):
            col_nombre = f"Activo_{i}"
            
            # Retornos del activo y el indice
            ret_activo = self.retornos_activos[col_nombre].values
            ret_indice = self.retornos_indice.values
            
            # Regresion lineal: activo = alfa + beta * indice
            # Usando scipy.stats.linregress para obtener estadisticas
            slope, intercept, r_value, p_value, std_err = stats.linregress(ret_indice, ret_activo)
            
            # Correlacion de Pearson
            corr = np.corrcoef(ret_indice, ret_activo)[0, 1]
            
            # Volatilidades
            vol_activo = np.std(ret_activo)
            vol_indice = np.std(ret_indice)
            
            # Beta alternativa: Cov(activo, indice) / Var(indice)
            cov = np.cov(ret_indice, ret_activo)[0, 1]
            var_indice = np.var(ret_indice)
            beta_alt = cov / var_indice
            
            resultados.append({
                'Activo': i,
                'Beta': slope,
                'Beta_Alternativa': beta_alt,
                'Alfa': intercept,
                'R_Squared': r_value**2,
                'Correlacion': corr,
                'Volatilidad_Activo': vol_activo,
                'Volatilidad_Indice': vol_indice,
                'P_Value': p_value,
                'Std_Error': std_err,
                'Ticker': self.caracteristicas.iloc[i-1]['Ticker'] if 'Ticker' in self.caracteristicas.columns else f"A{i}",
                'Sector': self.caracteristicas.iloc[i-1]['SECTOR'] if 'SECTOR' in self.caracteristicas.columns else 'N/A'
            })
        
        self.betas = pd.DataFrame(resultados)
        
        # Mostrar tabla resumen
        print("\n" + "="*80)
        print("TABLA RESUMEN: BETAS DE ACTIVOS")
        print("="*80)
        print(f"{'Act.':>3} | {'Beta':>7} | {'Alfa':>7} | {'R2':>6} | {'Corr':>6} | {'Vol Act.':>8} | {'Sector':>25}")
        print("-"*100)
        
        for _, row in self.betas.iterrows():
            print(f"{int(row['Activo']):3} | "
                  f"{row['Beta']:7.4f} | "
                  f"{row['Alfa']:7.5f} | "
                  f"{row['R_Squared']:6.3f} | "
                  f"{row['Correlacion']:6.3f} | "
                  f"{row['Volatilidad_Activo']:8.5f} | "
                  f"{row['Sector'][:25]:25}")
        
        print("-"*100)
        
        return self.betas
    
    
    def clasificar_activos(self):
        """
        Clasifica activos por su beta (defensivos vs agresivos).
        """
        if self.betas is None:
            raise ValueError("Debe calcular las betas primero")
        
        print("\n" + "="*80)
        print("CLASIFICACION DE ACTIVOS POR BETA")
        print("="*80)
        
        # Defensivos: beta < 0.8
        defensivos = self.betas[self.betas['Beta'] < 0.8].sort_values('Beta')
        
        # Neutral: 0.8 <= beta <= 1.2
        neutral = self.betas[(self.betas['Beta'] >= 0.8) & (self.betas['Beta'] <= 1.2)].sort_values('Beta')
        
        # Agresivos: beta > 1.2
        agresivos = self.betas[self.betas['Beta'] > 1.2].sort_values('Beta', ascending=False)
        
        # Negativos o muy bajos: beta < 0
        negativos = self.betas[self.betas['Beta'] < 0].sort_values('Beta')
        
        print(f"\nACTIVOS DEFENSIVOS (beta < 0.8): {len(defensivos)}")
        print("-"*50)
        if len(defensivos) > 0:
            for _, row in defensivos.head(10).iterrows():
                print(f"  Activo {int(row['Activo']):2} (Sector: {row['Sector'][:25]:25}): beta = {row['Beta']:7.4f}")
        else:
            print("  No hay activos defensivos")
        
        print(f"\nACTIVOS NEUTRALES (0.8 <= beta <= 1.2): {len(neutral)}")
        print("-"*50)
        if len(neutral) > 0:
            for _, row in neutral.head(10).iterrows():
                print(f"  Activo {int(row['Activo']):2} (Sector: {row['Sector'][:25]:25}): beta = {row['Beta']:7.4f}")
        else:
            print("  No hay activos neutrales")
        
        print(f"\nACTIVOS AGRESIVOS (beta > 1.2): {len(agresivos)}")
        print("-"*50)
        if len(agresivos) > 0:
            for _, row in agresivos.head(10).iterrows():
                print(f"  Activo {int(row['Activo']):2} (Sector: {row['Sector'][:25]:25}): beta = {row['Beta']:7.4f}")
        else:
            print("  No hay activos agresivos")
        
        if len(negativos) > 0:
            print(f"\nACTIVOS CON BETA NEGATIVA (beta < 0): {len(negativos)}")
            print("-"*50)
            for _, row in negativos.iterrows():
                print(f"  Activo {int(row['Activo']):2} (Sector: {row['Sector'][:25]:25}): beta = {row['Beta']:7.4f}")
        
        return {
            'defensivos': defensivos,
            'neutral': neutral,
            'agresivos': agresivos,
            'negativos': negativos
        }
    
    
    def visualizar_betas(self, figsize=(16, 10)):
        """
        Crea visualizaciones de las betas.
        
        Parameters:
        -----------
        figsize : tuple
            Tamanio de la figura
        """
        if self.betas is None:
            raise ValueError("Debe calcular las betas primero")
        
        print("\nGenerando visualizaciones...")
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Grafico 1: Distribucion de Betas
        ax1 = axes[0, 0]
        ax1.hist(self.betas['Beta'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
        ax1.axvline(1.0, color='red', linestyle='--', linewidth=2, label='beta=1 (Mercado)')
        ax1.axvline(self.betas['Beta'].mean(), color='green', linestyle='--', linewidth=2, label=f'Media: {self.betas["Beta"].mean():.3f}')
        ax1.set_xlabel('Beta', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frecuencia', fontsize=11, fontweight='bold')
        ax1.set_title('Distribucion de Betas', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Grafico 2: Beta vs R2
        ax2 = axes[0, 1]
        scatter = ax2.scatter(self.betas['Beta'], self.betas['R_Squared'], 
                             c=self.betas['Volatilidad_Activo'], cmap='viridis', 
                             s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax2.set_xlabel('Beta', fontsize=11, fontweight='bold')
        ax2.set_ylabel('R2 (Ajuste)', fontsize=11, fontweight='bold')
        ax2.set_title('Beta vs Calidad de Ajuste (color=Vol)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Volatilidad', fontsize=10)
        
        # Grafico 3: Betas ordenadas por valor
        ax3 = axes[1, 0]
        betas_sorted = self.betas.sort_values('Beta')
        colors = ['red' if b < 0.8 else 'gray' if b <= 1.2 else 'green' 
                 for b in betas_sorted['Beta']]
        ax3.barh(range(len(betas_sorted)), betas_sorted['Beta'], color=colors, alpha=0.7, edgecolor='black')
        ax3.axvline(1.0, color='black', linestyle='--', linewidth=2, label='beta=1')
        ax3.axvline(0.8, color='red', linestyle=':', linewidth=1.5, alpha=0.7, label='beta=0.8 (Defensivo)')
        ax3.axvline(1.2, color='green', linestyle=':', linewidth=1.5, alpha=0.7, label='beta=1.2 (Agresivo)')
        ax3.set_xlabel('Beta', fontsize=11, fontweight='bold')
        ax3.set_title('Betas Ordenadas (Rojo=Defensivo, Gris=Neutral, Verde=Agresivo)', fontsize=12, fontweight='bold')
        ax3.set_yticks([])
        ax3.legend(loc='lower right')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Grafico 4: Volatilidad Activo vs Volatilidad Indice (Beta como pendiente)
        ax4 = axes[1, 1]
        ax4.scatter(self.betas['Volatilidad_Indice'], self.betas['Volatilidad_Activo'],
                   s=100, alpha=0.6, edgecolors='black', linewidth=0.5, c='coral')
        
        # Linea de referencia (vol_activo = beta * vol_indice)
        vol_ind = self.betas['Volatilidad_Indice'].iloc[0]
        betas_sample = np.linspace(0, 2, 100)
        for beta_val in [0.5, 1.0, 1.5, 2.0]:
            x_vals = [vol_ind] * len(betas_sample)
            y_vals = beta_val * np.array(x_vals)
            if beta_val == 1.0:
                ax4.plot([0, max(self.betas['Volatilidad_Indice'])*1.1], 
                        [0, max(self.betas['Volatilidad_Indice'])*1.1], 
                        'k--', linewidth=2, label='beta=1', alpha=0.7)
        
        ax4.set_xlabel('Volatilidad del Indice', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Volatilidad del Activo', fontsize=11, fontweight='bold')
        ax4.set_title('Volatilidad: Activos vs Indice', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        plt.savefig('betas_analisis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("[OK] Visualizaciones guardadas: betas_analisis.png")
    
    
    def obtener_betas_por_sector(self):
        """
        Analiza las betas agrupadas por sector.
        """
        if self.betas is None:
            raise ValueError("Debe calcular las betas primero")
        
        print("\n" + "="*80)
        print("BETAS POR SECTOR")
        print("="*80)
        
        sectores_agrupados = self.betas.groupby('Sector')[['Beta', 'R_Squared', 'Volatilidad_Activo']].agg(['mean', 'std', 'count'])
        
        print("\nSectores con mas activos:")
        print(sectores_agrupados.sort_values(('Beta', 'count'), ascending=False).head(10))
        
        return sectores_agrupados
    
    
    def exportar_resultados(self, archivo_salida='competicion_sabado/notebooks/betas_resultados.csv'):
        """
        Exporta los resultados de las betas a un archivo CSV.
        
        Parameters:
        -----------
        archivo_salida : str
            Ruta del archivo de salida
        """
        if self.betas is None:
            raise ValueError("Debe calcular las betas primero")
        
        self.betas.to_csv(archivo_salida, index=False)
        print(f"\n[OK] Resultados exportados a: {archivo_salida}")


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("Modulo de Calculo de Betas")
    print("Uso:")
    print("  calculador = CalculadorBetas('data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv')")
    print("  betas = calculador.calcular_betas()")
    print("  clasificacion = calculador.clasificar_activos()")
    print("  calculador.visualizar_betas()")
