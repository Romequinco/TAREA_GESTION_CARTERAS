# MÓDULOS DE OPTIMIZACIÓN DE CARTERAS

Esta carpeta contiene los 5 módulos Python para la optimización de carteras.

## ESTRUCTURA

```
src/
├── 1datos.py                     # Exploración y Preparación de Datos
├── 2equiponderada_diversificacion.py  # Análisis de Carteras Equiponderadas y Diversificación
├── 3markowitz.py                 # Optimización Clásica de Markowitz
├── validacion.py                 # Validación y Selección Final
├── 5analisis_multipunto.py       # Análisis multipunto de diversificación
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
equiponderada = importlib.import_module('2equiponderada_diversificacion')
markowitz = importlib.import_module('3markowitz')
validacion = importlib.import_module('validacion')
multipunto = importlib.import_module('5analisis_multipunto')

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
from importar_modulos import datos, equiponderada, markowitz, validacion, multipunto

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
