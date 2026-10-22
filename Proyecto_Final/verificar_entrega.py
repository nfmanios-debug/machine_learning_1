"""Comprueba integridad, evidencia de ejecución y consistencia del paquete entregable."""
from pathlib import Path
import hashlib
import json
import zipfile
import nbformat
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
r = json.loads((ROOT / 'resultados.json').read_text(encoding='utf-8'))
v = json.loads((ROOT / 'validacion_ejecucion.json').read_text(encoding='utf-8'))
nb = nbformat.read(ROOT / 'cuaderno_PFI.ipynb', as_version=4)
nbformat.validate(nb)
# Una ejecución completa exige contadores consecutivos y ausencia de errores guardados.
codes = [c for c in nb.cells if c.cell_type == 'code']
assert [c.execution_count for c in codes] == list(range(1, len(codes) + 1))
assert all(o.output_type != 'error' for c in codes for o in c.outputs)
assert v['exito'] and v['nucleo_nuevo']
assert hashlib.sha256((ROOT / 'cuaderno_PFI.ipynb').read_bytes()).hexdigest() == v['sha256_notebook']
# Las métricas deben corresponder a la misma matriz de confusión y tamaño de prueba.
t = r['test']
assert sum(t[k] for k in ['TN', 'FP', 'FN', 'TP']) == r['n_test'] == t['n']
assert abs(t['costo'] - (5 * t['FN'] + t['FP']) / t['n']) < 1e-12
assert abs(t['sensibilidad'] - t['TP'] / (t['TP'] + t['FN'])) < 1e-12
assert r['n_desarrollo'] + r['n_umbral'] + r['n_test'] == r['filas_crudas']
assert r['etiqueta_simulada'] is True
# La prueba se predice una vez; el resto de cálculos usa esa misma salida.
sources = '\n'.join(c.source for c in codes)
assert sources.count('predict_proba(X_test)') == 1
assert '.fit(X_test' not in sources
assert len(PdfReader(ROOT / 'resumen_ejecutivo_EN.pdf').pages) == 1
assert len(PdfReader(ROOT / 'informe_PFI.pdf').pages) <= 15
body = (ROOT / 'resumen_ejecutivo_EN.md').read_text(encoding='utf-8').split('\n\n', 1)[1]
assert 250 <= len(body.split()) <= 350
manifest = json.loads((ROOT / 'manifiesto_sha256.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(ROOT / 'ML1_PFI_EquipoVESPA.zip') as z:
    assert z.testzip() is None
    assert all('/' not in n or n.startswith('datos_crudos/') for n in z.namelist())
    for name, expected in manifest.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
        assert hashlib.sha256(z.read(name)).hexdigest() == expected, name
print('OK: notebook ejecutado, métricas consistentes, PDFs, palabras, hashes y ZIP verificados.')
