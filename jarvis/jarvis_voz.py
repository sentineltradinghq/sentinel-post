"""Jarvis por voz (100% local).
Di "Hey Jarvis", espera el tono y da tu orden.
- Comandos (abre X, modo trading) se ejecutan al instante con el lanzador.
- Preguntas van a Ollama (qwen3.5:9b) y la respuesta se dice en voz alta.
"""
import logging, os, queue, re, sys, time, unicodedata
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd

BASE = Path.home() / ".openjarvis"
sys.path.insert(0, str(BASE))
logging.basicConfig(filename=BASE / "jarvis_voz.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
log = logging.getLogger("jarvis_voz")

MODELO_IA = "qwen3.5:9b"
OLLAMA = "http://localhost:11434/api/chat"
import json as _json
_CFG = {}
try:
    _CFG = _json.loads((BASE / "jarvis_voz.json").read_text(encoding="utf-8"))
except Exception:
    pass
UMBRAL_WAKE = float(_CFG.get("umbral", 0.3))   # sensibilidad de "Hey Jarvis" (más bajo = más sensible)
RATE, BLOQUE = 16000, 1280  # 80 ms por bloque
MAX_ORDEN_S, SILENCIO_S = 10, 1.2
RUIDO = 300.0  # nivel de ruido de fondo, se actualiza solo

def sistema():
    hoy = time.strftime("%d/%m/%Y")
    return ("Eres Jarvis, el asistente de voz de Yasmani, dueño de Sentinel Trading (trading algorítmico de cripto). "
            f"Hoy es {hoy}. Responde SIEMPRE en español, directo y concreto, con datos y cifras cuando los tengas, "
            "en 2 a 5 frases, sin listas, sin markdown ni emojis, porque se leerá en voz alta. "
            "Si te doy resultados de búsqueda web, úsalos como fuente principal y menciona la cifra o el hecho clave. "
            "Nunca digas que no tienes acceso a internet si te di resultados. Si de verdad no sabes, dilo en una frase.")


# ---------- voz (Windows SAPI) ----------
def _voz():
    import win32com.client
    v = win32com.client.Dispatch("SAPI.SpVoice")
    for i in range(v.GetVoices().Count):
        vo = v.GetVoices().Item(i)
        d = vo.GetDescription().lower()
        if "spanish" in d or "español" in d or "espanol" in d:
            v.Voice = vo
            break
    return v

VOZ = None
def hablar(texto: str):
    global VOZ
    log.info("Jarvis: %s", texto)
    try:
        if VOZ is None:
            VOZ = _voz()
        VOZ.Speak(texto)
    except Exception as e:
        log.error("TTS: %s", e)

def tono(alto=True):
    try:
        import winsound
        winsound.Beep(1200 if alto else 700, 120)
    except Exception:
        pass


# ---------- utilidades ----------
def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", " ", t).strip()

def limpiar_para_voz(t: str) -> str:
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.S)
    t = re.sub(r"[*#_`>|]", "", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------- interpretación de la orden ----------
def interpretar(texto: str):
    """Devuelve (accion, argumento). Acciones: modo, abrir, listar, salir, preguntar."""
    n = normalizar(texto)
    if not n:
        return ("nada", "")
    c = re.search(r"\b(cierra|cerrar|cierrame|termina)\b\s+(.*)", n)
    if c:
        nombre = re.sub(r"^(el|la|los|las|mi|a)\s+", "", c.group(2)).strip()
        nombre = re.sub(r"^(app|aplicacion|programa)\s+(de\s+)?", "", nombre).strip()
        if "modo" in nombre and "trad" in nombre:
            return ("cerrar_modo", "trading")
        if nombre:
            return ("cerrar", nombre)
    if "modo" in n and ("trading" in n or "trade" in n or "treiding" in n):
        return ("modo", "trading")
    if re.search(r"\b(apagate|detente|cierra el asistente|apaga el asistente)\b", n):
        return ("salir", "")
    if re.search(r"que (apps|aplicaciones|programas) (puedes|sabes) abrir|lista de (apps|aplicaciones)", n):
        return ("listar", "")
    m = re.search(r"\b(abre|abrir|abreme|abri|ejecuta|ejecutame|lanza|inicia|activa|activame|pon|ponme|muestrame)\b\s+(.*)", n)
    if m:
        nombre = re.sub(r"^(el|la|los|las|mi|a)\s+", "", m.group(2)).strip()
        nombre = re.sub(r"^(app|aplicacion|programa|pagina|web)\s+(de\s+)?", "", nombre).strip()
        nombre = re.sub(r"\s+(por favor|porfa)$", "", nombre)
        if nombre:
            return ("abrir", nombre)
    return ("preguntar", texto)


MONEDAS = {"bitcoin": "bitcoin", "btc": "bitcoin", "ethereum": "ethereum", "ether": "ethereum",
           "eth": "ethereum", "solana": "solana", "sol": "solana", "xrp": "ripple", "ripple": "ripple",
           "bnb": "binancecoin", "dogecoin": "dogecoin", "doge": "dogecoin"}

def precio_moneda(texto: str):
    n = normalizar(texto)
    if not re.search(r"\b(precio|cuanto (esta|vale|cuesta)|cotiza|a como esta|como esta)\b", n):
        return None
    for palabra, cid in MONEDAS.items():
        if re.search(rf"\b{palabra}\b", n):
            r = requests.get("https://api.coingecko.com/api/v3/simple/price", timeout=10, params={
                "ids": cid, "vs_currencies": "usd", "include_24hr_change": "true"}).json()[cid]
            p, c = r["usd"], r.get("usd_24h_change", 0) or 0
            precio = f"{p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if p >= 100:
                precio = precio.split(",")[0]
            mov = "sube" if c >= 0 else "baja"
            cambio = f"{abs(c):.1f}".replace(".", ",")
            return f"{palabra.capitalize()} está en {precio} dólares, {mov} {cambio} por ciento en 24 horas."
    return None

ACTUALIDAD = re.compile(r"\b(hoy|ahora|actual|ultim\w*|noticia\w*|paso|pasando|ocurrio|sucedio|ayer|semana|mes|"
                        r"precio|mercado|hackeo|hack|robo|binance|bybit|bitcoin|cripto\w*|busca|investiga|"
                        r"quien es|quien gano|cuando|clima|202\d)\b")

def buscar_web(consulta: str) -> str:
    try:
        from ddgs import DDGS
        d = DDGS()
        res = []
        try:
            res = list(d.news(consulta, max_results=5))
        except Exception:
            pass
        if len(res) < 3:
            res += list(d.text(consulta, max_results=5))
        return "\n".join(f"- {x.get('title','')}: {x.get('body','')} ({x.get('date','')})" for x in res[:8])
    except Exception as e:
        log.warning("búsqueda: %s", e)
        return ""

def preguntar_ia(texto: str) -> str:
    rapido = precio_moneda(texto)
    if rapido:
        return rapido
    contenido = texto
    if ACTUALIDAD.search(normalizar(texto)):
        resultados = buscar_web(texto)
        log.info("Búsqueda web: %d caracteres", len(resultados))
        if resultados:
            contenido = f"Pregunta: {texto}\n\nResultados de búsqueda web de hoy:\n{resultados}"
    r = requests.post(OLLAMA, timeout=180, json={
        "model": MODELO_IA, "stream": False, "think": False,
        "options": {"num_predict": 350},
        "messages": [{"role": "system", "content": sistema()},
                     {"role": "user", "content": contenido}]})
    r.raise_for_status()
    return limpiar_para_voz(r.json()["message"]["content"]) or "No tengo respuesta para eso."


def ejecutar(texto: str) -> bool:
    """Ejecuta la orden. Devuelve False si hay que cerrar el asistente."""
    try:
        return _ejecutar(texto)
    except Exception as e:
        log.exception("Error ejecutando la orden")
        hablar("Tuve un error con esa orden.")
        return True


def _ejecutar(texto: str) -> bool:
    import lanzador
    accion, arg = interpretar(texto)
    log.info("Orden: %r -> %s %r", texto, accion, arg)
    if accion == "nada":
        hablar("No te escuché.")
    elif accion == "modo":
        for x in lanzador.MODOS[arg]:
            lanzador._abrir(x)
        hablar("Modo trading activado.")
    elif accion == "abrir":
        res = lanzador._abrir(arg)
        hablar(f"Abriendo {arg}." if res.startswith("Abr") else f"No encontré {arg}.")
    elif accion == "pensar":
        pass
    elif accion == "cerrar":
        hablar(lanzador._cerrar(arg))
    elif accion == "cerrar_modo":
        for x in lanzador.MODOS[arg]:
            if x not in lanzador.WEBS:
                lanzador._cerrar(x)
        hablar("Cerré las apps del modo trading. Las pestañas del navegador quedan abiertas.")
    elif accion == "listar":
        hablar("Puedo abrir TradingView, Binance, Bybit, Discord, Grafana, Metricool, Whop, "
               "cualquier programa instalado, y activar el modo trading.")
    elif accion == "salir":
        hablar("Me apago. Hasta luego.")
        return False
    else:
        try:
            hablar(preguntar_ia(texto))
        except Exception as e:
            log.error("Ollama: %s", e)
            hablar("No pude conectarme con el modelo. Revisa que Ollama esté abierto.")
    return True


# ---------- modelos ----------
def cargar_wake():
    import openwakeword
    from openwakeword.model import Model
    try:
        openwakeword.utils.download_models(model_names=["hey_jarvis"])
    except Exception as e:
        log.warning("descarga wakeword: %s", e)
    return Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

def cargar_whisper():
    from faster_whisper import WhisperModel
    return WhisperModel("small", device="cpu", compute_type="int8")

def transcribir(modelo, audio_i16: np.ndarray) -> str:
    audio = audio_i16.astype(np.float32) / 32768.0
    segs, _ = modelo.transcribe(audio, language="es", beam_size=1, vad_filter=True)
    return " ".join(s.text for s in segs).strip()


# ---------- bucle principal ----------
def grabar_orden(cola) -> np.ndarray:
    trozos, silencio, inicio = [], 0.0, time.time()
    umbral = max(RUIDO * 2.5, 250.0)
    hablo = False
    while time.time() - inicio < MAX_ORDEN_S:
        b = cola.get()
        trozos.append(b)
        rms = float(np.sqrt(np.mean(b.astype(np.float32) ** 2)))
        if rms >= umbral:
            hablo = True
        if rms < umbral and (hablo or time.time() - inicio > 3.0):
            silencio += BLOQUE / RATE
            if silencio >= SILENCIO_S:
                break
        else:
            silencio = 0.0
    return np.concatenate(trozos)


def main():
    global RUIDO
    log.info("Iniciando Jarvis por voz")
    wake = cargar_wake()
    stt = cargar_whisper()
    cola = queue.Queue()

    def cb(indata, frames, t, status):
        cola.put(indata[:, 0].copy())

    with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=BLOQUE, callback=cb):
        hablar("Jarvis listo.")
        while True:
            bloque = cola.get()
            rms = float(np.sqrt(np.mean(bloque.astype(np.float32) ** 2)))
            RUIDO = 0.98 * RUIDO + 0.02 * rms
            puntajes = wake.predict(bloque)
            if max(puntajes.values()) < UMBRAL_WAKE:
                continue
            log.info("Palabra de activación detectada %s", puntajes)
            tono(True)
            audio = grabar_orden(cola)
            tono(False)
            texto = transcribir(stt, audio)
            if not texto:
                hablar("No te escuché bien, repite por favor.")
                wake.reset()
                continue
            log.info("Escuché: %r", texto)
            if not ejecutar(texto):
                break
            wake.reset()
            with cola.mutex:
                cola.queue.clear()


if __name__ == "__main__":
    if "--preparar" in sys.argv:
        print("Descargando modelos (solo la primera vez)...")
        cargar_wake(); cargar_whisper()
        print("Micrófono predeterminado:", sd.query_devices(kind="input")["name"])
        print("Listo.")
    elif "--probar" in sys.argv:
        hablar("Hola Yasmani, soy Jarvis. La voz funciona.")
    else:
        try:
            main()
        except Exception:
            log.exception("Error fatal")
            raise
