from PIL import Image, ImageDraw, ImageFont
import math
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
BG=(11,15,26); GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); CARD=(20,27,44); EDGE=(40,48,66)
ORANGE=(230,126,34); YEL=(241,196,15)
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
def tip(d,y,h,title,lines,ts=32,ls=26,sp=36):
    d.rounded_rectangle([80,y,1000,y+h],radius=20,fill=CARD,outline=GOLD,width=3)
    d.rounded_rectangle([104,y+24,330,y+66],radius=10,fill=GOLD)
    d.text((217,y+45),"TIP DEL DÍA",font=f(B,22),fill=BG,anchor="mm")
    d.text((104,y+86),title,font=f(B,ts),fill=WHITE)
    for i,t in enumerate(lines): d.text((104,y+138+i*sp),t,font=f(R,ls),fill=GREY)
def gauge(d,cx,cy,r,val,w=34):
    segs=[(0,25,RED),(25,45,ORANGE),(45,55,YEL),(55,75,(130,200,80)),(75,100,GREEN)]
    for a,b,c in segs:
        d.arc([cx-r,cy-r,cx+r,cy+r],start=180+a*1.8+0.8,end=180+b*1.8-0.8,fill=c,width=w)
    ang=math.radians(180+val*1.8)
    x=cx+(r-w-18)*math.cos(ang); y=cy+(r-w-18)*math.sin(ang)
    d.line([(cx,cy),(x,y)],fill=WHITE,width=8); d.ellipse([cx-16,cy-16,cx+16,cy+16],fill=WHITE)

# ---------- POST 1080x1350 ----------
W,H=1080,1350; img,d=base(W,H)
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.rounded_rectangle([760,76,1000,118],radius=10,fill=GOLD)
d.text((880,97),"MERCADO HOY",font=f(B,22),fill=BG,anchor="mm")
d.text((80,125),"Martes 10 nov 2026",font=f(R,26),fill=GREY)
d.text((80,190),"Inflación más alta",font=f(B,70),fill=RED)
d.text((80,272),"y Bitcoin pierde los $74K",font=f(B,48),fill=WHITE)
# bloque IPC
d.rounded_rectangle([80,360,1000,640],radius=20,fill=CARD,outline=EDGE,width=2)
d.text((110,385),"IPC DE EE. UU. · OCTUBRE (MENSUAL)",font=f(B,22),fill=GREY)
for i,(t,v,e) in enumerate([("General","+0,4 %","esperado +0,3 %"),("Subyacente","+0,3 %","esperado +0,2 %")]):
    x=110+i*450
    d.text((x,430),t,font=f(R,28),fill=WHITE)
    d.text((x,470),v,font=f(B,64),fill=RED)
    d.text((x,548),e,font=f(R,24),fill=GREY)
d.text((110,596),"Crecen las apuestas a una SUBIDA de tasas de la Fed en diciembre",font=f(B,22),fill=GOLD)
cw=293; y1=665
for i,(t,v,s,c) in enumerate([("BITCOIN","$73.710","−2,1% · mín. $72.670",RED),
                              ("ETHEREUM","$2.052","−3,8% · mín. $2.005",RED),
                              ("SOLANA","$83,2","−4,0% · mín. $81,3",RED)]):
    card(d,80+i*(cw+20),y1,cw,150,t,v,s,c,vs=42)
d.text((80,840),"Bono a 10 años toca 5 %  ·  Miedo y codicia: 31 (miedo)",font=f(R,25),fill=WHITE)
d.text((80,878),"Bot SOL 15m Long cerró −28,65 % (forward test, sin capital real).",font=f(R,25),fill=WHITE)
tip(d,935,285,"Revisa el calendario económico",
    ["IPC, Fed y empleo mueven todo el mercado en minutos.",
     "Ubica la hora del dato y evita abrir posiciones",
     "justo antes: espera a que el precio se asiente."],ts=32,ls=26,sp=38)
d.line([(80,1235),(1000,1235)],fill=EDGE,width=2)
d.text((80,1255),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1298),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1261),"Datos: BLS, TradingView, CoinGlass",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-11/2026-11-10_pm_ipc_caliente_btc.jpg",quality=92)

# ---------- HISTORIA COMPLEMENTARIA 1080x1920 ----------
W,H=1080,1920; img,d=base(W,H)
d.text((W//2,120),"SENTINEL TRADING",font=f(B,34),fill=GOLD,anchor="mm")
d.text((W//2,170),"El día en cifras · 10 nov 2026",font=f(R,30),fill=GREY,anchor="mm")
d.text((80,230),"Lo que no cupo",font=f(B,68),fill=WHITE)
d.text((80,315),"en el post",font=f(B,68),fill=GOLD)
rows=[("BTC","$73.710","−2,1%","Mín. $72.670 · −5 % en 7 días",RED),
      ("ETH","$2.052","−3,8%","Tocó $2.005 · −10 % en 7 días",RED),
      ("SOL","$83,2","−4,0%","Mín. $81,3 · −10,6 % en 7 días",RED)]
for i,(t,v,c,s,col) in enumerate(rows):
    y=420+i*140
    d.rounded_rectangle([80,y,1000,y+122],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((110,y+24),t,font=f(B,30),fill=GOLD)
    d.text((230,y+16),v,font=f(B,44),fill=WHITE)
    d.text((970,y+20),c,font=f(B,38),fill=col,anchor="ra")
    d.text((230,y+78),s,font=f(R,23),fill=GREY)
y=850
d.rounded_rectangle([80,y,1000,y+200],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((110,y+24),"OTRA NOTICIA",font=f(B,22),fill=RED)
d.text((110,y+58),"MARA vende parte de sus BTC",font=f(B,36),fill=WHITE)
for i,t in enumerate(["13.597 BTC (~$1.100 M) en seis semanas,",
                      "y dice que podría vender más (CoinDesk)."]):
    d.text((110,y+112+i*34),t,font=f(R,25),fill=GREY)
y=1070
d.rounded_rectangle([80,y,535,y+170],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((105,y+20),"ETF DE BTC (NOV)",font=f(B,20),fill=GREY)
d.text((105,y+56),"≈ −$1.480 M",font=f(B,44),fill=RED)
d.text((105,y+124),"lunes: −$201 M",font=f(R,21),fill=GREY)
d.rounded_rectangle([555,y,1000,y+170],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((580,y+20),"BOT SOL 15m LONG",font=f(B,20),fill=GREY)
d.text((580,y+56),"−28,65 %",font=f(B,46),fill=RED)
d.text((580,y+124),"Abierto desde septiembre",font=f(R,21),fill=GOLD)
tip(d,1265,280,"Revisa el calendario económico",
    ["Anota la hora del IPC, la Fed y el empleo.",
     "Evita abrir justo antes del dato: espera",
     "a que el precio se asiente y decide con plan."],ts=33,ls=27,sp=38)
d.text((W//2,1640),"Comunidad gratis: link en la bio",font=f(B,40),fill=GOLD,anchor="mm")
d.text((W//2,1705),"@sentineltradinghq",font=f(R,30),fill=WHITE,anchor="mm")
d.text((W//2,1760),"Contenido educativo. No es asesoría financiera.",font=f(R,24),fill=GREY,anchor="mm")
d.text((W//2,1810),"Datos: BLS, TradingView, CoinGlass, CoinDesk, SoSoValue",font=f(R,19),fill=GREY,anchor="mm")
d.text((W//2,1845),"Bots: forward test en vivo, sin capital real.",font=f(R,19),fill=GREY,anchor="mm")
img.save("historias/2026-11/2026-11-10_pm_complementaria.jpg",quality=92)
