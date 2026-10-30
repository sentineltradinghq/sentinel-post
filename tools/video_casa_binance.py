"""Reel: la casa Binance, el ladrón, el derrumbe, el pedo de Bitcoin y la vela roja."""
import math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tts"))
from voz import hablar, SR

random.seed(7); np.random.seed(7)
OUT = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(OUT, "frames_casa"); os.makedirs(FR, exist_ok=True)
W, H, FPS = 1080, 1920, 30
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
GOLD = (245, 166, 35); WHITE = (240, 242, 247); GREY = (150, 158, 175); RED = (231, 76, 60); GREEN = (46, 204, 113)
SUELO = 1450
VOZ = os.environ.get("VOZ", "ef_dora")
VEL = float(os.environ.get("VEL", "1.0"))
AGUDO = float(os.environ.get("AGUDO", "1.35"))  # >1 = más rápida y más aguda (voz de niño/caricatura)
NOMBRE = os.environ.get("NOMBRE", "casa_binance")

# ---------------- audio: guion ----------------
LINEAS = {
    "s1": "Esta es la casa donde millones guardan sus criptomonedas.",
    "s2": "Pero un ladrón encontró un hueco en la seguridad.",
    "s3": "Entró, tomó lo que pudo, y salió corriendo por la puerta.",
    "s4": "Y cuando se pierde la confianza, todo se viene abajo.",
    "s5": "Hasta Bitcoin se asustó.",
    "s6": "Protege tus fondos. No guardes todo en un solo exchange.",
    "s7": "Síguenos para más.",
}
def agudizar(a, k):
    n = int(len(a) / k)
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
voces = {k: agudizar(hablar(v, VOZ, VEL)[: -int(SR * 0.25)], AGUDO) for k, v in LINEAS.items()}
dur = {k: len(a) / SR for k, a in voces.items()}

def ruido(n): return np.random.uniform(-1, 1, n)
def suave(x, k): return np.convolve(x, np.ones(k) / k, mode="same")

def sfx_pedo(d=1.0):
    """Pedo delgado/agudo: chillido que tiembla y sube un poco al final."""
    t = np.arange(int(SR * d)) / SR
    f = 260 + 70 * np.sin(2 * np.pi * 6 * t) + 90 * (t / d) ** 2 + 15 * suave(ruido(len(t)), 300) * 6
    fase = 2 * np.pi * np.cumsum(f) / SR
    onda = np.sin(fase) + 0.35 * np.sign(np.sin(fase))
    onda = onda * (0.65 + 0.35 * np.sin(2 * np.pi * 31 * t)) + 0.08 * ruido(len(t))
    env = np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.2)
    return suave(onda, 3) * env * 0.5

def sfx_fum(d=0.45):
    t = np.arange(int(SR * d)) / SR
    n = suave(ruido(len(t)), 3) * (t / d) ** 2
    return n * 0.6

def sfx_golpe(d=0.6):
    t = np.arange(int(SR * d)) / SR
    return (np.sin(2 * np.pi * 55 * t) * 0.9 + suave(ruido(len(t)), 30) * 2) * np.exp(-t * 9) * 0.9

def sfx_derrumbe(d=1.8):
    t = np.arange(int(SR * d)) / SR
    n = suave(ruido(len(t)), 60) * 6
    return n * np.minimum(1, t / 0.1) * np.exp(-t * 1.6) * 0.8

# línea de tiempo (segundos)
T = {}
c = 0.4
for k in ["s1", "s2", "s3", "s4"]:
    T[k] = c; c += dur[k] + 0.35
T["derrumbe"] = T["s4"] + 0.7
T["moneda"] = c                     # aparece Bitcoin flotando
T["pedo"] = c + 0.7; c = T["pedo"] + 1.1
T["s5"] = c; c += dur["s5"] + 0.15
T["fum"] = c; c += 0.45             # la vela roja baja de golpe
T["golpe"] = c; c += 1.0
T["s6"] = c; c += dur["s6"] + 0.4
T["s7"] = c; c += dur["s7"] + 0.9
TOTAL = c

pista = np.zeros(int(SR * (TOTAL + 1)))
def mezclar(a, t, g=1.0):
    i = int(t * SR); pista[i:i + len(a)] += a[: len(pista) - i] * g
for k in LINEAS:
    v = voces[k]; mezclar(v / max(1e-6, np.abs(v).max()) * 0.85, T[k])
