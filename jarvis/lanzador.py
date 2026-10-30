"""Lanzador Sentinel: abre y cierra apps, juegos, carpetas y webs por nombre.
Lo usan Jarvis por voz (funciones directas) y OpenJarvis (servidor MCP)."""
import difflib, json, os, shutil, subprocess, unicodedata, webbrowser
from pathlib import Path

try:  # el servidor MCP solo hace falta para OpenJarvis; la voz usa las funciones directo
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("lanzador")
    _tool = mcp.tool
except ImportError:
    mcp = None
    def _tool():
        return lambda f: f


def _clave(t: str) -> str:
    t = unicodedata.normalize("NFD", (t or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return "".join(c for c in t if c.isalnum())


# ---------------- configuración ----------------
# Páginas web (solo si no hay acceso directo con ese nombre en el PC)
WEBS = {
    "bybitweb": "https://www.bybit.com/trade/usdt/BTCUSDT",
    "grafanaweb": "http://localhost:3000",
    "metricool": "https://app.metricool.com",
    "whop": "https://whop.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "github": "https://github.com",
    "facebook": "https://www.facebook.com/SentinelTradingHQ",
    "instagram": "https://www.instagram.com/sentineltradinghq/",
}
# Apodos: lo que dices -> nombre del acceso directo / programa
ALIAS = {
    "tradingview": "TradingView", "trading": "TradingView",
    "binance": "Binance", "bybit": "Bybit", "baibit": "Bybit",
    "discord": "Discord", "grafana": "abrir_grafana", "panelfreqtrade": "PANEL FREQTRADE",
    "freqtrade": "PANEL FREQTRADE", "panel": "PANEL FREQTRADE",
    "jarvis": "OpenJarvis", "openjarvis": "OpenJarvis",
    "chrome": "Google Chrome", "google": "Google Chrome", "navegador": "Firefox", "firefox": "Firefox",
    "steam": "Steam", "epic": "Epic Games Launcher", "epicgames": "Epic Games Launcher",
    "roblox": "Roblox Player", "robloxstudio": "Roblox Studio",
    "counter": "Counter-Strike 2", "counterstrike": "Counter-Strike 2", "cs2": "Counter-Strike 2",
    "overwatch": "Overwatch", "hogwarts": "Hogwarts Legacy", "deltaforce": "Delta Force",
    "asphalt": "Asphalt Legends", "oncehuman": "Once Human", "supersus": "Super Sus",
    "supermarket": "Supermarket Simulator", "supermarketsimulator": "Supermarket Simulator",
    "supermarkettogether": "Supermarket Together", "bongocat": "Bongo Cat",
    "tiktoklive": "TikTok LIVE Studio", "tiktok": "TikTok LIVE Studio",
    "capcut": "CapCut", "filmora": "Wondershare Filmora", "canva": "Canva", "wavepad": "WavePad",
    "afterburner": "MSI Afterburner", "nvidia": "NVIDIA App", "githubdesktop": "GitHub Desktop",
    "gitbash": "Git Bash", "driverbooster": "Driver Booster", "advancedsystemcare": "Advanced SystemCare",
    "codigos": "CODIGOS", "videos": "videos", "clases": "clases", "bots": "bots",
    "visa": "para la visa", "paralavisa": "para la visa", "backup": "rclone para backup",
}
# Programas y lugares de Windows
SISTEMA = {
    "cmd": "cmd", "ceemede": "cmd", "consola": "cmd", "simbolodelsistema": "cmd", "terminal": "wt",
    "powershell": "powershell", "blocdenotas": "notepad", "notepad": "notepad",
    "calculadora": "calc", "explorador": "explorer", "misarchivos": "explorer",
    "administradordetareas": "taskmgr", "configuracion": "ms-settings:", "paint": "mspaint",
    "esteequipo": "shell:MyComputerFolder", "miequipo": "shell:MyComputerFolder",
    "papelera": "shell:RecycleBinFolder", "papeleradereciclaje": "shell:RecycleBinFolder",
    "descargas": "shell:Downloads", "documentos": "shell:Personal", "escritorio": "shell:Desktop",
    "imagenes": "shell:My Pictures", "paneldecontrol": "control", "recortes": "ms-screenclip:",
}
# Procesos para cerrar programas de Windows
PROCESOS = {"cmd": "cmd", "consola": "cmd", "ceemede": "cmd", "simbolodelsistema": "cmd",
            "terminal": "windowsterminal", "powershell": "powershell", "blocdenotas": "notepad",
            "notepad": "notepad", "calculadora": "calculatorapp", "administradordetareas": "taskmgr",
            "configuracion": "systemsettings", "paint": "mspaint"}
PROTEGIDOS = {"explorer", "ollama", "ollamaappv", "python", "pythonw", "uv", "uvw", "svchost", "system",
              "winlogon", "csrss", "dwm", "lsass", "services", "searchapp", "shellexperiencehost"}
NAVEGADORES = {"chrome", "firefox", "msedge", "opera", "brave"}
MODOS = {"trading": ["tradingview", "binance", "bybit", "discord", "grafana"]}

CARPETAS = [
    Path.home() / "Desktop", Path.home() / "OneDrive" / "Desktop", Path(r"C:\Users\Public\Desktop"),
    Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")),
    Path(os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")),
]


# ---------------- búsqueda de accesos ----------------
def _inventario():
    """Todo lo que se puede abrir: accesos del escritorio y menú Inicio, carpetas y archivos del escritorio."""
    items = {}
    for carpeta in CARPETAS:
        if not carpeta.exists():
            continue
        es_escritorio = "Desktop" in str(carpeta)
        it = carpeta.iterdir() if es_escritorio else carpeta.rglob("*")
        for f in it:
            if f.name.lower() == "desktop.ini":
                continue
            if f.suffix.lower() in (".lnk", ".url", ".appref-ms") or es_escritorio:
                items.setdefault(_clave(f.stem), f)
    return items


def _encontrar(nombre: str):
    clave = _clave(nombre)
    destino = _clave(ALIAS.get(clave, nombre))
    items = _inventario()
    if destino in items:
        return items[destino]
    candidatos = [k for k in items if k.startswith(destino)] or [k for k in items if destino in k]
    if candidatos:
        return items[min(candidatos, key=len)]
    cerca = difflib.get_close_matches(destino, items.keys(), n=1, cutoff=0.75)
    return items[cerca[0]] if cerca else None


def _app_tienda(nombre: str):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-StartApps | ConvertTo-Json -Compress"],
                             capture_output=True, text=True, timeout=20).stdout
        apps = json.loads(out or "[]")
        apps = [apps] if isinstance(apps, dict) else apps
        d = _clave(ALIAS.get(_clave(nombre), nombre))
        for a in apps:
            if d and d in _clave(a.get("Name")):
                return a.get("AppID")
    except Exception:
        pass
    return None


def _start(objetivo: str):
    subprocess.Popen(["cmd", "/c", "start", "", objetivo])


# ---------------- abrir ----------------
def _abrir(nombre: str) -> str:
    clave = _clave(nombre)
    if clave in SISTEMA:
        _start(SISTEMA[clave]); return f"Abrí {nombre}."
    acceso = _encontrar(nombre)
    if acceso:
        os.startfile(str(acceso)); return f"Abrí {nombre}."
    for web in (clave, clave + "web"):
        if web in WEBS:
            webbrowser.open(WEBS[web]); return f"Abrí {nombre} en el navegador."
    app_id = _app_tienda(nombre)
    if app_id:
        subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"]); return f"Abrí {nombre}."
    if shutil.which(clave):
        _start(clave); return f"Abrí {nombre}."
    return f"No encontré '{nombre}' en el PC."


# ---------------- cerrar ----------------
def _exe_de_acceso(acceso: Path):
    if acceso is None or acceso.suffix.lower() != ".lnk":
        return None
    try:
        ps = f"(New-Object -ComObject WScript.Shell).CreateShortcut('{acceso}').TargetPath"
        t = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=15).stdout.strip()
        return _clave(Path(t).stem) if t.lower().endswith(".exe") else None
    except Exception:
        return None


def _ventanas():
    ps = ("Get-Process | Where-Object { $_.MainWindowHandle -ne 0 } | "
          "Select-Object Id, ProcessName, MainWindowTitle | ConvertTo-Json -Compress")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=20).stdout
    v = json.loads(out or "[]")
    return [v] if isinstance(v, dict) else v


