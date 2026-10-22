"""Genera documentos desde resultados ejecutados, sin entrenar ni consultar prueba."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
r = json.loads((ROOT / 'resultados.json').read_text(encoding='utf-8'))
v = json.loads((ROOT / 'validacion_ejecucion.json').read_text(encoding='utf-8'))
assert v['exito'] and v['celdas_ejecutadas'] == v['celdas_codigo'], 'Se exige ejecución completa'
t, b = r['test'], r['baseline_test']
cv = pd.read_csv(ROOT / 'comparacion_modelos.csv')
quality = pd.read_csv(ROOT / 'calidad_columnas.csv')
costs = pd.read_csv(ROOT / 'sensibilidad_costos.csv')
groups = pd.read_csv(ROOT / 'diagnostico_segmentos.csv')
delta = b['costo'] - t['costo']
ahorro = 100 * delta / b['costo']
modelo_ingles = {'Dummy': 'the constant baseline', 'Logistica': 'logistic regression',
                 'Arbol': 'a decision tree', 'Bosque': 'a random forest'}[r['modelo_final']]

def guardar(nombre, texto):
    # UTF-8 y terminador final uniforme para lectura y control de versiones.
    (ROOT / nombre).write_text(texto.strip() + '\n', encoding='utf-8')

def tabla_md(frame):
    cab = '| ' + ' | '.join(map(str, frame.columns)) + ' |\n'
    sep = '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |\n'
    return cab + sep + '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in frame.itertuples(index=False, name=None))

guardar('ficha_datos.md', f'''# Ficha de datos

## Procedencia y versión
Publicador: Secretaría Distrital de Salud de Bogotá (SDS). Sistema: VESPA.
Conjunto: Consumo abusivo o problemático de sustancias psicoactivas.
Fuente: https://datosabiertos.bogota.gov.co/dataset/consumo-abusivo-o-problematico-de-sustancias-psicoactivas
Ficha nacional consultada: https://www.datos.gov.co/es/dataset/Consumo-abusivo-o-problem-tico-de-sustancias-psico/xv5p-tmjx
Licencia declarada en esa ficha: Creative Commons Attribution 4.0 (CC BY 4.0),
https://creativecommons.org/licenses/by/4.0/. Se conserva la atribución a SDS.
Archivo: datos_crudos/osb_saludmental_-consumoabusivo_spageneral.csv.
Acceso local y consulta de documentación en esta sesión: 21 de octubre de 2026 (fecha de contexto del usuario, America/Bogota).
Fecha de descarga histórica del equipo: no documentada. No se equipara con la fecha de esta revisión.
El archivo fue suministrado por el usuario, no descargado automáticamente del portal durante la ejecución.
SHA-256: `{r['sha256_datos']}`. Tamaño: 15.879.321 bytes.

## Unidad y cobertura
101.500 filas y 21 columnas crudas; años 2015–2026. El rango no garantiza cobertura completa de 2026.
La columna CASOS contiene frecuencias publicadas; una fila no se equipara automáticamente a una persona.
La ausencia de identificador no permite verificar eventos repetidos de una persona.
Se trata de registros de vigilancia y atención, no de una muestra representativa de toda Bogotá.
La cobertura institucional, el acceso a atención y el reporte pueden generar sesgo de selección.
SaluData advierte que un evento puede involucrar varias sustancias; las categorías reales no son excluyentes.

## Diagnóstico por columna
Se encontraron 150 celdas nulas pandas (44 en SEXO y 106 en PERTENENCIAETNICA) y cero duplicados exactos.
Los marcadores textuales se cuentan por separado; no se suman dos veces con los nulos.

{tabla_md(quality)}

## Preparación y objetivo
Se conservan las 101.500 filas, incluidos tres registros intersexuales. No se imputan atributos sensibles
probabilísticamente. El Pipeline normaliza espacios y marcadores, representa categorías ausentes como
Desconocido, codifica categorías solo con entrenamiento y transforma SI/NO a 1/0.
Se seleccionan 14 predictores crudos; el ajuste final genera {r['columnas_transformadas']} columnas numéricas.
No se incluyen CASOS, vía de llegada a tratamiento, variables temporales ni la probabilidad generadora.
Alcohol es una etiqueta binaria **simulada**. Se usa probabilidad base 0,70 con incrementos heredados
del notebook original y límites [0,05; 0,95]. Los pesos no han sido estimados de datos observados de alcohol.
Los faltantes no aportan incrementos al generador. La semilla es 2026; se usa numpy.default_rng.
No existe una columna Alcohol observada en el CSV. No se solicita bono de datos reales para el resultado simulado.

## Referencias APA 7
Secretaría Distrital de Salud. (s. f.). *Consumo abusivo o problemático de sustancias psicoactivas* [Conjunto de datos]. Datos Abiertos Bogotá. Recuperado el 21 de octubre de 2026 de https://datosabiertos.bogota.gov.co/dataset/consumo-abusivo-o-problematico-de-sustancias-psicoactivas

Secretaría Distrital de Salud. (s. f.). *Consumo abusivo o problemático de sustancias psicoactivas en Bogotá D. C.* SaluData. https://saludata.saludcapital.gov.co/osb/indicadores/consumo-abusivo-spa/

La referencia identifica la fuente; el acceso efectivo a la ficha original falló en esta sesión. La licencia
se verificó en el catálogo nacional enlazado, y el contenido se verificó en la copia local por hash.
''')

guardar('declaracion_IA.md', '''# Declaración de uso de inteligencia artificial

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
''')

guardar('trazabilidad_CRISP_DM.md', '''# Trazabilidad CRISP-DM y retos

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
''')

guardar('cambios_sin_fuga.md', '''# Correcciones de fuga y validez

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
''')

summary = f'''Bogotá's public health teams face the challenge of prioritizing assessments while balancing missed cases against unnecessary referrals. This academic project explores that decision through a reproducible machine learning experiment using 101,500 published VESPA records. It does not provide a clinically validated screening tool.

The central limitation is explicit: the source file contains no observed alcohol outcome. We therefore generated a simulated binary label from predefined demographic and consumption-setting rules. Positive labels represent simulated alcohol involvement, not confirmed harmful drinking or future risk. Actual substance use may involve multiple substances, so the experimental binary distinction should not be interpreted as a real clinical classification.

Following CRISP-DM, we compared a constant baseline with logistic regression, a decision tree, and a random forest. Preprocessing was fitted inside cross-validation pipelines. Sixty percent of records supported model development, twenty percent supported threshold selection, and twenty percent remained reserved for a single final evaluation. Missing sensitive attributes were retained as unknown rather than probabilistically assigned, and minority sex categories were preserved.

We assumed that a missed positive costs five times as much as an unnecessary positive alert. This ratio is a transparent academic assumption, not an official monetary estimate. The selected model was {modelo_ingles}, with a decision threshold of {r['umbral_final']:.3f}. On the reserved test set, sensitivity was {t['sensibilidad']:.2%}, precision was {t['precision']:.1%}, and weighted error cost was {t['costo']:.4f} units per record, compared with {b['costo']:.4f} for the baseline. The alert rate was {t['fraccion_alertas']:.2%}, making workload a central consideration.

The cost advantage over the baseline was small, and its bootstrap interval included zero. Almost universal alerts offer little practical prioritization. The contribution is an auditable workflow demonstrating decision trade-offs. Any measured improvement reflects learning simulation rules; it does not establish public health impact. Before operational use, decision-makers would need observed outcomes, verified analysis units, temporal and person-level validation, agreed costs, service capacity, and fairness review. The recommended next step is data validation and experimental redesign, not deployment.'''
palabras = len(summary.split())
assert 250 <= palabras <= 350, palabras
guardar('resumen_ejecutivo_EN.md', '# Executive summary\n\n' + summary)

# Estilos comunes: títulos claros y tablas legibles; se construye un informe breve por secciones.
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PFITitle', fontName='Helvetica-Bold', fontSize=19, leading=23,
                          textColor=colors.HexColor('#184765'), spaceAfter=14))
styles.add(ParagraphStyle(name='PFIBody', fontName='Helvetica', fontSize=10.2, leading=14.3,
                          spaceAfter=9, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='PFISmall', fontName='Helvetica', fontSize=8, leading=10.5, spaceAfter=6))

def p(txt, style='PFIBody'):
    return Paragraph(escape(str(txt)).replace('\n', '<br/>'), styles[style])

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#d4dde3'))
    canvas.line(42, 40, A4[0]-42, 40)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#49606c'))
    canvas.drawString(42, 27, 'EAN | PFI | Etiqueta Alcohol simulada - sin uso clínico')
    canvas.drawRightString(A4[0]-42, 27, str(doc.page))

def documento(nombre, contenido):
    SimpleDocTemplate(str(ROOT / nombre), pagesize=A4, rightMargin=42, leftMargin=42,
                      topMargin=42, bottomMargin=52).build(contenido, onFirstPage=footer, onLaterPages=footer)

def tabla(datos, anchos):
    # Las celdas se envuelven como párrafos para evitar texto fuera de sus límites.
    tbl = Table([[p(x, 'PFISmall') for x in fila] for fila in datos], colWidths=anchos, repeatRows=1)
    tbl.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e4eef4')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), 7), ('LINEBELOW', (0,0), (-1,0), 0.8, colors.HexColor('#245a81')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f7f9')])]))
    return tbl

documento('resumen_ejecutivo_EN.pdf', [p('Executive summary', 'PFITitle'),
    p('Simulation-based decision experiment | Universidad EAN', 'PFISmall')] +
    [p(x) for x in summary.split('\n\n')])
assert len(PdfReader(ROOT / 'resumen_ejecutivo_EN.pdf').pages) == 1

story = []
def seccion(titulo, parrafos):
    if story:
        story.append(PageBreak())
    story.append(p(titulo, 'PFITitle'))
    for parrafo in parrafos:
        story.append(p(parrafo))

seccion('1. Problema, decisión y alcance', [
    'Proyecto Final Integrador | Machine Learning I | Universidad EAN',
    'Integrantes: Oscar Andrés Ramos Villanueva, Alvaro Cabezas y Nelsón Fabián Manios.',
    'Se explora una decisión hipotética de priorización de evaluaciones para la Secretaría Distrital de Salud de Bogotá. El ejercicio compara el costo de omitir positivos simulados con el de producir alertas innecesarias. No existe una intervención desplegada ni un impacto asistencial medido.',
    'La variable Alcohol es sintética. El archivo original no identifica alcohol por registro. Se heredan reglas aditivas de un notebook previo y se genera una realización aleatoria reproducible. Por tanto, las predicciones describen el simulador, no consumo observado, diagnóstico, causalidad o riesgo futuro.',
    'El paradigma supervisado sirve para estudiar la reproducción de una función probabilística conocida. El objetivo técnico es comparar familias bajo un protocolo sin fuga; el objetivo de decisión experimental es reducir (5 FN + FP) / n frente a una política constante. La relación 5:1 es un supuesto y se somete a sensibilidad.',
    'No se reclaman bonos de datos reales ni de enfoque: los predictores son publicados, pero el resultado es simulado y no se dispone de evidencia histórica suficiente de microcredenciales o R10. No se despliega un modelo clínico.',
    'Las funciones de pérdida de los algoritmos no se confunden con el costo de decisión. La exactitud se reporta como métrica secundaria: un porcentaje alto no basta si los errores importantes permanecen.'])

seccion('2. Datos y representatividad', [
    'Fuente: Secretaría Distrital de Salud, VESPA, Datos Abiertos Bogotá. La ficha nacional declara CC BY 4.0. Se adjunta el CSV suministrado por el usuario y se atribuye la fuente; no se afirma haber descargado la copia desde la API.',
    'La copia tiene 101.500 filas, 21 columnas (17 de texto y cuatro enteras), cero duplicados exactos y años 2015–2026. SEXO contiene 44 nulos y PERTENENCIAETNICA 106. Los marcadores textuales también indican ausencia y se documentan por columna en ficha_datos.md y calidad_columnas.csv.',
    'El hash SHA-256 permite identificar la versión exacta. La fecha histórica de descarga no se conoce; la revisión local corresponde al contexto de la sesión del 21 de octubre de 2026. El rango de años no garantiza cobertura anual completa.',
    'Los registros proceden de vigilancia y atención: representan eventos reportados bajo cobertura institucional, no toda la población. Acceso desigual, subregistro y selección institucional limitan representatividad. Sin identificador no se puede comprobar repetición por persona. CASOS es una frecuencia publicada y no se interpreta como reincidencia individual.',
    'SaluData describe policonsumo: un caso puede involucrar varias sustancias. La dicotomía Alcohol/Otras de la simulación simplifica ese fenómeno y no permite inferir la sustancia real. Los atributos sensibles y geográficos requieren revisión por su potencial de estigmatización.',
    'Se mantienen las tres filas intersexuales. Su baja frecuencia impide conclusiones de desempeño fiables para ese segmento; no justifica excluirlas del universo. No se inventan atributos sensibles mediante muestreo.'])

seccion('3. Preparación y diseño sin fuga', [
    f'La copia cruda se verifica por hash y esquema. La semilla es 2026. Se seleccionan 14 predictores originales y el ajuste final produce {r["columnas_transformadas"]} columnas transformadas. A diferencia del notebook inicial, no se fuerza un vocabulario de 176 columnas aprendido sobre toda la base.',
    f'Partición estratificada: {r["n_desarrollo"]:,} registros para desarrollo y CV, {r["n_umbral"]:,} para seleccionar umbral y {r["n_test"]:,} para prueba. Se separa antes de ajustar imputación o codificación. Los índices son disjuntos; las pruebas de invariantes están en el cuaderno.',
    'Un Pipeline normaliza marcadores y espacios; representa categorías ausentes como Desconocido; aplica OneHotEncoder con categorías desconocidas ignoradas; convierte sitios SI/NO a 1/0. Los seis sitios tienen un valor reservado -1 para ausencia. Cada fold ajusta su propio vocabulario. No se aplica escalamiento porque todas las entradas son indicadores.',
    'Se excluyen el objetivo, la probabilidad generadora, CASOS, vía de llegada a tratamiento y variables temporales. La exclusión temporal responde al simulador heredado, no demuestra irrelevancia del tiempo. No se aplica sobremuestreo: la asimetría se maneja mediante costos y umbral.',
    'La etiqueta se crea con probabilidad base 0,70 y ajustes de sitios, sexo y etapa vital; los límites son 0,05–0,95. No se aprenden distribuciones globales para generarla. Los faltantes aportan cero al ajuste. La nueva política de conservación y el generador default_rng cambian los conteos respecto de la versión previa.',
    'La partición aleatoria sirve para este experimento sintético. Un despliegue real requiere validar por tiempo y, cuando sea posible, por persona. Evitar fuga de transformación no elimina dependencias ni convierte una etiqueta sintética en observada.'])

seccion('4. Modelado y selección', [
    'Se compararon DummyClassifier (prior), regresión logística, árbol y bosque aleatorio. Se usaron cinco folds estratificados idénticos, con barajado y semilla fija. Las rejillas se declararon antes de entrenar: C = 0,1/1/10 para logística; profundidad 4/8/12 y hoja mínima 100 para árbol; profundidad 6/12/sin límite, 100 árboles y hoja mínima 30 para bosque.',
    'La búsqueda optimiza costo a un umbral de referencia de 1/6, fijado por la razón de costos 5:1. La familia final minimiza costo CV; ante empates se favorece menor desviación y menor complejidad. La reserva de umbral se utiliza después, sin volver a ajustar parámetros del modelo.',
    f'Familia seleccionada: {r["modelo_final"]}. Hiperparámetros: {json.dumps(r["parametros"], ensure_ascii=False)}. La selección incluye el baseline: no se garantiza que una familia compleja deba ganar.',
    'La siguiente desviación y varianza son muestrales entre cinco folds. No son intervalos de confianza independientes, ni incertidumbre sobre otras realizaciones del simulador. CV se usa para elegir parámetros y puede resultar optimista; la prueba final se reserva como evaluación separada.'])
story.append(tabla([['Familia', 'Costo CV', 'DE', 'Varianza', 'ROC-AUC']] +
    [[row.modelo, f'{row.costo_cv:.4f}', f'{row.sd_costo:.5f}', f'{row.var_costo:.2e}', f'{row.auc_cv:.4f}']
      for row in cv.itertuples()], [95, 90, 85, 110, 125]))
story.append(Spacer(1, 12))
story.append(p('Brecha de costo CV menos entrenamiento: ' + '; '.join(f'{row.modelo}: {row.brecha_costo:.4f}' for row in cv.itertuples()) +
    '. Una brecha positiva amplia es compatible con sobreajuste; no constituye una descomposición formal de sesgo y varianza.'))

seccion('5. Umbral, estabilidad y segmentos', [
    f'En la reserva independiente se minimizó el costo sobre una rejilla de 0 a 1 (paso 0,01), incluyendo 1/6. Los empates favorecen sensibilidad. El umbral elegido es {r["umbral_final"]:.3f}. El modelo permanece ajustado solo en desarrollo para no modificar su escala después de elegir el umbral.',
    'Las métricas de esa reserva son de selección y no una evaluación independiente del umbral. Los escenarios 1:1, 2:1, 5:1 y 10:1 muestran cómo cambia la carga de alertas. No se dispone de una restricción real de atención y no se inventa una.'])
story.append(tabla([['Costo FN/FP', 'Umbral', 'Costo', 'Sensibilidad', 'Alertas']] +
    [[int(row.costo_FN_relativo), f'{row.umbral:.3f}', f'{row.costo:.4f}', f'{row.sensibilidad:.1%}', f'{row.fraccion_alertas:.1%}']
     for row in costs.itertuples()], [100, 80, 95, 120, 110]))
story.append(Spacer(1, 10))
story.append(Image(str(ROOT / 'validacion_y_umbral.png'), width=505, height=184))
story.append(p('El diagnóstico por sexo y etapa vital está en diagnostico_segmentos.csv. No se calculan métricas de grupos con menos de 30 filas o una sola clase. Las diferencias reflejan en parte reglas del propio simulador y no prueban equidad real. La importancia por permutación usa reserva de umbral, tres repeticiones y hasta 3.000 registros, al umbral fijo 1/6; no tiene interpretación causal.'))

seccion('6. Evaluación final y límites', [
    'Se realizó una sola predicción probabilística sobre prueba, tras congelar familia, hiperparámetros y umbral. La política Dummy se calculó con la prevalencia de desarrollo. Todas las métricas, figuras e intervalos se derivan de esas predicciones; no se decidió ningún ajuste usando prueba.',
    f'Costo final: {t["costo"]:.4f}; baseline: {b["costo"]:.4f}; diferencia baseline menos modelo: {delta:.4f} unidades por registro ({ahorro:.2f}% del costo baseline). Esta es una comparación de errores sintéticos, no ahorro monetario ni impacto en salud.',
    f'Sensibilidad: {t["sensibilidad"]:.2%}; precisión: {t["precision"]:.2%}; especificidad: {t["especificidad"]:.2%}; F1: {t["f1"]:.4f}; exactitud: {t["accuracy"]:.2%}; ROC-AUC: {t["auc"]:.4f}; average precision (PR-AUC resumida): {t["pr_auc"]:.4f}; Brier: {t["brier"]:.4f}.',
    f'Alertas: {t["fraccion_alertas"]:.2%}. Confusión: TN={t["TN"]}, FP={t["FP"]}, FN={t["FN"]}, TP={t["TP"]}. La clase positiva siempre es Alcohol simulado.',
    f'Bootstrap pareado de 400 remuestreos: IC percentil 95% del costo [{t["IC95_costo"][0]:.4f}, {t["IC95_costo"][1]:.4f}], y de la diferencia frente a Dummy [{t["IC95_ahorro_vs_dummy"][0]:.4f}, {t["IC95_ahorro_vs_dummy"][1]:.4f}]. Los intervalos son condicionales al ajuste y a registros tratados como intercambiables. No cubren dependencia entre eventos, otras semillas ni cambios del generador.',
    'El intervalo de la diferencia incluye cero: no hay evidencia concluyente de reducción de costo frente al baseline bajo este análisis. La alerta casi universal ofrece escasa priorización práctica. Una sensibilidad cercana al 100% con especificidad casi nula no implica un modelo útil para administrar recursos limitados.'])
story.append(Image(str(ROOT / 'evaluacion_final.png'), width=505, height=148))
story.append(p('La simulación no puede validar un resultado que el CSV no observa. Una buena discriminación puede ser consecuencia de recuperar las reglas impuestas. Las probabilidades no están calibradas frente a diagnósticos reales.'))

seccion('7. Decisión, gobernanza y seguimiento', [
    'Decisión recomendada: conservar el trabajo como demostración académica reproducible y no desplegarlo para evaluación individual, priorización territorial real o asignación asistencial. El siguiente paso es obtener un resultado observado con definición explícita y documentar la unidad de análisis.',
    'Antes de un piloto: validar etiquetas de varias sustancias cuando corresponda, verificar permisos y minimización de datos, acordar costos y capacidad, separar por tiempo y persona, evaluar calibración y desempeño por grupos con incertidumbre, y comparar con la práctica existente.',
    'Roles propuestos: el custodio de datos valida procedencia, calidad y acceso; el equipo analítico revisa generalización, deriva y sesgos; un responsable de salud define la decisión y sus salvaguardas. No se atribuyen estos roles como trabajo histórico de los integrantes.',
    'Seguimiento propuesto para un futuro piloto validado: revisión mensual de faltantes, categorías nuevas, cambios de cobertura y volumen de alertas; evaluación periódica de sensibilidad y precisión cuando lleguen resultados observados. Los límites aceptables deben acordarse antes de operar. Suspender si cambia el resultado, falta evidencia de validez o se detecta perjuicio no resuelto.',
    'La fuente pública no elimina riesgos de combinación de cuasi-identificadores. Este repositorio utiliza la copia pública suministrada, sin intentar reidentificar personas. No se exportan listas de personas priorizadas. El uso futuro deberá revisar la normativa y autorización aplicables con la entidad responsable.',
    'La capacidad real y las pérdidas monetarias no están documentadas. Ninguna cifra del ejercicio debe convertirse en una promesa de cobertura, reducción de consumo o prevención de enfermedad.'])

seccion('8. Reproducibilidad, equipo y referencias', [
    f'Ejecución completa desde núcleo nuevo: {v["celdas_ejecutadas"]}/{v["celdas_codigo"]} celdas de código, sin errores; duración {v["duracion_segundos"]:.1f} segundos. El registro y hash del notebook están en validacion_ejecucion.json. Semilla 2026, CSV versionado por SHA-256 y dependencias fijadas en requirements.txt.',
    'La ejecución usa únicamente rutas relativas y no necesita conexión al portal. ejecutar_notebook.py crea un kernel local aislado. generar_entregables.py transforma los resultados ya calculados en documentos y ZIP; no vuelve a evaluar prueba.',
    'Los nombres del equipo proceden del original. No se conoce el reparto histórico de contribuciones ni el uso previo de IA por integrante. declaracion_IA.md documenta esta intervención y los datos que el equipo debe confirmar. No se inventan entregas R10–R18: trazabilidad_CRISP_DM.md vincula los artefactos consolidados actualmente.',
    'Secretaría Distrital de Salud. (s. f.). Consumo abusivo o problemático de sustancias psicoactivas [Conjunto de datos]. Datos Abiertos Bogotá. https://datosabiertos.bogota.gov.co/dataset/consumo-abusivo-o-problematico-de-sustancias-psicoactivas',
    'Secretaría Distrital de Salud. (s. f.). Consumo abusivo o problemático de sustancias psicoactivas en Bogotá D. C. SaluData. https://saludata.saludcapital.gov.co/osb/indicadores/consumo-abusivo-spa/',
    'Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). CRISP-DM 1.0: Step-by-step data mining guide. SPSS.',
    'Scikit-learn developers. (s. f.). Common pitfalls and recommended practices. https://scikit-learn.org/stable/common_pitfalls.html',
    'Scikit-learn developers. (s. f.). Tuning the decision threshold for class prediction. https://scikit-learn.org/stable/modules/classification_threshold.html'])
documento('informe_PFI.pdf', story)
assert len(PdfReader(ROOT / 'informe_PFI.pdf').pages) <= 15

guardar('README.md', f'''# Proyecto Final Integrador · EAN

**Alcohol es una etiqueta simulada. No es un modelo clínico ni de detección real.**
Equipo: Oscar Andrés Ramos Villanueva, Alvaro Cabezas y Nelsón Fabián Manios.

## Resultados ejecutados
- Modelo: {r['modelo_final']}; umbral: {r['umbral_final']:.3f}; costo FN/FP supuesto: 5:1.
- Prueba: sensibilidad {t['sensibilidad']:.2%}, precisión {t['precision']:.2%}, ROC-AUC {t['auc']:.4f}.
- Costo por registro: {t['costo']:.4f}, baseline {b['costo']:.4f}; alertas {t['fraccion_alertas']:.2%}.
- La ventaja de costo es mínima y su intervalo incluye cero; la alerta casi universal no demuestra utilidad operativa.
- CV: cinco folds en 60%; reserva de umbral 20%; prueba final única 20%.
- {v['celdas_ejecutadas']}/{v['celdas_codigo']} celdas ejecutadas desde núcleo nuevo, sin errores.

## Reproducción
Desde esta carpeta, con Python 3.12 y un entorno virtual:
```shell
python -m pip install -r requirements.txt
python ejecutar_notebook.py
python generar_entregables.py
```
También se puede abrir cuaderno_PFI.ipynb y ejecutar todas las celdas desde núcleo reiniciado.
La primera instalación necesita internet; el análisis usa exclusivamente el CSV incluido.
El script de ejecución crea su kernel en tmp/ sin modificar kernels del usuario.
La reproducción verifica el hash de datos; no sustituye automáticamente la copia por datos más recientes.
Reejecutar el protocolo fijado reproduce el experimento; no autoriza cambiar decisiones tras ver prueba.

## Entrega
- cuaderno_PFI.ipynb: código didáctico, narrativa CRISP-DM y salidas ejecutadas.
- informe_PFI.pdf: informe técnico de {len(PdfReader(ROOT / 'informe_PFI.pdf').pages)} páginas.
- resumen_ejecutivo_EN.pdf: una página; {palabras} palabras en el cuerpo.
- ficha_datos.md, declaracion_IA.md, trazabilidad_CRISP_DM.md y cambios_sin_fuga.md.
- datos_crudos/: copia pública suministrada y atribución en ficha_datos.md.
- resultados.json, tablas CSV, figuras y validacion_ejecucion.json: evidencia numérica.
- ML1_PFI_EquipoVESPA.zip: paquete con archivos planos salvo datos_crudos/.

EquipoVESPA es un identificador de empaquetado, no un nombre de equipo confirmado.
Las contribuciones individuales, la fecha histórica de descarga y el uso previo de IA deben ser
confirmados por los integrantes. No se fabricó evidencia histórica ni se reclamaron bonos.

## Cambios metodológicos
Se conserva el CSV de 101.500 filas; no se excluye Intersexual ni se imputa sexo/etnia al azar.
La limpieza, imputación y codificación se encapsulan en Pipeline; ninguna transformación se ajusta
sobre prueba. Se corrige el objetivo narrativo para que coincida con una simulación. No se garantiza
identidad con las 101.497 filas o 176 columnas del notebook original.
''')

# El manifiesto excluye al ZIP y a sí mismo para evitar dependencia circular.
archivos = [p for p in ROOT.rglob('*') if p.is_file() and 'tmp' not in p.relative_to(ROOT).parts
            and '__pycache__' not in p.relative_to(ROOT).parts and p.suffix != '.zip'
            and p.name not in ['manifiesto_sha256.json', '.gitignore']]
manifiesto = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(archivos)}
guardar('manifiesto_sha256.json', json.dumps(manifiesto, ensure_ascii=False, indent=2))
zip_path = ROOT / 'ML1_PFI_EquipoVESPA.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in archivos + [ROOT / 'manifiesto_sha256.json']:
        nombre = path.relative_to(ROOT).as_posix()
        assert '/' not in nombre or nombre.startswith('datos_crudos/')
        z.write(path, nombre)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
print(json.dumps({'resumen_palabras': palabras, 'resumen_paginas': 1,
                  'informe_paginas': len(PdfReader(ROOT / 'informe_PFI.pdf').pages),
                  'archivos_zip': len(archivos) + 1, 'zip_bytes': zip_path.stat().st_size}, indent=2))
