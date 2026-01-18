# RESUMEN TEÓRICO COMPLETO: CARTERAS EQUIPONDERADAS Y DIVERSIFICACIÓN

## INTRODUCCIÓN

Este documento presenta la teoría completa sobre el análisis de carteras equiponderadas y el efecto de la diversificación, basado en los notebooks teóricos de `teoria`. La diversificación es uno de los conceptos fundamentales en teoría de carteras, demostrando cómo se puede reducir el riesgo sin sacrificar rendimiento mediante la combinación de activos no perfectamente correlacionados.

---

## 1. CARTERAS EQUIPONDERADAS

### 1.1 Definición

Una cartera equiponderada (equally-weighted portfolio) es aquella donde cada activo tiene el mismo peso:

$$w_i = \frac{1}{n} \quad \forall i = 1, 2, ..., n$$

Donde $n$ es el número de activos en la cartera.

**Propiedades:**
- Todos los activos tienen la misma importancia en la cartera
- No requiere estimaciones de rentabilidades esperadas ni covarianzas (excepto para análisis)
- Es un benchmark simple y común en la práctica
- Representa una estrategia de inversión "naive" o sin información

### 1.2 Rentabilidad de Cartera Equiponderada

Para una cartera equiponderada, la rentabilidad esperada es simplemente el promedio de las rentabilidades individuales:

$$E(\tilde{R_p}) = \sum_{i=1}^{n} w_i E(\tilde{R_i}) = \frac{1}{n}\sum_{i=1}^{n} E(\tilde{R_i}) = \bar{\mu}$$

Donde $\bar{\mu}$ es la rentabilidad promedio de los activos.

**Interpretación:**
- La rentabilidad de la cartera es el promedio simple de rentabilidades individuales
- NO depende de las correlaciones entre activos
- Es aditiva y lineal

---

## 2. DESCOMPOSICIÓN DEL RIESGO EN CARTERAS EQUIPONDERADAS

### 2.1 Varianza General de una Cartera

La varianza de una cartera con $n$ activos viene dada por:

$$\sigma_p^2 = \sum_{i=1}^{n} w_i^2 \sigma_i^2 + \sum_{i=1}^{n}\sum_{j=1}^{n} w_i w_j \sigma_{ij} \quad \forall i \neq j$$

Donde:
- Primer término: Suma de varianzas individuales ponderadas
- Segundo término: Suma de covarianzas entre pares de activos

### 2.2 Varianza de Cartera Equiponderada

Para una cartera equiponderada donde $w_i = \frac{1}{n}$ para todos los activos:

$$\sigma_p^2 = \sum_{i=1}^{n} \left(\frac{1}{n}\right)^2 \sigma_i^2 + \sum_{i=1}^{n}\sum_{j=1}^{n} \frac{1}{n} \cdot \frac{1}{n} \sigma_{ij} \quad \forall i \neq j$$

Simplificando:

$$\sigma_p^2 = \frac{1}{n^2}\sum_{i=1}^{n} \sigma_i^2 + \frac{1}{n^2}\sum_{i=1}^{n}\sum_{j=1}^{n}\sigma_{ij} \quad \forall i \neq j$$

### 2.3 Reformulación usando Promedios

Definiendo:
- **Varianza media**: $\bar{V} = \frac{1}{n}\sum_{i=1}^{n} \sigma_i^2$ (promedio de varianzas individuales)
- **Covarianza media**: $\bar{\sigma_{ij}} = \frac{1}{n(n-1)}\sum_{i=1}^{n}\sum_{j=1}^{n}\sigma_{ij}$ (promedio de covarianzas entre pares)

La varianza puede expresarse como:

$$\boxed{\sigma_p^2 = \frac{1}{n}\bar{V} + \left(1 - \frac{1}{n}\right) \bar{\sigma_{ij}}}$$

**Descomposición:**
1. **Primer término** ($\frac{1}{n}\bar{V}$): Riesgo específico (diversificable)
2. **Segundo término** ($\left(1 - \frac{1}{n}\right)\bar{\sigma_{ij}}$): Riesgo sistemático (no diversificable)

---

## 3. EL EFECTO DE LA DIVERSIFICACIÓN

### 3.1 Límite de la Diversificación

**Cuando $n \to \infty$:**

$$\lim_{n \to \infty} \sigma_p^2 = \lim_{n \to \infty} \left[\frac{1}{n}\bar{V} + \left(1 - \frac{1}{n}\right)\bar{\sigma_{ij}}\right] = \bar{\sigma_{ij}}$$

**Interpretación Fundamental:**
- El primer término $\frac{1}{n}\bar{V}$ **tiende a cero** cuando aumenta el número de activos
- El segundo término $\bar{\sigma_{ij}}$ **permanece constante**
- **Conclusión**: La diversificación puede eliminar el riesgo específico, pero **NO** el riesgo sistemático

### 3.2 Riesgo Específico vs. Riesgo Sistemático

**Riesgo Específico (Diversificable):**
- **Representado por**: $\frac{1}{n}\bar{V}$ (varianza promedio de activos individuales)
- **Características**:
  - Disminuye a medida que aumenta el número de activos
  - Puede eliminarse completamente con diversificación suficiente
  - Es único de cada activo (riesgo idiosincrático)
  - También llamado "riesgo no sistemático" o "riesgo diversificable"
