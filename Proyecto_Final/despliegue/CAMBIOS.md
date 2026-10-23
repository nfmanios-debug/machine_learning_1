# Cambios para el despliegue

Alcohol es una etiqueta simulada. Los resultados no respaldan uso clínico.

## Frente al Colab final entregado

| Aspecto | Colab recibido | Base del despliegue |
|---|---|---|
| Archivo | Identificación temprana del consumo perjudicial de alcohol en Bogotá.ipynb | cuaderno_PFI.ipynb corregido del repositorio |
| Filas | 101.497, excluye tres registros intersexuales | 101.500, conserva todos los registros |
| Preparación | One-hot antes de separar | Pipeline dentro de cada fold |
| Particiones | Reúne train y test para CV | 60 % desarrollo / 20 % umbral / 20 % prueba |
| Hiperparámetros | Configuraciones fijas | GridSearchCV de 5 folds |
| Umbral | 0,62 para Alcohol explorado sobre prueba | 0,13 para Alcohol, seleccionado en reserva independiente |
| Costo | Prioridad narrativa a Otras SPA | Supuesto explícito 5 FN + FP, positivo Alcohol=1 |
| Modelo a publicar | Último ajuste del bucle de CV | Ganador ajustado en las 60.900 filas de desarrollo |
| Evaluación | Resultados afectados por reutilización de prueba | Métricas finales ya guardadas, no recalculadas en la app |
| Narrativa | Incluye afirmaciones de pacientes rescatados y texto de una versión inicial | Aprendizaje de un generador, sin impacto clínico demostrado |

El costo 5:1 y el objetivo positivo difieren del criterio narrativo del Colab. Se usan porque
ya estaban fijados en el protocolo corregido, no porque sean costos oficiales. No se selecciona
otra variante después de comparar la prueba. Se conservan las limitaciones, incluso si hacen
menos favorable la conclusión del modelo.

## Cambios de ingeniería

- Quitar dependencia de sesiones de Colab y montaje de Drive.
- Versionar Pipeline, coeficientes, esquema, ejemplos ficticios y tablas agregadas.
- Cargar el modelo una sola vez por proceso y cachear recursos; no reentrenar por interacción.
- Ejecutar inferencia del Pipeline en Streamlit y la misma regresión algebraica en HTML.
- Incrustar datos, CSS y JavaScript en la presentación para uso sin conexión.
- Exportar el cuaderno corregido con sus salidas, diferenciándolo del Colab original.
- Mantener fijas las métricas de prueba; el control de umbral solo explora validación.
- Documentar que el resultado de prueba clasifica casi todo como Alcohol y no acredita utilidad operativa.

El notebook del equipo y los documentos Word existentes no se modifican.
