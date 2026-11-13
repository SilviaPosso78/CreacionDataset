param([int]$Anio = 2026, [int]$AnioInicio = 0, [string]$Estacion = '26205080', [string]$FechaFin = '', [string]$Temperatura = 'TMX_CON', [string]$Lluvia = 'PTPM_CON')
if ($AnioInicio -eq 0) { $AnioInicio = $Anio }
if ($Anio - $AnioInicio + 1 -gt 30) { throw 'El portal limita las series diarias a 30 años por consulta.' }
$ErrorActionPreference = 'Stop'
$base = Join-Path $PSScriptRoot 'datos'
$portal = 'https://modulopersonalizado.ideam.gov.co/DhimeServicePortal/'
# Reproduce el acceso público del portal, sin guardar ni imprimir el token.
$widget = (Invoke-WebRequest 'https://atencionciudadano.ideam.gov.co/widgets/Ciudadano/Widget.js' -UseBasicParsing -TimeoutSec 40).Content
$cred = [regex]::Match($widget, 'username:\s*"([^"]+)",\s*password:\s*"([^"]+)"')
if (-not $cred.Success) { throw 'No se encontró la configuración de acceso del portal público.' }
$token = Invoke-RestMethod ($portal+'token') -Method Post -Body @{username=$cred.Groups[1].Value;password=$cred.Groups[2].Value;grant_type='password'} -TimeoutSec 40
$headers = @{Authorization=('Bearer '+$token.access_token)}
$restricciones = Invoke-RestMethod ($portal+'api/Restricciones/GestionDatos') -Headers $headers -TimeoutSec 40
$restricciones | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $base 'dhime_restricciones.json')
$items = @(
    @{IdParametro='TEMPERATURA';Etiqueta='TMX_CON';EsEjeY1=$false;EsEjeY2=$false;EsTipoLinea=$false;EsTipoBarra=$false;Calculo='';TipoSerie='Estandard'},
    @{IdParametro='PRECIPITACION';Etiqueta='PTPM_CON';EsEjeY1=$false;EsEjeY2=$false;EsTipoLinea=$false;EsTipoBarra=$false;Calculo='';TipoSerie='Estandard'}
)
$filtro = "((IdParametro~eq~'TEMPERATURA'~and~Etiqueta~eq~'TMX_CON'~and~IdEstacion~eq~'26205080')~or~(IdParametro~eq~'PRECIPITACION'~and~Etiqueta~eq~'PTPM_CON'~and~IdEstacion~eq~'26205080'))"
$filtro = $filtro.Replace('26205080', $Estacion)
$filtro = $filtro.Replace('TMX_CON', $Temperatura).Replace('PTPM_CON', $Lluvia)
$items[0].Etiqueta = $Temperatura
$items[1].Etiqueta = $Lluvia
if (-not $FechaFin) { $FechaFin = "$Anio-12-31" }
$parametros = @{sort='';filter=$filtro;group='';fechaInicio="$AnioInicio-01-01T05:00:00.000Z";fechaFin="${FechaFin}T05:00:00.000Z";mostrarGrado='true';mostrarCalificador='true';mostrarNivelAprobacion='true';tipoReporte='csv'}
$query = ($parametros.GetEnumerator() | ForEach-Object {[uri]::EscapeDataString($_.Key)+'='+[uri]::EscapeDataString($_.Value)}) -join '&'
$url = $portal+'api/Listas/ConsultarListaSeriesTiempoEstacionesPorFiltroString?'+$query
$respuesta = Invoke-RestMethod $url -Method Post -Headers $headers -ContentType 'application/json' -Body (ConvertTo-Json -InputObject $items -Compress) -TimeoutSec 60
if (-not $respuesta.zip) { throw ('El portal no entregó ZIP: '+$respuesta.mensaje) }
$prefijo = if ($Estacion -eq '26205080') { 'aldea' } else { $Estacion }
$nombre = if ($AnioInicio -eq $Anio) { "ideam_${prefijo}_$Anio.zip" } else { "ideam_${prefijo}_${AnioInicio}_${Anio}.zip" }
if ($Temperatura -ne 'TMX_CON') { $nombre = $nombre.Replace('.zip', "_${Temperatura}.zip") }
[IO.File]::WriteAllBytes((Join-Path $base $nombre), [Convert]::FromBase64String($respuesta.zip))
@{url=$url;items=$items;fechaConsulta='2026-11-10';archivo=$nombre} | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $base ($nombre+'.consulta.json'))
Write-Output "Descargado $nombre"
