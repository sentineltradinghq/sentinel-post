# Instala "Jarvis por voz" (Hey Jarvis) y lo deja arrancando con Windows
$dir = Join-Path $HOME ".openjarvis"
New-Item -ItemType Directory -Force $dir | Out-Null
$base = "https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/jarvis"
Invoke-WebRequest "$base/jarvis_voz.py" -OutFile "$dir\jarvis_voz.py" -UseBasicParsing
Invoke-WebRequest "$base/lanzador.py" -OutFile "$dir\lanzador.py" -UseBasicParsing

$deps = @("--python","3.11","--with","openwakeword","--with","onnxruntime","--with","faster-whisper","--with","sounddevice","--with","numpy","--with","requests","--with","pywin32","--with","ddgs")

Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*jarvis_voz.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Write-Host "1/3 Descargando modelos (puede tardar unos minutos la primera vez)..."
uv run @deps python "$dir\jarvis_voz.py" --preparar
Write-Host "2/3 Probando la voz..."
uv run @deps python "$dir\jarvis_voz.py" --probar

Write-Host "3/3 Configurando arranque automatico con Windows..."
$uvw = (Get-Command uvw -ErrorAction SilentlyContinue).Source
if (-not $uvw) { $uvw = (Get-Command uv).Source }
$argsTxt = (($deps + @("python", "`"$dir\jarvis_voz.py`"")) -join " ")
$startup = [Environment]::GetFolderPath("Startup")
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("$startup\Jarvis Voz.lnk")
$lnk.TargetPath = $uvw
$lnk.Arguments = "run $argsTxt"
$lnk.WorkingDirectory = $dir
$lnk.Save()
Copy-Item "$startup\Jarvis Voz.lnk" "$([Environment]::GetFolderPath('Desktop'))\Jarvis Voz.lnk" -Force

Start-Process $uvw -ArgumentList "run $argsTxt" -WorkingDirectory $dir
Write-Host "Listo. En unos segundos Jarvis dira 'Jarvis listo'. Di: Hey Jarvis... activa el modo trading"
