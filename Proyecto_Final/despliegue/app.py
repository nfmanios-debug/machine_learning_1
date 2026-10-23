"""Aplicación de sustentación EAN. Ejecutar con: streamlit run app.py."""
from pathlib import Path
import hashlib
import json
import sys
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

# Resolver imports y archivos desde este script, también al arrancar desde la raíz Git.
BASE = Path(__file__).resolve().parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
from modelado import AVISO, CATEGORICAS, BINARIAS, NOMBRES, PREDICTORAS

st.set_page_config(page_title='Alcohol simulado · EAN', page_icon='◈', layout='wide')
ARTEFACTOS = BASE / 'artefactos'
REPO = 'https://github.com/nfmanios-debug/machine_learning_1/tree/main/Proyecto_Final/despliegue'


@st.cache_data
def leer_json(nombre):
    """Cachear recursos versionados; no se consulta Drive ni se reciben datos personales."""
    return json.loads((ARTEFACTOS / nombre).read_text(encoding='utf-8'))


@st.cache_resource
def cargar_modelo():
    """Cargar únicamente nuestro artefacto local después de verificar su integridad."""
    archivo = ARTEFACTOS / 'pipeline.joblib'
    esperado = leer_json('trazabilidad.json')['sha256_pipeline']
    if hashlib.sha256(archivo.read_bytes()).hexdigest() != esperado:
        raise ValueError('El modelo no coincide con el artefacto verificado.')
    return joblib.load(archivo)


def tabla_csv(nombre, columnas=None):
    """Mostrar y permitir descargar exactamente la evidencia que se está discutiendo."""
    datos = pd.read_csv(ARTEFACTOS / nombre)
    st.dataframe(datos if columnas is None else datos[columnas], hide_index=True, width='stretch')
    st.download_button('Descargar tabla CSV', datos.to_csv(index=False).encode('utf-8-sig'),
                       file_name=nombre, mime='text/csv', key='descarga_' + nombre)
    return datos


def estilo_grafico(fig):
    """Dar un formato uniforme y legible a los gráficos de la sustentación."""
    fig.update_layout(template='plotly_white', font=dict(family='Arial', size=15),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=50, b=30))
    return fig


# La advertencia compartida permanece visible en todas las pantallas.
st.markdown('''<style>
.stApp {background:#f7f8f4;color:#112e38}
h1,h2,h3 {letter-spacing:-.035em;color:#112e38}
[data-testid="stSidebar"] {background:#e9f0ed}
.eyebrow {letter-spacing:.16em;font-size:.78rem;font-weight:700;color:#267c72}
.hero {background:#112e38;color:#fff;padding:2rem;border-radius:16px;margin:1rem 0 2rem}
.hero h2 {color:white;font-size:2.6rem;line-height:1.12;max-width:840px}
.hero p {color:#d8e9e4;max-width:780px}
</style>''', unsafe_allow_html=True)
st.sidebar.markdown('### EAN / Machine Learning I')
st.sidebar.caption('Proyecto Final Integrador · CRISP-DM')
pantalla = st.sidebar.radio('Recorrido', ['01 · Propósito', '02 · Datos', '03 · Experimento',
    '04 · Resultados', '05 · Demostración', '06 · Límites'], key='pantalla')
st.sidebar.markdown('**Etiqueta simulada · semilla 2026**')
st.sidebar.link_button('Código y entregables', REPO)
if (BASE / 'index.html').exists():
    st.sidebar.download_button('Descargar presentación HTML', (BASE / 'index.html').read_bytes(),
                               'presentacion_alcohol_simulado.html', 'text/html')
st.markdown('<div class="eyebrow">PROTOTIPO ACADÉMICO / UNIVERSIDAD EAN</div>', unsafe_allow_html=True)
st.warning(AVISO)
r = leer_json('resultados.json')
portable = leer_json('modelo_portable.json')

