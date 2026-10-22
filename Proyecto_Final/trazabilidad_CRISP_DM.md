# Trazabilidad CRISP-DM y retos

Esta es una reconstrucción documental realizada al completar el proyecto. No prueba que existieran
entregas históricas de R10–R18. No se inventan actas, fechas ni aportes individuales.

| Reto | Fase | Evidencia actual |
| --- | --- | --- |
| R10 | Negocio | Sección 1 del cuaderno e informe: destinatario, decisión hipotética, costos y riesgos |
| R11 | Datos | ficha_datos.md, calidad_columnas.csv, CSV crudo y hash |
| R12 | Preparación | Sección 3: partición antes del Pipeline, invariantes y baseline |
| R13 | Modelado/evaluación | comparacion_modelos.csv, metricas_folds.csv y busqueda_*.csv |
| R14 | Consolidación | cuaderno_PFI.ipynb ejecutado e informe_PFI.pdf |
| R15–R17 | Segmentos cuando aplique | diagnostico_segmentos.csv; no se fuerza clustering para una tarea simulada |
| R18 | Cierre | resumen_ejecutivo_EN.pdf, límites, plan de seguimiento y declaración IA |

## Cambios respecto de Investigacion.ipynb
La carga de Drive pasa a un CSV local verificado. Se mantiene la semilla 2026 y la estructura de las
reglas sintéticas, pero se usa default_rng, se retienen todas las filas y no se imputa antes de generar
la etiqueta. Por eso cambian conteos y tamaño de la matriz: no se promete identidad de resultados.
Se conserva la intención de normalizar y codificar; se corrige su ejecución dentro de Pipeline.
Se añaden tres familias, baseline, búsqueda CV, umbral independiente, evaluación y documentos.
La función original que ignoraba el argumento dataframe deja de utilizarse.
Se unifican Sin Dato y Sin dato. Alcohol=1 se usa consistentemente en todas las métricas.

## Aportes y roles
Integrantes declarados en el original: Oscar Andrés Ramos Villanueva, Alvaro Cabezas y Nelsón Fabián Manios.
El usuario informó que un compañero preparó la limpieza; no especificó cuál. No se asigna esa autoría.
Roles propuestos para revisión: custodio de datos, responsable de modelado y responsable de comunicación.
La distribución histórica y la participación individual deben ser confirmadas por el equipo.
