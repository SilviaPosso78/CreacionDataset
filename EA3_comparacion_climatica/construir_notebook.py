"""Construye y ejecuta el notebook con archivos oficiales ya descargados."""
from pathlib import Path
import contextlib, io, json, traceback, uuid

BASE = Path(__file__).resolve().parent
cells = []
def cell(kind, text):
    c = {'cell_type': kind, 'id': uuid.uuid4().hex[:8], 'metadata': {},
         'source': text.strip().splitlines(keepends=True)}
    if kind == 'code':
        c.update(execution_count=None, outputs=[])
    cells.append(c)

cell('markdown', '''
# EA3 · Observaciones climáticas de Medellín y Puebla — 2026
**Silvia Rosa Posso Mazo** · Consulta de fuentes: 10 de noviembre de 2026.

## A. Pregunta y expectativa inicial
**Pregunta guía:** ¿cómo se diferencian la temperatura mínima diaria y la precipitación de las estaciones seleccionadas de Medellín y Puebla durante enero–octubre de 2026?

**Predicción, antes de calcular las estadísticas:** espero que Medellín tenga mínimas diarias más altas y menos variables que Puebla, y que ambas estaciones presenten días lluviosos y cambios mensuales de precipitación. Es una expectativa que se contrasta con los datos, no una conclusión anticipada. Se utilizarán los mismos umbrales en ambas ciudades: día lluvioso si la precipitación es mayor que 0 mm y mínima elevada si supera 15 °C. Una mínima mayor que 15 °C no significa necesariamente un día caluroso.

## 1. Fuentes, periodo y alcance
Se utilizan **observaciones de estaciones**, descargadas del IDEAM (Colombia) y de CONAGUA/Servicio Meteorológico Nacional (México). No se emplean pronósticos ni datos inventados.

**Periodo común fijado para ambas ciudades: 1 de enero a 31 de octubre de 2026, ambos inclusive; frecuencia diaria; 304 fechas.** Se usan los meses terminados del año solicitado. No corresponde a un año calendario completo: 2026 todavía está en curso. No se utiliza una intersección de fechas ni se recorta una ciudad para ajustarla a la otra.

**Cobertura verificada:** ambas ciudades tienen **304 temperaturas mínimas y 304 precipitaciones**, sin duplicados ni valores ausentes en las variables seleccionadas. Se utiliza temperatura mínima porque la máxima de LA ALDEA tiene dos huecos en 2026. La actividad permite escoger una variable de temperatura comparable: se compara **mínima con mínima**, en °C. No se mezclan máximas con mínimas ni se completan observaciones artificialmente.

**Calidad:** las observaciones de IDEAM figuran En revisión o Preliminar. Tener todas las fechas no significa que la entidad haya finalizado su validación. El TXT de CONAGUA no publica un nivel de aprobación individual.

| Característica | Medellín, Colombia | Puebla, México |
|---|---|---|
| Fuente | IDEAM, portal DHIME | CONAGUA/SMN, Base de Datos Climatológica Nacional |
| Estación | LA ALDEA, 26205080 | PUEBLA (OBS), 21065, municipio Puebla |
| Ubicación | 6.34105556 N, −75.70094444; 1737 m, según catálogo IDEAM | 19.05 N, −98.16666667; 2179 m, según cabecera del registro |
| Archivo original descargado | `datos/ideam_aldea_2026_TMN_CON.zip` | `datos/mexico_21065_diarios.txt` |
| Columnas originales utilizadas | CodigoEstacion, NombreEstacion, Variable, Parametro, Fecha, Unidad, Valor, NivelAprobacion | FECHA, PRECIP, TMIN; EVAP y TMAX no se utilizan |
| Temperatura | Temperatura mínima diaria (`TMN_CON`), degC | TMIN, °C |
| Precipitación | Día pluviométrico convencional (`PTPM_CON`), mm | PRECIP, mm |
| Frecuencia utilizada | Diaria | Diaria |
| Periodo utilizado | 2026-01-01 a 2026-10-31 | 2026-01-01 a 2026-10-31 |
| Unidades de salida | °C y mm | °C y mm |
| Estado de validación | Se conserva NivelAprobacion: En revisión y Preliminar | El TXT no ofrece una bandera de aprobación por observación; no se le atribuye validación que no declare |

### Enlaces y trazabilidad
- IDEAM: [portal público de consulta](https://atencionciudadano.ideam.gov.co/). La descarga se obtuvo del servicio usado por ese portal, no de un enlace supuesto. La **consulta exacta sin credenciales** se conserva en `datos/ideam_aldea_2026_TMN_CON.zip.consulta.json` y se imprime más adelante.
- IDEAM: [catálogo de series de LA ALDEA](https://dhime.ideam.gov.co/server/rest/services/CNE/Estaciones/MapServer/8/query?f=json&where=idestacion%3D%2726205080%27&outFields=*&returnGeometry=false). Confirma municipio Medellín y las descripciones de las dos variables. Copia local: `datos/dhime_aldea.json`.
- CONAGUA: [registro diario histórico de Puebla, estación 21065](https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/pue/dia21065.txt). Es el archivo descargado y leído, con cabecera REGISTRO DIARIO HISTÓRICO, unidades y coordenadas.
- CONAGUA: [catálogo del mapa oficial](https://smn.conagua.gob.mx/tools/GUI/estaciones-climatologicas/data/estaciones_climatologicas.geojson). Su propiedad `diarios` contiene el enlace anterior; se guarda una ficha de la estación en `datos/fuentes_estaciones.json`.

Las tablas finales pueden leerse sin conexión a internet. El servicio de DHIME puede cambiar; el script `descargar_ideam.ps1` documenta cómo se obtuvo la descarga mediante el acceso público del portal. No se guardan tokens.
''')

