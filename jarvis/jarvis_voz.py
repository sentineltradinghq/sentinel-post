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
UMBRAL_WAKE = 0.5          # sensibilidad de "Hey Jarvis" (0-1; más alto = más estricto)
RATE, BLOQUE = 16000, 1280  # 80 ms por bloque
MAX_ORDEN_S, SILENCIO_S = 8, 1.0

SISTEMA = ("Eres Jarvis, el asistente de voz de Yasmani (Sentinel Trading). "
           "Responde SIEMPRE en español, en 1 a 3 frases cortas, sin listas, "
           "sin markdown ni emojis, porque tu respuesta se leerá en voz alta.")


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
    if "modo" in n and ("trading" in n or "trade" in n or "treiding" in n):
        return ("modo", "trading")
    if re.search(r"\b(apagate|detente|cierra el asistente|apaga el asistente)\b", n):
        return ("salir", "")
    if re.search(r"que (apps|aplicaciones|programas) (puedes|sabes) abrir|lista de (apps|aplicaciones)", n):
        return ("listar", "")
    m = re.search(r"\b(abre|abrir|abreme|abri|ejecuta|lanza|inicia)\b\s+(.*)", n)
    if m:
        nombre = re.sub(r"^(el|la|los|las|mi|a)\s+", "", m.group(2)).strip()
        nombre = re.sub(r"^(app|aplicacion|programa|pagina|web)\s+(de\s+)?", "", nombre).strip()
        nombre = re.sub(r"\s+(por favor|porfa)$", "", nombre)
        if nombre:
            return ("abrir", nombre)
    return ("preguntar", texto)


def preguntar_ia(texto: str) -> str:
    r = requests.post(OLLAMA, timeout=120, json={
        "model": MODELO_IA, "stream": False, "think": False,
        "options": {"num_predict": 220},
        "messages": [{"role": "system", "content": SISTEMA},
                     {"role": "user", "content": texto}]})
    r.raise_for_status()
    return limpiar_para_voz(r.json()["message"]["content"]) or "No tengo respuesta para eso."


def ejecutar(texto: str) -> bool:
    """Ejecuta la orden. Devuelve False si hay que cerrar el asistente."""
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
    umbral = None
    while time.time() - inicio < MAX_ORDEN_S:
        b = cola.get()
        trozos.append(b)
        rms = float(np.sqrt(np.mean(b.astype(np.float32) ** 2)))
        if umbral is None:
            umbral = max(rms * 2.5, 300.0)   # nivel de ruido inicial
        if rms < umbral and time.time() - inicio > 1.0:
            silencio += BLOQUE / RATE
            if silencio >= SILENCIO_S:
                break
        else:
            silencio = 0.0
    return np.concatenate(trozos)


def main():
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
            puntajes = wake.predict(bloque)
            if max(puntajes.values()) < UMBRAL_WAKE:
                continue
            log.info("Palabra de activación detectada %s", puntajes)
            tono(True)
            with cola.mutex:
                cola.queue.clear()
            audio = grabar_orden(cola)
            tono(False)
            texto = transcribir(stt, audio)
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
