import numpy as np
import pandas as pd
from pathlib import Path
import cvxpy as cp


class OptimizacionMultifactorial:
    
    def __init__(self, file_path, start_t=750, beta_min=1.2, annualization=252, 
                 ridge=1e-6, sigma_target=0.175, alpha_prefs=None):
        
        self.file_path = Path(file_path)
        self.START_T = start_t
        self.BETA_MIN = beta_min
        self.ANNUALIZATION = annualization
        self.RIDGE = ridge
        self.SIGMA_TARGET = sigma_target
        
        if alpha_prefs is None:
            alpha_prefs = {
                "Value": 0.40,
                "Momentum": 0.30,
                "Size": -0.20,
                "Beta": 0.10
            }
        self.ALPHA_PREFS = alpha_prefs
        
        self.SOLVER = self._pick_conic_solver()
        
        self.R_full = None
        self.rm_full = None
        self.meta = None
        self.R = None
        self.meta_sub = None
        self.X = None
        self.Sigma = None
        self.L = None
        self.alpha_score = None
        self.eligible_tickers = None
        self.w_opt = None
        self.results = None
        
    def _pick_conic_solver(self):
        installed = cp.installed_solvers()
        if "CLARABEL" in installed: return cp.CLARABEL
        if "SCS" in installed: return cp.SCS
        return cp.ECOS
    
    def cargar_datos(self):
        ret_df = pd.read_excel(self.file_path, sheet_name="Sheet1", engine="openpyxl")
        meta = pd.read_excel(self.file_path, sheet_name="Hoja2", engine="openpyxl")
        mkt = pd.read_excel(self.file_path, sheet_name="Indice", engine="openpyxl")
        
        ret_df.columns = [int(c) for c in ret_df.columns]
        meta["Ticker"] = meta["Ticker"].astype(int)
        mkt_r = pd.to_numeric(mkt["INDICE"], errors="coerce")
        
        R_full = ret_df.iloc[self.START_T:].copy()
        rm_full = mkt_r.iloc[self.START_T:].copy()
        T = min(len(R_full), len(rm_full))
        R_full = R_full.iloc[:T, :]
        rm_full = rm_full.iloc[:T]
        
        self.R_full = R_full
        self.rm_full = rm_full
        self.meta = meta
        
        return R_full, rm_full, meta
    
    def get_zscore(self, series):
        return (series - series.mean()) / series.std()
    
    def beta_vs_market(self, asset_r, market_r):
        aligned = pd.concat([asset_r, market_r], axis=1).dropna()
        if len(aligned) < 20: return np.nan
        return aligned.iloc[:, 0].cov(aligned.iloc[:, 1]) / aligned.iloc[:, 1].var()
    
    def calcular_factores(self):
        all_betas = self.R_full.apply(lambda s: self.beta_vs_market(s, self.rm_full))
        
        self.eligible_tickers = all_betas[all_betas >= self.BETA_MIN].index
        self.R = self.R_full[self.eligible_tickers]
        self.meta_sub = self.meta[self.meta["Ticker"].isin(self.eligible_tickers)].set_index("Ticker")
        
        signals = pd.DataFrame(index=self.eligible_tickers)
        signals["Beta"] = all_betas[self.eligible_tickers]
        
        pb = self.meta_sub["PRICE_TO_BOOK"].where(self.meta_sub["PRICE_TO_BOOK"] > 0.1, np.nan)
        signals["Value"] = 1.0 / pb
        
        signals["Size"] = np.log(self.meta_sub["CAPITALIZACIÓN"] / 1e9)
        
        signals["Momentum"] = self.R.iloc[-252:-20].apply(lambda x: (1 + x).prod() - 1)
        
        self.X = pd.DataFrame(index=self.eligible_tickers)
        self.X["Value"] = self.get_zscore(signals["Value"])
        self.X["Momentum"] = self.get_zscore(signals["Momentum"])
        self.X["Size"] = self.get_zscore(signals["Size"])
        self.X["Beta"] = signals["Beta"]
        
        self.X = self.X.fillna(0)
        
        return self.X, signals
    
    def preparar_optimizacion(self):
        n = len(self.eligible_tickers)
        Sigma = self.R.cov().values * self.ANNUALIZATION
        Sigma = Sigma + self.RIDGE * np.eye(n)
        L = np.linalg.cholesky(Sigma)
        
        alpha_vec = np.array([self.ALPHA_PREFS[col] for col in self.X.columns])
        alpha_score = self.X.values @ alpha_vec
        
        self.Sigma = Sigma
        self.L = L
        self.alpha_score = alpha_score
        
        return Sigma, L, alpha_score
    
    def optimizar(self):
        n = len(self.eligible_tickers)
        
        w = cp.Variable(n)
        
        constraints = [
            cp.sum(w) == 1,
            w >= 0,
            cp.norm(self.L @ w, 2) <= self.SIGMA_TARGET
        ]
        
        prob = cp.Problem(cp.Maximize(self.alpha_score @ w), constraints)
        prob.solve(solver=self.SOLVER)
        
        if prob.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(f"Falla en optimización: {prob.status}")
        
        w_opt = np.maximum(w.value, 0)
        w_opt /= w_opt.sum()
        
        self.w_opt = w_opt
        
        return w_opt
    
    def calcular_metricas(self):
        vol_p = np.sqrt(self.w_opt @ self.Sigma @ self.w_opt)
        exp_value = self.w_opt @ self.X["Value"]
        exp_mom = self.w_opt @ self.X["Momentum"]
        exp_size = self.w_opt @ self.X["Size"]
        beta_p = self.w_opt @ self.X["Beta"]
        
        self.results = {
            "vol_p": vol_p,
            "exp_value": exp_value,
            "exp_mom": exp_mom,
            "exp_size": exp_size,
            "beta_p": beta_p,
            "n_activos": len(self.eligible_tickers)
        }
        
        return self.results
    
    def get_pesos_detallados(self):
        df_w = pd.DataFrame({
            "Ticker": self.eligible_tickers,
            "Weight": self.w_opt,
            "Weight_Pct": self.w_opt * 100,
            "Score": self.alpha_score,
            "Sector": [self.meta_sub.loc[t, "SECTOR"] for t in self.eligible_tickers]
        }).sort_values("Weight", ascending=False)
        
        return df_w
    
    def printear_resultados(self):
        print("\n" + "="*60)
        print("CARTERA MULTIFACTORIAL OPTIMIZADA")
        print("="*60)
        print(f"Activos elegibles (Beta >= {self.BETA_MIN}): {self.results['n_activos']}")
        print(f"Volatilidad Realizada: {self.results['vol_p']*100:.2f}% (Target: {self.SIGMA_TARGET*100:.2f}%)")
        print(f"Beta Cartera: {self.results['beta_p']:.3f}")
        print(f"\nExposiciones Factoriales (z-scores):")
        print(f"  Value:    {self.results['exp_value']:+.3f}")
        print(f"  Momentum: {self.results['exp_mom']:+.3f}")
        print(f"  Size:     {self.results['exp_size']:+.3f}")
        print("="*60)
    
    def ejecutar_completo(self):
        print("[1] Cargando datos...")
        self.cargar_datos()
        
        print("[2] Calculando factores...")
        self.calcular_factores()
        
        print("[3] Preparando optimización...")
        self.preparar_optimizacion()
        
        print("[4] Optimizando cartera...")
        self.optimizar()
        
        print("[5] Calculando métricas...")
        self.calcular_metricas()
        
        print("[OK] Optimización completada")
        
        return self.w_opt, self.results
