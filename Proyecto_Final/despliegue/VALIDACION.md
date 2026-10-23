# Validación del despliegue

Fecha local de ejecución: 22 de octubre de 2026 (America/Bogota).

## Modelo

- Pipeline reconstruido con la configuración fijada en el experimento corregido.
- Ajuste: 60.900 filas. Reserva para comprobación: 20.300 filas.
- Prueba no consultada durante empaquetado ni en la aplicación.
- Diferencia máxima de costo frente a la curva guardada: 2,22 × 10⁻¹⁶.
- 105 escenarios ficticios comprobados con Pipeline, Python portable y JavaScript.
- Error absoluto máximo de probabilidad: 1,67 × 10⁻¹⁶; clases idénticas al umbral 0,13.
- Hashes y versiones: artefactos/trazabilidad.json.

## Aplicación

Comando ejecutado: python -m pytest test_despliegue.py -q -p no:cacheprovider.
Resultado: **3 pruebas aprobadas**. La prueba de recorrido cubre las seis pantallas,
los dos botones de gráficos, el control de umbral y las tres predicciones ficticias.
Las advertencias de etiqueta simulada se comprueban en todas las pantallas.

## HTML

Comando ejecutado: node validar_modelo_html.cjs.
Resultado: **105 casos con paridad y clases idénticas**.
La presentación tiene ocho diapositivas, tablas visibles y recursos incrustados.
No utiliza scripts, fuentes ni datos remotos para navegar, graficar o predecir.
La vista notebook.html muestra salidas guardadas y no ejecuta código Python.

## Revisión en navegador

Chrome, servidores locales 127.0.0.1:8501 (Streamlit) y :8502 (HTML).
Se verificaron portada, tablas, generación de gráficos, comparación de modelos,
formulario HTML con dos escenarios y predicción Streamlit.
Ejemplo A: 90,74 % en Streamlit y 90,7 % en HTML (diferente redondeo visual).
Ejemplo B en HTML: 13,2 %. Las probabilidades completas coinciden en las pruebas automáticas.
Capturas en evidencias/. No se ha simulado una prueba de carga multiusuario ni validación clínica.

## Alcance de la validación

La validación local y la publicación del código son distintas de activar un servicio público.
El estado y las URLs de alojamiento se registran en configuracion.json.
La activación de Streamlit requiere el acceso del titular a Community Cloud.
El resultado académico sigue siendo simulado: ninguna prueba técnica demuestra validez clínica.
