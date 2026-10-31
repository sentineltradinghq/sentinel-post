#!/usr/bin/env python3
"""Sentinel Trading — tarjeta de cada operación CERRADA de los bots.

Corre en el VPS cada 5 minutos (cron). Por cada cierre nuevo:
  1. Dibuja la tarjeta (velas reales + caja de posición simbólica + resultado en %).
  2. La manda al webhook de Discord.
  3. Sube la imagen y sus datos al repo de GitHub (para el resumen semanal).

Nunca publica entradas, solo cierres. Nunca muestra USDT, parámetros ni motivo de salida.

Uso:
  publicar_cierres.py            → publica los cierres nuevos
  publicar_cierres.py --init     → marca todos los cierres existentes como ya publicados
  publicar_cierres.py --prueba   → manda a Discord la tarjeta del último cierre (sin GitHub, sin marcar)
"""
import base64, json, os, sqlite3, sys, time, traceback
from datetime import datetime, timedelta, timezone

import requests
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FREQ = os.environ.get("FREQTRADE_DIR", "/root/freqtrade")
ESTADO = os.path.join(BASE, "estado.json")
SALIDA = os.path.join(BASE, "tarjetas")
REPO = "sentineltradinghq/sentinel-post"
BOGOTA = timezone(timedelta(hours=-5))
MAX_ANTIGUEDAD_H = 48       # si se pierde el estado, no inunda Discord con cierres viejos

# Los 10 bots activos: config → (moneda, nombre visible, producto)
BOTS = {
    "config15m.json":                     ("BTC", "BTC 15m Long",       "Sentinel Apex"),
    "config15mshort.json":                ("BTC", "BTC 15m Short",      "Sentinel Apex"),
    "config5m.json":                      ("BTC", "BTC 5m Long",        "Sentinel Apex"),
    "configbybit5mshort.json":            ("BTC", "BTC 5m Short",       "Sentinel Apex"),
    "config_btc15mlong_usdc_live.json":   ("BTC", "BTC 15m Long USDC",  "Sentinel Apex"),
    "config_btc15mshort_usdc_live.json":  ("BTC", "BTC 15m Short USDC", "Sentinel Apex"),
    "config_eth15m_long_live.json":       ("ETH", "ETH 15m Long",       "Sentinel Vertex"),
    "config_eth15mshort_live.json":       ("ETH", "ETH 15m Short",      "Sentinel Vertex"),
    "config_sol15mlong_binance_live.json": ("SOL", "SOL 15m Long",      "Sentinel Solstice"),
    "config_sol15mshort_bybit_live.json": ("SOL", "SOL 15m Short",      "Sentinel Solstice"),
}