- **Ejemplos**: 
  - Problemas específicos de una empresa (quiebra, escándalos)
  - Eventos que afectan solo a un sector o industria
  - Riesgos operacionales específicos de la compañía

**Riesgo Sistemático (No Diversificable):**
- **Representado por**: $\bar{\sigma_{ij}}$ (covarianza promedio entre activos)
- **Características**:
  - Permanece constante independientemente del número de activos
  - **NO** puede eliminarse mediante diversificación
  - Afecta a todos los activos del mercado simultáneamente
  - También llamado "riesgo de mercado" o "riesgo beta"
- **Ejemplos**:
  - Recesiones económicas globales
  - Cambios en tipos de interés
  - Crisis financieras sistémicas
  - Inflación generalizada
  - Cambios en políticas macroeconómicas

**Implicación Teórica:**
Este resultado justifica por qué los inversores exigen un premio por asumir riesgo: el riesgo sistemático no puede evitarse mediante diversificación, por lo que debe ser compensado con mayor rentabilidad esperada. Este es el fundamento del modelo CAPM (Capital Asset Pricing Model).

### 3.3 Frontera de Diversificación

La **frontera de diversificación** muestra cómo el riesgo total de la cartera evoluciona al aumentar el número de activos:

**Comportamiento Típico:**
- **N pequeño (2-10 activos)**: Reducción rápida de riesgo al añadir activos
- **N medio (10-30 activos)**: Reducción moderada, beneficios marginales decrecientes
- **N grande (30+ activos)**: Reducción muy pequeña, aproximación al límite sistemático

**Punto Óptimo Práctico:**
En la práctica, se considera que se ha alcanzado la "frontera eficiente de diversificación" cuando la reducción marginal de riesgo al añadir un activo más es menor a un umbral (típicamente 1-2%). Esto identifica el número óptimo de activos para inversión.

---

## 4. CONTRIBUCIÓN DE ACTIVOS A LA CARTERA

### 4.1 Contribución al Rendimiento

**Fórmula:**
$$Contribución_i^{Rendimiento} = w_i E(\tilde{R_i})$$

**Propiedades:**
- Depende **solo del peso** $w_i$ y la rentabilidad esperada del activo
- **NO depende de la composición de la cartera**
- Es aditiva: $E(\tilde{R_p}) = \sum_{i=1}^{N} w_i E(\tilde{R_i})$

**Para cartera equiponderada:**
$$Contribución_i^{Rendimiento} = \frac{1}{n} E(\tilde{R_i})$$

### 4.2 Contribución al Riesgo

**Fórmula:**
$$Contribución_i^{Riesgo} = w_i \cdot cov(\tilde{R_i}, \tilde{R_P}) = w_i \cdot \sigma_{i,P}$$

Donde $\sigma_{i,P}$ es la covarianza del activo $i$ con la cartera $P$.

**Propiedades:**
- Depende **tanto del peso** $w_i$ **como de la composición de la cartera**
- Un mismo activo puede aportar diferente riesgo a diferentes carteras
- La contribución total al riesgo es: $\sigma_p^2 = \sum_{i=1}^{N} w_i \sigma_{i,P}$

**Nota importante:** La contribución al riesgo se calcula como $w_i \times \sigma_{i,P}$, donde $\sigma_{i,P}$ es la covarianza con la **cartera total**, no con otros activos individuales.

### 4.3 Activos Diversificadores Ideales

**Criterio:**
Un activo es "diversificador ideal" si cumple **ambas** condiciones:

1. **Rentabilidad esperada positiva**: $E(\tilde{R_i}) > 0$
   - Aportará rendimiento a la cartera

2. **Covarianza negativa con la cartera**: $cov(\tilde{R_i}, \tilde{R_P}) < 0$
   - Reducirá el riesgo total de la cartera

**Por qué es ideal:**
Si un activo tiene:
- $E(\tilde{R_i}) > 0$ **Y** $cov(\tilde{R_i}, \tilde{R_P}) < 0$

Entonces:
- **Aumenta el rendimiento** de la cartera
- **Disminuye el riesgo** de la cartera

Este es el activo **perfecto** para diversificación: mejora ambas dimensiones simultáneamente.

**Interpretación de covarianza negativa:**
- Covarianza negativa significa que cuando la cartera tiene rendimientos bajos, este activo tiende a tener rendimientos altos
- Actúa como "seguro" o "hedge" para la cartera
- Ejemplos típicos: activos de sectores defensivos, activos de bajo riesgo en carteras de alto riesgo

---

## 5. SIMULACIÓN DE LA FRONTERA DE DIVERSIFICACIÓN

### 5.1 Método Monte Carlo

Para evaluar cuántos activos se necesitan para alcanzar el límite práctico de diversificación, se utiliza simulación Monte Carlo:

**Proceso:**
1. Para cada valor de N (número de activos):
   - Realizar múltiples simulaciones (ej: 100)
   - En cada simulación, seleccionar N activos aleatorios
   - Calcular riesgo de cartera equiponderada
   - Descomponer en riesgo específico y sistemático