cell('markdown', '''
## 2. Decisiones sobre los archivos iniciales y la búsqueda
El CSV aportado `descargaDhime.csv` contiene solo temperatura máxima de LA ALDEA durante 2026, con dos fechas ausentes antes de noviembre. Se descargaron de DHIME **temperatura mínima y precipitación**, fijando la misma consulta de enero a octubre para ambas variables. La mínima tiene todas las fechas del periodo solicitado. El TXT aportado de la estación 15266, Metepec, contiene **estadísticas mensuales**; no equivale a observaciones diarias. No se desagregaron esos valores para crear días ficticios.

Se localizó el archivo diario real de Metepec, pero presenta ocho fechas con alguna variable ausente durante enero–octubre de 2026 en la búsqueda inicial de máxima y precipitación. **Puebla sí tiene mínima y precipitación completas para ese periodo**, por lo que se escogió otra tabla mexicana, manteniendo CONAGUA como fuente. Los otros ensayos (Tacubaya y Guadalajara, así como series de Olaya Herrera y Pajarito) no proporcionaron una pareja completa para el periodo fijado. Se eligió la mínima de LA ALDEA, sin rellenar los dos huecos de su máxima.

La revisión anterior de 2022 y la propuesta de NOAA quedan reemplazadas por este trabajo de **2026 con IDEAM y CONAGUA**. El identificador `g4t8-zkc3` de datos.gov.co es de calidad del aire y no se utiliza para temperatura o precipitación.
''')

cell('code', '''
from pathlib import Path
from datetime import date, timedelta
from collections import Counter
import csv, hashlib, json, math, re, statistics, zipfile

BASE = Path.cwd()
if (BASE / 'EA3_comparacion_climatica').is_dir():
    BASE = BASE / 'EA3_comparacion_climatica'
DATOS = BASE / 'datos'
INICIO, FIN = date(2026, 1, 1), date(2026, 10, 31)
FECHAS = [(INICIO + timedelta(days=n)).isoformat()
          for n in range((FIN - INICIO).days + 1)]
assert len(FECHAS) == 304
print(f'Periodo común: {INICIO} a {FIN}; {len(FECHAS)} días; frecuencia diaria.')
''')

