from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(20,27,43); BG=(11,15,26)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,70),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,112),"Noticia · ETF de Bitcoin",font=f(R,26),fill=GREY)
d.text((80,175),"Europa estrena ETF de Bitcoin",font=f(B,56),fill=WHITE)
d.text((80,250),"mientras EE. UU. vive su peor mes",font=f(B,48),fill=GOLD)
# dos paneles
def panel(x,titulo,valor,sub,col):
    d.rounded_rectangle([x,345,x+445,585],radius=22,fill=PANEL)
    d.text((x+222,385),titulo,font=f(B,26),fill=GREY,anchor="mm")
    d.text((x+222,460),valor,font=f(B,64),fill=col,anchor="mm")
    for i,s in enumerate(sub): d.text((x+222,525+i*32),s,font=f(R,23),fill=WHITE,anchor="mm")
panel(80,"SUIZA · BBIT","+350 BTC",["≈ $21 M al arrancar","1.er ETF suizo con BTC directo"],GREEN)
panel(555,"ETF BTC EE. UU.","-$5.390 M",["salidas en noviembre","7 días seguidos en rojo"],RED)
# barras récord
d.rounded_rectangle([60,620,1020,860],radius=22,fill=PANEL)
d.text((90,650),"Salidas mensuales récord (ETF spot BTC EE. UU.)",font=f(B,25),fill=GREY)
mx=5390; X0=330; X1=880
for i,(lab,val,col,txt) in enumerate([("Junio 2026",4510,GREY,"-$4.510 M"),("Nov. 2026*",5390,RED,"-$5.390 M")]):
    y=710+i*70
    d.text((90,y+20),lab,font=f(B,26),fill=WHITE,anchor="lm")
    d.rounded_rectangle([X0,y,X0+(X1-X0)*val/mx,y+40],radius=8,fill=col)
    d.text((X0+(X1-X0)*val/mx+15,y+20),txt,font=f(B,24),fill=col,anchor="lm")
d.text((90,835),"*hasta el 25 de noviembre",font=f(R,20),fill=GREY,anchor="lm")
pts=[("1","Aprobado por el regulador suizo (FINMA) el 20 de octubre."),
     ("2","Debutó el 26-nov en la bolsa SIX: +0,6% en su 1.a hora."),
     ("3","Bitcoin sin reacción: ~$60.600, Wall Street cerrado.")]
for i,(k,t) in enumerate(pts):
    y=895+i*58
    d.ellipse([82,y,124,y+42],fill=GOLD); d.text((103,y+21),k,font=f(B,24),fill=BG,anchor="mm")
    d.text((142,y+21),t,font=f(R,26),fill=WHITE,anchor="lm")
d.text((80,1080),"Tip: un ETF nuevo es una puerta, no compras.",font=f(B,29),fill=GREEN)
d.text((80,1125),"Lo que mueve el precio son los flujos de dinero.",font=f(R,27),fill=WHITE)
d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-26_pm_etf_suiza_bbit.jpg",quality=92)
