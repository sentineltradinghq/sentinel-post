from PIL import Image, ImageDraw, ImageFont
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
BG=(11,15,26); GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); CARD=(20,27,44); EDGE=(40,48,66)
def base(W,H):
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
    for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
    return img,d
def card(d,x,y,w,h,t,v,s,c,vs=44):
    d.rounded_rectangle([x,y,x+w,y+h],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((x+22,y+20),t,font=f(B,20),fill=GREY)
    d.text((x+22,y+54),v,font=f(B,vs),fill=WHITE)
    d.text((x+22,y+h-44),s,font=f(R,21),fill=c)

# ---------- POST 1080x1350 ----------
W,H=1080,1350; img,d=base(W,H)
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.rounded_rectangle([730,76,1000,118],radius=10,fill=RED)
d.text((865,97),"CIERRE DEL DÍA",font=f(B,22),fill=WHITE,anchor="mm")
d.text((80,125),"Actualización · jueves 5 nov 2026",font=f(R,26),fill=GREY)
d.text((80,200),"Wall Street cierra",font=f(B,68),fill=WHITE)
d.text((80,282),"en rojo y Bitcoin",font=f(B,68),fill=WHITE)
d.text((80,364),"borra el rebote",font=f(B,68),fill=RED)
cw=293; y0=470
for i,(t,v,s) in enumerate([("NASDAQ 100","−6,4%","Chips e IA"),("S&P 500","−4,4%","Venta amplia"),("LIQUIDADOS","$1.080 M","88% largos")]):
    card(d,80+i*(cw+20),y0,cw,160,t,v,s,RED if i<2 else GOLD)
cw2=293; y1=650
for i,(t,v,s) in enumerate([("BITCOIN","$76.010","−5,4% hoy"),("ETHEREUM","$2.239","−7,5% hoy"),("SOLANA","$90,1","−5,6% hoy")]):
    card(d,80+i*(cw2+20),y1,cw2,160,t,v,s,RED)
d.text((80,835),"BTC: de $80.800 a un mínimo de $75.500.",font=f(R,27),fill=WHITE)
d.text((80,875),"Nada queda del salto a $81K del miércoles.",font=f(R,27),fill=GREY)
# tip block
ty=935
d.rounded_rectangle([80,ty,1000,ty+250],radius=20,fill=CARD,outline=GOLD,width=3)
d.rounded_rectangle([104,ty+24,330,ty+66],radius=10,fill=GOLD)
d.text((217,ty+45),"TIP DEL DÍA",font=f(B,22),fill=BG,anchor="mm")
d.text((104,ty+86),"Volatilidad alta = posición más pequeña",font=f(B,32),fill=WHITE)
for i,t in enumerate(["Si el precio se mueve el doble, la misma",
                      "posición arriesga el doble. Opera más",
                      "pequeño o no operes: el mercado sigue mañana."]):
    d.text((104,ty+138+i*36),t,font=f(R,26),fill=GREY)
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1246),"Datos: TradingView, CoinGlass",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-11/2026-11-05_pm_cierre_wallstreet_btc.jpg",quality=92)

# ---------- HISTORIA COMPLEMENTARIA 1080x1920 ----------
W,H=1080,1920; img,d=base(W,H)
d.text((W//2,130),"SENTINEL TRADING",font=f(B,34),fill=GOLD,anchor="mm")
d.text((W//2,180),"El día en cifras · 5 nov 2026",font=f(R,30),fill=GREY,anchor="mm")
d.text((80,260),"Lo que no cupo",font=f(B,72),fill=WHITE)
d.text((80,350),"en el post",font=f(B,72),fill=GOLD)
rows=[("BTC","$76.010","−5,4%","Mín. $75.500 · Máx. $80.800"),
      ("ETH","$2.239","−7,5%","El que más cayó de los tres"),
      ("SOL","$90,1","−5,6%","Mín. del día $88,7")]
for i,(t,v,c,s) in enumerate(rows):
    y=470+i*150
    d.rounded_rectangle([80,y,1000,y+130],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((110,y+28),t,font=f(B,30),fill=GOLD)
    d.text((230,y+20),v,font=f(B,46),fill=WHITE)
    d.text((970,y+24),c,font=f(B,40),fill=RED,anchor="ra")
    d.text((230,y+84),s,font=f(R,24),fill=GREY)
y=935
d.rounded_rectangle([80,y,1000,y+300],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((110,y+28),"LIQUIDACIONES 24 H",font=f(B,24),fill=GREY)
d.text((110,y+66),"$1.080 M",font=f(B,60),fill=WHITE)
d.text((110,y+150),"Largos  88%",font=f(B,28),fill=RED); d.text((560,y+150),"Cortos  12%",font=f(B,28),fill=GREEN)
d.rectangle([110,y+198,970,y+226],fill=GREEN); d.rectangle([110,y+198,110+int(860*0.88),y+226],fill=RED)
d.text((110,y+244),"~210.000 traders · mayor: largo de ETH de $10,9 M",font=f(R,24),fill=GREY)
y=1265
d.rounded_rectangle([80,y,1000,y+120],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((110,y+22),"Miedo y codicia: 50 (neutral)",font=f(B,30),fill=WHITE)
d.text((110,y+70),"Lectura de esta mañana, antes de la caída",font=f(R,24),fill=GREY)
y=1415
d.rounded_rectangle([80,y,1000,y+270],radius=20,fill=CARD,outline=GOLD,width=3)
d.rounded_rectangle([104,y+24,330,y+66],radius=10,fill=GOLD)
d.text((217,y+45),"TIP DEL DÍA",font=f(B,22),fill=BG,anchor="mm")
d.text((104,y+88),"Cripto no está aislada",font=f(B,34),fill=WHITE)
for i,t in enumerate(["Cuando las tecnológicas caen fuerte, BTC",
                      "suele acompañar. Mira también el Nasdaq",
                      "antes de operar en días de miedo."]):
    d.text((104,y+142+i*38),t,font=f(R,27),fill=GREY)
d.text((W//2,1755),"Comunidad gratis: link en la bio",font=f(B,40),fill=GOLD,anchor="mm")
d.text((W//2,1815),"@sentineltradinghq",font=f(R,30),fill=WHITE,anchor="mm")
d.text((W//2,1865),"Contenido educativo. No es asesoría financiera.",font=f(R,24),fill=GREY,anchor="mm")
img.save("historias/2026-11/2026-11-05_pm_complementaria.jpg",quality=92)
