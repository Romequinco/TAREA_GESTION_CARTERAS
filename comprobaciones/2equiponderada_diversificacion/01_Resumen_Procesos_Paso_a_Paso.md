# RESUMEN DETALLADO: PROCESOS PASO A PASO DEL MODULO 2EQUIPONDERADA_DIVERSIFICACION

## INTRODUCCION

El modulo `2equiponderada_diversificacion.py` analiza carteras equiponderadas, descompone su riesgo en componentes sistematico y especifico, simula la frontera de diversificacion y muestra contribuciones de cada activo.

---

## FUNCIONES Y PROCESOS DETALLADOS

### 1) FUNCION: `analizar_cartera_equiponderada(retornos)`

**Proposito**  
Descomponer el riesgo de una cartera equiponderada con la formula teorica.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Obtiene `n = retornos.shape[1]`.
3. Calcula covarianza diaria: `cov_diaria = retornos.cov().values`.
4. Varianza media diaria: promedio de la diagonal.
5. Covarianza media diaria: promedio del triangulo superior (sin diagonal).
6. Anualiza varianza y covarianza (multiplica por 252).
7. Riesgo especifico: `(1 / n) * varianza_media`.
8. Riesgo sistematico: `covarianza_media`.
9. Varianza total: `riesgo_especifico + riesgo_sistematico`.
10. Volatilidad total: `sqrt(varianza_cartera)`.
11. Verifica la formula con varianza real de cartera equiponderada:
    - Si la diferencia > 1e-6, imprime advertencia.
12. Retorna diccionario con todas las medidas.

**Salidas**
- Diccionario con `varianza_media`, `covarianza_media`, `riesgo_especifico`,
  `riesgo_sistematico`, `varianza_cartera`, `volatilidad_cartera`.
- Posible advertencia en consola si la verificacion numerica no coincide.

---

### 2) FUNCION: `simular_frontera_diversificacion(retornos, n_valores=None, n_simulaciones=100)`

**Proposito**  
Simular el efecto de diversificacion al variar N, usando carteras equiponderadas aleatorias.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Obtiene `n_total = retornos.shape[1]`.
3. Define `n_valores` por defecto si es `None`.
4. Filtra valores que exceden `n_total`.
5. Si no quedan valores validos, lanza error.
6. Fija semilla `np.random.seed(42)` para reproducibilidad.
7. Para cada `n`:
   - Repite `n_simulaciones` veces:
     - Seleccion aleatoria de activos sin reemplazo.
     - Calcula covarianza diaria del subconjunto.
     - Calcula varianza media y covarianza media.
     - Si no hay pares (caso limite), usa covarianza media 0.0.
     - Anualiza y calcula volatilidad.
   - Promedia volatilidad y componentes de riesgo.
   - Calcula reduccion porcentual vs `n` anterior.
8. Construye DataFrame de resultados.
9. Imprime una tabla resumen formateada en consola.
10. Retorna el DataFrame.

**Salidas**
- DataFrame con columnas: `n_activos`, `volatilidad_media`, `volatilidad_std`,
  `riesgo_especifico`, `riesgo_sistematico`, `reduccion_pct`.
- Tabla impresa en consola con estadisticas por N.

---

### 3) FUNCION: `detectar_frontera_optima(df_simulacion, umbral_reduccion=2.0)`

**Proposito**  
Detectar el N optimo donde la reduccion marginal de riesgo cae bajo el umbral.

**Paso a paso**
1. Valida que `df_simulacion` no este vacio.
2. Busca el primer `n_activos` con `reduccion_pct < umbral_reduccion`.
3. Si existe, retorna ese N.
4. Si no existe, retorna el maximo N disponible.

---

### 4) FUNCION: `analizar_contribuciones(retornos, pesos=None)`

**Proposito**  
Medir contribuciones al rendimiento y al riesgo, e identificar activos diversificadores.

**Paso a paso**
1. Valida que `retornos` no este vacio.
2. Si `pesos` es `None`, usa equiponderada (1/N).
3. Valida longitud de pesos y que sumen 1 (tolerancia 1e-6).
4. Calcula rendimientos esperados anualizados: `retornos.mean() * 252`.
5. Contribucion al rendimiento: `pesos * rendimientos_esperados`.
6. Covarianzas con la cartera:
   - `cov_matrix_diaria = retornos.cov().values`
   - `covarianzas_cartera_diaria = cov_matrix_diaria @ pesos`
   - Anualiza multiplicando por 252.
7. Contribucion al riesgo: `pesos * covarianzas_cartera`.
8. Marca diversificadores: `rendimiento > 0` y `covarianza < 0`.
9. Retorna DataFrame ordenado por `contribucion_riesgo` descendente.

---

### 5) FUNCION: `visualizar_frontera_diversificacion(df_simulacion, ruta_guardado=None)`

**Proposito**  
Visualizar la frontera de diversificacion y la descomposicion del riesgo.

**Paso a paso**
1. Valida que `df_simulacion` no este vacio.
2. Crea figura con 2 subplots.
3. Subplot 1:
   - Grafica volatilidad media vs N.
   - Banda de confianza con `volatilidad_std`.
   - Dibuja limite teorico (ultimo `riesgo_sistematico`).
   - Marca frontera practica donde `reduccion_pct < 2%`.
4. Subplot 2:
   - Convierte varianzas a volatilidades (%).
   - Dibuja area de riesgo especifico.
   - Dibuja linea de riesgo total usando suma de varianzas y raiz.
   - Dibuja linea del limite sistematico.
   - Anota que las volatilidades no se suman directamente.
5. `plt.tight_layout()` y guarda si hay `ruta_guardado`.
6. Retorna la figura.

---

## FLUJO DE TRABAJO TIPICO

1. `resultado_eq = analizar_cartera_equiponderada(retornos)`
2. `df_frontera = simular_frontera_diversificacion(retornos, n_simulaciones=100)`
3. `n_optimo = detectar_frontera_optima(df_frontera, umbral_reduccion=2.0)`
4. `df_contrib = analizar_contribuciones(retornos)`
5. `visualizar_frontera_diversificacion(df_frontera, ruta_guardado='output.png')`

---

## VALIDACIONES Y SALIDAS EN CONSOLA

- Error si el DataFrame esta vacio.
- Advertencia si la formula teorica no coincide con el calculo directo.
- Tabla impresa al simular la frontera.

---

## NOTAS IMPORTANTES

- Varianzas y covarianzas se anualizan multiplicando por 252.
- Volatilidades se obtienen con raiz cuadrada.
- La reduccion porcentual mide el beneficio marginal de diversificacion.
- La grafica de riesgo total usa suma de varianzas, no suma de volatilidades.
