# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MODULO 4SELECCION_ACTIVOS

## INTRODUCCION

El modulo `4seleccion_activos.py` selecciona un subconjunto de activos para mejorar la optimizacion posterior. Usa la frontera de diversificacion (modulo 2), metricas de Sharpe y correlacion (modulo 1) y luego optimiza con Markowitz (modulo 3).

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1) FUNCION: `detectar_n_optimo_activos(retornos, umbral_reduccion=2.0, n_simulaciones=100)`

**Proposito**  
Detectar automaticamente el numero optimo de activos segun la frontera de diversificacion.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Importa dinamicamente el modulo `2equiponderada_diversificacion`:
   - Revisa `sys.modules` primero.
   - Si no existe, intenta `importlib.import_module`.
   - Si falla, agrega `.../src` al `sys.path` y reintenta.
3. Simula la frontera con `simular_frontera_diversificacion`.
4. Detecta `n_optimo` con `detectar_frontera_optima`.
5. Extrae la fila del N optimo para obtener:
   - `reduccion_en_optimo`
   - `volatilidad_en_optimo`
6. Retorna diccionario con N optimo y detalles.

**Salidas**
- `{'n_optimo', 'df_frontera', 'reduccion_en_optimo', 'volatilidad_en_optimo'}`.

---

### 2) FUNCION: `calcular_metricas_seleccion(retornos, rf_anual=0.02)`

**Proposito**  
Calcular metricas de calidad por activo para la seleccion.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Convierte `rf_anual` a tasa diaria.
3. Calcula media y volatilidad diaria.
4. Calcula Sharpe anualizado y reemplaza infinitos por 0.
5. Anualiza rendimiento y volatilidad.
6. Calcula matriz de correlacion.
7. Calcula correlacion promedio de cada activo con el resto.
8. Define puntuacion de diversificacion: `1 - correlacion_promedio`.
9. Arma DataFrame y ordena por Sharpe descendente.

**Salidas**
- DataFrame con columnas: `activo`, `sharpe_ratio`, `rendimiento_anual`,
  `volatilidad_anual`, `correlacion_promedio`, `puntuacion_diversificacion`.

---

### 3) FUNCION: `seleccionar_activos_por_sharpe_decorrelacion(...)`

**Proposito**  
Seleccionar los N activos con mejor balance entre Sharpe y baja correlacion.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Valida que `n_activos` sea valido.
3. Valida que `peso_sharpe + peso_decorrelacion == 1`.
4. Calcula metricas con `calcular_metricas_seleccion`.
5. Normaliza Sharpe y diversificacion a escala [0, 1].
6. Calcula `score_combinado` con los pesos indicados.
7. Ordena por `score_combinado` y selecciona top N.
8. Calcula correlacion promedio entre seleccionados (triangulo superior).
9. Calcula Sharpe promedio de seleccionados.
10. Si la correlacion promedio > 0.8, imprime advertencia.
11. Retorna diccionario con activos, indices y metricas.

**Salidas**
- Diccionario con `activos_seleccionados`, `indices_seleccionados`,
  `metricas`, `correlacion_promedio_seleccion`, `sharpe_promedio_seleccion`.
- Posible advertencia en consola por correlacion alta.

---

### 4) FUNCION: `filtrar_retornos_activos_seleccionados(retornos, activos_seleccionados)`

**Proposito**  
Filtrar el DataFrame de retornos a los activos seleccionados.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Valida que la lista no este vacia.
3. Verifica que todos los activos existan en columnas.
4. Filtra y retorna el DataFrame con el orden preservado.

---

### 5) FUNCION PRINCIPAL: `optimizar_cartera_con_seleccion(...)`

**Proposito**  
Ejecutar el pipeline completo: seleccionar activos y optimizar cartera.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Importa dinamicamente modulo 1 (`1datos`) y modulo 3 (`3markowitz`).
3. PASO 1 (si `n_optimo` es None):
   - Imprime "Detectando numero optimo de activos..."
   - Llama `detectar_n_optimo_activos`.
   - Imprime el N detectado.
4. PASO 2:
   - Imprime "Seleccionando activos optimos..."
   - Calcula pesos de criterio (`peso_sharpe`, `peso_decorrelacion`).
   - Llama `seleccionar_activos_por_sharpe_decorrelacion`.
   - Imprime cantidad y Sharpe promedio.
5. PASO 3:
   - Imprime "Filtrando retornos a activos seleccionados..."
   - Llama `filtrar_retornos_activos_seleccionados`.
6. PASO 4:
   - Imprime "Preparando datos para optimizacion..."
   - Usa `PreparadorDatos` para obtener `mu`, `Sigma`, `rf`.
7. PASO 5:
   - Imprime metodo usado.
   - Optimiza con `optimizar_sharpe_maximo` o `optimizar_markowitz_lambda`.
   - Si falla, lanza error.
8. PASO 6:
   - Reconstruye vector de 50 posiciones con ceros y mapea pesos optimizados.
   - Si la suma no coincide con `1 - peso_rf`, renormaliza y advierte.
9. PASO 7:
   - Calcula metricas finales.
   - Calcula baseline equiponderado de 50 activos para comparar.
10. Imprime resultados finales (Sharpe, rentabilidad, volatilidad).
11. Retorna diccionario con pesos completos, metricas y detalles.

**Salidas**
- Diccionario con `pesos_completos`, `activos_seleccionados`, `indices_seleccionados`,
  `n_activos_usados`, `metricas_cartera`, `comparacion_baseline`,
  `detalles_seleccion`, `peso_rf`.
- Mensajes impresos en consola durante cada paso.

---

### 6) FUNCION: `visualizar_seleccion_activos(resultado_seleccion, retornos_completos, ruta_guardado=None)`

**Proposito**  
Generar una figura 2x2 con visualizaciones del proceso.

**Paso a paso**
1. Valida que `resultado_seleccion` no sea `None`.
2. Subplot 1: barras de pesos para los 50 activos (azul seleccionados, gris resto).
3. Subplot 2: scatter de rendimiento vs volatilidad, con etiquetas para seleccionados.
4. Subplot 3: heatmap de correlaciones de activos seleccionados con valores.
5. Subplot 4: comparacion de cartera equiponderada vs optimizada (puntos con anotaciones).
6. Guarda la figura si hay `ruta_guardado`.
7. Retorna la figura.

---

### 7) FUNCION: `comparar_estrategias(retornos, rf_anual=0.02)`

**Proposito**  
Comparar tres estrategias: equiponderada 50, Markowitz 50 y seleccion + Markowitz.

**Paso a paso**
1. Importa dinamicamente modulo 1 y 3.
2. Estrategia 1: equiponderada 50 activos.
3. Estrategia 2: Markowitz max Sharpe sobre 50 activos.
4. Estrategia 3: seleccion + Markowitz con N detectado.
5. Construye DataFrame comparativo con Sharpe, rentabilidad, volatilidad, N.
6. Grafica comparacion en tres barras (Sharpe, rentabilidad, volatilidad).
7. Retorna DataFrame y figura.

---

## VALIDACIONES Y SALIDAS EN CONSOLA

- Errores si `retornos` esta vacio o `n_activos` invalido.
- Advertencias si la correlacion promedio seleccionada es alta.
- Mensajes de progreso en cada paso del pipeline.