def _cerrar(nombre: str) -> str:
    clave = _clave(nombre)
    if clave in WEBS:
        return f"{nombre} está en el navegador; ciérralo desde la pestaña."
    objetivos = set()
    if clave in PROCESOS:
        objetivos.add(PROCESOS[clave])
    else:
        exe = _exe_de_acceso(_encontrar(nombre))
        if exe:
            objetivos.add(exe)
        objetivos.add(_clave(ALIAS.get(clave, nombre)))
    if objetivos & PROTEGIDOS or clave in ("explorador", "esteequipo", "escritorio"):
        return f"Por seguridad no cierro {nombre}."
    ventanas = _ventanas()
    ids = [w["Id"] for w in ventanas if any(o and o in _clave(w["ProcessName"]) for o in objetivos)]
    if not ids:  # buscar por título de ventana (nunca en navegadores)
        ids = [w["Id"] for w in ventanas
               if _clave(w["ProcessName"]) not in NAVEGADORES | PROTEGIDOS
               and any(o and o in _clave(w.get("MainWindowTitle")) for o in objetivos)]
    if not ids:
        return f"No encontré {nombre} abierto."
    lista = ",".join(str(i) for i in ids)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"Get-Process -Id {lista} -ErrorAction SilentlyContinue | ForEach-Object {{ [void]$_.CloseMainWindow() }}"],
                   timeout=20)
    return f"Cerré {nombre}."


