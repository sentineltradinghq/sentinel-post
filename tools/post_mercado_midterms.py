from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); CARD=(20,27,44); EDGE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Mercado cripto · lunes 2 nov 2026",font=f(R,26),fill=GREY)
d.text((80,210),"Binance libera retiros",font=f(B,70),fill=WHITE)
d.text((80,295),"y mañana vota EE. UU.",font=f(B,70),fill=WHITE)
d.text((80,380),"¿Apostar o esperar?",font=f(B,70),fill=GOLD)
cards=[("BITCOIN","$76.730","−1,9% en 24 h",RED),
       ("ETHEREUM","$2.248","−1,1% en 24 h",RED),
       ("MIEDO Y CODICIA","37","Miedo · ayer 34",GOLD)]
cw=293; y0=500
for i,(t,v,s,c) in enumerate(cards):
    x=80+i*(cw+20)
    d.rounded_rectangle([x,y0,x+cw,y0+170],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((x+22,y0+22),t,font=f(B,20),fill=GREY)
    d.text((x+22,y0+58),v,font=f(B,44),fill=WHITE)
    d.text((x+22,y0+122),s,font=f(R,20),fill=c)
# dos noticias
ny=705
rows=[("BINANCE","Salida neta de ~$3.640 M al reabrir retiros.","Dice haber repuesto ~95% de lo robado."),
      ("EE. UU.","Elecciones de mitad de mandato el 3 de nov.","Más incertidumbre para la regulación cripto.")]
for i,(tag,l1,l2) in enumerate(rows):
    y=ny+i*118
    d.rounded_rectangle([80,y,1000,y+100],radius=16,fill=CARD,outline=EDGE,width=2)
    d.rounded_rectangle([98,y+30,250,y+70],radius=10,fill=GOLD)
    d.text((174,y+50),tag,font=f(B,20),fill=(11,15,26),anchor="mm")
    d.text((272,y+20),l1,font=f(B,24),fill=WHITE)
    d.text((272,y+56),l2,font=f(R,22),fill=GREY)
d.text((80,950),"Nivel que vigila el mercado en BTC: $76.000",font=f(R,26),fill=GREY)
d.text((80,1005),"Ante un evento incierto, un sistema:",font=f(B,32),fill=GOLD)
items=["No apuesta al resultado de una votación","Respeta su riesgo, aunque haya ruido","Espera su señal, no el titular"]
for i,t in enumerate(items):
    yy=1060+i*46
    d.text((80,yy),"✓",font=f(B,30),fill=GREEN); d.text((125,yy+2),t,font=f(R,28),fill=WHITE)
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1246),"Datos: CNBC, CoinDesk, Motley Fool, alternative.me",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-11/2026-11-02_pm_mercado_binance_elecciones.jpg",quality=92)