2. Promediar resultados de todas las simulaciones
3. Calcular reducción porcentual vs N-1

**Por qué múltiples simulaciones:**
- Diferentes selecciones de activos pueden dar diferentes resultados
- El promedio captura el comportamiento "típico" o esperado
- Permite calcular bandas de confianza (desviación estándar)

### 5.2 Métricas de la Frontera

**Volatilidad Total:**
$$\sigma_p = \sqrt{\sigma_p^2} = \sqrt{\frac{1}{n}\bar{V} + \left(1 - \frac{1}{n}\right)\bar{\sigma_{ij}}}$$

**Riesgo Específico (volatilidad):**
$$\sigma_{especifico} = \sqrt{\frac{1}{n}\bar{V}}$$

**Riesgo Sistemático (volatilidad):**
$$\sigma_{sistematico} = \sqrt{\bar{\sigma_{ij}}}$$

**Nota crítica:** Las volatilidades **NO** se suman directamente:
$$\sigma_{total} \neq \sigma_{especifico} + \sigma_{sistematico}$$

La relación correcta es:
$$\sigma_{total}^2 = \sigma_{especifico}^2 + \sigma_{sistematico}^2$$

Por lo tanto:
$$\sigma_{total} = \sqrt{\sigma_{especifico}^2 + \sigma_{sistematico}^2}$$

### 5.3 Reducción Marginal de Riesgo

**Definición:**
La reducción porcentual de riesgo al añadir un activo más:

$$Reducción\% = \frac{\sigma_p(N-1) - \sigma_p(N)}{\sigma_p(N-1)} \times 100\%$$

**Interpretación:**
- Mide el beneficio marginal de diversificación
- Valores altos (>5%): Diversificación muy beneficiosa
- Valores bajos (<2%): Beneficios marginales pequeños
- Umbral práctico: Cuando reducción < 2%, se considera que se alcanzó el límite

---

## 6. ANUALIZACIÓN Y CONSISTENCIA TEMPORAL

### 6.1 Anualización de Varianzas y Covarianzas

**Varianza:**
$$\sigma^2_{anual} = \sigma^2_{diaria} \times 252$$

**Covarianza:**
$$\sigma_{ij,anual} = \sigma_{ij,diaria} \times 252$$

**Razón:**
- Varianzas y covarianzas escalan **linealmente** con el tiempo
- 252 días de trading por año es la convención estándar
- Mantiene la consistencia temporal en todos los cálculos

### 6.2 Anualización de Volatilidades

**Volatilidad:**
$$\sigma_{anual} = \sigma_{diaria} \times \sqrt{252}$$

**Razón:**
- La volatilidad escala con la **raíz cuadrada** del tiempo
- Viene de la teoría de procesos estocásticos (Browniano)
- Si $\sigma^2_{anual} = \sigma^2_{diaria} \times 252$, entonces $\sigma_{anual} = \sigma_{diaria} \times \sqrt{252}$

**Importante:**
La relación entre varianza y volatilidad es crucial:
- Se suman **varianzas** (no volatilidades)
- Se toma raíz cuadrada del resultado para obtener volatilidad total

---

## 7. VERIFICACIÓN NUMÉRICA

### 7.1 Verificación de Fórmula Teórica

Para validar que la descomposición teórica es correcta, se puede calcular la varianza de dos formas:

**Método 1: Fórmula teórica**
$$\sigma_p^2 = \frac{1}{n}\bar{V} + \left(1 - \frac{1}{n}\right)\bar{\sigma_{ij}}$$

**Método 2: Cálculo directo**
$$\sigma_p^2 = \mathbf{w}^T \mathbf{C} \mathbf{w}$$

Donde:
- $\mathbf{w} = [1/n, 1/n, ..., 1/n]^T$ (vector de pesos equiponderados)
- $\mathbf{C}$ es la matriz de covarianzas

**Validación:**
Si la diferencia entre ambos métodos es menor que una tolerancia numérica (ej: $10^{-6}$), se confirma que la fórmula teórica es correcta.

---

## CONCLUSIONES TEÓRICAS

1. **La diversificación reduce el riesgo específico** mediante la combinación de activos no perfectamente correlacionados

2. **El riesgo sistemático no puede diversificarse** y representa el límite teórico de reducción de riesgo

3. **La fórmula de descomposición** $\sigma_p^2 = \frac{1}{n}\bar{V} + \left(1 - \frac{1}{n}\right)\bar{\sigma_{ij}}$ es fundamental para entender el efecto de diversificación

4. **La frontera de diversificación** identifica el número óptimo de activos necesario para alcanzar el límite práctico

5. **Los activos diversificadores ideales** tienen rentabilidad positiva y covarianza negativa con la cartera

6. **Las varianzas se suman, no las volatilidades**: $\sigma_{total} = \sqrt{\sigma_{especifico}^2 + \sigma_{sistematico}^2}$

7. **La anualización debe ser consistente**: varianzas/covarianzas se multiplican por 252, volatilidades por $\sqrt{252}$