cell('code', '''
# IDEAM: se lee el CSV dentro del ZIP original, sin modificarlo.
with zipfile.ZipFile(DATOS / 'ideam_aldea_2026_TMN_CON.zip') as archivo:
    nombres = [n for n in archivo.namelist() if n.lower().endswith('.csv')]
    assert len(nombres) == 1
    crudo_ideam = list(csv.DictReader(
        archivo.read(nombres[0]).decode('utf-8-sig').splitlines()))

parametros = {
    'Temperatura mínima diaria': ('tmin_c', 'degC'),
    'Día pluviométrico (convencional)': ('precipitacion_mm', 'mm'),
}
medellin = {f: {'fecha': f, 'ciudad': 'Medellín', 'pais': 'Colombia',
               'estacion': '26205080', 'tmin_c': None, 'precipitacion_mm': None,
               'estado_tmin': 'Sin observación', 'estado_precipitacion': 'Sin observación'}
            for f in FECHAS}
vistas = set()
for r in crudo_ideam:
    assert r['CodigoEstacion'] == '26205080'
    assert r['Parametro'] in parametros
    columna, unidad = parametros[r['Parametro']]
    assert r['Unidad'] == unidad, f'Unidad inesperada: {r}'
    fecha = r['Fecha'][:10]
    assert fecha in medellin, f'Fecha fuera de la consulta fijada: {fecha}'
    clave = (fecha, columna)
    assert clave not in vistas, f'Observación duplicada: {clave}'
    vistas.add(clave)
    valor = float(r['Valor'])
    assert math.isfinite(valor)
    medellin[fecha][columna] = valor
    estado = 'estado_tmin' if columna == 'tmin_c' else 'estado_precipitacion'
    medellin[fecha][estado] = r['NivelAprobacion']

print('IDEAM: filas originales:', len(crudo_ideam))
print('Parámetros, unidades y estados:', dict(Counter(
    (r['Parametro'], r['Unidad'], r['NivelAprobacion']) for r in crudo_ideam)))
print('Conversión: degC y °C designan la misma unidad; no se modifica el valor.')
''')

cell('code', '''
# CONAGUA: se conserva el TXT histórico completo y se selecciona el MISMO periodo.
texto_mx = (DATOS / 'mexico_21065_diarios.txt').read_text(encoding='utf-8-sig')
assert 'REGISTRO DIARIO HISTÓRICO' in texto_mx
assert re.search(r'ESTACIÓN\\s*:\\s*21065', texto_mx)
assert 'PUEBLA (OBS)' in texto_mx

def numero_o_ausente(texto):
    if texto.strip() in {'', 'NULO'}:
        return None
    valor = float(texto)
    assert math.isfinite(valor)
    return valor

puebla = {}
for linea in texto_mx.splitlines():
    if not re.match(r'^\\d{4}-\\d{2}-\\d{2}\\t', linea):
        continue
    partes = linea.split('\\t')  # conserva columnas vacías: no desplazar TMIN
    fecha = partes[0]
    if not INICIO.isoformat() <= fecha <= FIN.isoformat():
        continue
    assert len(partes) == 5, f'Estructura inesperada: {linea}'
    assert fecha not in puebla, f'Fecha duplicada: {fecha}'
    puebla[fecha] = {'fecha': fecha, 'ciudad': 'Puebla', 'pais': 'México',
        'estacion': '21065', 'tmin_c': numero_o_ausente(partes[4]),
        'precipitacion_mm': numero_o_ausente(partes[1]),
        'estado_tmin': 'No informado en el TXT',
        'estado_precipitacion': 'No informado en el TXT'}

print('Puebla:', len(puebla), 'fechas observadas en el periodo fijado.')
print('Columnas: FECHA → fecha; TMIN → tmin_c; PRECIP → precipitacion_mm.')
print('Unidades originales: TMIN en °C; PRECIP en mm. No requieren conversión.')
print('Las cantidades 0.01 mm se conservan exactamente como las publica la fuente.')
''')

cell('markdown', '''
## 3. Verificación del calendario y de la calidad
Se comprueban el rango, la frecuencia, los duplicados, las unidades y los valores ausentes. Crear una fila de calendario con una celda vacía **no crea una observación**: permite mostrar el hueco sin borrar fechas. En los CSV finales, una celda vacía representa ausencia, mientras que `0.0` de lluvia es una observación de precipitación cero.

Los valores negativos de precipitación no se aceptan. La comprobación de rango térmico es únicamente un control de plausibilidad, no una certificación de calidad del IDEAM o CONAGUA. Se conservan las fechas asignadas por cada organismo; no se desplazan para alinear valores. Los archivos no acreditan que los horarios exactos de cierre de los periodos de 24 horas sean idénticos entre las dos redes.
''')

