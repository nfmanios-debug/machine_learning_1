"""Generar la presentación autónoma y una vista HTML del cuaderno corregido."""
from pathlib import Path
import html
import json
import pandas as pd
import nbformat
from nbconvert import HTMLExporter

BASE = Path(__file__).resolve().parent


def main():
    """Incrustar solo resultados agregados y coeficientes; no filas individuales."""
    def leer(nombre):
        return json.loads((BASE / 'artefactos' / nombre).read_text(encoding='utf-8'))
    r = leer('resultados.json')
    curva = pd.read_csv(BASE / 'artefactos' / 'curva_umbrales.csv')
    config = json.loads((BASE / 'configuracion.json').read_text(encoding='utf-8'))
    data = {'resultados': r, 'modelo': leer('modelo_portable.json'),
            'agregados': leer('agregados.json'), 'curva': curva.to_dict('records'),
            'streamlit_url': config['streamlit_url']}
    plantilla = (BASE / 'plantilla.html').read_text(encoding='utf-8')
    cv = pd.DataFrame(r['comparacion_cv'])[['modelo', 'costo_cv', 'sd_costo', 'var_costo', 'auc_cv']]
    cv.columns = ['Modelo', 'Costo medio CV', 'Desv. costo', 'Varianza costo', 'ROC-AUC CV']
    # Mostrar varianzas pequeñas en notación científica evita redondearlas a cero.
    cv['Varianza costo'] = cv['Varianza costo'].map(lambda x: f'{x:.3e}')
    seleccion = curva[curva.umbral.round(2).isin([0.13, 0.30, 0.50, 0.62, 0.80])][
        ['umbral', 'costo', 'sensibilidad', 'fraccion_alertas']]
    seleccion.columns = ['Umbral', 'Costo', 'Sensibilidad', 'Fracción alertas']
    test = pd.DataFrame([{'Modelo': 'Logística', 'Costo': r['test']['costo'],
                         'Sensibilidad': r['test']['sensibilidad'], 'Precisión': r['test']['precision']},
                        {'Modelo': 'Dummy', 'Costo': r['baseline_test']['costo'],
                         'Sensibilidad': r['baseline_test']['sensibilidad'], 'Precisión': r['baseline_test']['precision']}])
    def tabla(df):
        return df.to_html(index=False, border=0, float_format=lambda x: f'{x:.6f}', escape=True)
    campos = {
        '__PAYLOAD__': json.dumps(data, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c'),
        '__CV_TABLE__': tabla(cv), '__THRESHOLD_TABLE__': tabla(seleccion),
        '__TEST_TABLE__': tabla(test), '__DATA_TABLE__': tabla(pd.DataFrame(data['agregados']['ANO']).rename(columns={'categoria':'Año','registros':'Filas'})),
        '__PIPELINE_CODE__': html.escape((BASE / 'modelado.py').read_text(encoding='utf-8')),
        '__AUC__': f"{r['test']['auc']:.4f}".replace('.', ','),
        '__ALERTS__': f"{r['test']['fraccion_alertas']:.2%}".replace('.', ','),
        '__INTERVAL__': ' a '.join(f'{v:.6f}'.replace('.', ',') for v in r['test']['IC95_ahorro_vs_dummy']),
        **{f'__{k}__': f"{r['test'][k]:,}".replace(',', '.') for k in ['TN','FP','FN','TP']}}
    for clave, valor in campos.items():
        plantilla = plantilla.replace(clave, valor)
    (BASE / 'index.html').write_text(plantilla, encoding='utf-8')
    # Exportar outputs guardados no vuelve a ejecutar el cuaderno ni a consultar prueba.
    nb = nbformat.read(BASE.parent / 'cuaderno_PFI.ipynb', as_version=4)
    nb.cells.insert(0, nbformat.v4.new_markdown_cell(
        '# Evidencia del experimento corregido\n'
        '**Alcohol es una etiqueta simulada.** Esta es la base del despliegue; no es una exportación '
        'del Colab final recibido. Los resultados de ambas versiones no se mezclan. '
        'La vista conserva código, tablas y gráficos guardados; no ejecuta celdas Python.\n\n'
        '[Volver a la presentación](index.html)'))
    exporter = HTMLExporter(template_name='lab')
    exporter.embed_images = True
    contenido, _ = exporter.from_notebook_node(nb)
    (BASE / 'notebook.html').write_text(contenido, encoding='utf-8')
    print('Generados index.html y notebook.html; no se ejecutó prueba.')


if __name__ == '__main__':
    main()

