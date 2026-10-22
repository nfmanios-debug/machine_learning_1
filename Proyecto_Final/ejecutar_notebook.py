"""Ejecuta el cuaderno desde un núcleo nuevo y conserva evidencia de éxito o error."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parent
# El kernel se define localmente: no cambia la configuración del usuario.
kernel_dir = ROOT / 'tmp' / 'kernels' / 'pfi'
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / 'kernel.json').write_text(json.dumps({
    'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
    'display_name': 'PFI local', 'language': 'python'}), encoding='utf-8')
os.environ['MPLCONFIGDIR'] = str(ROOT / 'tmp' / 'matplotlib')
os.environ['IPYTHONDIR'] = str(ROOT / 'tmp' / 'ipython')
os.environ['JUPYTER_RUNTIME_DIR'] = str(ROOT / 'tmp' / 'runtime')
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
path = ROOT / 'cuaderno_PFI.ipynb'
nb = nbformat.read(path, as_version=4)
nbformat.validate(nb)
for cell in nb.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None
km = KernelManager(kernel_name='pfi', kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_dir.parent)]))
def progreso(cell, cell_index, **kwargs):
    print(f'Celda {cell_index + 1}/{len(nb.cells)}: {cell.cell_type}', flush=True)
client = NotebookClient(nb, timeout=3600, km=km, resources={'metadata': {'path': str(ROOT)}},
                        allow_errors=False, on_cell_start=progreso)
inicio = time.time()
exito, error = False, None
try:
    client.execute()
    exito = True
except Exception as exc:
    error = str(exc)
    raise
finally:
    # El notebook y el registro reflejan lo ocurrido, incluso si la ejecución falla.
    nbformat.write(nb, path)
    registro = {'exito': exito, 'nucleo_nuevo': True, 'duracion_segundos': round(time.time() - inicio, 2),
        'fin_utc': datetime.now(timezone.utc).isoformat(), 'error': error,
        'celdas_codigo': sum(c.cell_type == 'code' for c in nb.cells),
        'celdas_ejecutadas': sum(c.cell_type == 'code' and c.execution_count is not None for c in nb.cells),
        'sha256_notebook': hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT / 'validacion_ejecucion.json').write_text(json.dumps(registro, indent=2), encoding='utf-8')
    print(json.dumps(registro, indent=2), flush=True)
