import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')


class EstrategiaBullMarket:
    
    def __init__(self, datos_retornos, betas_df):
        self.datos = datos_retornos
        self.betas = betas_df
        self.pesos = None
        self.activos_filtrados = None
        
    def calcular_momentum(self, ventana_corta=130, ventana_larga=252):
        momentum_6m = (self.datos.iloc[-1] - self.datos.iloc[-ventana_corta]) / self.datos.iloc[-ventana_corta]
        momentum_12m = (self.datos.iloc[-1] - self.datos.iloc[-ventana_larga]) / self.datos.iloc[-ventana_larga]
        
        return momentum_6m, momentum_12m
    
    def calcular_media_movil_200(self):
        sma_200 = self.datos.rolling(window=200).mean().iloc[-1]
        precio_actual = self.datos.iloc[-1]
        
        encima_sma = precio_actual > sma_200
        
        return encima_sma
    
    def calcular_retorno_relativo_benchmark(self, benchmark_col=None):
        if benchmark_col is None:
            benchmark_returns = self.datos.mean()
        else:
            benchmark_returns = self.datos.iloc[:, benchmark_col].mean()
        
        asset_returns = self.datos.mean()
        retorno_relativo = asset_returns - benchmark_returns
        
        return retorno_relativo > 0
    
    def filtrar_activos(self):
        momentum_6m, momentum_12m = self.calcular_momentum()
        encima_sma200 = self.calcular_media_movil_200()
        retorno_relativo_positivo = self.calcular_retorno_relativo_benchmark()
        
        criterios = (
            (momentum_6m > 0) & 
            (momentum_12m > 0) & 
            (encima_sma200) & 
            (retorno_relativo_positivo)
        )
        
        activos_filtrados_idx = np.where(criterios)[0]
        
        if len(activos_filtrados_idx) < 5:
            top_momentum = np.argsort(momentum_12m)[-10:]
            activos_filtrados_idx = top_momentum
        
        self.activos_filtrados = activos_filtrados_idx
        
        return activos_filtrados_idx
    
    def sharpe_ratio_bull(self, w, datos_subset, lambda_upside=1.2):
        retornos = datos_subset.mean() * 252
        volatilidad = np.sqrt(np.dot(w, np.dot(datos_subset.cov() * 252, w)))
        
        retorno_cartera = np.sum(w * retornos)
        
        upside_capture = retorno_cartera / volatilidad if volatilidad > 0 else 0
        
        return upside_capture * lambda_upside
    
    def optimizar_cartera_bull(self):
        if self.activos_filtrados is None:
            self.filtrar_activos()
        
        if len(self.activos_filtrados) == 0:
            self.activos_filtrados = np.arange(60)
        
        datos_subset = self.datos.iloc[:, self.activos_filtrados]
        retornos_subset = datos_subset.mean() * 252
        
        def neg_sharpe_bull(w):
            return -self.sharpe_ratio_bull(w, datos_subset)
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0.02, 0.5) for _ in range(len(self.activos_filtrados)))
        x0 = np.array([1.0 / len(self.activos_filtrados)] * len(self.activos_filtrados))
        
        result = minimize(neg_sharpe_bull, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        pesos_vector = np.zeros(60)
        pesos_vector[self.activos_filtrados] = result.x
        
        self.pesos = pesos_vector
        
        return pesos_vector
    
    def obtener_resumen(self):
        if self.pesos is None:
            self.optimizar_cartera_bull()
        
        activos_con_peso = [(i+1, self.pesos[i]) for i in range(60) if self.pesos[i] > 0.001]
        activos_con_peso.sort(key=lambda x: x[1], reverse=True)
        
        retornos_cartera = np.sum(self.pesos * self.datos.mean()) * 252
        vol_cartera = np.sqrt(np.dot(self.pesos, np.dot(self.datos.cov() * 252, self.pesos)))
        sharpe_cartera = retornos_cartera / vol_cartera if vol_cartera > 0 else 0
        
        return {
            'activos': activos_con_peso,
            'retorno_anualizado': retornos_cartera,
            'volatilidad': vol_cartera,
            'sharpe': sharpe_cartera,
            'n_activos': len(activos_con_peso)
        }
