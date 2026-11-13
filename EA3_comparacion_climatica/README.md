# Comparación climática — 2026

**Repositorio GitHub:** [https://github.com/SilviaPosso78/CreacionDataset](https://github.com/SilviaPosso78/CreacionDataset).

Notebook: [EA3_Posso_Mazo_Silvia_Rosa.ipynb](EA3_Posso_Mazo_Silvia_Rosa.ipynb).

Se comparan Medellín (IDEAM, LA ALDEA 26205080) y Puebla, México (CONAGUA/SMN, PUEBLA OBS 21065). El periodo es **2026-01-01 a 2026-10-31**, con **304 días en ambas ciudades**, temperatura **mínima diaria en °C** y precipitación diaria en **mm**. Las dos variables están completas, sin duplicados ni imputaciones. Los estados de aprobación de IDEAM se conservan: En revisión o Preliminar.

## Flujo de trabajo

1. Se obtienen las observaciones diarias de IDEAM para Medellín y de CONAGUA/SMN para Puebla.
2. Se selecciona el periodo común, se verifican fechas, unidades, valores faltantes y duplicados, y se organizan las tablas en CSV.
3. El notebook carga las tablas, construye arrays NumPy, aplica máscaras y calcula estadísticas descriptivas.
4. Se comparan las temperaturas mínimas y la precipitación mensual con tres gráficas; finalmente, se interpretan los resultados y sus limitaciones.

## Tablas finales

- [Medellín, diario 2026](datos/medellin_2026_diario.csv).
- [Puebla, diario 2026](datos/puebla_2026_diario.csv).
- [Informe de verificación, fuentes y huellas SHA-256](datos/verificacion_2026.json).
- [Fichas de las estaciones](datos/fuentes_estaciones.json).

Columnas: `fecha`, `ciudad`, `pais`, `estacion`, `tmin_c`, `precipitacion_mm`, `estado_tmin`, `estado_precipitacion`. Cada fila representa un día. `degC` se rotula como °C sin cambiar los valores; la precipitación ya está en mm.

## Archivos originales utilizados

- [ZIP descargado de IDEAM](datos/ideam_aldea_2026_TMN_CON.zip), con 608 observaciones: 304 temperaturas mínimas y 304 precipitaciones.
- [Consulta exacta de IDEAM, sin tokens](datos/ideam_aldea_2026_TMN_CON.zip.consulta.json).
- [TXT histórico de Puebla](datos/mexico_21065_diarios.txt), publicado en [CONAGUA/SMN](https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/pue/dia21065.txt).

El notebook contiene la predicción inicial, la revisión de tipos y calidad, arrays NumPy, cortes, máscaras, broadcasting, estadísticas, tres gráficas comparativas y conclusiones con cifras. Las gráficas y las explicaciones quedan dentro del notebook.

Para ejecutarlo, instala las dependencias con `pip install -r requirements.txt` desde esta carpeta y selecciona ese entorno como kernel. Con las dependencias instaladas funciona sin conexión usando los archivos incluidos. `construir_notebook.py` permite reconstruirlo y ejecutar todas sus celdas con un kernel real. No modifica `AE1/` ni `AE2/`.

Para repetir la descarga de IDEAM desde PowerShell:

```powershell
./descargar_ideam.ps1 -Anio 2026 -FechaFin '2026-10-31' -Temperatura TMN_CON
```

El script sigue el mecanismo público del portal DHIME y no almacena tokens. La carpeta `datos` conserva únicamente los datos finales y sus archivos de trazabilidad; se eliminaron las descargas de otros años, otras estaciones y las pruebas de búsqueda. El CSV y el TXT iniciales del usuario no se modificaron.
