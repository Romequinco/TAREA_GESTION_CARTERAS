import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')


class CarteraOptimaMercado:
    
    def __init__(self, datos_retornos, betas_df, caracteristicas_df, n_optimo):
        self.datos = datos_retornos
        self.betas = betas_df
        self.caracteristicas = caracteristicas_df
        self.n_optimo = n_optimo
        self.pesos = None
        
    def seleccionar_activos(self):
        df_combined = self.betas.copy()
        
        retornos_anualizados = self.datos.mean() * 252
        volatilidades = self.datos.std() * np.sqrt(252)
        sharpe = retornos_anualizados / volatilidades
        sharpe = sharpe.fillna(0)
        
        df_combined['Sharpe'] = sharpe.values
        df_combined['Volatilidad_Anualizada'] = volatilidades.values
        df_combined['Retorno_Anualizado'] = retornos_anualizados.values
        
        corr_matrix = self.datos.corr()
        correlaciones_promedio = corr_matrix.mean()
        df_combined['Correlacion_Promedio'] = correlaciones_promedio.values
        
        score = (0.4 * (df_combined['Sharpe'] - df_combined['Sharpe'].min()) / (df_combined['Sharpe'].max() - df_combined['Sharpe'].min()) +
                 0.3 * (df_combined['Volatilidad_Anualizada'].max() - df_combined['Volatilidad_Anualizada']) / (df_combined['Volatilidad_Anualizada'].max() - df_combined['Volatilidad_Anualizada'].min()) +
                 0.3 * (df_combined['Correlacion_Promedio'].max() - df_combined['Correlacion_Promedio']) / (df_combined['Correlacion_Promedio'].max() - df_combined['Correlacion_Promedio'].min()))
        
        df_combined['Score'] = score
        self.activos_seleccionados = df_combined.nlargest(self.n_optimo, 'Score')
        
        return self.activos_seleccionados
    
    def optimizar_pesos(self):
        activos_indices = self.activos_seleccionados['Activo'].values - 1
        datos_subset = self.datos.iloc[:, activos_indices]
        
        def portfolio_volatility(w):
            return np.sqrt(np.dot(w, np.dot(datos_subset.cov() * 252, w)))
        
        retornos_subset = datos_subset.mean() * 252
        def negative_sharpe(w):
            return -np.sum(w * retornos_subset) / portfolio_volatility(w)
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(len(activos_indices)))
        x0 = np.array([1.0 / len(activos_indices)] * len(activos_indices))
        
        result = minimize(negative_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        pesos_vector = np.zeros(60)
        pesos_vector[activos_indices] = result.x
        self.pesos = pesos_vector
        
        return pesos_vector


class CarteraAgresivaTech:
    
    def __init__(self, datos_retornos, betas_df, caracteristicas_df):
        self.datos = datos_retornos
        self.betas = betas_df
        self.caracteristicas = caracteristicas_df
        self.pesos = None
        
    def seleccionar_activos_tech(self):
        tech_sectors = ['Software & IT Services', 'Semiconductors & Semiconductors', 'Technology Hardware']
        activos_tech = self.betas[self.betas['Sector'].isin(tech_sectors) & (self.betas['Beta'] > 1.2)].copy()
        
        volatilidades = self.datos.std() * np.sqrt(252)
        activos_tech['Volatilidad_Anualizada'] = [volatilidades.iloc[int(a)-1] for a in activos_tech['Activo']]
        
        capitalizaciones = self.caracteristicas['CAPITALIZACIÓN'].values
        price_to_book = self.caracteristicas['PRICE_TO_BOOK'].values
        
        self.activos_tech = activos_tech.copy()
        self.activos_tech['Capitalizacion'] = [capitalizaciones[int(a)-1] if not pd.isna(capitalizaciones[int(a)-1]) else 0 for a in self.activos_tech['Activo']]
        self.activos_tech['PriceToBook'] = [price_to_book[int(a)-1] if not pd.isna(price_to_book[int(a)-1]) else 0 for a in self.activos_tech['Activo']]
        
        self.activos_tech = self.activos_tech.sort_values('Volatilidad_Anualizada')
        
        return self.activos_tech
    
    def optimizar_pesos(self):
        activos_indices = [int(a) - 1 for a in self.activos_tech['Activo'].values]
        datos_subset = self.datos.iloc[:, activos_indices]
        
        def portfolio_volatility(w):
            return np.sqrt(np.dot(w, np.dot(datos_subset.cov() * 252, w)))
        
        retornos_subset = datos_subset.mean() * 252
        
        def negative_sharpe(w):
            port_vol = portfolio_volatility(w)
            if port_vol == 0:
                return 1e10
            return -np.sum(w * retornos_subset) / port_vol
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(len(activos_indices)))
        x0 = np.array([1.0 / len(activos_indices)] * len(activos_indices))
        
        result = minimize(negative_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        pesos_vector = np.zeros(60)
        pesos_vector[activos_indices] = result.x
        self.pesos = pesos_vector
        
        return pesos_vector


class CarteraGrowthMomentum:
    
    def __init__(self, datos_retornos, betas_df, caracteristicas_df):
        self.datos = datos_retornos
        self.betas = betas_df
        self.caracteristicas = caracteristicas_df
        self.pesos = None
        
    def seleccionar_activos(self):
        retornos_anualizados = self.datos.mean() * 252
        
        ventana_momentum = 60
        datos_recent = self.datos.tail(ventana_momentum)
        retornos_momentum = (datos_recent.iloc[-1] - datos_recent.iloc[0]) / datos_recent.iloc[0]
        
        capitalizaciones = self.caracteristicas['CAPITALIZACIÓN'].values
        price_to_book = self.caracteristicas['PRICE_TO_BOOK'].values
        
        df_seleccion = self.betas.copy()
        df_seleccion['Retorno_Anualizado'] = retornos_anualizados.values
        df_seleccion['Momentum'] = retornos_momentum.values
        df_seleccion['Capitalizacion'] = capitalizaciones
        df_seleccion['PriceToBook'] = price_to_book
        
        tech_growth_sectors = ['Software & IT Services', 'Semiconductors & Semiconductors', 
                              'Specialty Retailers', 'Technology Hardware', 'Pharmaceuticals']
        df_filtered = df_seleccion[df_seleccion['Sector'].isin(tech_growth_sectors)].copy()
        
        df_filtered = df_filtered[df_filtered['Beta'] >= 0.8]
        
        score_growth_momentum = (0.35 * (df_filtered['Retorno_Anualizado'] - df_filtered['Retorno_Anualizado'].min()) / 
                                (df_filtered['Retorno_Anualizado'].max() - df_filtered['Retorno_Anualizado'].min()) +
                                0.35 * (df_filtered['Momentum'] - df_filtered['Momentum'].min()) / 
                                (df_filtered['Momentum'].max() - df_filtered['Momentum'].min()) +
                                0.30 * (df_filtered['Beta'] - df_filtered['Beta'].min()) / 
                                (df_filtered['Beta'].max() - df_filtered['Beta'].min()))
        
        df_filtered['Score'] = score_growth_momentum
        
        self.activos_growth = df_filtered.nlargest(8, 'Score')
        
        return self.activos_growth
    
    def optimizar_pesos(self):
        activos_indices = [int(a) - 1 for a in self.activos_growth['Activo'].values]
        datos_subset = self.datos.iloc[:, activos_indices]
        
        def portfolio_volatility(w):
            return np.sqrt(np.dot(w, np.dot(datos_subset.cov() * 252, w)))
        
        retornos_subset = datos_subset.mean() * 252
        
        def negative_sharpe(w):
            port_vol = portfolio_volatility(w)
            if port_vol == 0:
                return 1e10
            return -np.sum(w * retornos_subset) / port_vol
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(len(activos_indices)))
        x0 = np.array([1.0 / len(activos_indices)] * len(activos_indices))
        
        result = minimize(negative_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        pesos_vector = np.zeros(60)
        pesos_vector[activos_indices] = result.x
        self.pesos = pesos_vector
        
        return pesos_vector
