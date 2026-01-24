<!-- HTML version would be simpler, but I'll provide a comprehensive markdown guide -->

# Configuración Paramétrica de Datos

## 📋 Descripción

El sistema de configuración paramétrica permite elegir **de forma flexible y sin modificar código** cuál de los dos conjuntos de datos disponibles usar en los análisis de carteras.

### Datasets Disponibles

| Código | Nombre | Activos | Fecha | Archivo |
|--------|--------|---------|-------|---------|
| `anterior` | Datos Anteriores (U50) | 50 | 16 Enero 2026 | `prod_long_sharpe_u50_20260116_v5_train_dataset.csv` |
| `nuevo` | Datos Nuevos (U60) | 60 | 25 Enero 2026 | `prod_long_sharpe_u60_20260125_v1_train_dataset.csv` |

---

## 🚀 Uso Rápido

### Opción 1: Cambio Permanente (Editar archivo)

```python
# En config_datos.py, línea ~29:
FUENTE_DATOS_ACTIVA = "nuevo"  # Cambia "nuevo" por "anterior"
```

Después, en cualquier notebook:

```python
from config_datos import cargar_datos

datos = cargar_datos()  # Carga de la fuente definida
```

### Opción 2: Cambio Dinámico (En sesión)

```python
from config_datos import cambiar_fuente_datos, cargar_datos

# Cambiar a la otra fuente
cambiar_fuente_datos("anterior")

# Cargar datos de la nueva fuente
datos = cargar_datos()
```

### Opción 3: Especificar Fuente en Cada Carga

```python
from config_datos import cargar_datos

# Cargar del dataset específico sin cambiar la configuración activa
datos_anterior = cargar_datos("anterior")
datos_nuevo = cargar_datos("nuevo")
```

---

## 📦 Funciones Disponibles

### `cargar_datos(fuente=None)`
Carga los datos del archivo CSV especificado.

```python
from config_datos import cargar_datos

# Usar fuente activa
df = cargar_datos()

# Especificar fuente
df_anterior = cargar_datos("anterior")
df_nuevo = cargar_datos("nuevo")
```

**Retorna**: `pd.DataFrame` con los datos cargados

---

### `cambiar_fuente_datos(nueva_fuente)`
Cambia la fuente de datos activa en la sesión actual.

```python
from config_datos import cambiar_fuente_datos

cambiar_fuente_datos("anterior")  # Cambia a datos anteriores
```

**Nota**: Este cambio solo afecta la sesión actual. Para cambios permanentes, edita `config_datos.py`.

---

### `listar_opciones_disponibles()`
Muestra todas las opciones de datos disponibles.

```python
from config_datos import listar_opciones_disponibles

listar_opciones_disponibles()
```

**Salida**:
```
================================================================================
OPCIONES DE DATOS DISPONIBLES
================================================================================

Código: anterior
  Nombre: Datos Anteriores (U50 - 16 Enero 2026)
  Ruta: data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv
  Descripción: Dataset original con 50 activos, versión 5 del 16/01/2026

Código: nuevo
  Nombre: Datos Nuevos (U60 - 25 Enero 2026)
  Ruta: data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv
  Descripción: Dataset nuevo con 60 activos, versión 1 del 25/01/2026

Fuente ACTIVA: nuevo
================================================================================
```

---

### `obtener_info_datos(fuente=None)`
Obtiene información sobre una fuente de datos específica.

```python
from config_datos import obtener_info_datos

info = obtener_info_datos("nuevo")
print(info)
# Salida:
# {
#     'nombre': 'Datos Nuevos (U60 - 25 Enero 2026)',
#     'ruta': 'data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv',
#     'descripcion': 'Dataset nuevo con 60 activos, versión 1 del 25/01/2026'
# }
```

---

### `comparar_datos_disponibles()`
Compara características de ambos datasets.

```python
from config_datos import comparar_datos_disponibles

comparar_datos_disponibles()
```

**Salida**:
```
================================================================================
COMPARACIÓN DE CONJUNTOS DE DATOS DISPONIBLES
================================================================================

Datos Anteriores (U50 - 16 Enero 2026):
  Ruta: data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv
  Filas: 6358
  Columnas: 50
  Tamaño: 2.45 MB
  Tipo de datos:
    - asset1: float64
    - asset2: float64
    ... y 48 columnas más

Datos Nuevos (U60 - 25 Enero 2026):
  Ruta: data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv
  Filas: 6358
  Columnas: 60
  Tamaño: 2.95 MB
  Tipo de datos:
    - asset1: float64
    - asset2: float64
    ... y 58 columnas más

================================================================================
```

