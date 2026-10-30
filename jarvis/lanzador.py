"""Lanzador Sentinel: servidor MCP para que OpenJarvis abra apps, webs y modos."""
import json, os, subprocess, webbrowser
from pathlib import Path
try:  # el servidor MCP solo hace falta para OpenJarvis; la voz usa las funciones directo
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("lanzador")
    _tool = mcp.tool
except ImportError:
    mcp = None
    def _tool():
        return lambda f: f

# Páginas web: nombre -> URL
WEBS = {
    "bybit": "https://www.bybit.com/trade/usdt/BTCUSDT",
    "grafana": "http://localhost:3000",
    "metricool": "https://app.metricool.com",
    "whop": "https://whop.com",
}
# Apps del PC: nombre -> texto a buscar en los accesos directos de Windows
APPS = {
    "tradingview": "TradingView",
    "binance": "Binance",
    "discord": "Discord",
}
# Modos: varias cosas de una vez
MODOS = {
    "trading": ["tradingview", "binance", "bybit", "discord", "grafana"],
}

CARPETAS = [
    Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")),
    Path(os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")),
    Path.home() / "Desktop",
    Path(r"C:\Users\Public\Desktop"),
]


def _buscar_acceso(texto: str):
    t = texto.lower()
    for carpeta in CARPETAS:
        if not carpeta.exists():
            continue
        for ext in ("*.lnk", "*.url", "*.appref-ms"):
            for f in carpeta.rglob(ext):
                if t in f.stem.lower():
                    return f
    return None


def _buscar_app_tienda(texto: str):
    """Apps de Microsoft Store: busca su AppID con Get-StartApps."""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-StartApps | ConvertTo-Json -Compress"],
            capture_output=True, text=True, timeout=20).stdout
        apps = json.loads(out or "[]")
        if isinstance(apps, dict):
            apps = [apps]
        for a in apps:
            if texto.lower() in (a.get("Name") or "").lower():
                return a.get("AppID")
    except Exception:
        pass
    return None


def _abrir(nombre: str) -> str:
    clave = nombre.lower().strip().replace(" ", "")
    if clave in WEBS:
        webbrowser.open(WEBS[clave])
        return f"Abrí {nombre} en el navegador."
    texto = APPS.get(clave, nombre)
    acceso = _buscar_acceso(texto)
    if acceso:
        os.startfile(str(acceso))
        return f"Abrí {nombre}."
    app_id = _buscar_app_tienda(texto)
    if app_id:
        subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
        return f"Abrí {nombre}."
    return f"No encontré '{nombre}' en el PC. Revisa el nombre o agrégalo al lanzador."


@_tool()
def abrir_app(nombre: str) -> str:
    """Abre una aplicación del PC o una página web por su nombre.
    Ejemplos: TradingView, Binance, Bybit, Discord, Grafana, Metricool, Whop,
    o cualquier programa instalado en Windows."""
    return _abrir(nombre)


@_tool()
def activar_modo(modo: str) -> str:
    """Abre varias apps de una vez. Modos disponibles: trading
    (TradingView, Binance, Bybit, Discord y Grafana)."""
    clave = modo.lower().replace("modo", "").strip()
    if clave not in MODOS:
        return f"No existe el modo '{modo}'. Modos: {', '.join(MODOS)}."
    return "\n".join(_abrir(x) for x in MODOS[clave])


@_tool()
def listar_opciones() -> str:
    """Lista las apps, páginas y modos que el lanzador conoce."""
    return (f"Apps: {', '.join(APPS)}\nWebs: {', '.join(WEBS)}\n"
            f"Modos: {', '.join(MODOS)}\nTambién puedo intentar abrir cualquier programa instalado por su nombre.")


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit("Falta el paquete mcp<2")
    mcp.run()
