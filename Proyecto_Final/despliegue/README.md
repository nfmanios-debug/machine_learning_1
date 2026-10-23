# Despliegue interactivo · Proyecto Final Integrador EAN

**Alcohol es una etiqueta simulada. No es un diagnóstico ni una estimación validada de riesgo clínico.**

Esta carpeta contiene una aplicación Streamlit, una presentación HTML de ocho diapositivas
y el modelo de demostración. La presentación incluye inferencia real de la regresión exportada
en JavaScript, por lo que funciona también sin internet. No ejecuta celdas Python.

## Abrir la demostración

- Presentación: abrir **index.html** con Chrome, Edge o Firefox. No requiere instalación.
- Notebook con código, tablas y gráficos guardados: **notebook.html**.
- Aplicación pública: https://ean-alcohol-simulado.streamlit.app/
- Estado y URLs de publicación: **configuracion.json**.
- Presentación pública en GitHub Pages:
  https://nfmanios-debug.github.io/machine_learning_1/Proyecto_Final/despliegue/

En el HTML, usar las flechas inferiores o el selector de sección. Los botones de gráficos
reconstruyen visualizaciones con resultados guardados. El botón de predicción calcula una
probabilidad nueva con los coeficientes entrenados. La descarga CSV conserva los valores
sin redondear. El notebook exportado es una vista de evidencia, no un entorno ejecutable.
Para llevar la presentación sin conexión basta index.html; incluir notebook.html si se quiere
abrir también el cuaderno desde su enlace. Los enlaces a fuentes y GitHub necesitan internet.

## Ejecutar Streamlit en el computador

Desde esta carpeta, con Python 3.12 y un entorno virtual:

~~~shell
python -m venv .venv
~~~

Activar en Windows PowerShell:

~~~powershell
.\.venv\Scripts\Activate.ps1
~~~

O en macOS/Linux:

~~~shell
source .venv/bin/activate
~~~

Después:

~~~shell
python -m pip install -r requirements.txt
python -m streamlit run app.py
~~~

El comando muestra la URL local. La primera instalación requiere internet.
La aplicación carga el artefacto incluido: no reentrena al iniciar y no monta Google Drive.
Desde la raíz del repositorio también funciona:
python -m streamlit run Proyecto_Final/despliegue/app.py

## Publicar en Streamlit Community Cloud

1. El titular inicia sesión en https://share.streamlit.io y acepta sus términos.
2. Vincular GitHub con el alcance necesario para este repositorio.
3. Create app → repositorio **nfmanios-debug/machine_learning_1** → rama **main**.
4. Main file path: **Proyecto_Final/despliegue/app.py**.
5. Advanced settings → **Python 3.12** → Deploy.
6. Probar las seis secciones y una predicción desde una ventana sin sesión del propietario.
7. Registrar la URL efectivamente creada en configuracion.json, campo streamlit_url.
8. Ejecutar python generar_html.py y subir el HTML/configuración actualizados.

requirements.txt está junto a app.py para que el servicio use el entorno de la app,
sin instalar la lista completa de dependencias del informe académico.
No se necesitan secretos. Nunca se solicitan credenciales dentro de la app.

La cuenta debe completar su propio acceso; una aplicación validada localmente o un commit
en GitHub no equivalen por sí solos a un alojamiento Streamlit activo.

## Publicar la presentación con GitHub Pages

En Settings → Pages del repositorio:
Source **Deploy from a branch** → Branch **main** → carpeta **/(root)** → Save.
Después del build, abrir la ruta /Proyecto_Final/despliegue/ indicada arriba.
No hace falta modificar archivos fuera de la carpeta solicitada.
GitHub sirve el HTML estático; la predicción del HTML corre localmente en el navegador.

## Base metodológica y relación con el Colab recibido

Se utiliza **../cuaderno_PFI.ipynb**, el experimento corregido y ejecutado del repositorio
(commit base 2f87811dbc048e1a1af17f3cd5eda3c80950c190).
El Colab final se conserva como referencia del equipo, pero no se despliega su evaluación
tal cual: ajustaba la codificación antes de separar, reunía entrenamiento y prueba para CV,
y exploraba umbrales sobre prueba. Además, su modelo era el del último fold.

**Las métricas no son intercambiables.** La aplicación y el HTML usan exclusivamente la
evaluación del protocolo corregido. El archivo notebook.html corresponde a ese protocolo,
no a una exportación silenciosamente modificada del Colab final. Véase CAMBIOS.md.

