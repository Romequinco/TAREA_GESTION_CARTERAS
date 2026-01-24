#!/usr/bin/env python3
"""
================================================================================
REFERENCIA RÁPIDA - Sistema de Configuración Paramétrica de Datos
================================================================================

Este archivo contiene ejemplos rápidos y copiar-pegar listos para usar el 
sistema de configuración de datos.

"""

# ==============================================================================
# 1. CARGAR DATOS CON LA FUENTE ACTIVA (MÁS SIMPLE)
# ==============================================================================

from config_datos import cargar_datos

# Cargar datos de la fuente configurada como activa (por defecto "nuevo")
datos = cargar_datos()

print(f"Datos cargados: {datos.shape}")
# Salida: Datos cargados: (1758, 60)


# ==============================================================================
# 2. CARGAR DATOS ESPECÍFICOS
# ==============================================================================

# Cargar datos anteriores sin cambiar la configuración
datos_anterior = cargar_datos("anterior")  # (1760, 50)

# Cargar datos nuevos sin cambiar la configuración
datos_nuevo = cargar_datos("nuevo")  # (1758, 60)


# ==============================================================================
# 3. CAMBIAR LA FUENTE ACTIVA EN SESIÓN
# ==============================================================================

from config_datos import cambiar_fuente_datos

# Cambiar a datos anteriores
cambiar_fuente_datos("anterior")

# Ahora al cargar sin especificar fuente, usará "anterior"
datos = cargar_datos()  # (1760, 50)

# Cambiar de vuelta a nuevos datos
cambiar_fuente_datos("nuevo")
datos = cargar_datos()  # (1758, 60)


# ==============================================================================
# 4. VER OPCIONES DISPONIBLES
# ==============================================================================

from config_datos import listar_opciones_disponibles

listar_opciones_disponibles()

# Salida:
# ================================================================================
# OPCIONES DE DATOS DISPONIBLES
# ================================================================================
# 
# Código: anterior
#   Nombre: Datos Anteriores (U50 - 16 Enero 2026)
#   Ruta: data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv
#   Descripción: Dataset original con 50 activos, versión 5 del 16/01/2026
# 
# Código: nuevo
#   Nombre: Datos Nuevos (U60 - 25 Enero 2026)
#   Ruta: data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv
#   Descripción: Dataset nuevo con 60 activos, versión 1 del 25/01/2026
# 
# Fuente ACTIVA: nuevo
# ================================================================================


# ==============================================================================
# 5. COMPARAR DATASETS
# ==============================================================================

from config_datos import comparar_datos_disponibles

comparar_datos_disponibles()

# Salida: Tabla comparativa con dimensiones, tipos de datos, tamaño, etc.


# ==============================================================================
# 6. OBTENER INFORMACIÓN DE UNA FUENTE
# ==============================================================================

from config_datos import obtener_info_datos

# Información del dataset "nuevo"
info_nuevo = obtener_info_datos("nuevo")
print(info_nuevo)
# Salida:
# {
#     'nombre': 'Datos Nuevos (U60 - 25 Enero 2026)',
#     'ruta': 'data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv',
#     'descripcion': 'Dataset nuevo con 60 activos, versión 1 del 25/01/2026'
# }


# ==============================================================================
# 7. USAR EN REBALANCEO_CARTERAS.IPynb
# ==============================================================================

# En lugar de:
# 
# tickers_sp500 = list(pd.read_csv("data/sp500_tickers.csv"))
# precios = yf.download(tickers_sp500, start="2015-01-01")['Close']
# precios_activos_select = precios.copy()
#
# Usar:

import pandas as pd
import numpy as np

# Importar la función
from config_datos import cargar_datos

# Cargar datos (automáticamente detecta formato y encoding)
precios_activos_select = cargar_datos()

# ¡Eso es todo! Ahora puedes usar precios_activos_select en tu análisis


# ==============================================================================
# 8. PATRÓN: ANALIZAR CON AMBOS DATASETS
# ==============================================================================

from config_datos import cargar_datos

# Cargar ambos datasets
datos_anterior = cargar_datos("anterior")
datos_nuevo = cargar_datos("nuevo")

# Comparar características
print(f"Dataset anterior: {datos_anterior.shape}")  # (1760, 50)
print(f"Dataset nuevo: {datos_nuevo.shape}")        # (1758, 60)

# Análisis con datos anteriores
print("\nAnálisis con datos anteriores:")
print(datos_anterior.describe())