# ---------------------------------------------------------------- utilidades
def log(*a):
    print(datetime.now(BOGOTA).strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def cargar_env():
    ruta = os.path.join(BASE, "config.env")
    if os.path.exists(ruta):
        for linea in open(ruta):
            if "=" in linea and not linea.strip().startswith("#"):
                k, v = linea.strip().split("=", 1)
                os.environ.setdefault(k, v.strip().strip('"'))


def leer_estado():
    try:
        return json.load(open(ESTADO))
    except Exception:
        return {}


def guardar_estado(e):
    tmp = ESTADO + ".tmp"
    json.dump(e, open(tmp, "w"), indent=1)
    os.replace(tmp, ESTADO)


def fecha(s):
    s = str(s).replace("T", " ").split("+")[0]
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise ValueError(s)


def bots():
    """Lee cada config y devuelve los bots con base de datos existente."""
    lista = []
    for archivo, (moneda, nombre, producto) in BOTS.items():
        ruta = os.path.join(FREQ, "user_data", archivo)
        try:
            c = json.load(open(ruta))
        except Exception as e:
            log("no pude leer", archivo, e); continue
        db = c.get("db_url") or ("sqlite:///tradesv3.dryrun.sqlite" if c.get("dry_run") else "sqlite:///tradesv3.sqlite")
        db = db.replace("sqlite:///", "")
        if not os.path.isabs(db):
            db = os.path.join(FREQ, db)
        if not os.path.exists(db):
            continue
        lista.append(dict(config=archivo, moneda=moneda, nombre=nombre, producto=producto, db=db,
                          exchange=c.get("exchange", {}).get("name", "binance"), timeframe=c.get("timeframe")))
    return lista


def cierres(bot):
    con = sqlite3.connect(f"file:{bot['db']}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cols = {r[1] for r in con.execute("pragma table_info(trades)")}
    tf = "timeframe" if "timeframe" in cols else "NULL as timeframe"
    filas = con.execute(f"""select id, pair, is_short, open_rate, close_rate, close_profit, leverage,
                            open_date, close_date, {tf} from trades
                            where is_open=0 and close_date is not null and close_rate is not null
                            order by close_date""").fetchall()
    con.close()
    out = []
    for f in filas:
        d = dict(f)
        d["open_date"], d["close_date"] = fecha(d["open_date"]), fecha(d["close_date"])
        d["timeframe"] = bot["timeframe"] or (f"{d['timeframe']}m" if str(d["timeframe"]).isdigit() else d["timeframe"]) or "15m"
        d["clave"] = f"{bot['config']}|{d['id']}"
        out.append(d)
    return out


# ---------------------------------------------------------------- velas
TF_MIN = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "4h": 240, "1d": 1440}


def velas(bot, t):
    """Velas reales del exchange alrededor del trade (máx ~110)."""
    import ccxt
    tf = t["timeframe"] if t["timeframe"] in TF_MIN else "15m"
    span = (t["close_date"] - t["open_date"]).total_seconds() / 60
    for cand in ["5m", "15m", "1h", "4h", "1d"]:
        if TF_MIN[cand] >= TF_MIN[tf] and span / TF_MIN[cand] <= 70:
            tf = cand; break
    else:
        tf = "1d"
    m = TF_MIN[tf]
    antes, despues = 25, 8
    n = int(span / m) + antes + despues + 2
    desde = int((t["open_date"] - timedelta(minutes=m * antes)).timestamp() * 1000)
    nombre = "bybit" if "bybit" in bot["exchange"].lower() else "binance"
    ex = getattr(ccxt, nombre)({"options": {"defaultType": "future" if nombre == "binance" else "linear"}, "enableRateLimit": True})
    datos = ex.fetch_ohlcv(t["pair"], tf, since=desde, limit=min(n, 300))
    return tf, datos


# ---------------------------------------------------------------- dibujo
W, H = 1080, 1350
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_f = {}
def F(p, s):
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]
GOLD = (245, 166, 35); WHITE = (240, 242, 247); GREY = (150, 158, 175); RED = (231, 76, 60)
GREEN = (46, 204, 113); CARD = (20, 27, 43); BG = (11, 15, 26)


def precio_txt(v):
    dec = 0 if v >= 1000 else 2 if v >= 10 else 4
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct_txt(p):
    s = f"{p * 100:+.2f}".replace(".", ",")
    return s.rstrip("0").rstrip(",") + " %" if "," in s else s + " %"


