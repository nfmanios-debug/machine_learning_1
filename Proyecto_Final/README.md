# Proyecto Final Integrador · EAN

**Alcohol es una etiqueta simulada. No es un modelo clínico ni de detección real.**
Equipo: Oscar Andrés Ramos Villanueva, Alvaro Cabezas y Nelsón Fabián Manios.

## Resultados ejecutados
- Modelo: Logistica; umbral: 0.130; costo FN/FP supuesto: 5:1.
- Prueba: sensibilidad 99.98%, precisión 64.39%, ROC-AUC 0.7614.
- Costo por registro: 0.3564, baseline 0.3567; alertas 99.87%.
- La ventaja de costo es mínima y su intervalo incluye cero; la alerta casi universal no demuestra utilidad operativa.
- CV: cinco folds en 60%; reserva de umbral 20%; prueba final única 20%.
- 8/8 celdas ejecutadas desde núcleo nuevo, sin errores.

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
- informe_PFI.pdf: informe técnico de 8 páginas.
- resumen_ejecutivo_EN.pdf: una página; 319 palabras en el cuerpo.
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
