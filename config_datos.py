"""
================================================================================
CONFIGURACIÓN PARAMÉTRICA - SELECCIÓN DE FUENTE DE DATOS
================================================================================

Archivo de configuración para seleccionar la fuente de datos a usar en los 
análisis de carteras y rebalanceo. Permite cambiar fácilmente entre diferentes
conjuntos de datos sin modificar el código principal.

"""

import os
import pandas as pd
from pathlib import Path


# ============================================================================
# 1. OPCIONES DISPONIBLES DE DATOS
# ============================================================================

OPCIONES_DATOS = {
    "anterior": {
        "nombre": "Datos Anteriores (U50 - 16 Enero 2026)",
        "ruta": "data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv",
        "descripcion": "Dataset original con 50 activos, versión 5 del 16/01/2026"
    },
    "nuevo": {
        "nombre": "Datos Nuevos (U60 - 25 Enero 2026)",
        "ruta": "data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv",
        "descripcion": "Dataset nuevo con 60 activos, versión 1 del 25/01/2026"
    }
}


# ============================================================================
# 2. SELECCIÓN DE DATOS ACTIVA
# ============================================================================
# Cambia este valor a "anterior" o "nuevo" para seleccionar la fuente de datos

FUENTE_DATOS_ACTIVA = "nuevo"  # Opciones: "anterior" o "nuevo"


# ============================================================================
# 3. FUNCIONES DE UTILIDAD
# ============================================================================

def obtener_ruta_datos(fuente=None):
    """
    Obtiene la ruta del archivo CSV según la fuente seleccionada.
    
    Parameters:
    -----------
    fuente : str, optional
        Código de la fuente de datos ("anterior" o "nuevo").
        Si es None, usa FUENTE_DATOS_ACTIVA.
    
    Returns:
    --------
    str
        Ruta absoluta del archivo CSV.
    
    Raises:
    -------
    ValueError
        Si la fuente no es válida o el archivo no existe.
    """
    if fuente is None:
        fuente = FUENTE_DATOS_ACTIVA
    
    if fuente not in OPCIONES_DATOS:
        raise ValueError(
            f"Fuente de datos inválida: {fuente}. "
            f"Opciones válidas: {list(OPCIONES_DATOS.keys())}"
        )
    
    ruta_relativa = OPCIONES_DATOS[fuente]["ruta"]
    ruta_absoluta = Path(ruta_relativa).absolute()
    
    if not ruta_absoluta.exists():
        raise FileNotFoundError(
            f"Archivo de datos no encontrado: {ruta_absoluta}\n"
            f"Verificar que el archivo existe en: {ruta_relativa}"
        )
    
    return str(ruta_absoluta)


def obtener_info_datos(fuente=None):
    """
    Obtiene información sobre la fuente de datos seleccionada.
    
    Parameters:
    -----------
    fuente : str, optional
        Código de la fuente de datos. Si es None, usa FUENTE_DATOS_ACTIVA.
    
    Returns:
    --------
    dict
        Diccionario con información de la fuente.
    """
    if fuente is None:
        fuente = FUENTE_DATOS_ACTIVA
    
    if fuente not in OPCIONES_DATOS:
        raise ValueError(f"Fuente de datos inválida: {fuente}")
    
    return OPCIONES_DATOS[fuente]


def listar_opciones_disponibles():
    """
    Lista todas las opciones de datos disponibles.
    
    Returns:
    --------
    None (imprime información en consola)
    """
    print("\n" + "=" * 80)
    print("OPCIONES DE DATOS DISPONIBLES")
    print("=" * 80)
    
    for codigo, info in OPCIONES_DATOS.items():
        print(f"\nCódigo: {codigo}")
        print(f"  Nombre: {info['nombre']}")
        print(f"  Ruta: {info['ruta']}")
        print(f"  Descripción: {info['descripcion']}")
    
    print(f"\nFuente ACTIVA: {FUENTE_DATOS_ACTIVA}")
    print("=" * 80 + "\n")


