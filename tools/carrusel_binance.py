from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; I="/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
F=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); RED=(231,76,60); GREEN=(46,204,113); CARD=(20,27,43); BG=(11,15,26)
TOTAL=6

def base(n, seccion):
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
    for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
    d.text((80,70),"SENTINEL TRADING",font=F(B,28),fill=GOLD)
    d.text((80,108),seccion,font=F(R,24),fill=GREY)
    d.text((1000,70),f"{n}/{TOTAL}",font=F(B,28),fill=GREY,anchor="ra")
    d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
    d.text((80,1255),"@sentineltradinghq",font=F(B,26),fill=WHITE)
    d.text((1000,1258),"Desliza →" if n<TOTAL else "Info en desarrollo · No es asesoría",font=F(R,22),fill=GREY,anchor="ra")
    return img,d

def wrap(d,texto,x,y,font,fill,ancho=920,inter=1.45):
    palabras=texto.split(); linea=""
    for p in palabras:
        prueba=(linea+" "+p).strip()
        if d.textlength(prueba,font=font)>ancho:
            d.text((x,y),linea,font=font,fill=fill); y+=int(font.size*inter); linea=p
        else: linea=prueba
    if linea: d.text((x,y),linea,font=font,fill=fill); y+=int(font.size*inter)
    return y

def titulo(d,a,b,y=170):
    d.text((80,y),a,font=F(B,58),fill=WHITE)
    if b: d.text((80,y+72),b,font=F(B,58),fill=GOLD)
    return y+(160 if b else 90)

out=[]
# 1 portada
img,d=base(1,"Análisis · 30 de octubre de 2026")
d.text((80,250),"El robo más",font=F(B,82),fill=WHITE)
d.text((80,350),"grande de la",font=F(B,82),fill=WHITE)
d.text((80,450),"historia cripto",font=F(B,82),fill=GOLD)
d.rounded_rectangle([80,600,1000,760],radius=20,fill=CARD)
d.text((120,625),"$6.300.000.000",font=F(B,72),fill=RED)
d.text((120,712),"robados a Binance en una sola tarde",font=F(R,30),fill=GREY)
y=wrap(d,"Qué pasó, cuánto se llevaron, cómo entraron, qué dijo Binance y qué significa para ti. Te lo contamos todo en 5 partes.",80,830,F(R,34),WHITE)
out.append(img)

# 2 cronología
img,d=base(2,"Parte 1 · Cómo se desarrolló")
y=titulo(d,"Una tarde que nadie","en cripto va a olvidar")
eventos=[("Jue 3:24 p. m.","Salen los primeros fondos de las billeteras calientes de Binance."),
         ("5:32 p. m.","Binance suspende los retiros: \"problema de seguridad\"."),
         ("7:07 p. m.","También suspende los depósitos y avisa a las autoridades."),
         ("9:21 p. m.","Primera explicación: la laptop comprometida de un ingeniero."),
         ("11:17 p. m.","Analistas apuntan a TraderTraitor, hackers de Corea del Norte."),
         ("Vie 2:37 a. m.","Binance encuentra \"puntos adicionales de brecha\".")]
y+=20
for h,t in eventos:
    d.ellipse([86,y+8,104,y+26],fill=GOLD)
    d.text((125,y),h,font=F(B,28),fill=GOLD)
    y=wrap(d,t,125,y+40,F(R,28),WHITE,ancho=870,inter=1.35)+22
d.text((80,1180),"Horas de Colombia (UTC-5).",font=F(R,22),fill=GREY)
out.append(img)

# 3 qué se llevaron
img,d=base(3,"Parte 2 · Qué se llevaron")
y=titulo(d,"65 tokens,","8 blockchains")
rows=[("BTC","≈ 18.270 BTC","$1.440 M"),("USDT","≈ 1.770 M","$1.770 M"),("ETH","≈ 460.500 ETH","$1.040 M"),
      ("USDC","≈ 823 M","$823 M"),("XRP","≈ 233,5 M","$297 M"),("TRX","≈ 684,6 M","$241 M"),("SOL","≈ 970.500","$94 M")]
y+=10
for k,q,v in rows:
    d.rounded_rectangle([80,y,1000,y+62],radius=12,fill=CARD)
    d.text((110,y+15),k,font=F(B,30),fill=GOLD); d.text((270,y+15),q,font=F(R,30),fill=WHITE); d.text((970,y+15),v,font=F(R,30),fill=GREY,anchor="ra")
    y+=74