def duracion_txt(td):
    m = int(td.total_seconds() // 60)
    d, h, mm = m // 1440, (m % 1440) // 60, m % 60
    if d: return f"{d} día{'s' if d > 1 else ''} {h} h"
    if h: return f"{h} h {mm} min"
    return f"{mm} min"


def tarjeta(bot, t, ohlcv, tf, balance_mes, ruta):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(15, 20, 33))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(15, 20, 33))
    gano = t["close_profit"] >= 0
    lado = "SHORT" if t["is_short"] else "LONG"

    d.text((80, 60), "SENTINEL TRADING", font=F(FB, 30), fill=GOLD)
    d.text((80, 102), "Operación cerrada", font=F(FR, 26), fill=GREY)
    d.rounded_rectangle([760, 56, 1000, 102], radius=20, fill=(15, 50, 35))
    d.ellipse([792, 72, 806, 86], fill=GREEN)
    d.text((892, 79), "EN VIVO", font=F(FB, 22), fill=GREEN, anchor="mm")
    par = t["pair"].split(":")[0]
    d.text((80, 160), f"{bot['producto']} · {par} · {t['timeframe']}", font=F(FB, 34), fill=WHITE)
    col_lado = RED if t["is_short"] else GREEN
    d.rounded_rectangle([80, 210, 230, 252], radius=10, fill=(90, 30, 30) if t["is_short"] else (15, 60, 40))
    d.text((155, 231), lado, font=F(FB, 24), fill=col_lado, anchor="mm")
    lev = t.get("leverage") or 1
    d.text((250, 214), f"Apalancamiento {lev:g}x", font=F(FR, 28), fill=GREY)

    gx0, gx1, gy0, gy1 = 80, 960, 300, 860
    d.rounded_rectangle([gx0 - 10, gy0 - 10, gx1 + 110, gy1 + 10], radius=16, fill=(14, 19, 32))
    entrada, salida = t["open_rate"], t["close_rate"]
    if ohlcv:
        m = TF_MIN[tf] * 60000
        t_ent = int(t["open_date"].timestamp() * 1000); t_sal = int(t["close_date"].timestamp() * 1000)
        ie = max(0, min(len(ohlcv) - 1, min(range(len(ohlcv)), key=lambda i: abs(ohlcv[i][0] + m / 2 - t_ent))))
        isal = max(ie, min(range(len(ohlcv)), key=lambda i: abs(ohlcv[i][0] + m / 2 - t_sal)))
        n = len(ohlcv)
        lo = min(min(c[3] for c in ohlcv), entrada, salida); hi = max(max(c[2] for c in ohlcv), entrada, salida)
    else:
        n, ie, isal = 40, 12, 32
        lo, hi = min(entrada, salida), max(entrada, salida)
    dist = abs(salida - entrada) or entrada * 0.01
    lo = min(lo, entrada - dist * 1.15); hi = max(hi, entrada + dist * 1.15)
    pad = (hi - lo) * 0.08; lo -= pad; hi += pad
    sy = lambda v: gy1 - (v - lo) / (hi - lo) * (gy1 - gy0)
    cw = (gx1 - gx0) / n; cx = lambda i: gx0 + i * cw + cw / 2
    xa, xb = cx(ie), cx(isal) + max(0, 12 - (cx(isal) - cx(ie)))
    alto = abs(sy(entrada) - sy(salida)) or 20
    favor_arriba = not t["is_short"]          # zona de ganancia: arriba en long, abajo en short (simbólica y pareja)
    yg = (sy(entrada) - alto, sy(entrada)) if favor_arriba else (sy(entrada), sy(entrada) + alto)
    yr = (sy(entrada), sy(entrada) + alto) if favor_arriba else (sy(entrada) - alto, sy(entrada))
    d.rectangle([xa, yg[0], xb, yg[1]], fill=(46, 204, 113, 55))
    d.rectangle([xa, yr[0], xb, yr[1]], fill=(231, 76, 60, 55))
    d.line([(xa, sy(entrada)), (xb, sy(entrada))], fill=WHITE, width=2)
    if ohlcv:
        for i, (_, o, h, l, c, _v) in enumerate(ohlcv):
            col = GREEN if c >= o else RED; x = cx(i)
            d.line([(x, sy(h)), (x, sy(l))], fill=col, width=2)
            d.rectangle([x - cw * 0.32, sy(max(o, c)), x + cw * 0.32, sy(min(o, c))], fill=col)
    d.polygon([(xa, sy(entrada) - 14), (xa - 12, sy(entrada) - 34), (xa + 12, sy(entrada) - 34)], fill=GOLD)
    d.text((xa - 8, sy(entrada) - 64), "Entrada", font=F(FB, 22), fill=GOLD, anchor="ra")
    cs = GREEN if gano else RED
    d.ellipse([xb - 11, sy(salida) - 11, xb + 11, sy(salida) + 11], fill=cs, outline=WHITE, width=3)
    ly = sy(salida) - 58 if sy(salida) > sy(entrada) else sy(salida) + 22
    ly = max(gy0 - 5, min(gy1 - 30, ly))
    d.rounded_rectangle([xb - 46, ly, xb + 46, ly + 34], radius=8, fill=(11, 15, 26, 230), outline=cs, width=2)
    d.text((xb, ly + 17), "Salida", font=F(FB, 20), fill=cs, anchor="mm")
    for v in (lo + (hi - lo) * 0.1, (lo + hi) / 2, hi - (hi - lo) * 0.1):
        d.text((gx1 + 100, sy(v)), precio_txt(v), font=F(FR, 18), fill=GREY, anchor="rm")
    if ohlcv:
        d.text((gx0, gy1 + 22), f"Velas de {tf}", font=F(FR, 18), fill=GREY)

    d.rounded_rectangle([80, 900, 1000, 1060], radius=20, fill=CARD)
    d.text((120, 920), "Resultado", font=F(FR, 26), fill=GREY)
    d.text((120, 958), pct_txt(t["close_profit"]), font=F(FB, 72), fill=cs)
    d.text((960, 935), "Sobre el margen", font=F(FB, 30), fill=WHITE, anchor="ra")
    d.text((960, 985), "Duración: " + duracion_txt(t["close_date"] - t["open_date"]), font=F(FR, 26), fill=GREY, anchor="ra")
    cierre = t["close_date"].astimezone(BOGOTA)
    d.text((960, 1022), "Cerró: " + cierre.strftime("%d/%m %I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m."),
           font=F(FR, 26), fill=GREY, anchor="ra")
    d.text((120, 1090), f"Entrada {precio_txt(entrada)}   →   Salida {precio_txt(salida)}", font=F(FB, 30), fill=WHITE)
    g, p = balance_mes
    d.text((120, 1140), f"Este mes en {bot['moneda']}: {g} ganada{'s' if g != 1 else ''} · {p} perdida{'s' if p != 1 else ''}",
           font=F(FR, 28), fill=GREY)
    d.text((80, 1250), "@sentineltradinghq", font=F(FB, 28), fill=WHITE)
    d.text((80, 1295), "Forward test en vivo, sin capital real. No es asesoría financiera.", font=F(FR, 21), fill=GREY)
    img.save(ruta, quality=95, subsampling=0)          # JPG nítido (GitHub / redes)
    img.save(ruta[:-4] + ".png", optimize=True)          # PNG sin pérdida (Discord)