# Análisis con datos nuevos
print("\nAnálisis con datos nuevos:")
print(datos_nuevo.describe())


# ==============================================================================
# 9. PATRÓN: LOOP SOBRE DATASETS
# ==============================================================================

from config_datos import OPCIONES_DATOS, cargar_datos

for codigo, info in OPCIONES_DATOS.items():
    print(f"\nAnalizando: {info['nombre']}")
    
    datos = cargar_datos(codigo)
    
    # Tu análisis aquí
    print(f"  Dimensiones: {datos.shape}")
    print(f"  Media: {datos.mean().head()}")
    print(f"  Volatilidad: {datos.std().head()}")


# ==============================================================================
# 10. PATRÓN: FUNCIÓN REUTILIZABLE
# ==============================================================================

def analizar_datos(fuente="nuevo"):
    """
    Función que carga datos y realiza análisis.
    
    Parámetros:
    -----------
    fuente : str
        Código del dataset ("anterior" o "nuevo")
    
    Retorna:
    --------
    dict
        Diccionario con estadísticas del análisis
    """
    from config_datos import cargar_datos, obtener_info_datos
    
    # Cargar datos
    datos = cargar_datos(fuente)
    info = obtener_info_datos(fuente)
    
    print(f"Analizando: {info['nombre']}")
    
    # Análisis
    resultados = {
        "nombre": info['nombre'],
        "dimensiones": datos.shape,
        "media": datos.mean(),
        "volatilidad": datos.std(),
        "correlacion": datos.corr().mean().mean(),
        "sharpe": datos.mean() / datos.std()  # Simplificado
    }
    
    return resultados

# Usar la función
resultados_nuevo = analizar_datos("nuevo")
resultados_anterior = analizar_datos("anterior")

print(f"\nNuevo Sharpe promedio: {resultados_nuevo['sharpe'].mean():.4f}")
print(f"Anterior Sharpe promedio: {resultados_anterior['sharpe'].mean():.4f}")


# ==============================================================================
# 11. CAMBIAR PERMANENTEMENTE LA FUENTE
# ==============================================================================

# Opción 1: Editar config_datos.py directamente
# Línea ~29:
# FUENTE_DATOS_ACTIVA = "anterior"  # Cambiar de "nuevo" a "anterior"

# Opción 2: Variable de entorno (opcional, requiere modificación de config_datos.py)
# import os
# FUENTE = os.getenv("CONFIG_DATOS_FUENTE", "nuevo")


# ==============================================================================
# 12. MANEJO DE ERRORES
# ==============================================================================

from config_datos import cargar_datos

# Capturar errores
try:
    datos = cargar_datos("fuente_inexistente")
except ValueError as e:
    print(f"Error: {e}")
    # Fallback a fuente por defecto
    datos = cargar_datos("nuevo")


# ==============================================================================
# RESUMEN DE FUNCIONES
# ==============================================================================

"""
Función                       Uso                              Retorna
==================================================================================
cargar_datos(fuente)          Carga datos                      pd.DataFrame
cambiar_fuente_datos(nueva)   Cambia fuente activa             None
listar_opciones_disponibles() Lista opciones                   None (imprime)
obtener_info_datos(fuente)    Obtiene info de fuente           dict
comparar_datos_disponibles()  Compara datasets                 None (imprime)
obtener_ruta_datos(fuente)    Obtiene ruta del archivo         str

==================================================================================
CÓDIGOS DE FUENTES VÁLIDOS: "anterior", "nuevo"
==================================================================================
"""


# ==============================================================================
# EJEMPLOS DE SALIDA
# ==============================================================================

# Ejecutar este archivo para ver ejemplos:
if __name__ == "__main__":
    print("=" * 80)
    print("EJEMPLOS DE USO - Sistema de Configuración Paramétrica de Datos")
    print("=" * 80)
    
    # Ejemplo 1: Cargar datos
    print("\n[Ejemplo 1] Cargar datos con fuente activa:")
    datos = cargar_datos()
    print(f"Shape: {datos.shape}")
    print(f"Primeras 3 activos: {list(datos.columns[:3])}")
    
    # Ejemplo 2: Listar opciones
    print("\n[Ejemplo 2] Opciones disponibles:")
    listar_opciones_disponibles()
    
    # Ejemplo 3: Comparar
    print("\n[Ejemplo 3] Comparación de datasets:")
    comparar_datos_disponibles()

