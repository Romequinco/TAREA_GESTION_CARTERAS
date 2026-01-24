import sys
sys.path.insert(0, './competicion sabado/codigo')
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')

datos_retornos = pd.read_excel('./data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv', sheet_name='Sheet1')
datos_retornos.columns = [f'Activo_{i}' for i in range(1, 61)]
betas_df = pd.read_csv('./competicion sabado/betas_resultados.csv')

def optimize_cartera_con_minimo(datos_subset, peso_minimo=0.05):
    retornos_subset = datos_subset.mean() * 252
    
    def neg_sharpe(w):
        port_ret = np.sum(w * retornos_subset)
        port_vol = np.sqrt(np.dot(w, np.dot(datos_subset.cov() * 252, w)))
        if port_vol <= 0:
            return 1e10
        return -port_ret / port_vol
    
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'ineq', 'fun': lambda w: w - peso_minimo}
    ]
    bounds = tuple((peso_minimo, 1) for _ in range(datos_subset.shape[1]))
    x0 = np.array([1.0 / datos_subset.shape[1]] * datos_subset.shape[1])
    
    result = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

print('[CARTERA 1: OPTIMA MERCADO - 8 ACTIVOS]')
retornos_anualizados = datos_retornos.mean() * 252
volatilidades = datos_retornos.std() * np.sqrt(252)
sharpe = retornos_anualizados / volatilidades
sharpe = sharpe.fillna(0)

df_ranking = betas_df.copy()
df_ranking['Sharpe'] = sharpe.values
df_ranking['Volatilidad_Anualizada'] = volatilidades.values

corr_matrix = datos_retornos.corr()
correlaciones_promedio = corr_matrix.mean()
df_ranking['Correlacion_Promedio'] = correlaciones_promedio.values

score = (0.4 * (df_ranking['Sharpe'] - df_ranking['Sharpe'].min()) / (df_ranking['Sharpe'].max() - df_ranking['Sharpe'].min()) +
         0.3 * (df_ranking['Volatilidad_Anualizada'].max() - df_ranking['Volatilidad_Anualizada']) / (df_ranking['Volatilidad_Anualizada'].max() - df_ranking['Volatilidad_Anualizada'].min()) +
         0.3 * (df_ranking['Correlacion_Promedio'].max() - df_ranking['Correlacion_Promedio']) / (df_ranking['Correlacion_Promedio'].max() - df_ranking['Correlacion_Promedio'].min()))

df_ranking['Score'] = score
activos_c1 = df_ranking.nlargest(8, 'Score')['Activo'].values - 1

datos_c1 = datos_retornos.iloc[:, activos_c1]
pesos_c1_subset = optimize_cartera_con_minimo(datos_c1)
pesos_c1 = np.zeros(60)
pesos_c1[activos_c1] = pesos_c1_subset

w1_display = [(int(idx+1), pesos_c1[idx]) for idx in activos_c1]
w1_display.sort(key=lambda x: x[1], reverse=True)
print(f'Activos: {sorted([a for a, _ in w1_display])}')
for a, w in w1_display:
    print(f'  Activo {a:2d}: {w:.6f}')
print(f'Suma pesos: {sum([w for _, w in w1_display]):.6f}')

print('\n[CARTERA 2: AGRESIVA TECH - 8 ACTIVOS]')
tech_sectors = ['Software & IT Services', 'Semiconductors & Semiconductors']
activos_tech = betas_df[betas_df['Sector'].isin(tech_sectors)]['Activo'].values - 1

if len(activos_tech) < 8:
    non_tech = betas_df[~betas_df['Sector'].isin(tech_sectors)]['Activo'].values - 1
    tech_vols = [(i, volatilidades.iloc[i]) for i in activos_tech]
    non_tech_vols = [(i, volatilidades.iloc[i]) for i in non_tech]
    non_tech_vols.sort(key=lambda x: x[1])
    
    activos_c2 = [x[0] for x in tech_vols] + [x[0] for x in non_tech_vols[:8-len(activos_tech)]]
else:
    tech_vols = [(i, volatilidades.iloc[i]) for i in activos_tech]
    tech_vols.sort(key=lambda x: x[1])
    activos_c2 = [x[0] for x in tech_vols[:8]]

datos_c2 = datos_retornos.iloc[:, activos_c2]
pesos_c2_subset = optimize_cartera_con_minimo(datos_c2)
pesos_c2 = np.zeros(60)
pesos_c2[activos_c2] = pesos_c2_subset

w2_display = [(int(idx+1), pesos_c2[idx]) for idx in activos_c2]
w2_display.sort(key=lambda x: x[1], reverse=True)
print(f'Activos: {sorted([a for a, _ in w2_display])}')
for a, w in w2_display:
    print(f'  Activo {a:2d}: {w:.6f}')
print(f'Suma pesos: {sum([w for _, w in w2_display]):.6f}')

print('\n[CARTERA 3: GROWTH+MOMENTUM - 8 ACTIVOS]')
ventana_momentum = 60
datos_recent = datos_retornos.tail(ventana_momentum)
retornos_momentum = (datos_recent.iloc[-1] - datos_recent.iloc[0]) / (datos_recent.iloc[0] + 1e-10)

tech_growth_sectors = ['Software & IT Services', 'Semiconductors & Semiconductors', 'Specialty Retailers', 'Technology Hardware', 'Pharmaceuticals']
df_gm = betas_df[betas_df['Sector'].isin(tech_growth_sectors)].copy()
df_gm['Momentum'] = [retornos_momentum.iloc[int(a)-1] for a in df_gm['Activo']]

if len(df_gm) >= 8:
    score_gm = (0.5 * (df_gm['Momentum'].rank(pct=True)) + 0.5 * (df_gm['Beta'].rank(pct=True)))
    df_gm['Score'] = score_gm
    activos_c3 = df_gm.nlargest(8, 'Score')['Activo'].values - 1
else:
    activos_c3 = df_gm['Activo'].values - 1
    si_falta = 8 - len(activos_c3)
    activos_no_gm = betas_df[~betas_df['Sector'].isin(tech_growth_sectors)]['Activo'].values - 1
    activos_adicionales = np.random.choice(activos_no_gm, min(si_falta, len(activos_no_gm)), replace=False)
    activos_c3 = np.concatenate([activos_c3, activos_adicionales])[:8]

datos_c3 = datos_retornos.iloc[:, activos_c3]
pesos_c3_subset = optimize_cartera_con_minimo(datos_c3)
pesos_c3 = np.zeros(60)
pesos_c3[activos_c3] = pesos_c3_subset

w3_display = [(int(idx+1), pesos_c3[idx]) for idx in activos_c3]
w3_display.sort(key=lambda x: x[1], reverse=True)
print(f'Activos: {sorted([a for a, _ in w3_display])}')
for a, w in w3_display:
    print(f'  Activo {a:2d}: {w:.6f}')
print(f'Suma pesos: {sum([w for _, w in w3_display]):.6f}')

print('\n[EXPORTANDO VECTORES]')
df_vectores = pd.DataFrame({
    'Cartera_Optima_Mercado': pesos_c1,
    'Cartera_Agresiva_Tech': pesos_c2,
    'Cartera_Growth_Momentum': pesos_c3
})
df_vectores.to_csv('./competicion sabado/vectores_pesos_carteras.csv', index=False)
print('[OK] Vectores guardados: vectores_pesos_carteras.csv')
