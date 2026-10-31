"""Carrusel del resumen semanal de los bots (lo usa la tarea programada de los domingos).

Lee resultados/datos/AAAA-MM/*.json (los sube el VPS en cada cierre) y genera
posts/AAAA-MM/AAAA-MM-DD_resumen_semanal_N.jpg (1080×1350, JPG).

Uso: python tools/resumen_semanal.py [AAAA-MM-DD domingo]   (por defecto: hoy en Bogotá)
Imprime en JSON: rutas de las imágenes y las cifras (para redactar el texto del post).
"""
import glob, json, os, sys
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOG = timezone(timedelta(hours=-5))
W, H = 1080, 1350
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F = lambda p, s: ImageFont.truetype(p, s)
GOLD = (245, 166, 35); WHITE = (240, 242, 247); GREY = (150, 158, 175); RED = (231, 76, 60)
GREEN = (46, 204, 113); CARD = (20, 27, 43); BG = (11, 15, 26)
PRODUCTOS = [("Sentinel Apex", "BTC"), ("Sentinel Vertex", "ETH"), ("Sentinel Solstice", "SOL")]
MESES = "ene feb mar abr may jun jul ago sep oct nov dic".split()


def pct(v):
    s = f"{v:+.2f}".replace(".", ",")
    return (s.rstrip("0").rstrip(",") if "," in s else s) + " %"


def base(n, total):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(15, 20, 33))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(15, 20, 33))
    d.text((80, 70), "SENTINEL TRADING", font=F(FB, 32), fill=GOLD)
    d.text((1000, 76), f"{n}/{total}", font=F(FR, 26), fill=GREY, anchor="ra")
    d.text((80, 1250), "@sentineltradinghq", font=F(FB, 28), fill=WHITE)
    d.text((80, 1295), "Forward test en vivo, sin capital real. No es asesoría financiera.", font=F(FR, 21), fill=GREY)
    return img, d


