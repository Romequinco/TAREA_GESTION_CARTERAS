# OPTIMIZACIÓN DE CARTERAS PARA COMPETICIÓN

Proyecto completo para optimización de carteras con el objetivo de maximizar el Sharpe Ratio anualizado.

## ESTRUCTURA DEL PROYECTO

```
.
├── src/                           # Módulos de código fuente
│   ├── 1datos.py                 # Exploración y Preparación de Datos
│   ├── 2equiponderada_diversificacion.py  # Análisis de Carteras Equiponderadas y Diversificación
│   ├── 3markowitz.py             # Optimización Clásica de Markowitz
│   ├── 4seleccion_activos.py     # Selección Óptima de Activos
│   ├── 5analisis_multipunto.py   # Análisis multipunto de diversificación
│   ├── validacion.py             # Validación y Exportación Final
│   ├── importar_modulos.py        # Script auxiliar para importar módulos
│   ├── README.md                 # Guía rápida de uso
│   └── README_MODULOS.md         # Documentación completa de módulos
├── data/                         # Datos de entrenamiento
│   └── prod_long_sharpe_u50_20260116_v5_train_dataset.csv
├── notebooks_demostracion/       # Notebooks de demostración
│   ├── Modulo1_Exploracion_Datos.ipynb
│   ├── Modulo2_Equiponderada_Diversificacion.ipynb
│   ├── Modulo3_Markowitz.ipynb
│   ├── Modulo4_Seleccion_Activos.ipynb
│   ├── Modulo5_Comparacion_Multipunto.ipynb
│   ├── Modulo8_Validacion.ipynb
│   └── outputs/                  # Imágenes y archivos generados
├── comprobaciones/               # Documentación detallada por módulo
│   ├── 1datos/
│   ├── 2equiponderada_diversificacion/
│   ├── 3markowitz/
│   ├── 4seleccion_activos/
│   └── 5analisis_multipunto/
├── teoria/                        # Material teórico de referencia
├── requirements.txt              # Dependencias del proyecto
├── RESUMEN_COMPLETO_PROYECTO.md  # Resumen detallado del proyecto
└── RESUMEN_CORTO_PROYECTO.md     # Resumen ejecutivo con diagrama
```

## INSTALACIÓN

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Los datos ya están en la carpeta `data/`

## USO RÁPIDO

### Desde Python

```python
import importlib
import sys
sys.path.append('src')

# Importar módulos
datos = importlib.import_module('1datos')
equiponderada = importlib.import_module('2equiponderada_diversificacion')
markowitz = importlib.import_module('3markowitz')
seleccion = importlib.import_module('4seleccion_activos')
multipunto = importlib.import_module('5analisis_multipunto')
validacion = importlib.import_module('validacion')

# Cargar datos
retornos = datos.cargar_retornos('data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv')

# Preparar datos
preparador = datos.PreparadorDatos(retornos, rf_anual=0.02)
preparador.calcular_estadisticas()
mu, Sigma, rf = preparador.obtener_estadisticas()

# Optimizar
cartera = markowitz.optimizar_sharpe_maximo(mu, Sigma, rf)
print(f"Sharpe Ratio: {cartera['sharpe']:.4f}")
```

### Desde Notebooks

Ejecutar los notebooks en `notebooks_demostracion/` en orden:
1. Modulo1_Exploracion_Datos.ipynb
2. Modulo2_Equiponderada_Diversificacion.ipynb
3. Modulo3_Markowitz.ipynb
4. Modulo4_Seleccion_Activos.ipynb
5. Modulo5_Comparacion_Multipunto.ipynb
6. Modulo8_Validacion.ipynb

## DOCUMENTACIÓN

- **Documentación completa**: Ver `src/README_MODULOS.md`
- **Guía rápida**: Ver `src/README.md`
- **Resumen completo**: Ver `RESUMEN_COMPLETO_PROYECTO.md`
- **Resumen ejecutivo**: Ver `RESUMEN_CORTO_PROYECTO.md`
- **Material teórico**: Ver `teoria/resumen/Notebook_Ejecutivo_Resumen_Completo.ipynb`
- **Comprobaciones detalladas**: Ver `comprobaciones/` (documentación por módulo)

## MÓDULOS

1. **1datos**: Carga, exploración y preparación de datos (1760 días × 50 activos)
2. **2equiponderada_diversificacion**: Análisis de carteras equiponderadas y diversificación
3. **3markowitz**: Optimización clásica de Markowitz (máximo Sharpe Ratio)
4. **4seleccion_activos**: Selección óptima de activos basada en diversificación y Sharpe
5. **5analisis_multipunto**: Análisis comparativo de múltiples puntos en la frontera
6. **validacion**: Validación de restricciones, cálculo de métricas y exportación final

## DEPENDENCIAS

Ver `requirements.txt` para la lista completa. Principales:
- numpy
- pandas
- matplotlib
- seaborn
- cvxpy
- scipy