- Se mantienen 101.500 filas, incluidos tres registros intersexuales.
- Se usan 14 predictores crudos y 185 columnas transformadas; no se fuerzan las 176 de Colab.
- Semilla 2026; división 60 % desarrollo, 20 % reserva de umbral, 20 % prueba.
- Baseline Dummy y tres familias; GridSearchCV de cinco folds con transformaciones dentro de Pipeline.
- Regresión Logística C=0.1; costo académico (5 FN + FP)/n, Alcohol=1.
- Umbral final 0.13 seleccionado con la reserva, no el 0.62 del Colab.
- Los resultados de prueba se leen del JSON guardado; la app nunca abre X_test.
- ROC-AUC de prueba 0.7614; alertas 99.87 %. El intervalo del ahorro de costo frente
  a Dummy incluye cero. **No se demuestra capacidad útil de priorización.**

preparar_modelo.py reconstruye únicamente el ajuste ya elegido en las mismas 60.900 filas.
Comprueba que la curva de costo en validación coincide con la guardada. No hace nuevas
búsquedas, no modifica el umbral y descarta la partición de prueba sin predecirla.
Los hashes del CSV, notebook y modelo están en artefactos/trazabilidad.json.

## Reproducir y verificar

~~~shell
python -m pip install -r requirements-dev.txt
python preparar_modelo.py
python generar_html.py
python -m pytest test_despliegue.py -q
node validar_modelo_html.cjs
~~~

La preparación requiere el CSV y los resultados del directorio padre ya incluidos en Git.
El empaquetado y la generación HTML no vuelven a ejecutar la evaluación de prueba.
Para reproducir el experimento completo, seguir ../README.md antes de preparar el despliegue.
Una reproducción idéntica no autoriza cambiar decisiones tras observar prueba.

Las pruebas comparan 105 escenarios ficticios entre el Pipeline, Python portable y el motor
JavaScript exacto incrustado en el HTML; tolerancia 1e-12. También recorren todas las pantallas
de Streamlit, generan gráficos y prueban tres predicciones. VALIDACION.md documenta lo ejecutado.

## Organización

- app.py: seis pantallas Streamlit, tablas descargables, gráficos y formulario de inferencia.
- index.html: presentación autónoma con predicción local.
- plantilla.html / generar_html.py: fuentes de la presentación y exportación del cuaderno.
- notebook.html: vista completa del cuaderno corregido con sus salidas guardadas.
- modelado.py / preparar_modelo.py: Pipeline y empaquetado reproducible.
- artefactos/: modelo joblib confiable, coeficientes JSON, agregados y resultados versionados.
- evidencias/: capturas de validación de las interfaces.
- test_despliegue.py / validar_modelo_html.cjs: comprobaciones funcionales y de paridad.
- configuracion.json: estado y URLs verificadas del alojamiento.

Solo se carga el joblib incluido y verificado por hash. No se aceptan modelos de terceros
ni archivos cargados por visitantes. Las entradas son ficticias, se mantienen en la sesión
y no se escriben en disco. El proveedor de alojamiento puede conservar logs técnicos;
esto no equivale a ausencia de logs de infraestructura.

## Guion de sustentación y retirada

1. Propósito: distinguir problema de salud pública y experimento sintético.
2. Datos: mostrar una tabla y pulsar Generar gráfico.
3. Experimento: explicar separación, Pipeline y costos supuestos.
4. Modelos y umbral: mostrar variabilidad y mover el control de validación.
5. Prueba: reconocer que las alertas casi universales limitan la utilidad.
6. Demostración: ejecutar dos ejemplos inventados y explicar qué significa la probabilidad.
7. Límites: cerrar con las condiciones que faltarían para investigar una aplicación real.

Antes de presentar, abrir Streamlit y probar la predicción; Community Cloud puede hibernar.
Conservar los dos HTML localmente. Después de que el docente revise la evidencia, eliminar
la app en Streamlit y despublicar Pages si se desea, conservando el repositorio.
No hay eliminación automática programada.

## Fuente y uso de IA

Fuente: Secretaría Distrital de Salud de Bogotá / VESPA. La ficha nacional declara
CC BY 4.0; se conserva la atribución de ../ficha_datos.md. Las tablas cuentan registros,
no personas únicas. No se publican filas individuales adicionales en esta carpeta.

Codex asistió en implementación, documentación y pruebas a petición del usuario.
Se aceptó la adaptación interactiva y el empaquetado del experimento corregido.
Se descartó presentar métricas sintéticas como beneficios clínicos o reutilizar el
umbral seleccionado sobre prueba. No se inventaron resultados ni aportes del equipo.

