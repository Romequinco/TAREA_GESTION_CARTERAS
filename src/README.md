# MÓDULOS DE OPTIMIZACIÓN DE CARTERAS

Esta carpeta contiene los 5 módulos Python para la optimización de carteras.

## ESTRUCTURA

```
src/
├── 1datos.py                     # Exploración y Preparación de Datos
├── 2markowitz.py                 # Optimización Clásica de Markowitz
├── 3factores.py                  # Construcción de Factores y Señales
├── 4multifactorial.py            # Optimización Multifactorial Avanzada
├── 5validacion.py                # Validación y Selección Final
├── importar_modulos.py           # Script auxiliar para importar módulos
└── README_MODULOS.md             # Documentación completa de los módulos
```

## USO

### Importar módulos

Como los nombres de módulo empiezan con números, se debe usar `importlib`:

```python
import importlib
import sys
sys.path.append('src')  # O la ruta relativa desde donde ejecutes

# Importar módulos
datos = importlib.import_module('1datos')
markowitz = importlib.import_module('2markowitz')
factores = importlib.import_module('3factores')
multifactorial = importlib.import_module('4multifactorial')
validacion = importlib.import_module('5validacion')

# Usar las funciones
retornos = datos.cargar_retornos('data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv')
preparador = datos.PreparadorDatos(retornos, rf_anual=0.02)
preparador.calcular_estadisticas()
mu, Sigma, rf = preparador.obtener_estadisticas()
```

O usar el script auxiliar:

```python
import sys
sys.path.append('src')
from importar_modulos import datos, markowitz, factores, multifactorial, validacion

retornos = datos.cargar_retornos('data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv')
```

## DEPENDENCIAS

Ver `requirements.txt` en la raíz del proyecto para las versiones específicas.

Dependencias principales:
- numpy
- pandas
- matplotlib
- seaborn
- cvxpy
- scipy

## DOCUMENTACIÓN

Para documentación detallada de cada módulo, ver `README_MODULOS.md` en esta misma carpeta.
