"""
================================================================================
EXTRACTOR DE DATOS - COMPETICIÓN SÁBADO
================================================================================

Módulo para cargar, explorar y procesar los datos de retornos de la competición.

Características:
- Carga datos desde CSV (formato Excel oculto)
- Análisis estadístico completo
- Validación de datos
- Generación de métricas clave

Autor: Oscar Romero
Fecha: Enero 2026

"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')


class ExtractorDatos:
    """
    Clase para extraer, cargar y explorar datos de retornos.
    
    Attributes:
    -----------
    ruta_datos : str
        Ruta al archivo de datos
    datos : pd.DataFrame
        DataFrame con los datos cargados
    _procesados : bool
        Flag indicando si los datos han sido procesados
    """
    
    def __init__(self, ruta_datos):
        """
        Inicializa el extractor.
        
        Parameters:
        -----------
        ruta_datos : str
            Ruta al archivo CSV/Excel con los datos
        """
        self.ruta_datos = Path(ruta_datos)
        self.datos = None
        self._procesados = False
        
        print(f"Extractor inicializado")
        print(f"Ruta de datos: {self.ruta_datos}")
    
    
    def cargar_datos(self):
        """
        Carga los datos desde el archivo.
        Intenta múltiples formatos y encodings.
        """
        print("\n" + "="*80)
        print("PASO 1: CARGAR DATOS")
        print("="*80)
        
        if not self.ruta_datos.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.ruta_datos}")
        
        print(f"\nCargando datos desde: {self.ruta_datos.name}")
        
        # Intentar cargar como Excel primero
        try:
            self.datos = pd.read_excel(self.ruta_datos)
            print(f"✓ Detectado formato Excel")
        except Exception as e:
            # Si falla, intentar como CSV
            try:
                encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                for enc in encodings:
                    try:
                        self.datos = pd.read_csv(self.ruta_datos, encoding=enc)
                        print(f"✓ Cargado como CSV (encoding: {enc})")
                        break
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
            except Exception as e:
                raise ValueError(f"No se pudo cargar el archivo: {e}")
        
        if self.datos is None:
            raise ValueError("No se pudo cargar el archivo con ningún formato")
        
        print(f"[OK] Datos cargados correctamente")
        print(f"  Dimensiones: {self.datos.shape[0]} filas × {self.datos.shape[1]} columnas")
        print(f"  Memoria: {self.datos.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return self.datos
    
    
    def validar_datos(self):
        """
        Valida la integridad de los datos.
        """
        print("\n" + "="*80)
        print("PASO 2: VALIDAR DATOS")
        print("="*80)
        
        if self.datos is None:
            raise ValueError("Debe cargar los datos primero")
        
        # Verificar valores faltantes
        print(f"\nValores faltantes:")
        valores_faltantes = self.datos.isnull().sum().sum()
        print(f"  Total de NaN: {valores_faltantes}")
        if valores_faltantes > 0:
            print(f"  [WARN] Advertencia: Hay valores faltantes")
        else:
            print(f"  [OK] No hay valores faltantes")
        
        # Verificar tipos de datos
        print(f"\nTipos de datos:")
        tipos_unicos = self.datos.dtypes.unique()
        print(f"  Tipos únicos: {tipos_unicos}")
        
        # Verificar valores infinitos
        valores_inf = np.isinf(self.datos.select_dtypes(include=[np.number])).sum().sum()
        print(f"\nValores infinitos: {valores_inf}")
        if valores_inf > 0:
            print(f"  [WARN] Advertencia: Hay valores infinitos")
        
        # Verificar rangos de valores
        print(f"\nRango de valores:")
        print(f"  Mínimo: {self.datos.select_dtypes(include=[np.number]).min().min():.6f}")
        print(f"  Máximo: {self.datos.select_dtypes(include=[np.number]).max().max():.6f}")
        print(f"  Media: {self.datos.select_dtypes(include=[np.number]).mean().mean():.6f}")
        
        print(f"\n[OK] Validación completada")
        return True
    
    
    def estadisticas_descriptivas(self):
        """
        Calcula estadísticas descriptivas de los datos.
        
        Returns:
        --------
        dict
            Diccionario con estadísticas calculadas
        """
        print("\n" + "="*80)
        print("PASO 3: ESTADÍSTICAS DESCRIPTIVAS")
        print("="*80)
        
        if self.datos is None:
            raise ValueError("Debe cargar los datos primero")
        
        # Seleccionar solo columnas numéricas
        datos_numericos = self.datos.select_dtypes(include=[np.number])
        
        # Estadísticas generales
        print(f"\nEstadísticas Generales:")
        print(f"  Número de activos (columnas): {datos_numericos.shape[1]}")
        print(f"  Número de observaciones: {datos_numericos.shape[0]}")
        print(f"  Período: {datos_numericos.shape[0]} días de retornos")
        
        # Retornos
        print(f"\nRetornos Diarios (Estadísticas):")
        print(f"  Media: {datos_numericos.mean().mean():.6f}")
        print(f"  Mediana: {datos_numericos.median().median():.6f}")
        print(f"  Desv. Est. promedio: {datos_numericos.std().mean():.6f}")
        print(f"  Mínimo: {datos_numericos.min().min():.6f}")
        print(f"  Máximo: {datos_numericos.max().max():.6f}")
        
        # Retornos acumulados
        retornos_acumulados = np.exp(datos_numericos.sum()) - 1
        print(f"\nRetornos Acumulados por Activo:")
        print(f"  Media: {retornos_acumulados.mean():.4f} ({retornos_acumulados.mean()*100:.2f}%)")
        print(f"  Mínimo: {retornos_acumulados.min():.4f} ({retornos_acumulados.min()*100:.2f}%)")
        print(f"  Máximo: {retornos_acumulados.max():.4f} ({retornos_acumulados.max()*100:.2f}%)")
        
        # Volatilidad anualizada (asumiendo 252 días de trading)
        vol_anualizada = datos_numericos.std() * np.sqrt(252)
        print(f"\nVolatilidad Anualizada:")
        print(f"  Media: {vol_anualizada.mean():.4f} ({vol_anualizada.mean()*100:.2f}%)")
        print(f"  Mínimo: {vol_anualizada.min():.4f} ({vol_anualizada.min()*100:.2f}%)")
        print(f"  Máximo: {vol_anualizada.max():.4f} ({vol_anualizada.max()*100:.2f}%)")
        
        # Sharpe Ratio (asumiendo retorno libre de riesgo = 0)
        sharpe_ratio = (datos_numericos.mean() * 252) / (datos_numericos.std() * np.sqrt(252))
        print(f"\nSharpe Ratio (asumiendo Rf=0%):")
        print(f"  Media: {sharpe_ratio.mean():.4f}")
        print(f"  Mínimo: {sharpe_ratio.min():.4f}")
        print(f"  Máximo: {sharpe_ratio.max():.4f}")
        
        # Correlación
        correlacion = datos_numericos.corr()
        print(f"\nCorrelación entre Activos:")
        print(f"  Correlación promedio: {correlacion.values[np.triu_indices_from(correlacion.values, k=1)].mean():.4f}")
        print(f"  Correlación mínima: {correlacion.values[np.triu_indices_from(correlacion.values, k=1)].min():.4f}")
        print(f"  Correlación máxima: {correlacion.values[np.triu_indices_from(correlacion.values, k=1)].max():.4f}")
        
        # Asimetría y Curtosis
        print(f"\nAsimetría (Skewness):")
        skewness = datos_numericos.skew()
        print(f"  Media: {skewness.mean():.4f}")
        print(f"  Mínimo: {skewness.min():.4f}")
        print(f"  Máximo: {skewness.max():.4f}")
        
        print(f"\nCurtosis (Kurtosis):")
        kurtosis = datos_numericos.kurtosis()
        print(f"  Media: {kurtosis.mean():.4f}")
        print(f"  Mínimo: {kurtosis.min():.4f}")
        print(f"  Máximo: {kurtosis.max():.4f}")
        
        # Guardar estadísticas
        stats = {
            'n_activos': datos_numericos.shape[1],
            'n_observaciones': datos_numericos.shape[0],
            'retorno_medio': datos_numericos.mean().mean(),
            'volatilidad_media': datos_numericos.std().mean(),
            'vol_anualizada_media': vol_anualizada.mean(),
            'sharpe_ratio_medio': sharpe_ratio.mean(),
            'correlacion_media': correlacion.values[np.triu_indices_from(correlacion.values, k=1)].mean(),
            'retorno_acumulado_medio': retornos_acumulados.mean(),
            'skewness_media': skewness.mean(),
            'kurtosis_media': kurtosis.mean()
        }
        
        print(f"\n[OK] Estadísticas calculadas")
        return stats
    
    
    def activos_extremos(self, n=5):
        """
        Identifica los activos con mejores y peores rendimientos.
        
        Parameters:
        -----------
        n : int
            Número de activos a mostrar
        """
        print("\n" + "="*80)
        print("PASO 4: ACTIVOS EXTREMOS")
        print("="*80)
        
        datos_numericos = self.datos.select_dtypes(include=[np.number])
        
        # Retornos acumulados
        retornos_acumulados = np.exp(datos_numericos.sum()) - 1
        retornos_acumulados = retornos_acumulados.sort_values(ascending=False)
        
        print(f"\nTop {n} Mejores Activos (por retorno acumulado):")
        for i, (activo, retorno) in enumerate(retornos_acumulados.head(n).items(), 1):
            print(f"  {i}. Activo {activo}: {retorno:.4f} ({retorno*100:.2f}%)")
        
        print(f"\nTop {n} Peores Activos (por retorno acumulado):")
        for i, (activo, retorno) in enumerate(retornos_acumulados.tail(n).items(), 1):
            print(f"  {i}. Activo {activo}: {retorno:.4f} ({retorno*100:.2f}%)")
        
        # Volatilidad
        volatilidades = datos_numericos.std()
        print(f"\nTop {n} Activos Más Volátiles:")
        for i, (activo, vol) in enumerate(volatilidades.nlargest(n).items(), 1):
            print(f"  {i}. Activo {activo}: {vol:.6f}")
        
        print(f"\nTop {n} Activos Menos Volátiles:")
        for i, (activo, vol) in enumerate(volatilidades.nsmallest(n).items(), 1):
            print(f"  {i}. Activo {activo}: {vol:.6f}")
        
        # Sharpe Ratio
        sharpe_ratio = (datos_numericos.mean() * 252) / (datos_numericos.std() * np.sqrt(252))
        print(f"\nTop {n} Activos Mejores por Sharpe Ratio:")
        for i, (activo, sharpe) in enumerate(sharpe_ratio.nlargest(n).items(), 1):
            print(f"  {i}. Activo {activo}: {sharpe:.4f}")
        
        print(f"\n[OK] Análisis de activos extremos completado")
    
    
    def resumen_completo(self):
        """
        Ejecuta el pipeline completo de exploración.
        """
        print("\n" + "="*80)
        print("EXTRACTOR DE DATOS - COMPETICIÓN SÁBADO")
        print("="*80)
        
        # Cargar
        self.cargar_datos()
        
        # Validar
        self.validar_datos()
        
        # Estadísticas
        stats = self.estadisticas_descriptivas()
        
        # Activos extremos
        self.activos_extremos(n=5)
        
        print("\n" + "="*80)
        print("[OK] EXPLORACIÓN COMPLETADA")
        print("="*80 + "\n")
        
        return stats
    
    
    def obtener_datos(self):
        """Retorna los datos cargados."""
        if self.datos is None:
            raise ValueError("Debe cargar los datos primero")
        return self.datos.copy()


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Crear extractor
    ruta = "../../data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv"
    
    extractor = ExtractorDatos(ruta)
    
    # Ejecutar exploración completa
    stats = extractor.resumen_completo()
