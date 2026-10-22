# Declaración de uso de inteligencia artificial

Herramienta usada en esta intervención: OpenAI Codex, asistente en la aplicación de escritorio.
Fecha de contexto de la sesión: 21 de octubre de 2026. La ejecución registra adicionalmente su hora UTC.
No se declara un identificador de modelo ni versiones de herramientas de IA no verificables.

## Prompts y alcance
1. Solicitud inicial (síntesis, no transcripción): actuar como ingeniero y científico de datos senior,
   completar el proyecto CRISP-DM, baseline y tres familias, Pipeline sin fuga, CV, costo y umbral,
   ficha de datos, declaración de IA y resumen ejecutivo en inglés de 250–350 palabras.
2. Prompt del usuario: «revisa el archivo adjunto (notebbok) si puedes definir y extaer los insumos faltantes».
3. Solicitud de revisión (síntesis): interpretar la imagen de métricas y comprobar carga por API
   desde Datos Abiertos Bogotá conservando la limpieza existente.
4. Solicitud de carga (extracto literal): «Revisa si coincide con el esquema del notebook y prepara
   la carga reproducible conservando el proceso de limpieza existente; señala por separado los cambios
   necesarios para evitar fuga de datos.»
5. Prompt de autorización final: «Avanza con todo el desarrollo y los entregables, dejando claro que
   Alcohol es una etiqueta simulada. Corrige la fuga de datos, instala las dependencias necesarias y
   ejecuta el notebook completo para validar los resultados. y deja la publicación de todos los entregables
   en el repo dentro de la carpeta proyecto final con el commit adecuado».

## Contenido incorporado
- Carga por hash y rutas relativas; notebook completo comentado y reestructurado en CRISP-DM.
- Pipeline, tratamiento explícito de desconocidos y conservación de categorías de sexo minoritarias.
- Baseline, logística, árbol y bosque; CV de cinco folds; selección por costo 5:1 asumido.
- Reserva independiente para el umbral, prueba final única, variabilidad, escenarios y diagnósticos.
- Código para ejecutar, generar documentos, verificar resultados y empaquetar entregables.
- Redacción del informe, ficha, resumen, trazabilidad y limitaciones.

## Contenido descartado o corregido
- Interpretar Alcohol como diagnóstico real, estimación de prevalencia o predicción futura.
- Afirmar validación epidemiológica por comparar gráficos con las propias reglas del simulador.
- Imputar sexo/etnia usando distribuciones del conjunto completo y codificar antes de dividir.
- Eliminar registros intersexuales por su escasez sin una justificación válida.
- Inventar costos oficiales, contribuciones individuales, fecha original de descarga o historial R10–R18.
- Usar exactitud como criterio principal y confundir FP con FN.

## Verificación humana y atribución
Los nombres del equipo se tomaron del notebook original: Oscar Andrés Ramos Villanueva,
Alvaro Cabezas y Nelsón Fabián Manios. No se conoce qué integrante usó IA previamente ni sus prompts.
No se atribuye esta conversación a una persona concreta. Cada integrante debe confirmar su uso previo,
su aporte y su comprensión antes de la entrega académica. Esta declaración documenta únicamente
la intervención observable; no afirma que el equipo haya revisado o aceptado cada línea.
Los resultados numéricos proceden de ejecución del código, no de generación de cifras por el asistente.