cell('code', '''
assert sorted(medellin) == sorted(puebla) == FECHAS
assert min(medellin) == min(puebla) == INICIO.isoformat()
assert max(medellin) == max(puebla) == FIN.isoformat()
tablas = {'Medellín': list(medellin.values()), 'Puebla': [puebla[f] for f in FECHAS]}
auditoria = []
for ciudad, filas in tablas.items():
    assert len({r['fecha'] for r in filas}) == 304
    for variable in ['tmin_c', 'precipitacion_mm']:
        faltantes = [r['fecha'] for r in filas if r[variable] is None]
        validos = [r[variable] for r in filas if r[variable] is not None]
        if variable == 'precipitacion_mm':
            assert all(v >= 0 for v in validos)
        else:
            assert all(-30 <= v <= 55 for v in validos)
        auditoria.append({'ciudad': ciudad, 'variable': variable,
            'dias_calendario': len(filas), 'observaciones': len(validos),
            'ausentes': len(faltantes), 'fechas_ausentes': faltantes})
        print(f'{ciudad:9} {variable:18} {len(validos):3}/304 observaciones; '
              f'ausentes: {faltantes or "ninguno"}')

assert all(r['tmin_c'] is not None for r in tablas['Medellín'])
assert all(r['precipitacion_mm'] is not None for r in tablas['Medellín'])
assert all(r['tmin_c'] is not None and r['precipitacion_mm'] is not None
           for r in tablas['Puebla'])
print('Calendarios y extremos iguales; 304 días completos en ambas ciudades; sin duplicados ni imputaciones.')
''')

cell('code', '''
# Exportación reproducible: ambas tablas conservan todas las fechas del periodo.
for ciudad, filas in tablas.items():
    nombre = 'medellin_2026_diario.csv' if ciudad == 'Medellín' else 'puebla_2026_diario.csv'
    with (DATOS / nombre).open('w', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print(nombre, '—', len(filas), 'filas')
    for r in filas[:3]:
        print(r['fecha'], 'Tmin:', r['tmin_c'], '°C; precipitación:', r['precipitacion_mm'], 'mm')

consulta = json.loads((DATOS / 'ideam_aldea_2026_TMN_CON.zip.consulta.json').read_text(encoding='utf-8-sig'))
fuentes = {
    'Medellín': consulta['url'],
    'Puebla': 'https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/pue/dia21065.txt',
}
archivos = ['ideam_aldea_2026_TMN_CON.zip', 'mexico_21065_diarios.txt',
            'medellin_2026_diario.csv', 'puebla_2026_diario.csv']
informe = {'consulta': '2026-11-10', 'inicio': INICIO.isoformat(), 'fin': FIN.isoformat(),
    'frecuencia': 'diaria', 'unidades': {'tmin_c': '°C', 'precipitacion_mm': 'mm'},
    'conversiones': 'Sin conversión numérica; degC se rotula °C.',
    'fuentes': fuentes, 'auditoria': auditoria,
    'series_temperatura_completas': True,
    'sha256': {n: hashlib.sha256((DATOS/n).read_bytes()).hexdigest() for n in archivos}}
(DATOS / 'verificacion_2026.json').write_text(
    json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
print('Enlace exacto de la consulta IDEAM:', fuentes['Medellín'])
print('Informe de verificación y huellas SHA-256 guardados en verificacion_2026.json.')
''')

cell('markdown', '''
## 4. Uso correcto en la comparación posterior
Las dos tablas tienen el mismo calendario de 304 días. La temperatura mínima y la precipitación pueden compararse en las mismas 304 fechas, con iguales unidades y sin excluir días por faltantes. El periodo es idéntico para ambas ciudades; no se calculó mediante una unión interna que eliminara fechas.

LA ALDEA representa una estación dentro del municipio de Medellín, no un promedio del centro urbano. Puebla se representa con su observatorio. Las diferencias de altitud, entorno y horario de observación limitan la interpretación; el análisis describe estas estaciones en 2026 y no demuestra por sí solo un cambio climático.

**Resultado de la búsqueda:** archivos reales descargados, unidades y calendario verificados, dos tablas diarias de 2026 guardadas con 304 observaciones de temperatura mínima y 304 de precipitación cada una, sin faltantes. Las condiciones de calendario, frecuencia y variables comparables se cumplen para el periodo indicado; no se afirma que 2026 sea un año terminado.
''')