mezclar(sfx_derrumbe(), T["derrumbe"], 0.8)
mezclar(sfx_pedo(), T["pedo"], 0.9)
mezclar(sfx_fum(), T["fum"], 0.8)
mezclar(sfx_golpe(), T["golpe"], 1.0)
pista = np.clip(pista[: int(SR * TOTAL)], -1, 1)
with wave.open(os.path.join(OUT, NOMBRE + "_audio.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((pista * 32767).astype(np.int16).tobytes())

# ---------------- dibujo ----------------
def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x

fondo = Image.new("RGB", (W, H))
fd = ImageDraw.Draw(fondo)
for y in range(H):
    k = min(1, y / SUELO)
    fd.line([(0, y), (W, y)], fill=(int(lerp(8, 28, k)), int(lerp(11, 36, k)), int(lerp(22, 62, k))))
for _ in range(90):
    x, y = random.randint(0, W), random.randint(430, 1100); r = random.choice([1, 1, 2])
    fd.ellipse([x - r, y - r, x + r, y + r], fill=(200, 205, 220))
fd.ellipse([840, 470, 940, 570], fill=(235, 232, 210))
fd.ellipse([815, 455, 915, 555], fill=(14, 19, 34))
fd.rectangle([0, SUELO, W, H], fill=(18, 22, 34))
fd.line([(0, SUELO), (W, SUELO)], fill=(60, 70, 95), width=4)

CX0, CX1, CY0 = 170, 910, 870         # cuerpo de la casa
TECHO = 600
HUECO = (735, 1310, 860, SUELO)
PUERTA = (478, 1250, 602, SUELO)

def casa(hueco=0.0, puerta=0.0, grietas=0.0):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.polygon([(CX0 - 40, CY0 + 5), (540, TECHO), (CX1 + 40, CY0 + 5)], fill=(30, 36, 54), outline=GOLD)
    d.line([(CX0 - 40, CY0 + 5), (540, TECHO), (CX1 + 40, CY0 + 5)], fill=GOLD, width=6)
    d.rectangle([CX0, CY0, CX1, SUELO], fill=(44, 54, 80), outline=(70, 82, 112), width=4)
    for y in range(CY0 + 40, SUELO, 40):            # ladrillos sutiles
        d.line([(CX0 + 4, y), (CX1 - 4, y)], fill=(50, 61, 89), width=2)
    d.rounded_rectangle([300, 935, 780, 1060], 14, fill=(11, 15, 26), outline=GOLD, width=5)
    d.text((540, 998), "BINANCE", font=F(B, 92), fill=GOLD, anchor="mm")
    for x0 in (230, 700):
        d.rectangle([x0, 1110, x0 + 150, 1220], fill=(250, 214, 120), outline=(30, 36, 54), width=6)
        d.line([(x0 + 75, 1110), (x0 + 75, 1220)], fill=(30, 36, 54), width=5)
        d.line([(x0, 1165), (x0 + 150, 1165)], fill=(30, 36, 54), width=5)
    x0, y0, x1, y1 = PUERTA
    if puerta <= 0:
        d.rectangle(PUERTA, fill=(96, 62, 38), outline=(60, 38, 22), width=5)
        d.ellipse([x1 - 30, 1345, x1 - 16, 1359], fill=GOLD)
    else:
        d.rectangle(PUERTA, fill=(6, 8, 14))
        ancho = (x1 - x0) * (1 - 0.8 * ease(puerta))
        d.polygon([(x0, y0), (x0 + ancho, y0 + 18 * ease(puerta)), (x0 + ancho, y1 - 18 * ease(puerta)), (x0, y1)],
                  fill=(96, 62, 38), outline=(60, 38, 22))
    if hueco > 0:
        hx0, hy0, hx1, hy1 = HUECO; cx = (hx0 + hx1) / 2; e = ease(hueco)
        pts = []
        for i in range(15):
            a = math.pi + math.pi * i / 14
            rr = (1 + 0.18 * math.sin(i * 2.7)) * e
            pts.append((cx + math.cos(a) * (hx1 - hx0) / 2 * rr, hy1 + math.sin(a) * (hy1 - hy0) * rr))
        d.polygon(pts, fill=(5, 6, 10))
        d.line(pts, fill=(170, 178, 196), width=6)
        rnd = random.Random(5)
        for i in range(int(7 * e)):
            bx = rnd.uniform(hx0 - 50, hx1 + 50); by = SUELO - rnd.uniform(8, 22)
            d.rectangle([bx, by, bx + 30, by + 15], fill=(120, 84, 60), outline=(70, 46, 30), width=2)
    if grietas > 0:
        rnd = random.Random(3)
        for _ in range(7):
            x, y = rnd.randint(CX0 + 40, CX1 - 40), CY0 + 10
            for _ in range(int(9 * grietas)):
                nx, ny = x + rnd.randint(-45, 45), y + rnd.randint(30, 75)
                d.line([(x, y), (nx, ny)], fill=(8, 10, 16), width=5); x, y = nx, ny
    return L

def ladron(L, x, fase, mira=1, bolsa=False, alfa=255):
    d = ImageDraw.Draw(L); y = SUELO
    osc = math.sin(fase)
    oscuro = (24, 24, 32, alfa); piel = (226, 176, 130, alfa); blanco = (238, 238, 242, alfa)
    cad = (x, y - 78)
    for s in (1, -1):
        a = osc * 0.6 * s
        d.line([cad, (x + math.sin(a) * 72 * mira, y - 6 + abs(math.cos(a)) * 0)], fill=oscuro, width=16)
    if bolsa:
        bx, by = x - 50 * mira, y - 165 + abs(osc) * 6
        d.ellipse([bx - 42, by - 42, bx + 42, by + 42], fill=(188, 128, 26, alfa), outline=(120, 80, 14, alfa), width=4)
        d.text((bx, by + 4), "$", font=F(B, 50), fill=(255, 238, 180, alfa), anchor="mm")
    d.rectangle([x - 28, y - 152, x + 28, y - 76], fill=blanco)
    for yy in range(y - 146, y - 76, 18):
        d.rectangle([x - 28, yy, x + 28, yy + 9], fill=oscuro)
    for s in (1, -1):
        a = -osc * 0.8 * s
        d.line([(x, y - 140), (x + math.sin(a) * 60 * mira, y - 140 + math.cos(a) * 52)], fill=oscuro, width=13)
    d.ellipse([x - 27, y - 210, x + 27, y - 156], fill=piel)
    d.chord([x - 29, y - 216, x + 29, y - 166], 180, 360, fill=oscuro)
    d.rectangle([x - 28, y - 192, x + 28, y - 178], fill=oscuro)
    for s in (-10, 10):
        d.ellipse([x + s + 6 * mira - 4, y - 189, x + s + 6 * mira + 4, y - 181], fill=blanco)

def moneda(L, x, y, susto=0.0, ang=0):
    m = Image.new("RGBA", (260, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(m); c = 130
    d.ellipse([c - 95, c - 95, c + 95, c + 95], fill=(208, 130, 18), outline=(150, 90, 10), width=6)
    d.ellipse([c - 78, c - 78, c + 78, c + 78], fill=GOLD)
    d.text((c, c + 18), "B", font=F(B, 96), fill=(255, 246, 220), anchor="mm")
    for xx in (c - 12, c + 8):
        d.rectangle([xx, c - 44, xx + 7, c - 26], fill=(255, 246, 220))
        d.rectangle([xx, c + 58, xx + 7, c + 72], fill=(255, 246, 220))
    r = 15 + 5 * susto
    for ex in (c - 34, c + 34):
        d.ellipse([ex - r, c - 64 - r, ex + r, c - 64 + r], fill=WHITE, outline=(60, 40, 10), width=3)
        d.ellipse([ex - 6, c - 64 - 6 + 4 * susto, ex + 6, c - 64 + 6 + 4 * susto], fill=(20, 20, 26))
    if susto > 0.3:
        d.ellipse([c + 70, c - 70, c + 88, c - 40], fill=(120, 190, 255))
    m = m.rotate(ang, resample=Image.BICUBIC)
    L.alpha_composite(m, (int(x - 130), int(y - 130)))

# trozos para el derrumbe
CASA_FINAL = casa(hueco=1, puerta=0, grietas=1)
TROZOS = []
TAM = 92
for gy in range(TECHO, SUELO, TAM):
    for gx in range(CX0 - 45, CX1 + 45, TAM):
        t = CASA_FINAL.crop((gx, gy, gx + TAM, gy + TAM))
        if t.getbbox() is None:
            continue
        TROZOS.append(dict(img=t, x=gx, y=gy, retraso=random.uniform(0, 0.35) + (SUELO - gy) / 2600,
                           vx=random.uniform(-160, 160), giro=random.uniform(-260, 260),
                           piso=SUELO - random.uniform(0, 150)))

POLVO = [dict(x=random.uniform(CX0 - 60, CX1 + 60), r=random.uniform(40, 110), vy=random.uniform(30, 110),
              vx=random.uniform(-90, 90), retraso=random.uniform(0.2, 0.8)) for _ in range(46)]

def subtitulo(d, txt, a):
    pal = txt.split(); lin = [""]
    for p in pal:
        if len(lin[-1] + " " + p) > 26: lin.append(p)
        else: lin[-1] = (lin[-1] + " " + p).strip()
    for i, l in enumerate(lin):
        d.text((W // 2, 275 + i * 68), l, font=F(B, 56), fill=WHITE + (int(255 * a),), anchor="mm",
               stroke_width=4, stroke_fill=(0, 0, 0, int(255 * a)))

def actual(t):
    k = None
    for kk in LINEAS:
        if t >= T[kk] - 0.1 and t < T[kk] + dur[kk] + 0.3: k = kk
    return k

N = int(TOTAL * FPS)
for f in range(N):
    t = f / FPS
    img = fondo.copy().convert("RGBA"); L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sacudir = 0
    t2, t3, t4 = T["s2"], T["s3"], T["derrumbe"]

    # casa
    if t < t4 - 0.7:
        sube = ease((t - 0.1) / 1.0)
        hueco = ease((t - (t2 + dur["s2"] * 0.45)) / 0.5) if t > t2 else 0
        puerta = ease((t - t3) / 0.35) if t > t3 else 0
        cerrar = ease((t - (t3 + dur["s3"] * 0.85)) / 0.3) if t > t3 + dur["s3"] * 0.85 else 0
        cs = casa(hueco, puerta * (1 - cerrar))
        if sube < 1:
            cs = cs.crop((0, 0, W, SUELO + 4)); hh = SUELO + 4
            dy = int((1 - sube) * 900)
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tmp.alpha_composite(cs, (0, dy))
            tmp = tmp.crop((0, 0, W, SUELO + 4)); cs = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cs.alpha_composite(tmp, (0, 0))
        L.alpha_composite(cs)
    elif t < t4:
        g = ease((t - (t4 - 0.7)) / 0.6); sacudir = 10 * g
        L.alpha_composite(casa(1, 0, g))
    else:
        tt = t - t4
        for p in TROZOS:
            s = max(0, tt - p["retraso"])
            yy = p["y"] + 0.5 * 3200 * s * s
            caido = yy + TAM >= p["piso"]
            if caido:
                s_land = math.sqrt(max(0, 2 * (p["piso"] - TAM - p["y"]) / 3200)); yy = p["piso"] - TAM; s = s_land
            img_t = p["img"].rotate(p["giro"] * s, expand=True) if s > 0 else p["img"]
            L.alpha_composite(img_t, (int(p["x"] + p["vx"] * s), int(yy)))
        if tt < 0.9: sacudir = 14 * (1 - tt / 0.9)

    # ladrón
    if t2 <= t < t3:
        k = (t - t2) / (dur["s2"] + 0.35)
        destino = (HUECO[0] + HUECO[2]) / 2
        if k < 0.55:
            x = lerp(1180, destino + 40, k / 0.55); alfa = 255
        else:
            x = destino + 40 - 60 * (k - 0.55) / 0.45; alfa = int(255 * max(0, 1 - (k - 0.55) / 0.3))
        if alfa > 0: ladron(L, x, t * 12, -1, False, alfa)
    if t3 + 0.2 <= t < t3 + dur["s3"] + 0.35:
        k = (t - t3 - 0.2) / (dur["s3"] + 0.1)
        x = lerp((PUERTA[0] + PUERTA[2]) / 2, -160, ease(k) * 0.4 + k * 0.6)
        ladron(L, x, t * 20, -1, True, 255)

    # polvo
    if t >= t4:
        tt = t - t4
        P = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(P)
        for p in POLVO:
            s = tt - p["retraso"]
            if s <= 0: continue
            a = int(150 * max(0, 1 - s / 2.6))
            if a <= 0: continue
            r = p["r"] * (1 + s * 0.9); x = p["x"] + p["vx"] * s; y = SUELO - 30 - p["vy"] * s
            pd.ellipse([x - r, y - r, x + r, y + r], fill=(120, 124, 138, a))
        L.alpha_composite(P)

    # Bitcoin, pedo y vela roja
    tm, tp, tf, tg = T["moneda"], T["pedo"], T["fum"], T["golpe"]
    MX, MY = 360, 820
    if t >= tm:
        flot = math.sin(t * 3) * 10
        x, y, ang, susto = MX, MY + flot, 0, 0
        if t < tm + 0.5:
            y = MY + (1 - ease((t - tm) / 0.5)) * 700
        if tp <= t < tf:
            susto = 1; x += random.uniform(-5, 5); y += random.uniform(-4, 4)
        if t >= tf:
            s = t - tf; caer = min(1, s / 0.55)
            yfin = SUELO - 95
            y = lerp(MY, yfin, caer ** 2); ang = -90 * caer; susto = 1
            if caer >= 1:
                rb = s - 0.55; y = yfin - max(0, math.sin(rb * 9) * 40 * math.exp(-rb * 5))
        if tp <= t < tp + 1.6:        # nubes de gas
            gs = t - tp
            G = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(G)
            for i in range(13):
                s = gs - i * 0.06
                if s <= 0: continue
                r = 34 + s * 115; a = int(185 * max(0, 1 - s / 1.3))
                gx = MX - 70 - s * 160 - i * 8 + math.sin(i * 2) * 20; gy = MY + 80 + s * 40 + math.cos(i * 3) * 18
                gd.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(140, 200, 80, a))
            L.alpha_composite(G)
            if gs < 1.2:
                d = ImageDraw.Draw(L); a = int(255 * min(1, gs / 0.15) * max(0, 1 - (gs - 0.8) / 0.4))
                d.text((MX - 120, MY + 210), "¡PRRRT!", font=F(B, 70), fill=(170, 230, 90, a), anchor="mm",
                       stroke_width=5, stroke_fill=(0, 0, 0, a))
        moneda(L, x, y, susto, ang)
    if t >= tf:
        s = t - tf; k = ease(s / 0.42)
        vx, top = 760, 720
        d = ImageDraw.Draw(L)
        bot = lerp(top + 10, SUELO, k)
        d.line([(vx, top - 50), (vx, bot + 30 * k)], fill=RED, width=8)
        d.rectangle([vx - 48, top, vx + 48, bot], fill=RED)
        if s < 0.7:
            for i in range(4):
                d.line([(vx - 70 - i * 18, top + 40 * i), (vx - 70 - i * 18, bot - 60)], fill=(231, 76, 60, 90), width=4)
        if s > 0.25:
            a = int(255 * min(1, (s - 0.25) / 0.1) * max(0, 1 - (s - 1.6) / 0.5))
            sz = int(110 + 30 * max(0, 1 - (s - 0.25) / 0.2))
            d.text((780, 600), "¡FUM!", font=F(B, sz), fill=RED + (a,), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, a))
        if 0.42 <= s < 0.9: sacudir = 18 * (1 - (s - 0.42) / 0.48)

    # textos
    d = ImageDraw.Draw(L)
    d.text((80, 140), "SENTINEL TRADING", font=F(B, 40), fill=GOLD)
    k = actual(t)
    if k:
        a = min(1, (t - T[k] + 0.1) / 0.2) * min(1, (T[k] + dur[k] + 0.3 - t) / 0.2)
        subtitulo(d, LINEAS[k], max(0, a))
    if t >= T["s6"]:
        a = ease((t - T["s6"]) / 0.4)
        d.text((W // 2, 1580), "Protege tus fondos.", font=F(B, 60), fill=WHITE + (int(255 * a),), anchor="mm")
        d.text((W // 2, 1660), "No guardes todo en un solo exchange.", font=F(B, 44), fill=GREEN + (int(255 * a),), anchor="mm")
    if t >= T["s7"]:
        a = ease((t - T["s7"]) / 0.4)
        d.text((W // 2, 1770), "Síguenos: @sentineltradinghq", font=F(B, 46), fill=GOLD + (int(255 * a),), anchor="mm")
    d.text((W // 2, 1860), "Contenido educativo. No es asesoría financiera.", font=F(R, 28), fill=GREY, anchor="mm")

    img.alpha_composite(L)
    if sacudir:
        img = img.transform(img.size, Image.AFFINE, (1, 0, random.uniform(-sacudir, sacudir), 0, 1, random.uniform(-sacudir, sacudir)),
                            fillcolor=(11, 15, 26))
    img.convert("RGB").save(os.path.join(FR, f"f{f:04d}.jpg"), quality=88)

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FR, "f%04d.jpg"),
                "-i", os.path.join(OUT, NOMBRE + "_audio.wav"), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                os.path.join(OUT, NOMBRE + ".mp4")], check=True)
print("listo", round(TOTAL, 1), "s", {k: round(v, 2) for k, v in T.items()})