# ---------------- controles de Windows ----------------
def _teclas(codigo: int, veces: int = 1):
    ps = f"$w=New-Object -ComObject WScript.Shell; 1..{veces} | % {{ $w.SendKeys([char]{codigo}) }}"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=15)


def _control(accion: str) -> str:
    if accion == "subir_volumen":
        _teclas(175, 5); return "Subí el volumen."
    if accion == "bajar_volumen":
        _teclas(174, 5); return "Bajé el volumen."
    if accion == "silenciar":
        _teclas(173); return "Listo."
    if accion == "bloquear":
        subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"]); return "Bloqueando la pantalla."
    if accion == "minimizar":
        subprocess.run(["powershell", "-NoProfile", "-Command", "(New-Object -ComObject Shell.Application).MinimizeAll()"], timeout=15)
        return "Minimicé todo."
    if accion == "captura":
        _start("ms-screenclip:"); return "Selecciona el área de la captura."
    return "No conozco ese control."


# ---------------- herramientas para OpenJarvis ----------------
@_tool()
def abrir_app(nombre: str) -> str:
    """Abre una app, juego, carpeta, archivo del escritorio o página web por su nombre
    (TradingView, Binance, Bybit, Discord, Steam, Roblox, CapCut, CODIGOS, Descargas, CMD...)."""
    return _abrir(nombre)


@_tool()
def cerrar_app(nombre: str) -> str:
    """Cierra una app o juego abierto por su nombre (como darle a la X). No cierra pestañas del navegador
    ni procesos del sistema."""
    return _cerrar(nombre)


@_tool()
def activar_modo(modo: str) -> str:
    """Abre varias apps de una vez. Modos: trading (TradingView, Binance, Bybit, Discord y Grafana)."""
    clave = _clave(modo).replace("modo", "")
    if clave not in MODOS:
        return f"No existe el modo '{modo}'. Modos: {', '.join(MODOS)}."
    return "\n".join(_abrir(x) for x in MODOS[clave])


@_tool()
def control_windows(accion: str) -> str:
    """Controles del PC: subir_volumen, bajar_volumen, silenciar, bloquear, minimizar, captura."""
    return _control(accion)


@_tool()
def listar_opciones() -> str:
    """Lista todo lo que el lanzador puede abrir."""
    nombres = sorted({p.stem for p in _inventario().values()})
    return ("Puedo abrir: " + ", ".join(nombres[:150]) + "\nWindows: " + ", ".join(SISTEMA) +
            "\nWebs: " + ", ".join(WEBS) + "\nModos: " + ", ".join(MODOS))


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit("Falta el paquete mcp<2")
    mcp.run()