y+=15
y=wrap(d,"La buena noticia: cerca de $3.000 millones ya están congelados. Tether, Circle, Ripple y otros bloquearon las stablecoins robadas antes de que el atacante pudiera moverlas.",80,y,F(R,29),WHITE)
d.text((80,1180),"Cifras preliminares de rastreadores on-chain.",font=F(R,22),fill=GREY)
out.append(img)

# 4 cómo entraron
img,d=base(4,"Parte 3 · Cómo entraron")
d.text((80,170),"No rompieron la blockchain.",font=F(B,52),fill=WHITE)
d.text((80,236),"Entraron por una persona.",font=F(B,52),fill=GOLD)
y=320
y=wrap(d,"Según Binance, el atacante tomó control de la laptop de un ingeniero DevOps y desde ahí autorizó transacciones. La empresa dice que no hay evidencia de que se filtraran claves privadas.",80,y+10,F(R,30),WHITE)
d.rounded_rectangle([80,y+15,1000,y+170],radius=16,fill=CARD); d.rectangle([80,y+15,88,y+170],fill=GOLD)
d.text((110,y+35),"“No fue un ataque de un solo clic;",font=F(I,30),fill=WHITE)
d.text((110,y+80),"fue un proceso más complejo.”",font=F(I,30),fill=WHITE)
d.text((110,y+125),"— Richard Teng, co-CEO de Binance",font=F(R,24),fill=GREY)
y+=200
y=wrap(d,"Varias firmas de análisis (TRM, Chainalysis, ZachXBT) lo atribuyen a TraderTraitor, una unidad ligada al Grupo Lazarus de Corea del Norte. Es el mismo tipo de ataque que vimos con Bybit en 2025, que se llevó $1.500 millones.",80,y,F(R,30),WHITE)
out.append(img)

# 5 qué dijo binance
img,d=base(5,"Parte 4 · La respuesta oficial")
y=titulo(d,"Lo que prometió","Binance")
for q in ["“Los fondos de los usuarios están seguros.”","“Cubriremos todas las pérdidas.”"]:
    d.rounded_rectangle([80,y,1000,y+80],radius=16,fill=CARD); d.rectangle([80,y,88,y+80],fill=GOLD)
    d.text((110,y+22),q,font=F(I,31),fill=WHITE); y+=98
y+=10
puntos=[("Cómo van a pagar","Con su fondo de emergencia SAFU (cerca de $1.000 M en BTC) y reservas propias de la empresa."),
        ("Retiros","Siguen pausados. Binance dice que volverían en unas 48 horas, hacia el domingo."),
        ("Transparencia","Prometen un informe técnico completo cuando termine la investigación.")]
for k,v in puntos:
    d.text((80,y),k,font=F(B,30),fill=GOLD)
    y=wrap(d,v,80,y+44,F(R,29),WHITE)+18
d.text((80,1180),"Citas traducidas del inglés.",font=F(R,22),fill=GREY)
out.append(img)

# 6 qué significa
img,d=base(6,"Parte 5 · Qué significa para ti")
y=titulo(d,"Lo que viene","y la lección")
d.text((80,y),"Fechas clave",font=F(B,32),fill=WHITE); y+=52
for t in ["Domingo: ¿vuelven los retiros a tiempo?","1 de noviembre: nueva prueba de reservas. Veremos si Binance ya repuso lo robado."]:
    y=wrap(d,"• "+t,80,y,F(R,29),WHITE)+6
y+=20
d.text((80,y),"Mercado",font=F(B,32),fill=WHITE); y+=52
y=wrap(d,"BTC ronda los $77.000, con caídas de 3% a 5% desde el hackeo.",80,y,F(R,29),RED)+20
d.rounded_rectangle([80,y,1000,y+300],radius=18,fill=CARD)
d.text((110,y+25),"La lección de siempre",font=F(B,32),fill=GOLD)
yy=y+80
for t in ["No dejes todo tu capital en un solo exchange.","Lo que no vas a operar, guárdalo en tu propia billetera.","Activa 2FA y listas blancas de retiro."]:
    yy=wrap(d,"✓ "+t,110,yy,F(R,28),WHITE,ancho=860,inter=1.35)+10
out.append(img)

for i,im in enumerate(out,1):
    im.save(f"posts/2026-10/2026-10-30_binance_carrusel_{i}.jpg",quality=92)
print("ok")
