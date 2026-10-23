"""Empaquetar el modelo del experimento corregido sin reevaluar el conjunto de prueba.

Ejecutar desde cualquier directorio: python preparar_modelo.py.
Solo usa el CSV versionado y resultados ya fijados en Proyecto_Final.
"""
from pathlib import Path
import hashlib
import importlib.metadata as metadata
import json
import shutil
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from modelado import (SEMILLA, CATEGORICAS, BINARIAS, PREDICTORAS, MARCADORES,
                      NOMBRES, AVISO, crear_pipeline, simular_etiqueta, probabilidad_portable)

BASE = Path(__file__).resolve().parent
PROYECTO = BASE.parent
ARTEFACTOS = BASE / 'artefactos'


def main():
    """Reconstruir solo el ajuste seleccionado y contrastar la reserva de validación."""
    ARTEFACTOS.mkdir(exist_ok=True)
    resultados = json.loads((PROYECTO / 'resultados.json').read_text(encoding='utf-8'))
    archivo = PROYECTO / 'datos_crudos' / 'osb_saludmental_-consumoabusivo_spageneral.csv'
    assert hashlib.sha256(archivo.read_bytes()).hexdigest() == resultados['sha256_datos']
    assert resultados['modelo_final'] == 'Logistica' and resultados['parametros'] == {'modelo__C': 0.1}
    df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig')
    df = df.astype({c: 'int64' if c in ['ANO', 'MESNOTIFICACION', 'TRIMESTRE', 'CASOS'] else 'object'
                    for c in df.columns})
    y = simular_etiqueta(df)
    x_train, x_test, y_train, y_test = train_test_split(df[PREDICTORAS], y,
        test_size=0.2, stratify=y, random_state=SEMILLA)
    x_dev, x_val, y_dev, y_val = train_test_split(x_train, y_train,
        test_size=0.25, stratify=y_train, random_state=SEMILLA + 1)
    assert set(x_dev.index).isdisjoint(x_val.index)
    assert set(x_train.index).isdisjoint(x_test.index)
    # Se descarta prueba: las métricas publicadas se leen, no se recalculan ni optimizan.
    del x_test, y_test
    modelo = crear_pipeline().fit(x_dev, y_dev)
    prob_val = modelo.predict_proba(x_val)[:, 1]
    curva = pd.read_csv(PROYECTO / 'curva_umbrales.csv')
    max_error_costo = 0.0
    for fila in curva.itertuples():
        pred = prob_val >= fila.umbral
        costo = np.mean(5 * ((y_val.to_numpy() == 1) & ~pred) + ((y_val.to_numpy() == 0) & pred))
        max_error_costo = max(max_error_costo, abs(float(costo) - fila.costo))
    assert max_error_costo < 1e-12, 'El ajuste ya no reproduce el experimento guardado.'
    joblib.dump(modelo, ARTEFACTOS / 'pipeline.joblib', compress=3)

    # Exportación algebraica transparente para ejecutar el mismo modelo en HTML sin servidor.
    onehot = modelo['columnas'].named_transformers_['categorias']['onehot']
    pesos = modelo['modelo'].coef_[0]
    portable = {'etiqueta_simulada': True, 'aviso': AVISO,
        'umbral': resultados['umbral_final'], 'intercepto': float(modelo['modelo'].intercept_[0]),
        'clases': [int(v) for v in modelo.classes_], 'pesos_categoricos': {}, 'pesos_binarios': {},
        'marcadores': sorted(MARCADORES), 'nombres': NOMBRES}
    offset = 0
    for col, cats in zip(CATEGORICAS, onehot.categories_):
        portable['pesos_categoricos'][col] = dict(zip(cats.tolist(), pesos[offset:offset + len(cats)].tolist()))
        offset += len(cats)
    portable['pesos_binarios'] = dict(zip(BINARIAS, pesos[offset:].tolist()))
    assert offset + len(BINARIAS) == resultados['columnas_transformadas']
    # Los ejemplos se inventan a partir del vocabulario; no se publican filas individuales.
    neutro = {c: 'Desconocido' for c in CATEGORICAS} | {c: 'NO' for c in BINARIAS}
    ejemplos = [
        {'nombre': 'A · Adultez / vivienda', 'valores': neutro | {'SEXO': 'Hombre', 'CURSO_DE_VIDA': 'Adultez', BINARIAS[0]: 'SI'}},
        {'nombre': 'B · Juventud / espacios abiertos', 'valores': neutro | {'SEXO': 'Mujer', 'CURSO_DE_VIDA': 'Juventud', BINARIAS[1]: 'SI', BINARIAS[2]: 'SI', BINARIAS[4]: 'SI'}},
        {'nombre': 'C · Información incompleta', 'valores': neutro.copy()}]
    # Casos adicionales verifican categorías desconocidas, marcadores y normalización.
    casos = [e['valores'] for e in ejemplos] + [
        neutro | {'SEXO': None, 'NOMBREUPZ': 'UPZ NUEVA', BINARIAS[0]: ' si '},
        neutro | {'SEXO': 'Sin Dato', BINARIAS[3]: 'sin informacion'}]
    rng = np.random.default_rng(2026)
    for _ in range(100):
        casos.append({c: str(rng.choice(list(portable['pesos_categoricos'][c]) + ['NUEVA', 'Sin Dato']))
                      for c in CATEGORICAS} | {c: str(rng.choice(['SI', 'NO', 'Desconocido'])) for c in BINARIAS})
    esperadas = modelo.predict_proba(pd.DataFrame(casos))[..., 1]
    diferencia = max(abs(probabilidad_portable(c, portable) - p) for c, p in zip(casos, esperadas))
    assert diferencia < 1e-12
    for ejemplo, p in zip(ejemplos, esperadas):
        ejemplo['probabilidad'] = float(p)
    portable['ejemplos'] = ejemplos
    (ARTEFACTOS / 'modelo_portable.json').write_text(json.dumps(portable, ensure_ascii=False, indent=2), encoding='utf-8')
    (ARTEFACTOS / 'casos_paridad.json').write_text(json.dumps([
        {'valores': c, 'probabilidad': float(p)} for c, p in zip(casos, esperadas)], ensure_ascii=False), encoding='utf-8')
    # Agregados de una dimensión: no se exponen fichas ni cruces que identifiquen registros.
    resumen = {}
    for col in ['ANO', 'NOMBRELOCALIDADRESIDENCIA', 'CURSO_DE_VIDA']:
        cuenta = df[col].fillna('Desconocido').astype(str).value_counts().sort_index()
        resumen[col] = [{'categoria': str(k), 'registros': int(v)} for k, v in cuenta.items()]
    (ARTEFACTOS / 'agregados.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')
    for nombre in ['resultados.json', 'comparacion_modelos.csv', 'metricas_folds.csv',
                   'curva_umbrales.csv', 'sensibilidad_costos.csv', 'calidad_columnas.csv']:
        shutil.copy2(PROYECTO / nombre, ARTEFACTOS / nombre)
    evidencia = {'etiqueta_simulada': True, 'base': '../cuaderno_PFI.ipynb',
        'sha256_notebook': hashlib.sha256((PROYECTO / 'cuaderno_PFI.ipynb').read_bytes()).hexdigest(),
        'sha256_csv': resultados['sha256_datos'], 'n_ajuste': len(x_dev), 'n_validacion': len(x_val),
        'test_consultado_en_empaquetado': False, 'max_error_costo_validacion': max_error_costo,
        'max_error_paridad_python': diferencia, 'casos_paridad': len(casos),
        'sha256_pipeline': hashlib.sha256((ARTEFACTOS / 'pipeline.joblib').read_bytes()).hexdigest(),
        'versiones': {p: metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'joblib']},
        'python': sys.version.split()[0]}
    (ARTEFACTOS / 'trazabilidad.json').write_text(json.dumps(evidencia, indent=2), encoding='utf-8')
    print(json.dumps(evidencia, indent=2))


if __name__ == '__main__':
    main()