def cargar_datos(fuente=None):
    """
    Carga los datos del archivo CSV o Excel especificado.
    Detecta automáticamente el formato del archivo.
    Intenta múltiples encodings en caso de error (para CSV).
    
    Parameters:
    -----------
    fuente : str, optional
        Código de la fuente de datos. Si es None, usa FUENTE_DATOS_ACTIVA.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame con los datos cargados.
    """
    ruta = obtener_ruta_datos(fuente)
    info = obtener_info_datos(fuente)
    
    print(f"\nCargando datos desde: {info['nombre']}")
    print(f"Ruta: {ruta}")
    
    # Detectar formato del archivo
    extension = Path(ruta).suffix.lower()
    df = None
    
    # Si es Excel
    if extension in ['.xlsx', '.xls']:
        try:
            print(f"Detectado formato Excel (.{extension}), cargando...")
            df = pd.read_excel(ruta)
            print(f"✓ Datos cargados correctamente desde Excel")
        except Exception as e:
            print(f"Error al cargar Excel: {e}")
            raise
    
    # Si es CSV o sin extensión
    else:
        # Primero intentar detectar si es un archivo Excel con extensión CSV
        try:
            df = pd.read_excel(ruta)
            print(f"✓ Detectado formato Excel oculto (archivo con extensión .csv)")
            print(f"✓ Datos cargados correctamente desde Excel")
        except Exception:
            # Si no es Excel, intentar como CSV con múltiples encodings
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'utf-16']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(ruta, encoding=encoding)
                    print(f"✓ Datos cargados correctamente (encoding: {encoding})")
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
                except Exception as e:
                    print(f"  Error con encoding {encoding}: {e}")
                    continue
            
            if df is None:
                raise ValueError(
                    f"No se pudo cargar el archivo con los encodings disponibles: {encodings}\n"
                    f"Verificar que el archivo {ruta} está en un formato CSV o Excel válido"
                )
    
    print(f"  Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
    print(f"  Memoria: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return df


def cambiar_fuente_datos(nueva_fuente):
    """
    Cambia la fuente de datos activa.
    
    NOTA: Esta función solo cambia el valor en memoria durante la sesión.
    Para cambios permanentes, edita el valor de FUENTE_DATOS_ACTIVA en este archivo.
    
    Parameters:
    -----------
    nueva_fuente : str
        Código de la nueva fuente de datos ("anterior" o "nuevo").
    
    Raises:
    -------
    ValueError
        Si la fuente no es válida.
    """
    global FUENTE_DATOS_ACTIVA
    
    if nueva_fuente not in OPCIONES_DATOS:
        raise ValueError(
            f"Fuente de datos inválida: {nueva_fuente}. "
            f"Opciones válidas: {list(OPCIONES_DATOS.keys())}"
        )
    
    print(f"\n⚠ Cambiando fuente de datos de '{FUENTE_DATOS_ACTIVA}' a '{nueva_fuente}'")
    FUENTE_DATOS_ACTIVA = nueva_fuente
    info = obtener_info_datos(nueva_fuente)
    print(f"✓ Nueva fuente activa: {info['nombre']}\n")


# ============================================================================
# 4. COMPARACIÓN DE DATOS
# ============================================================================

def comparar_datos_disponibles():
    """
    Compara las características de los conjuntos de datos disponibles.
    
    Returns:
    --------
    None (imprime información comparativa en consola)
    """
    print("\n" + "=" * 80)
    print("COMPARACIÓN DE CONJUNTOS DE DATOS DISPONIBLES")
    print("=" * 80)
    
    # Intentar múltiples encodings
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'utf-16']
    
    for codigo, info in OPCIONES_DATOS.items():
        try:
            ruta = obtener_ruta_datos(codigo)
            extension = Path(ruta).suffix.lower()
            df = None
            
            # Si es Excel
            if extension in ['.xlsx', '.xls']:
                df = pd.read_excel(ruta)
            else:
                # Intentar cargar CSV con diferentes encodings
                for encoding in encodings:
                    try:
                        df = pd.read_csv(ruta, encoding=encoding)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
                
                # Si no funciona como CSV, intentar como Excel oculto
                if df is None:
                    try:
                        df = pd.read_excel(ruta)
                    except Exception:
                        pass
            
            if df is not None:
                print(f"\n{info['nombre']}:")
                print(f"  Ruta: {info['ruta']}")
                print(f"  Filas: {len(df)}")
                print(f"  Columnas: {len(df.columns)}")
                print(f"  Tamaño: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                print(f"  Tipo de datos:")
                for col in df.columns[:3]:  # Mostrar primeras 3 columnas
                    print(f"    - {col}: {df[col].dtype}")
                if len(df.columns) > 3:
                    print(f"    ... y {len(df.columns) - 3} columnas más")
            else:
                print(f"\n{info['nombre']}: No se pudo cargar (encoding no reconocido)")
                
        except Exception as e:
            print(f"\n{info['nombre']}: ERROR - {e}")
    
    print("\n" + "=" * 80 + "\n")


# ============================================================================
# 5. EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CONFIGURACIÓN DE DATOS - EJEMPLO DE USO")
    print("=" * 80)
    
    # Listar opciones disponibles
    listar_opciones_disponibles()
    
    # Comparar datos
    comparar_datos_disponibles()
    
    # Cargar datos de la fuente activa
    print("Cargando datos de la fuente activa...")
    datos = cargar_datos()
    print(f"\nPrimeras filas:")
    print(datos.head())
