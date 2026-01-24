import sys
sys.path.insert(0, './competicion sabado/codigo')
import pandas as pd
import numpy as np
from construccion_carteras import CarteraOptimaMercado, CarteraAgresivaTech, CarteraGrowthMomentum
from analisis_numero_optimo import AnalisisNumeroOptimo

datos_retornos = pd.read_excel('./data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv', sheet_name='Sheet1')
datos_retornos.columns = [f'Activo_{i}' for i in range(1, 61)]
betas_df = pd.read_csv('./competicion sabado/betas_resultados.csv')
caracteristicas_df = pd.read_excel('./data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv', sheet_name='Hoja2')

print('[CARGANDO]')
analizador = AnalisisNumeroOptimo(datos_retornos)
df_frontera = analizador.simular_frontera_diversificacion(n_valores=[2,3,4,5,6,7,8,9,10], n_simulaciones=50)
n_optimo = analizador.detectar_n_optimo(umbral_reduccion=2.0)
print(f'[OK] N optimo: {n_optimo}\n')

print('[CARTERA 1: OPTIMA MERCADO]')
cartera1 = CarteraOptimaMercado(datos_retornos, betas_df, caracteristicas_df, n_optimo)
activos1 = cartera1.seleccionar_activos()
pesos1 = cartera1.optimizar_pesos()
w1_nonzero = [(i+1, pesos1[i]) for i in range(60) if pesos1[i] > 0.001]
w1_nonzero.sort(key=lambda x: x[1], reverse=True)
print(f'Activos: {[a for a, _ in w1_nonzero]}')
for a, w in w1_nonzero[:5]:
    print(f'  Activo {a}: {w:.6f}')

print('\n[CARTERA 2: AGRESIVA TECH]')
cartera2 = CarteraAgresivaTech(datos_retornos, betas_df, caracteristicas_df)
activos2 = cartera2.seleccionar_activos_tech()
pesos2 = cartera2.optimizar_pesos()
w2_nonzero = [(i+1, pesos2[i]) for i in range(60) if pesos2[i] > 0.001]
w2_nonzero.sort(key=lambda x: x[1], reverse=True)
print(f'Activos: {[a for a, _ in w2_nonzero]}')
for a, w in w2_nonzero[:5]:
    print(f'  Activo {a}: {w:.6f}')

print('\n[CARTERA 3: GROWTH+MOMENTUM]')
cartera3 = CarteraGrowthMomentum(datos_retornos, betas_df, caracteristicas_df)
activos3 = cartera3.seleccionar_activos()
pesos3 = cartera3.optimizar_pesos()
w3_nonzero = [(i+1, pesos3[i]) for i in range(60) if pesos3[i] > 0.001]
w3_nonzero.sort(key=lambda x: x[1], reverse=True)
print(f'Activos: {[a for a, _ in w3_nonzero]}')
for a, w in w3_nonzero[:5]:
    print(f'  Activo {a}: {w:.6f}')

print('\n[EXPORTANDO VECTORES]')
df_vectores = pd.DataFrame({
    'Cartera_Optima_Mercado': pesos1,
    'Cartera_Agresiva_Tech': pesos2,
    'Cartera_Growth_Momentum': pesos3
})
df_vectores.to_csv('./competicion sabado/vectores_pesos_carteras.csv', index=False)
print('[OK] Vectores guardados: vectores_pesos_carteras.csv')
