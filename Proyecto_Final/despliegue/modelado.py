"""Transformaciones del cuaderno corregido; Alcohol es una etiqueta simulada."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder

SEMILLA = 2026
CATEGORICAS = ['SEXO', 'NOMBRELOCALIDADRESIDENCIA', 'NOMBREUPZ', 'CURSO_DE_VIDA',
               'NIVELEDUCATIVO', 'PERTENENCIAETNICA', 'ESTADOCIVIL', 'TIPOASEGURAMIENTO']
BINARIAS = ['SITIOHABITUALCONSUMO_' + sitio for sitio in
            ['VIVIENDA', 'PARQUE', 'EST_EDUCATIVO', 'BARES_TABERNAS', 'VIA_PUBLICA', 'CASA_AMIGOS']]
PREDICTORAS = CATEGORICAS + BINARIAS
MARCADORES = {'sin dato', 'sin informacion', 'n.a.', 'upz sin asignar'}
AVISO = 'Alcohol es una etiqueta simulada. Prototipo académico; no es un diagnóstico ni una estimación validada de riesgo clínico.'
NOMBRES = dict(zip(PREDICTORAS, ['Sexo registrado', 'Localidad', 'UPZ', 'Curso de vida',
    'Nivel educativo', 'Pertenencia étnica', 'Estado civil', 'Aseguramiento',
    'Vivienda', 'Parque', 'Establecimiento educativo', 'Bares / tabernas', 'Vía pública', 'Casa de amigos']))


def normalizar_predictoras(frame):
    """Conservar filas y normalizar sin aprender estadísticas de los datos recibidos."""
    salida = frame[PREDICTORAS].copy()
    for col in CATEGORICAS:
        texto = salida[col].astype('string').str.strip()
        texto = texto.mask(texto.str.lower().isin(MARCADORES))
        salida[col] = texto.astype(object).where(texto.notna(), np.nan)
    for col in BINARIAS:
        salida[col] = salida[col].astype('string').str.strip().str.upper().map({'SI': 1.0, 'NO': 0.0})
    return salida


def crear_pipeline():
    """Reconstruir la configuración elegida en CV, sin volver a seleccionar modelos."""
    categorias = Pipeline([
        ('faltantes', SimpleImputer(strategy='constant', fill_value='Desconocido')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=True))])
    sitios = Pipeline([('faltantes', SimpleImputer(strategy='constant', fill_value=-1.0))])
    columnas = ColumnTransformer([('categorias', categorias, CATEGORICAS),
                                  ('sitios', sitios, BINARIAS)], sparse_threshold=1.0)
    return Pipeline([('normalizar', FunctionTransformer(normalizar_predictoras)),
                     ('columnas', columnas),
                     ('modelo', LogisticRegression(C=0.1, max_iter=1000, random_state=SEMILLA))])


def simular_etiqueta(df):
    """Reproducir exactamente el generador académico de cuaderno_PFI, semilla 2026."""
    prob = np.full(len(df), 0.70)
    for col, delta in zip(BINARIAS, [0.10, -0.25, -0.20, 0.15, -0.10, 0.10]):
        prob += np.where(df[col].eq('SI'), delta, 0.0)
    prob += np.where(df.CURSO_DE_VIDA.isin(['Adultez', 'Vejez']), 0.10, 0.0)
    prob -= np.where(df.CURSO_DE_VIDA.isin(['Adolescencia', 'Juventud']), 0.15, 0.0)
    prob += np.where(df.SEXO.eq('Hombre'), 0.05, 0.0)
    return pd.Series((np.random.default_rng(SEMILLA).uniform(size=len(df)) <=
                      np.clip(prob, 0.05, 0.95)).astype(int), index=df.index, name='Alcohol')


def probabilidad_portable(ejemplo, exportado):
    """Evaluar la regresión exportada; sirve para comprobar la versión HTML."""
    z = exportado['intercepto']
    for columna, pesos in exportado['pesos_categoricos'].items():
        valor = ejemplo.get(columna)
        texto = '' if valor is None else str(valor).strip()
        if valor is None or texto.lower() in MARCADORES:
            texto = 'Desconocido'
        z += pesos.get(texto, 0.0)  # handle_unknown='ignore' produce ceros.
    for columna, peso in exportado['pesos_binarios'].items():
        valor = str(ejemplo.get(columna, '')).strip().upper()
        z += peso * {'SI': 1.0, 'NO': 0.0}.get(valor, -1.0)
    return float(1 / (1 + np.exp(-z)))
