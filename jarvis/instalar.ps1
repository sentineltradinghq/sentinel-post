# Instala el Lanzador Sentinel para OpenJarvis
$dir = Join-Path $HOME ".openjarvis"
New-Item -ItemType Directory -Force $dir | Out-Null
$base = "https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/jarvis"
Invoke-WebRequest "$base/lanzador.py" -OutFile "$dir\lanzador.py" -UseBasicParsing
Invoke-WebRequest "$base/configurar.py" -OutFile "$dir\configurar.py" -UseBasicParsing
uv run --with tomlkit python "$dir\configurar.py"
Write-Host "Probando el lanzador (debe abrir Bybit en el navegador)..."
uv run --with mcp python -c "import sys; sys.path.insert(0, r'$dir'); import lanzador; print(lanzador._abrir('bybit'))"
Write-Host "Cierra OpenJarvis por completo y vuelve a abrirlo."