---

## 📝 Ejemplo Completo

### En Rebalanceo_carteras.ipynb

**Antes** (código manual):
```python
# Opción 1: Descargar de yfinance
tickers_sp500 = list(pd.read_csv("data/sp500_tickers.csv"))
precios = yf.download(tickers_sp500, start="2015-01-01")['Close']

# Opción 2: Leer CSV
precios = pd.read_csv("data/prod_long_sharpe_u50_20260116_v5_train_dataset.csv")
```

**Después** (código parametrizado):
```python
from config_datos import cargar_datos

# Simple: usa la fuente configurada
precios_activos_select = cargar_datos()

# O cambiar dinámicamente si lo necesitas
cambiar_fuente_datos("anterior")
precios_activos_select = cargar_datos()
```

---

## ⚙️ Estructura del Archivo config_datos.py

```python
# 1. OPCIONES DISPONIBLES
OPCIONES_DATOS = {
    "anterior": {...},
    "nuevo": {...}
}

# 2. SELECCIÓN ACTIVA
FUENTE_DATOS_ACTIVA = "nuevo"  # ← CAMBIAR AQUÍ para cambio permanente

# 3. FUNCIONES
- cargar_datos(fuente=None)
- cambiar_fuente_datos(nueva_fuente)
- listar_opciones_disponibles()
- obtener_info_datos(fuente=None)
- comparar_datos_disponibles()
```

---

## 🔧 Agregar Nuevas Fuentes de Datos

Para agregar un nuevo dataset:

1. **Edita `config_datos.py`**:

```python
OPCIONES_DATOS = {
    "anterior": {...},
    "nuevo": {...},
    "otra_fuente": {  # ← Nueva entrada
        "nombre": "Mi Nuevo Dataset",
        "ruta": "data/mi_dataset.csv",
        "descripcion": "Descripción del dataset"
    }
}
```

2. **Usa la nueva fuente**:

```python
datos = cargar_datos("otra_fuente")
```

---

## 📊 Notebooks de Ejemplo

- **`notebooks_demostracion/Ejemplo_Seleccion_Datos.ipynb`**: Demostración completa de todas las funciones
- **`teoria/tema_6/Rebalanceo_carteras.ipynb`**: Notebook principal (puede usar la configuración)

---

## ⚠️ Notas Importantes

1. **Rutas relativas**: Las rutas en `OPCIONES_DATOS` son relativas al directorio raíz del proyecto.

2. **Validación de archivos**: El sistema verifica que los archivos existan antes de intentar cargarlos.

3. **Cambios en sesión vs permanentes**:
   - `cambiar_fuente_datos()` → solo afecta la sesión actual
   - Editar `FUENTE_DATOS_ACTIVA` → cambio permanente

4. **Backward compatibility**: El código anterior que usaba `yf.download()` sigue funcionando sin cambios.

---

## 🐛 Solución de Problemas

### Error: "Archivo de datos no encontrado"

**Causa**: La ruta del archivo es incorrecta o el archivo no existe.

**Solución**:
```python
from config_datos import listar_opciones_disponibles

# Verificar rutas configuradas
listar_opciones_disponibles()

# Verificar que los archivos existen
import os
for codigo, info in OPCIONES_DATOS.items():
    ruta = info['ruta']
    existe = os.path.exists(ruta)
    print(f"{codigo}: {existe}")
```

### Error: "Fuente de datos inválida"

**Causa**: El código de la fuente no existe en `OPCIONES_DATOS`.

**Solución**:
```python
# Usar código válido
cargar_datos("anterior")  # ✓ Válido
cargar_datos("nuevo")     # ✓ Válido
# cargar_datos("xyz")     # ✗ Error

# O agregar la nueva fuente a OPCIONES_DATOS
```

---

## 📞 Contacto

Para preguntas o sugerencias sobre la configuración paramétrica, consultar el archivo `config_datos.py` o el ejemplo en `notebooks_demostracion/Ejemplo_Seleccion_Datos.ipynb`.
