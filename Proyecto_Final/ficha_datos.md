# Ficha de datos

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
SHA-256: `468301ee4e637df11eb825136b9abe03300a947d0ce6bb2bfba48356c5cd5d85`. Tamaño: 15.879.321 bytes.

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

| columna | tipo | faltantes_nan | unicos | marcadores_textuales |
| --- | --- | --- | --- | --- |
| ANO | int64 | 0 | 12 | 0 |
| SEXO | object | 44 | 3 | 0 |
| NOMBRELOCALIDADRESIDENCIA | object | 0 | 22 | 5011 |
| MESNOTIFICACION | int64 | 0 | 12 | 0 |
| TRIMESTRE | int64 | 0 | 4 | 0 |
| TIPOASEGURAMIENTO | object | 0 | 8 | 51 |
| SITIOHABITUALCONSUMO_VIVIENDA | object | 0 | 2 | 0 |
| SITIOHABITUALCONSUMO_PARQUE | object | 0 | 2 | 0 |
| SITIOHABITUALCONSUMO_EST_EDUCATIVO | object | 0 | 2 | 0 |
| SITIOHABITUALCONSUMO_BARES_TABERNAS | object | 0 | 2 | 0 |
| SITIOHABITUALCONSUMO_VIA_PUBLICA | object | 0 | 2 | 0 |
| SITIOHABITUALCONSUMO_CASA_AMIGOS | object | 0 | 2 | 0 |
| NIVELEDUCATIVO | object | 0 | 13 | 700 |
| CURSO_DE_VIDA | object | 0 | 4 | 0 |
| COMOACUDIOTRATAMIENTO | object | 0 | 8 | 12996 |
| PERTENENCIAETNICA | object | 106 | 8 | 0 |
| ORIENTSEXUAL | object | 0 | 5 | 29060 |
| PAISNACIONALIDAD | object | 0 | 24 | 65411 |
| NOMBREUPZ | object | 0 | 116 | 12618 |
| ESTADOCIVIL | object | 0 | 7 | 574 |
| CASOS | int64 | 0 | 35 | 0 |

## Preparación y objetivo
Se conservan las 101.500 filas, incluidos tres registros intersexuales. No se imputan atributos sensibles
probabilísticamente. El Pipeline normaliza espacios y marcadores, representa categorías ausentes como
Desconocido, codifica categorías solo con entrenamiento y transforma SI/NO a 1/0.
Se seleccionan 14 predictores crudos; el ajuste final genera 185 columnas numéricas.
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