cell('markdown', '''
## B. Carga de las dos tablas y tipos para el análisis
Las tablas finales se leen de `datos/`. Se convierten las fechas a `datetime64[D]` y las mediciones a `float64`. Se muestran dimensiones, columnas, primeras filas, extremos del periodo, duplicados y faltantes. Si aparecieran faltantes se conservarían como `NaN`, nunca como ceros. Las máscaras de validez deben aplicarse a ambas ciudades para cada variable.
''')
cell('code', '''
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, HTML

def tabla_html(encabezados, filas):
    from html import escape
    cab = ''.join('<th>' + escape(str(x)) + '</th>' for x in encabezados)
    cuerpo = ''.join('<tr>' + ''.join('<td>' + escape(str(x)) + '</td>' for x in fila)
                     + '</tr>' for fila in filas)
    display(HTML('<table><thead><tr>' + cab + '</tr></thead><tbody>' + cuerpo + '</tbody></table>'))

ciudades = ['Medellín', 'Puebla']
cargadas = []
for nombre in ['medellin_2026_diario.csv', 'puebla_2026_diario.csv']:
    with (DATOS / nombre).open(encoding='utf-8', newline='') as archivo:
        filas = list(csv.DictReader(archivo))
    cargadas.append(filas)
    f = np.array([r['fecha'] for r in filas], dtype='datetime64[D]')
    valores = np.array([[float(r[k]) if r[k] else np.nan
                        for k in ['tmin_c', 'precipitacion_mm']] for r in filas], dtype=np.float64)
    print(nombre, 'dimensiones:', (len(filas), len(filas[0])), 'columnas:', list(filas[0]))
    print('Tipos:', f.dtype, valores.dtype, 'fechas:', f.min(), 'a', f.max())
    print('Duplicados:', len(f) - len(np.unique(f)),
          'faltantes [temperatura, precipitación]:', np.isnan(valores).sum(axis=0))
    tabla_html(['Fecha', 'Mínima (°C)', 'Precipitación (mm)'],
               [[r['fecha'], r['tmin_c'], r['precipitacion_mm']] for r in filas[:5]])

fechas = np.array([r['fecha'] for r in cargadas[0]], dtype='datetime64[D]')
fechas_puebla = np.array([r['fecha'] for r in cargadas[1]], dtype='datetime64[D]')
assert np.array_equal(fechas, fechas_puebla)
assert np.all(np.diff(fechas) == np.timedelta64(1, 'D'))
# Filas = días; columnas = Medellín, Puebla.
temperatura = np.array([[float(rs[i]['tmin_c']) if rs[i]['tmin_c'] else np.nan
                         for rs in cargadas] for i in range(len(fechas))])
lluvia = np.array([[float(rs[i]['precipitacion_mm']) if rs[i]['precipitacion_mm'] else np.nan
                    for rs in cargadas] for i in range(len(fechas))])
validas_t = np.isfinite(temperatura).all(axis=1)
validas_p = np.isfinite(lluvia).all(axis=1)
validas_ambas = validas_t & validas_p
print('Disponibles para comparar: temperatura', validas_t.sum(),
      '; precipitación', validas_p.sum(), '; ambas', validas_ambas.sum())
assert validas_ambas.sum() == 304
''')
cell('markdown', '''
## C. Análisis con NumPy: cortes, máscaras y broadcasting
Se inspeccionan los primeros siete días de ambas matrices. Las máscaras identifican lluvia observada (> 0 mm) y mínimas elevadas (> 15 °C); los umbrales son iguales para ambas ciudades. También se cuentan días con al menos 1 mm para distinguir lluvia apreciable de cantidades muy pequeñas.

El **broadcasting** permite restar el vector de promedios de las dos ciudades, de forma `(2,)`, a la matriz de temperaturas, de forma `(304, 2)`. Así se obtiene cuánto se aparta cada mínima del promedio de su propia estación, sin escribir un ciclo por día.
''')
cell('code', '''
print('Corte [0:7] — fechas:', fechas[:7])
print('Temperatura mínima (°C), columnas Medellín/Puebla:\\n', temperatura[:7, :])
print('Lluvia (mm), columnas Medellín/Puebla:\\n', lluvia[:7, :])
UMBRAL_T = 15.0
lluviosos = (lluvia > 0.0) & np.isfinite(lluvia)
lluvia_apreciable = (lluvia >= 1.0) & np.isfinite(lluvia)
minimas_elevadas = (temperatura > UMBRAL_T) & np.isfinite(temperatura)
promedios_t = np.mean(temperatura[validas_t], axis=0)
dispersion = np.std(temperatura[validas_t], axis=0, ddof=0)
desviaciones = temperatura - promedios_t  # broadcasting: (304, 2) - (2,)
assert np.allclose(desviaciones.mean(axis=0), 0.0, atol=1e-10)
print('Broadcasting:', temperatura.shape, '-', promedios_t.shape, '=', desviaciones.shape)
print('Desviaciones de los primeros siete días (°C):\\n', np.round(desviaciones[:7], 2))
print('Primeras cinco fechas lluviosas por ciudad:')
for j, ciudad in enumerate(ciudades):
    print(ciudad, fechas[lluviosos[:, j]][:5], '; mínimas >15 °C:', minimas_elevadas[:, j].sum())

resumen = []
for j, ciudad in enumerate(ciudades):
    t, p = temperatura[validas_t, j], lluvia[validas_p, j]
    resumen.append([ciudad, len(t), round(np.mean(t), 2), round(np.min(t), 2),
                    round(np.max(t), 2), round(np.std(t, ddof=0), 2),
                    round(np.sum(p), 2), int(lluviosos[:, j].sum()),
                    int(lluvia_apreciable[:, j].sum()), int(minimas_elevadas[:, j].sum())])
tabla_html(['Ciudad', 'Días', 'Mínima media (°C)', 'Menor mínima (°C)',
            'Mayor mínima (°C)', 'Desv. poblacional (°C)', 'Lluvia total (mm)',
            'Días >0 mm', 'Días ≥1 mm', 'Días mínima >15 °C'], resumen)
''')
cell('markdown', '''
## D. Gráficas comparativas
Se agregan los mismos días por mes: promedio de las temperaturas mínimas diarias y suma de las precipitaciones diarias. La línea representa **media mensual de mínimas**, no temperatura media diaria ni temperatura máxima. La precipitación mensual es un acumulado, no un promedio. Solo se muestran enero–octubre; noviembre y diciembre no se estiman.
''')
cell('code', '''
mes_diario = fechas.astype('datetime64[M]')
meses = np.unique(mes_diario)
etiquetas_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct']
t_mensual = np.array([temperatura[(mes_diario == m) & validas_t].mean(axis=0) for m in meses])
p_mensual = np.array([lluvia[(mes_diario == m) & validas_p].sum(axis=0) for m in meses])
assert np.allclose(p_mensual.sum(axis=0), lluvia.sum(axis=0))
tabla_html(['Mes 2026', 'Días', 'Mínima media Medellín (°C)', 'Mínima media Puebla (°C)',
            'Lluvia Medellín (mm)', 'Lluvia Puebla (mm)'],
           [[str(m), int((mes_diario == m).sum()), *np.round(t_mensual[i], 2),
             *np.round(p_mensual[i], 2)] for i, m in enumerate(meses)])
plt.rcParams.update({'figure.figsize': (10, 4.6), 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
colores = ['#087E8B', '#B85B15']
fig, ax = plt.subplots()
for j, ciudad in enumerate(ciudades):
    ax.plot(etiquetas_meses, t_mensual[:, j], marker='o', color=colores[j], label=ciudad)
ax.set(title='Temperatura mínima: promedio mensual — enero–octubre de 2026',
       xlabel='Mes de 2026', ylabel='Promedio de mínimas diarias (°C)')
ax.grid(axis='y', alpha=0.2)
ax.legend()
fig.tight_layout()
plt.show()
''')
cell('code', '''
mes_frio = np.argmin(t_mensual, axis=0)
mes_calido = np.argmax(t_mensual, axis=0)
display(Markdown(
    f'**Lectura de la gráfica 1.** Medellín tiene una mínima media del periodo de '
    f'{promedios_t[0]:.2f} °C y Puebla de {promedios_t[1]:.2f} °C. '
    f'La menor media mensual ocurre en {etiquetas_meses[mes_frio[0]]} para Medellín '
    f'({t_mensual[mes_frio[0], 0]:.2f} °C) y en {etiquetas_meses[mes_frio[1]]} para Puebla '
    f'({t_mensual[mes_frio[1], 1]:.2f} °C). **No permite concluir** cómo fueron las máximas '
    f'diarias ni que exista una tendencia climática de largo plazo.'))
''')
cell('code', '''
x = np.arange(len(meses))
fig, ax = plt.subplots()
ancho = 0.38
for j, ciudad in enumerate(ciudades):
    ax.bar(x + (j - 0.5) * ancho, p_mensual[:, j], width=ancho,
           color=colores[j], label=ciudad)
ax.set_xticks(x, etiquetas_meses)
ax.set(title='Precipitación acumulada por mes — enero–octubre de 2026',
       xlabel='Mes de 2026', ylabel='Precipitación acumulada (mm)')
ax.grid(axis='y', alpha=0.2)
ax.set_axisbelow(True)
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0)
fig.tight_layout()
plt.show()
''')
cell('code', '''
mes_lluvioso = np.argmax(p_mensual, axis=0)
fraccion_may_oct = p_mensual[4:, :].sum(axis=0) / p_mensual.sum(axis=0) * 100
display(Markdown(
    f'**Lectura de la gráfica 2.** El mayor acumulado mensual de Medellín es '
    f'{p_mensual[mes_lluvioso[0], 0]:.2f} mm en {etiquetas_meses[mes_lluvioso[0]]}; '
    f'el de Puebla es {p_mensual[mes_lluvioso[1], 1]:.2f} mm en {etiquetas_meses[mes_lluvioso[1]]}. '
    f'Mayo–octubre reúne el {fraccion_may_oct[0]:.1f}% y el {fraccion_may_oct[1]:.1f}% '
    f'de la lluvia del periodo, respectivamente. **No permite concluir** que llovió '
    f'todos los días de esos meses ni que esos acumulados se repitan cada año.'))
''')
cell('code', '''
# Bordes idénticos para comparar las distribuciones sin cambiar de escala.
bordes = np.linspace(temperatura[validas_t].min() - 0.5,
                     temperatura[validas_t].max() + 0.5, 16)
fig, ax = plt.subplots()
for j, ciudad in enumerate(ciudades):
    ax.hist(temperatura[validas_t, j], bins=bordes, color=colores[j],
            alpha=0.55, label=ciudad, edgecolor='white')
ax.axvline(UMBRAL_T, color='#333333', linestyle='--', label='Umbral común: 15 °C')
ax.set(title='Distribución de las temperaturas mínimas diarias — 2026',
       xlabel='Temperatura mínima diaria (°C)', ylabel='Número de días')
ax.legend()
fig.tight_layout()
plt.show()
''')
cell('code', '''
dispersion = np.std(temperatura[validas_t], axis=0, ddof=0)
display(Markdown(
    f'**Lectura de la gráfica 3.** La desviación estándar de las mínimas es '
    f'{dispersion[0]:.2f} °C en Medellín y {dispersion[1]:.2f} °C en Puebla. '
    f'El umbral común de 15 °C se supera en {minimas_elevadas[:, 0].sum()} y '
    f'{minimas_elevadas[:, 1].sum()} días, respectivamente. El histograma **no permite '
    f'concluir** en qué orden ocurrieron esos días, ni atribuir las diferencias a una causa.'))
''')
cell('markdown', '''
## E. Interpretación y respuesta a la pregunta guía
Los hallazgos siguientes se refieren exclusivamente a las estaciones elegidas y a enero–octubre de 2026. Se distingue la diferencia térmica de la similitud de presencia de lluvia; ambas se respaldan con los mismos días observados. Los porcentajes de mayo–octubre describen este periodo, no establecen por sí solos una temporada típica de largo plazo.
''')
cell('code', '''
total_p = lluvia[validas_p].sum(axis=0)
lluviosos_n = lluviosos.sum(axis=0)
coincidencia_lluvia = int(lluviosos.all(axis=1).sum())
mayor_t = ciudades[int(np.argmax(promedios_t))]
menor_variacion = ciudades[int(np.argmin(dispersion))]
display(Markdown(
    f'1. **Diferencia térmica:** la mínima media es {promedios_t[0]:.2f} °C en Medellín '
    f'y {promedios_t[1]:.2f} °C en Puebla; la diferencia Medellín − Puebla es '
    f'{promedios_t[0] - promedios_t[1]:.2f} °C. {mayor_t} tiene el promedio mayor y '
    f'{menor_variacion} la menor variabilidad diaria. La expectativa térmica inicial '
    f'{"se sostiene" if promedios_t[0] > promedios_t[1] and dispersion[0] < dispersion[1] else "no se sostiene completamente"} '
    f'en estos datos.\\n\\n'
    f'2. **Similitud:** ambas estaciones registran días con lluvia: '
    f'{lluviosos_n[0]} de 304 en Medellín y {lluviosos_n[1]} de 304 en Puebla; '
    f'en {coincidencia_lluvia} fechas ambas reportan más de 0 mm. Esto solo indica '
    f'coincidencia de registros diarios; no prueba que se trate del mismo fenómeno meteorológico.\\n\\n'
    f'3. **Diferencia en acumulados:** Medellín registra {total_p[0]:.2f} mm y Puebla '
    f'{total_p[1]:.2f} mm, una diferencia de {total_p[0] - total_p[1]:.2f} mm. '
    f'Los días con al menos 1 mm son {lluvia_apreciable[:, 0].sum()} y '
    f'{lluvia_apreciable[:, 1].sum()}, respectivamente; este conteo evita interpretar '
    f'todas las cantidades muy pequeñas como episodios de igual importancia.'))
''')
cell('markdown', '''
### Alcance y limitaciones
El calendario común evita comparar meses distintos. Quedan **304 observaciones por ciudad y por variable**, sin faltantes ni fechas duplicadas; por eso no fue necesario eliminar fechas en las comparaciones diarias. Se seleccionó temperatura mínima porque la máxima de LA ALDEA tenía dos ausencias; no se sustituyeron por cero ni se interpolaron. Los archivos de respaldo y los estados de aprobación permiten revisar esa elección.

Los datos del IDEAM están En revisión o Preliminar, y el TXT de CONAGUA no informa un estado de aprobación individual. LA ALDEA y el observatorio de Puebla representan puntos de observación; las diferencias de altitud y entorno pueden influir, pero este análisis no aísla sus efectos. Los periodos diarios se conservan con las fechas de cada fuente y sus ventanas horarias pueden diferir. Los resultados no representan toda la ciudad, no prueban causalidad y no permiten describir un año completo ni cambio climático: faltan noviembre y diciembre de 2026.

### Revisión de la entrega
- Dos ciudades de países diferentes: Medellín, Colombia, y Puebla, México.
- Mismo periodo: 2026-01-01 a 2026-10-31; frecuencia diaria; °C y mm.
- Fuentes, columnas, unidades, estados de aprobación y decisiones documentados.
- Carga desde `datos/`, tipos, dimensiones, faltantes y duplicados revisados.
- NumPy: arrays, cortes, máscaras booleanas, estadísticas y broadcasting.
- Tres gráficas con títulos, ejes, unidades, leyendas y lecturas con límites.
- Hallazgos con evidencia y notebook ejecutado en orden dentro de EA3.

**Reproducir:** seleccionar un kernel Python con NumPy y Matplotlib (`pip install -r requirements.txt`, desde esta carpeta) y ejecutar todas las celdas en orden. Los datos ya están incluidos, por lo que no se necesita descargarlos ni modificar AE1 o AE2. Los scripts de descarga y construcción son auxiliares: la explicación completa está en este notebook.
''')

