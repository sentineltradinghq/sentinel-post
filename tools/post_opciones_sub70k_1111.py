import sys; sys.path.insert(0,"tools")
from PIL import Image, ImageDraw, ImageFont
import math
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
def tip(d,y,h,title,lines,ts=32,ls=26,sp=36):
    d.rounded_rectangle([80,y,1000,y+h],radius=20,fill=CARD,outline=GOLD,width=3)
    d.rounded_rectangle([104,y+24,330,y+66],radius=10,fill=GOLD)
    d.text((217,y+45),"TIP DEL DÍA",font=f(B,22),fill=BG,anchor="mm")
    d.text((104,y+86),title,font=f(B,ts),fill=WHITE)
    for i,t in enumerate(lines): d.text((104,y+138+i*sp),t,font=f(R,ls),fill=GREY)
def bar(d,x,y,label,old,new,col):
    d.text((x,y),label,font=f(B,26),fill=WHITE)
    maxw=560
    d.text((x,y+44),"Hace 1 semana",font=f(R,20),fill=GREY)
    d.rounded_rectangle([x+170,y+44,x+170+int(maxw*old/60),y+68],radius=8,fill=EDGE)
    d.text((x+180+int(maxw*old/60),y+42),f"{old} %",font=f(B,22),fill=GREY)
    d.text((x,y+82),"Hoy",font=f(R,20),fill=GREY)
    d.rounded_rectangle([x+170,y+82,x+170+int(maxw*new/60),y+110],radius=8,fill=col)
    d.text((x+180+int(maxw*new/60),y+80),f"{new} %",font=f(B,26),fill=col)

TIPT="Planea tu peor escenario hoy"
TIPL=["Pregúntate: ¿qué hago si BTC cae a $70K?",
      "Decide antes tu stop y tu tamaño. Los grandes",
      "se cubren con calma; no esperes al pánico."]

# ---------- POST 1080x1350 ----------
W,H=1080,1350; img,d=base(W,H)
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.rounded_rectangle([760,76,1000,118],radius=10,fill=GOLD)
d.text((880,97),"MERCADO HOY",font=f(B,22),fill=BG,anchor="mm")
d.text((80,125),"Miércoles 11 nov 2026",font=f(R,26),fill=GREY)
d.text((80,185),"Las opciones se cubren:",font=f(B,58),fill=WHITE)
d.text((80,258),"¿BTC bajo $70K en Navidad?",font=f(B,54),fill=RED)
d.rounded_rectangle([80,350,1000,660],radius=20,fill=CARD,outline=EDGE,width=2)
d.text((110,372),"PROBABILIDAD SEGÚN EL MERCADO DE OPCIONES (DERIVE)",font=f(B,20),fill=GREY)
bar(d,110,410,"BTC bajo $70.000 en Navidad",15,31,RED)
bar(d,110,530,"BTC sobre $80.000 en Navidad",53,26,GREEN)
cw=293; y1=680
for i,(t,v,s,c) in enumerate([("BITCOIN","$74.440","+1,0% hoy",GREEN),
                              ("ETHEREUM","$2.078","+1,3% hoy",GREEN),
                              ("SOLANA","$84,8","+1,8% hoy",GREEN)]):
    card(d,80+i*(cw+20),y1,cw,145,t,v,s,c,vs=42)
d.text((80,845),"Miedo y codicia: 26 (miedo)  ·  ETF de BTC: 4 días de salidas",font=f(R,24),fill=WHITE)
d.text((80,882),"Puts (apuestas a la baja) 1,5x sobre calls en Deribit",font=f(R,24),fill=WHITE)
tip(d,935,285,TIPT,TIPL,ts=32,ls=26,sp=38)
d.line([(80,1235),(1000,1235)],fill=EDGE,width=2)
d.text((80,1255),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1298),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1261),"Datos: The Block, CoinDesk, TradingView",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-11/2026-11-11_pm_opciones_sub70k.jpg",quality=92)

# ---------- HISTORIA COMPLEMENTARIA 1080x1920 ----------
W,H=1080,1920; img,d=base(W,H)
d.text((W//2,120),"SENTINEL TRADING",font=f(B,34),fill=GOLD,anchor="mm")
d.text((W//2,170),"El día en cifras · 11 nov 2026",font=f(R,30),fill=GREY,anchor="mm")
d.text((80,230),"Lo que no cupo",font=f(B,68),fill=WHITE)
d.text((80,315),"en el post",font=f(B,68),fill=GOLD)
rows=[("BTC","$74.440","+1,0%","Rango del día $73.140 – $74.700",GREEN),
      ("ETH","$2.078","+1,3%","Rango del día $2.041 – $2.101",GREEN),
      ("SOL","$84,8","+1,8%","Rango del día $82,2 – $85,7",GREEN)]
for i,(t,v,c,s,col) in enumerate(rows):
    y=420+i*140
    d.rounded_rectangle([80,y,1000,y+122],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((110,y+24),t,font=f(B,30),fill=GOLD)
    d.text((230,y+16),v,font=f(B,44),fill=WHITE)
    d.text((970,y+20),c,font=f(B,38),fill=col,anchor="ra")
    d.text((230,y+78),s,font=f(R,23),fill=GREY)
y=850
d.rounded_rectangle([80,y,1000,y+200],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((110,y+24),"LA FED",font=f(B,22),fill=RED)
d.text((110,y+58),"~90 % ve SUBIDA de tasas en dic.",font=f(B,34),fill=WHITE)
for i,t in enumerate(["Tras el IPC caliente de ayer (CME FedWatch).",
                      "Waller: hasta medio punto si sigue alta."]):
    d.text((110,y+112+i*34),t,font=f(R,25),fill=GREY)
y=1070
for j,(t,v,s,c) in enumerate([("ETF DE BTC","−$95 M","martes · 4.º día seguido",RED),
                              ("LIQUIDACIONES 24 H","$725 M","85 % largos en BTC",RED)]):
    x=80+j*475
    d.rounded_rectangle([x,y,x+445,y+170],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((x+25,y+20),t,font=f(B,20),fill=GREY)
    d.text((x+25,y+56),v,font=f(B,46),fill=c)
    d.text((x+25,y+124),s,font=f(R,21),fill=GOLD)
tip(d,1265,280,TIPT,TIPL,ts=33,ls=27,sp=38)
d.text((W//2,1640),"Comunidad gratis: link en la bio",font=f(B,40),fill=GOLD,anchor="mm")
d.text((W//2,1705),"@sentineltradinghq",font=f(R,30),fill=WHITE,anchor="mm")
d.text((W//2,1760),"Contenido educativo. No es asesoría financiera.",font=f(R,24),fill=GREY,anchor="mm")
d.text((W//2,1810),"Datos: TradingView, CoinDesk, CoinGlass, SoSoValue, CME",font=f(R,19),fill=GREY,anchor="mm")
d.text((W//2,1845),"Miedo y codicia: 26 (miedo)",font=f(R,19),fill=GREY,anchor="mm")
img.save("historias/2026-11/2026-11-11_pm_complementaria.jpg",quality=92)