# ---------------------------------------------------------------- envíos
def a_discord(ruta, bot, t, prueba=False):
    url = os.environ.get("DISCORD_WEBHOOK", "")
    if not url:
        raise RuntimeError("falta DISCORD_WEBHOOK en config.env")
    emoji = "🟢" if t["close_profit"] >= 0 else "🔴"
    texto = (f"{emoji} **{bot['producto']} · {bot['nombre']}** cerró **{pct_txt(t['close_profit'])}** sobre el margen\n"
             f"-# Forward test en vivo, sin capital real. No es asesoría financiera.")
    if prueba:
        texto = "🧪 Prueba de instalación (último cierre registrado)\n" + texto
    png = ruta[:-4] + ".png"
    archivo, tipo = (png, "image/png") if os.path.exists(png) else (ruta, "image/jpeg")
    with open(archivo, "rb") as f:
        r = requests.post(url, data={"payload_json": json.dumps({"content": texto, "username": "Sentinel Resultados"})},
                          files={"files[0]": (os.path.basename(archivo), f, tipo)}, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Discord {r.status_code}: {r.text[:200]}")


def a_github(ruta_repo, contenido_bytes, mensaje):
    tok = os.environ.get("GITHUB_TOKEN", "")
    if not tok:
        raise RuntimeError("falta GITHUB_TOKEN en config.env")
    api = f"https://api.github.com/repos/{REPO}/contents/{ruta_repo}"
    h = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
    cuerpo = {"message": mensaje, "content": base64.b64encode(contenido_bytes).decode(), "branch": "main",
              "committer": {"name": "Sentinel VPS", "email": "noreply@sentineltrading.local"}}
    r = requests.get(api, headers=h, timeout=30)
    if r.status_code == 200:
        cuerpo["sha"] = r.json()["sha"]
    r = requests.put(api, headers=h, json=cuerpo, timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"GitHub {r.status_code}: {r.text[:200]}")


def balance(todos, moneda, cuando):
    g = p = 0
    for bot, t in todos:
        c = t["close_date"].astimezone(BOGOTA)
        if bot["moneda"] == moneda and c.year == cuando.year and c.month == cuando.month:
            g += t["close_profit"] >= 0; p += t["close_profit"] < 0
    return g, p


def procesar(bot, t, todos, prueba=False):
    os.makedirs(SALIDA, exist_ok=True)
    cierre = t["close_date"].astimezone(BOGOTA)
    nombre = f"{cierre:%Y-%m-%d_%H%M}_{bot['nombre'].lower().replace(' ', '_')}_{t['id']}"
    ruta = os.path.join(SALIDA, nombre + ".jpg")
    try:
        tf, ohlcv = velas(bot, t)
    except Exception as e:
        log("sin velas para", bot["nombre"], e); tf, ohlcv = t["timeframe"], []
    tarjeta(bot, t, ohlcv, tf, balance(todos, bot["moneda"], cierre), ruta)
    return nombre, ruta


def main():
    cargar_env()
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    estado = leer_estado()
    todos = []
    for bot in bots():
        try:
            todos += [(bot, t) for t in cierres(bot)]
        except Exception as e:
            log("error leyendo", bot["db"], e)
    todos.sort(key=lambda x: x[1]["close_date"])

    if modo == "--init":
        for bot, t in todos:
            estado[t["clave"]] = {"discord": True, "github": True, "init": True}
        guardar_estado(estado)
        log(f"init: {len(todos)} cierres existentes marcados como publicados en {len(bots())} bots")
        return
    if modo == "--prueba":
        if not todos:
            log("no hay cierres para probar"); return
        bot, t = todos[-1]
        _, ruta = procesar(bot, t, todos, prueba=True)
        a_discord(ruta, bot, t, prueba=True)
        log("prueba enviada a Discord:", ruta)
        return

    if modo == "--anteriores":
        # publica los N cierres anteriores al último (Discord + GitHub);
        # el último solo se sube a GitHub, porque ya llegó a Discord como tarjeta de prueba
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        if todos:
            for bot, t in todos[-(n + 1):-1]:
                estado[t["clave"]] = {"forzar": True}
            estado[todos[-1][1]["clave"]] = {"discord": True, "forzar": True}
            guardar_estado(estado)
            log(f"se publicarán {min(n, len(todos) - 1)} cierres anteriores y el último se sube a GitHub")

    ahora = datetime.now(timezone.utc)
    for bot, t in todos:
        e = estado.get(t["clave"], {})
        if e.get("discord") and e.get("github"):
            continue
        if not e and ahora - t["close_date"] > timedelta(hours=MAX_ANTIGUEDAD_H):
            estado[t["clave"]] = {"discord": True, "github": True, "viejo": True}; continue
        try:
            nombre, ruta = procesar(bot, t, todos)
            if not e.get("discord"):
                a_discord(ruta, bot, t); e["discord"] = True
                log("Discord ✓", bot["nombre"], pct_txt(t["close_profit"]))
            if not e.get("github"):
                mes = t["close_date"].astimezone(BOGOTA).strftime("%Y-%m")
                datos = dict(bot=bot["nombre"], producto=bot["producto"], moneda=bot["moneda"], par=t["pair"],
                             lado="short" if t["is_short"] else "long", timeframe=t["timeframe"],
                             apalancamiento=t.get("leverage") or 1, resultado_pct=round(t["close_profit"] * 100, 3),
                             entrada=t["open_rate"], salida=t["close_rate"],
                             abierta=t["open_date"].isoformat(), cerrada=t["close_date"].isoformat(),
                             imagen=f"resultados/imagenes/{mes}/{nombre}.jpg")
                a_github(f"resultados/imagenes/{mes}/{nombre}.jpg", open(ruta, "rb").read(), f"Cierre {bot['nombre']} {pct_txt(t['close_profit'])}")
                a_github(f"resultados/datos/{mes}/{nombre}.json", json.dumps(datos, ensure_ascii=False, indent=1).encode(), f"Datos cierre {bot['nombre']}")
                e["github"] = True
                log("GitHub ✓", nombre)
        except Exception as ex:
            log("error con", t["clave"], ex); traceback.print_exc()
        estado[t["clave"]] = e
        guardar_estado(estado)
        time.sleep(1)
    guardar_estado(estado)


if __name__ == "__main__":
    main()
