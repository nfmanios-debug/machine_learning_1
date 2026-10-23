"""Pruebas de inferencia, navegación, gráficos y separación de métricas."""
from pathlib import Path
import json
import sys
import joblib
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from modelado import probabilidad_portable


def test_paridad_modelo():
    """Comparar el modelo serializado con la forma portable en 105 entradas ficticias."""
    model = joblib.load(BASE / 'artefactos/pipeline.joblib')
    portable = json.loads((BASE / 'artefactos/modelo_portable.json').read_text(encoding='utf-8'))
    cases = json.loads((BASE / 'artefactos/casos_paridad.json').read_text(encoding='utf-8'))
    inputs = [c['valores'] for c in cases]
    reference = [c['probabilidad'] for c in cases]
    np.testing.assert_allclose(model.predict_proba(pd.DataFrame(inputs))[:, 1], reference, atol=1e-12, rtol=0)
    np.testing.assert_allclose([probabilidad_portable(c, portable) for c in inputs], reference, atol=1e-12, rtol=0)


def test_app_recorrido():
    """Abrir cada sección y ejecutar las acciones que se mostrarán en la sustentación."""
    app = AppTest.from_file(str(BASE / 'app.py'), default_timeout=40).run()
    assert not app.exception
    assert any('etiqueta simulada' in w.value for w in app.warning)
    for page in ['02 · Datos', '03 · Experimento', '04 · Resultados', '05 · Demostración', '06 · Límites']:
        app.sidebar.radio(key='pantalla').set_value(page).run()
        assert not app.exception, (page, app.exception)
        assert any('etiqueta simulada' in w.value for w in app.warning)
        if page == '02 · Datos':
            assert len(app.dataframe) >= 1
            app.button(key='grafico_datos').click().run()
            assert not app.exception
            assert len(app.get('plotly_chart')) == 1
        elif page == '04 · Resultados':
            app.button(key='grafico_modelos').click().run()
            assert not app.exception
            assert len(app.get('plotly_chart')) == 2
            app.slider(key='umbral_exploratorio').set_value(0.62).run()
            assert not app.exception
            # La interacción cambia validación; el umbral final de prueba permanece fijo.
            assert any(m.label == 'Umbral fijado · Alcohol' and m.value == '0.13' for m in app.metric)
        elif page == '05 · Demostración':
            portable = json.loads((BASE / 'artefactos/modelo_portable.json').read_text(encoding='utf-8'))
            for i in range(3):
                app.selectbox(key='ejemplo').set_value(i).run()
                next(b for b in app.button if b.label == '▶ Ejecutar predicción').click().run()
                assert not app.exception
                assert abs(app.session_state['ultima_prediccion']['probabilidad'] -
                           portable['ejemplos'][i]['probabilidad']) < 1e-12


def test_html_autonomo():
    """Comprobar que la presentación no depende de librerías o datos remotos."""
    from bs4 import BeautifulSoup
    html = (BASE / 'index.html').read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    assert len(soup.select('section.slide')) == 8
    assert not soup.select('script[src], link[rel="stylesheet"], img[src^="http"]')
    assert len(soup.select('table')) >= 4
    assert '__PAYLOAD__' not in html
    data = json.loads(soup.select_one('#payload').string)
    assert data['modelo']['etiqueta_simulada'] is True
    assert data['resultados']['test']['n'] == 20300
    assert 'Alcohol es una etiqueta simulada' in soup.select_one('.notice').text

