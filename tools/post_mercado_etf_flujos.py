from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); CARD=(20,27,44); EDGE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Mercado cripto · martes 3 nov 2026",font=f(R,26),fill=GREY)
d.text((80,210),"Salen ~$1.040 M",font=f(B,70),fill=WHITE)
d.text((80,295),"de los ETF de Bitcoin...",font=f(B,70),fill=WHITE)
d.text((80,380),"y el precio rebota",font=f(B,70),fill=GOLD)
cards=[("BITCOIN","$77.700","+1,3% hoy",GREEN),
       ("ETHEREUM","$2.287","+1,6% hoy",GREEN),
       ("ETF BTC (2 DÍAS)","−$1.042 M","30 oct + 2 nov",RED)]
cw=293; y0=500
for i,(t,v,s,c) in enumerate(cards):
    x=80+i*(cw+20)
    d.rounded_rectangle([x,y0,x+cw,y0+170],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((x+22,y0+22),t,font=f(B,20),fill=GREY)
    d.text((x+22,y0+58),v,font=f(B,42),fill=WHITE)
    d.text((x+22,y0+122),s,font=f(R,20),fill=c)
ny=705
rows=[("BLACKROCK","IBIT: salida de −$405 M el 2 de nov.","Fidelity (FBTC) apenas +$6,7 M ese día."),
      ("EE. UU.","Hoy se vota en las elecciones de mitad","de mandato. Resultados esta noche.")]
for i,(tag,l1,l2) in enumerate(rows):
    y=ny+i*118
    d.rounded_rectangle([80,y,1000,y+100],radius=16,fill=CARD,outline=EDGE,width=2)
    d.rounded_rectangle([98,y+30,250,y+70],radius=10,fill=GOLD)
    d.text((174,y+50),tag,font=f(B,19),fill=(11,15,26),anchor="mm")
    d.text((272,y+20),l1,font=f(B,24),fill=WHITE)
    d.text((272,y+56),l2,font=f(R,22),fill=GREY)
d.text((80,950),"Flujo de ETF = dinero que entra o sale de los fondos",font=f(R,26),fill=GREY)
d.text((80,1005),"Cómo leer los flujos sin enloquecer:",font=f(B,32),fill=GOLD)
items=["Un solo día no marca tendencia","Míralos junto al precio, no solos","Son contexto, no una señal de entrada"]
for i,t in enumerate(items):
    yy=1060+i*46
    d.text((80,yy),"✓",font=f(B,30),fill=GREEN); d.text((125,yy+2),t,font=f(R,28),fill=WHITE)
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1246),"Datos: SoSoValue vía crypto.news, TradingView",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-11/2026-11-03_pm_mercado_etf_flujos.jpg",quality=92)
