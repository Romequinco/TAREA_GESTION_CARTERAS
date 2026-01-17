# OPTIMIZACIÓN DE CARTERAS PARA COMPETICIÓN

Proyecto completo para optimización de carteras con el objetivo de maximizar el Sharpe Ratio anualizado.

## ESTRUCTURA DEL PROYECTO

```
.
├── src/                           # Módulos de código fuente
│   ├── 1datos.py                 # Exploración y Preparación de Datos
│   ├── 2markowitz.py             # Optimización Clásica de Markowitz
│   ├── 3factores.py              # Construcción de Factores y Señales
│   ├── 4multifactorial.py        # Optimización Multifactorial Avanzada
│   ├── 5validacion.py            # Validación y Selección Final
│   ├── importar_modulos.py        # Script auxiliar para importar módulos
│   ├── README.md                 # Guía rápida de uso
│   └── README_MODULOS.md         # Documentación completa de módulos
├── data/                         # Datos de entrenamiento
│   └── prod_long_sharpe_u50_20260116_v5_train_dataset.csv
├── notebooks_demostracion/       # Notebooks de demostración
│   ├── Modulo1_Exploracion_Datos.ipynb
│   ├── Modulo2_Markowitz.ipynb
│   ├── Modulo3_Factores.ipynb
│   ├── Modulo4_Multifactorial.ipynb
│   └── Modulo5_Validacion.ipynb
├── notebooks_gestion_cartera/    # Material teórico de referencia
└── requirements.txt              # Dependencias del proyecto
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
markowitz = importlib.import_module('2markowitz')

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
2. Modulo2_Markowitz.ipynb
3. Modulo3_Factores.ipynb
4. Modulo4_Multifactorial.ipynb
5. Modulo5_Validacion.ipynb

## DOCUMENTACIÓN

- **Documentación completa**: Ver `src/README_MODULOS.md`
- **Guía rápida**: Ver `src/README.md`
- **Material teórico**: Ver `notebooks_gestion_cartera/resumen/Notebook_Ejecutivo_Resumen_Completo.ipynb`

## MÓDULOS

1. **1datos**: Carga, exploración y preparación de datos
2. **2markowitz**: Optimización clásica de Markowitz
3. **3factores**: Construcción de factores y señales
4. **4multifactorial**: Optimización multifactorial avanzada
5. **5validacion**: Validación y selección final

## DEPENDENCIAS

Ver `requirements.txt` para la lista completa. Principales:
- numpy
- pandas
- matplotlib
- seaborn
- cvxpy
- scipy