if pantalla == '01 · Propósito':
    st.markdown('''<div class="hero"><p>DE LOS REGISTROS A UNA DEMOSTRACIÓN REPRODUCIBLE</p>
    <h2>Explorar la clasificación.<br>Reconocer sus límites.</h2>
    <p>Identificación temprana del consumo perjudicial de alcohol en Bogotá es la motivación del
    proyecto. Este experimento aprende una etiqueta generada; todavía no identifica consumo real.</p></div>''', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Registros del archivo', '101.500')
    b.metric('Familias + baseline', '3 + 1')
    c.metric('Semilla', '2026')
    st.subheader('La decisión que sí podemos apoyar')
    st.write('Demostrar cómo cambia una clasificación al variar un umbral y por qué una buena '
             'métrica discriminativa no garantiza una herramienta útil. No se priorizan personas ni recursos reales.')
    st.info('La aplicación usa el protocolo corregido de cuaderno_PFI.ipynb. Las métricas del Colab '
            'recibido no se mezclan con esta evaluación: cambian la preparación y las particiones.')
    st.caption('Equipo: Oscar Andrés Ramos Villanueva · Alvaro José Cabezas Jiménez · Nelsón Fabián Manios Ascencio')

elif pantalla == '02 · Datos':
    st.title('Registros reales, objetivo simulado')
    st.write('Fuente: Secretaría Distrital de Salud de Bogotá / VESPA. Se conservan las 101.500 filas '
             'y 21 columnas crudas. El modelo utiliza 14 predictores; su codificación produce 185 columnas.')
    st.caption('Se cuentan filas, no personas únicas ni prevalencia. CASOS no equivale necesariamente a reincidencia.')
    agrupacion = st.selectbox('Explorar registros por', ['ANO', 'NOMBRELOCALIDADRESIDENCIA', 'CURSO_DE_VIDA'],
                             format_func=lambda x: {'ANO': 'Año', 'NOMBRELOCALIDADRESIDENCIA': 'Localidad', 'CURSO_DE_VIDA': 'Curso de vida'}[x])
    datos = pd.DataFrame(leer_json('agregados.json')[agrupacion])
    st.dataframe(datos, hide_index=True, width='stretch')
    if st.button('▶ Generar gráfico', key='grafico_datos', type='primary'):
        st.session_state['agrupacion_visible'] = agrupacion
    if st.session_state.get('agrupacion_visible') == agrupacion:
        fig = px.bar(datos, x='categoria', y='registros', color_discrete_sequence=['#237f73'],
                     labels={'categoria': 'Categoría publicada', 'registros': 'Número de filas'},
                     title='Cobertura de registros; no riesgo poblacional')
        st.plotly_chart(estilo_grafico(fig), width='stretch')
    with st.expander('Calidad por columna'):
        tabla_csv('calidad_columnas.csv')
    st.markdown('[Ficha de datos y atribución CC BY 4.0](https://github.com/nfmanios-debug/machine_learning_1/blob/main/Proyecto_Final/ficha_datos.md)')

elif pantalla == '03 · Experimento':
    st.title('Separar antes de aprender')
    a, b, c = st.columns(3)
    a.metric('Desarrollo · CV de 5 pliegues', '60.900', '60 %', delta_color='off')
    b.metric('Selección del umbral', '20.300', '20 %', delta_color='off')
    c.metric('Prueba final reservada', '20.300', '20 %', delta_color='off')
    st.write('Cada fold ajusta su propio Pipeline: normalización → faltantes → one-hot → modelo. '
             'Se comparan Dummy, Regresión Logística, Árbol y Random Forest mediante GridSearchCV.')
    st.code('Costo por registro = (5 × falsos negativos de Alcohol + falsos positivos de Alcohol) / n', language=None)
    st.caption('La relación 5:1 es un supuesto académico, no un costo oficial. Alcohol=1 en todas las métricas.')
    st.write('Los hiperparámetros se eligen en desarrollo. El umbral se fija en la reserva de validación. '
             'La prueba se utiliza una vez, al final del experimento. Esta app lee sus métricas ya calculadas.')
    with st.expander('Ver cómo funciona el Pipeline'):
        st.code((BASE / 'modelado.py').read_text(encoding='utf-8'), language='python')

elif pantalla == '04 · Resultados':
    st.title('Discriminar no equivale a priorizar')
    a, b, c = st.columns(3)
    a.metric('ROC-AUC · prueba', f"{r['test']['auc']:.4f}")
    b.metric('Umbral fijado · Alcohol', f"{r['umbral_final']:.2f}")
    c.metric('Clasificados como Alcohol · prueba', f"{r['test']['fraccion_alertas']:.2%}")
    st.error('La alerta casi universal no aporta una priorización útil. El intervalo de la ventaja '
             'de costo frente al baseline incluye cero. No se demuestra impacto clínico.')
    st.subheader('Comparación en validación cruzada')
    cv = tabla_csv('comparacion_modelos.csv', ['modelo', 'costo_cv', 'sd_costo', 'var_costo', 'auc_cv', 'sd_auc'])
    if st.button('▶ Comparar modelos', type='primary', key='grafico_modelos'):
        st.session_state['mostrar_modelos'] = True
    if st.session_state.get('mostrar_modelos'):
        fig = px.bar(cv, x='modelo', y='costo_cv', error_y='sd_costo',
                     color_discrete_sequence=['#237f73'], title='Costo CV: media ± desviación entre pliegues')
        st.plotly_chart(estilo_grafico(fig), width='stretch')
    st.subheader('Explorar el umbral en la reserva de validación')
    st.caption('Exploración didáctica de resultados guardados: no cambia el modelo ni el umbral oficial de 0,13.')
    umbral = st.slider('Umbral exploratorio', 0.0, 1.0, float(r['umbral_final']), 0.01, key='umbral_exploratorio')
    curva = pd.read_csv(ARTEFACTOS / 'curva_umbrales.csv')
    fila = curva.iloc[(curva.umbral - umbral).abs().argmin()]
    a, b, c = st.columns(3)
    a.metric('Sensibilidad · validación', f'{fila.sensibilidad:.2%}')
    b.metric('Alertas · validación', f'{fila.fraccion_alertas:.2%}')
    c.metric('Costo · validación', f'{fila.costo:.4f}')
    fig = px.line(curva, x='umbral', y='costo', color_discrete_sequence=['#237f73'])
    fig.add_vline(x=umbral, line_dash='dash', line_color='#bc6c35')
    st.plotly_chart(estilo_grafico(fig), width='stretch')
    with st.expander('Evaluación final fija y escenarios'):
        st.dataframe(pd.DataFrame([{'modelo': 'Logística', **r['test']},
                                   {'modelo': 'Dummy', **r['baseline_test']}]).drop(columns=['IC95_costo', 'IC95_ahorro_vs_dummy']), hide_index=True)
        st.write('IC 95 % de ahorro de costo por registro:', r['test']['IC95_ahorro_vs_dummy'])
        tabla_csv('sensibilidad_costos.csv')

elif pantalla == '05 · Demostración':
    st.title('Ejecutar el modelo sobre un ejemplo ficticio')
    st.write('Modifica un perfil inventado y pulsa ejecutar. El servidor aplica el Pipeline entrenado '
             'y calcula una nueva probabilidad. No se guardan las entradas del formulario.')
    elegido = st.selectbox('Ejemplo ficticio', range(len(portable['ejemplos'])),
                           format_func=lambda i: portable['ejemplos'][i]['nombre'], key='ejemplo')
    valores = portable['ejemplos'][elegido]['valores']
    with st.form('prediccion'):
        entrada = {}
        cols = st.columns(2)
        for i, col in enumerate(CATEGORICAS):
            opciones = sorted(set(portable['pesos_categoricos'][col]) | {'Desconocido'})
            entrada[col] = cols[i % 2].selectbox(NOMBRES[col], opciones,
                index=opciones.index(valores[col]), key=f'{col}_{elegido}')
        st.caption('Sitios de consumo del escenario inventado; pueden marcarse varios.')
        cols = st.columns(3)
        for i, col in enumerate(BINARIAS):
            opciones = ['NO', 'SI', 'Desconocido']
            entrada[col] = cols[i % 3].selectbox(NOMBRES[col], opciones,
                index=opciones.index(valores[col]), key=f'{col}_{elegido}')
        ejecutar = st.form_submit_button('▶ Ejecutar predicción', type='primary')
    if ejecutar:
        with st.spinner('Aplicando el Pipeline entrenado…'):
            prob = float(cargar_modelo().predict_proba(pd.DataFrame([entrada], columns=PREDICTORAS))[0, 1])
        # Guardar solo el último resultado de esta sesión; nunca escribir perfiles al disco.
        st.session_state['ultima_prediccion'] = {'probabilidad': prob, 'entrada': entrada, 'ejemplo': elegido}
    salida = st.session_state.get('ultima_prediccion')
    if salida and salida['ejemplo'] == elegido:
        prob = salida['probabilidad']
        st.subheader('Resultado de la última ejecución')
        a, b = st.columns(2)
        a.metric('P(Alcohol simulado)', f'{prob:.2%}')
        b.metric('Clase asignada', 'Alcohol simulado' if prob >= r['umbral_final'] else 'Otras SPA simuladas')
        st.progress(prob)
        st.caption(f"Regla fija: P ≥ {r['umbral_final']:.2f}. No expresa certeza clínica. Si cambias el formulario, vuelve a ejecutar.")
        with st.expander('Entradas de la última ejecución'):
            st.json(salida['entrada'])

else:
    st.title('Qué demuestra y qué falta')
    st.write('El despliegue demuestra reproducción técnica e inferencia interactiva. La variable objetivo '
             'no fue observada: el algoritmo aprende asociaciones del simulador. No demuestra prevención, '
             'personas atendidas, ahorro institucional ni detección temprana real.')
    st.markdown('''- **Datos:** registros de atención, cobertura desigual y ausencia de identificador individual.
- **Sesgos:** las reglas sintéticas incorporan sexo, curso de vida y lugares de consumo.
- **Decisión:** no utilizar para negar atención, asignar recursos ni clasificar personas reales.
- **Siguiente paso:** disponer de etiquetas observadas, definir unidad de análisis y validar por tiempo/persona.
- **Gobernanza:** acordar costos, capacidad y revisión humana antes de cualquier piloto institucional.''')
    st.subheader('Trazabilidad del despliegue')
    st.json(leer_json('trazabilidad.json'))
    st.caption('El empaquetado ajustó el ganador en las mismas 60.900 filas y verificó la reserva de validación; no volvió a consultar prueba.')

