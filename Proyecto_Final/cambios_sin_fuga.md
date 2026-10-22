# Correcciones de fuga y validez

1. Las particiones se forman con predictores crudos: 60% desarrollo, 20% umbral, 20% prueba.
2. Los vocabularios y transformaciones quedan en Pipeline y se ajustan dentro de cada fold.
3. Se sustituye la imputación probabilística por localidad por categoría desconocida; no se aprende
   información de prueba ni se inventan sexo o etnia.
4. Se seleccionan hiperparámetros y familia por CV con umbral fijo previo de 1/6.
5. El umbral final se elige en una reserva no usada para ajustar parámetros del modelo.
6. El modelo no se reajusta tras elegir el umbral. Prueba se predice una vez, al final.
7. Las tablas globales de calidad son descriptivas del archivo; no se usan para seleccionar modelos.
8. La etiqueta se genera por reglas fijas por fila, sin estimaciones globales. Esto evita fuga de
   preparación, pero no resuelve la falta de una etiqueta observada ni prueba validez clínica.
9. CV usada para selección puede ser optimista; se informa y se mantiene prueba independiente.
10. La partición aleatoria solo evalúa el simulador; la independencia de personas no está demostrada.

También se conserva la categoría Intersexual, se corrigen marcadores y se documenta policonsumo.
No se confunde ninguna de estas decisiones con la validación de un diagnóstico real.
