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
def tip(d,y,h,title,lines,ts=32,ls=26,sp=36):
    d.rounded_rectangle([80,y,1000,y+h],radius=20,fill=CARD,outline=GOLD,width=3)
    d.rounded_rectangle([104,y+24,330,y+66],radius=10,fill=GOLD)
    d.text((217,y+45),"TIP DEL DÍA",font=f(B,22),fill=BG,anchor="mm")
    d.text((104,y+86),title,font=f(B,ts),fill=WHITE)
    for i,t in enumerate(lines): d.text((104,y+138+i*sp),t,font=f(R,ls),fill=GREY)

# ---------- POST 1080x1350 ----------
W,H=1080,1350; img,d=base(W,H)
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.rounded_rectangle([760,76,1000,118],radius=10,fill=GOLD)
d.text((880,97),"MERCADO HOY",font=f(B,22),fill=BG,anchor="mm")
d.text((80,125),"Viernes 6 nov 2026",font=f(R,26),fill=GREY)
d.text((80,200),"Wall Street rebota,",font=f(B,68),fill=WHITE)
d.text((80,282),"Bitcoin no",font=f(B,68),fill=RED)
d.text((80,370),"Empleo fuerte en EE. UU. y BTC en mínimos desde agosto",font=f(R,27),fill=GREY)
cw=293; y0=430
for i,(t,v,s,c) in enumerate([("EMPLEO EE. UU.","+165.000","Esperado: 65.000",GOLD),
                              ("NASDAQ 100","+1,4%","Rebote tras el −6%",GREEN),
                              ("S&P 500","+0,3%","Leve alza",GREEN)]):
    card(d,80+i*(cw+20),y0,cw,160,t,v,s,c,vs=42 if i==0 else 44)
y1=610
for i,(t,v,s,c) in enumerate([("BITCOIN","$75.950","Mín. $74.760",RED),
                              ("ETHEREUM","$2.239","+0,1% hoy",GREY),
                              ("SOLANA","$90,2","+1,1% hoy",GREEN)]):
    card(d,80+i*(cw+20),y1,cw,160,t,v,s,c)
d.text((80,800),"BTC tocó su nivel más bajo desde el 21 de agosto.",font=f(R,27),fill=WHITE)
d.text((80,840),"Miedo y codicia: 28 (miedo). Ayer estaba en 50.",font=f(R,27),fill=GREY)
tip(d,920,265,"Espera el cierre de la vela",
    ["Una mecha que perfora un soporte no es una",
     "ruptura confirmada. Decide con el cierre de",
     "la vela, y con tu stop puesto desde antes."])
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1246),"Datos: TradingView, BLS",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-11/2026-11-06_pm_wallstreet_rebota_btc_no.jpg",quality=92)

# ---------- HISTORIA COMPLEMENTARIA 1080x1920 ----------
W,H=1080,1920; img,d=base(W,H)
d.text((W//2,120),"SENTINEL TRADING",font=f(B,34),fill=GOLD,anchor="mm")
d.text((W//2,170),"El día en cifras · 6 nov 2026",font=f(R,30),fill=GREY,anchor="mm")
d.text((80,230),"Lo que no cupo",font=f(B,68),fill=WHITE)
d.text((80,315),"en el post",font=f(B,68),fill=GOLD)
rows=[("BTC","$75.950","−0,1%","Mín. $74.760 · el más bajo desde el 21 ago",RED),
      ("ETH","$2.239","+0,1%","Plano tras caer −7,5% el jueves",GREY),
      ("SOL","$90,2","+1,1%","El único de los tres en verde",GREEN)]
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
d.text((110,y+58),"EE. UU. corta a MEXC Global",font=f(B,36),fill=WHITE)
for i,t in enumerate(["El Tesoro (FinCEN) la acusa de mover ~$16.000 M",
                      "ligados a Irán, Corea del Norte y Rusia."]):
    d.text((110,y+112+i*34),t,font=f(R,25),fill=GREY)
y=1070
d.rounded_rectangle([80,y,535,y+170],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((105,y+20),"ETF CRIPTO (JUEVES)",font=f(B,20),fill=GREY)
d.text((105,y+56),"−$500 M+",font=f(B,46),fill=RED)
d.text((105,y+124),"−$1.100 M+ en la semana",font=f(R,21),fill=GREY)
d.rounded_rectangle([555,y,1000,y+170],radius=18,fill=CARD,outline=EDGE,width=2)
d.text((580,y+20),"BOTS SENTINEL",font=f(B,20),fill=GREY)
d.text((580,y+56),"0 cierres",font=f(B,46),fill=WHITE)
d.text((580,y+124),"esta semana · resumen el domingo",font=f(R,20),fill=GOLD)
tip(d,1265,280,"Espera el cierre de la vela",
    ["Que el precio toque un soporte no es una",
     "ruptura. Confírmala con el cierre de la vela",
     "y ten tu stop definido antes de entrar."],ts=34,ls=27,sp=38)
d.text((W//2,1640),"Comunidad gratis: link en la bio",font=f(B,40),fill=GOLD,anchor="mm")
d.text((W//2,1705),"@sentineltradinghq",font=f(R,30),fill=WHITE,anchor="mm")
d.text((W//2,1760),"Contenido educativo. No es asesoría financiera.",font=f(R,24),fill=GREY,anchor="mm")
d.text((W//2,1810),"Datos: TradingView, BLS, The Block, Alternative.me",font=f(R,20),fill=GREY,anchor="mm")
img.save("historias/2026-11/2026-11-06_pm_complementaria.jpg",quality=92)
