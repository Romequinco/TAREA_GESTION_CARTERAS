# POSIBLES MEJORAS Y SIGUIENTES PASOS

## 1) MEJORAS EN DATOS Y ESTIMACION
- Usar estimadores robustos o shrinkage para Σ (Ledoit-Wolf, OAS).
- Aplicar winsorizacion o filtros de outliers en retornos.
- Estimar μ con medias moviles o modelos factor (CAPM / APT).

## 2) MEJORAS EN SELECCION
- Seleccion por clustering de correlaciones (diversificacion por grupos).
- Penalizar activos con alta correlacion mutua en el score.
- Estabilidad temporal: seleccionar activos que sean top en varias ventanas.

## 3) MEJORAS EN OPTIMIZACION
- Regularizacion L2 / L1 para reducir concentracion.
- Restricciones de rotacion (turnover) para evitar cambios extremos.
- Optimizar con objetivos alternativos: risk parity o min CVaR.

## 4) VALIDACION Y ROBUSTEZ
- Validacion out-of-sample (train/test) y backtest simple.
- Sensibilidad a parametros (peso_sharpe, peso_decorrelacion, umbral).
- Comparar con benchmarks reales o indices sinteticos.

## 5) VISUALIZACIONES Y REPORTES
- Graficos de estabilidad de pesos por ventana.
- Tabla de contribucion al riesgo antes y despues de seleccionar.
- Reporte automatico en PDF o notebook.