nb = {'cells': cells, 'metadata': {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.12.13'}}, 'nbformat': 4, 'nbformat_minor': 5}

# Ejecuta con un kernel real y conserva tablas y gráficas en las salidas del notebook.
import os, sys
for variable, carpeta in [('JUPYTER_CONFIG_DIR', '.jupyter-config'),
                          ('JUPYTER_RUNTIME_DIR', '.jupyter-runtime'),
                          ('IPYTHONDIR', '.ipython'), ('MPLCONFIGDIR', '.matplotlib')]:
    os.environ[variable] = str(BASE / carpeta)
os.environ['JUPYTER_PATH'] = str(BASE / '.jupyter')
kernel_dir = BASE / '.jupyter' / 'kernels' / 'python3'
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / 'kernel.json').write_text(json.dumps({
    'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
    'display_name': 'Python 3', 'language': 'python'}), encoding='utf-8')
import nbformat
from nbclient import NotebookClient
notebook = nbformat.reads(json.dumps(nb), as_version=4)
NotebookClient(notebook, timeout=120, kernel_name='python3',
               resources={'metadata': {'path': str(BASE)}}).execute()
# Las interpretaciones calculadas se guardan como celdas Markdown, después de cada
# gráfica y en las conclusiones. El resto del análisis sigue siendo ejecutable.
for i, c in enumerate(notebook.cells):
    if c.cell_type != 'code':
        continue
    textos = [o.get('data', {}).get('text/markdown') for o in c.get('outputs', [])]
    textos = [t for t in textos if t]
    if textos:
        notebook.cells[i] = nbformat.v4.new_markdown_cell('\n\n'.join(textos), id=c.id)
# Verifica de nuevo el notebook final con las explicaciones ya en Markdown.
NotebookClient(notebook, timeout=120, kernel_name='python3',
               resources={'metadata': {'path': str(BASE)}}).execute()
nbformat.validate(notebook)
destino = BASE / 'EA3_Posso_Mazo_Silvia_Rosa.ipynb'
nbformat.write(notebook, destino)
print('Notebook ejecutado y guardado:', destino)