def main():
    fin = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=BOG) if len(sys.argv) > 1 else datetime.now(BOG)
    fin = fin.replace(hour=23, minute=59, second=59)
    ini = (fin - timedelta(days=6)).replace(hour=0, minute=0, second=0)
    ops = []
    for f in glob.glob(os.path.join(RAIZ, "resultados", "datos", "*", "*.json")):
        o = json.load(open(f))
        c = datetime.fromisoformat(o["cerrada"]).astimezone(BOG)
        if ini <= c <= fin:
            o["_c"] = c; ops.append(o)
    ops.sort(key=lambda o: o["_c"])
    g = sum(o["resultado_pct"] >= 0 for o in ops); p = len(ops) - g
    rango = f"{ini.day} {MESES[ini.month - 1]} – {fin.day} {MESES[fin.month - 1]} {fin.year}"
    carpeta = os.path.join(RAIZ, "posts", fin.strftime("%Y-%m")); os.makedirs(carpeta, exist_ok=True)
    total = 5
    rutas = []

    # 1. portada
    img, d = base(1, total)
    d.text((80, 200), "Resumen semanal", font=F(FB, 76), fill=WHITE)
    d.text((80, 295), "de los bots", font=F(FB, 76), fill=GOLD)
    d.text((80, 400), rango, font=F(FR, 34), fill=GREY)
    cajas = [("Operaciones", str(len(ops)), WHITE), ("Ganadas", str(g), GREEN), ("Perdidas", str(p), RED)]
    for i, (t, v, col) in enumerate(cajas):
        x0 = 80 + i * 313
        d.rounded_rectangle([x0, 500, x0 + 293, 700], radius=20, fill=CARD)
        d.text((x0 + 146, 560), v, font=F(FB, 80), fill=col, anchor="mm")
        d.text((x0 + 146, 650), t, font=F(FR, 28), fill=GREY, anchor="mm")
    if ops:
        mejor = max(ops, key=lambda o: o["resultado_pct"]); peor = min(ops, key=lambda o: o["resultado_pct"])
        d.rounded_rectangle([80, 740, 1000, 960], radius=20, fill=CARD)
        d.text((120, 770), "Mejor cierre", font=F(FR, 28), fill=GREY)
        d.text((120, 812), f"{mejor['bot']}  {pct(mejor['resultado_pct'])}", font=F(FB, 38), fill=GREEN if mejor["resultado_pct"] >= 0 else RED)
        d.text((120, 870), "Peor cierre", font=F(FR, 28), fill=GREY)
        d.text((120, 905), f"{peor['bot']}  {pct(peor['resultado_pct'])}", font=F(FB, 38), fill=GREEN if peor["resultado_pct"] >= 0 else RED)
    d.text((80, 1020), "Ganadas y perdidas, todas a la vista.", font=F(FB, 36), fill=WHITE)
    d.text((80, 1075), "Desliza para ver cada bot →", font=F(FR, 32), fill=GOLD)
    rutas.append(img)

    # 2-4. un slide por producto
    for n, (prod, moneda) in enumerate(PRODUCTOS, start=2):
        img, d = base(n, total)
        d.text((80, 170), prod, font=F(FB, 64), fill=GOLD)
        d.text((80, 255), f"Bots de {moneda}", font=F(FR, 34), fill=GREY)
        lista = [o for o in ops if o["producto"] == prod]
        gg = sum(o["resultado_pct"] >= 0 for o in lista)
        pp = len(lista) - gg
        d.text((1000, 275), f"{gg} ganada{'s' if gg != 1 else ''} · {pp} perdida{'s' if pp != 1 else ''}",
               font=F(FB, 30), fill=WHITE, anchor="rm")
        if not lista:
            d.rounded_rectangle([80, 340, 1000, 520], radius=20, fill=CARD)
            d.text((540, 410), "Sin cierres esta semana", font=F(FB, 42), fill=WHITE, anchor="mm")
            d.text((540, 465), "El sistema también sabe esperar.", font=F(FR, 30), fill=GREY, anchor="mm")
        for i, o in enumerate(lista[:9]):
            y = 340 + i * 92
            d.rounded_rectangle([80, y, 1000, y + 78], radius=14, fill=CARD)
            col = GREEN if o["resultado_pct"] >= 0 else RED
            d.rectangle([80, y + 10, 88, y + 68], fill=col)
            d.text((115, y + 39), o["bot"], font=F(FB, 32), fill=WHITE, anchor="lm")
            dia = f"{o['_c'].day} {MESES[o['_c'].month - 1]}"
            d.text((690, y + 39), dia, font=F(FR, 26), fill=GREY, anchor="rm")
            d.text((975, y + 39), pct(o["resultado_pct"]), font=F(FB, 36), fill=col, anchor="rm")
        if len(lista) > 9:
            d.text((540, 1180), f"y {len(lista) - 9} cierres más", font=F(FR, 28), fill=GREY, anchor="mm")
        d.text((80, 1205), "Resultado de cada operación sobre el margen.", font=F(FR, 24), fill=GREY)
        rutas.append(img)

    # 5. cierre
    img, d = base(5, total)
    d.text((80, 230), "Así se ve operar", font=F(FB, 70), fill=WHITE)
    d.text((80, 320), "con un sistema", font=F(FB, 70), fill=GOLD)
    for i, l in enumerate(["Hay semanas buenas y semanas malas.", "Lo que no cambia es la disciplina:",
                           "riesgo definido antes de entrar,", "sin pánico y sin FOMO."]):
        d.text((80, 470 + i * 60), l, font=F(FR, 38), fill=WHITE)
    d.rounded_rectangle([80, 800, 1000, 980], radius=20, fill=CARD)
    d.text((540, 860), "Sigue cada cierre en vivo", font=F(FB, 40), fill=GOLD, anchor="mm")
    d.text((540, 925), "Comunidad gratis en Discord: link en la bio", font=F(FR, 32), fill=WHITE, anchor="mm")
    rutas.append(img)

    salida = []
    for i, im in enumerate(rutas, 1):
        r = os.path.join(carpeta, f"{fin:%Y-%m-%d}_resumen_semanal_{i}.jpg"); im.save(r, quality=92)
        salida.append(os.path.relpath(r, RAIZ))
    resumen = dict(rango=rango, operaciones=len(ops), ganadas=g, perdidas=p, imagenes=salida,
                   por_producto={prod: [dict(bot=o["bot"], resultado_pct=o["resultado_pct"]) for o in ops if o["producto"] == prod]
                                 for prod, _ in PRODUCTOS})
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
