from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26))
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(20,27,43); LINE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Educación · Cripto a largo plazo",font=f(R,26),fill=GREY)
d.text((80,205),"DCA: comprar por partes",font=f(B,62),fill=WHITE)
d.text((80,283),"el mismo monto, cada mes, sin adivinar",font=f(B,40),fill=GOLD)
d.text((80,345),"Ejemplo: $100 en BTC cada mes, 4 meses.",font=f(R,29),fill=GREY)

px0,py0,px1,py1=80,400,1000,820
d.rounded_rectangle([px0,py0,px1,py1],radius=20,fill=PANEL)
d.text((110,425),"MES",font=f(B,22),fill=GOLD)
d.text((330,425),"PRECIO BTC",font=f(B,22),fill=GOLD)
d.text((970,425),"COMPRAS",font=f(B,22),fill=GOLD,anchor="ra")
rows=[("1","$80.000","0,00125 BTC"),("2","$60.000","0,00167 BTC"),("3","$70.000","0,00143 BTC"),("4","$75.000","0,00133 BTC")]
for i,(m,p,q) in enumerate(rows):
    y=472+i*52
    d.text((110,y),m,font=f(B,28),fill=WHITE)
    d.text((330,y),p,font=f(R,28),fill=WHITE)
    d.text((970,y),q,font=f(B,28),fill=WHITE,anchor="ra")
    d.line([(110,y+42),(970,y+42)],fill=LINE,width=1)
d.text((110,690),"Total: $400  →  0,00568 BTC",font=f(B,28),fill=WHITE)
d.text((110,735),"Tu precio promedio:",font=f(R,27),fill=GREY)
d.text((970,733),"≈ $70.440",font=f(B,30),fill=GREEN,anchor="ra")
d.text((110,775),"Promedio simple de los 4 precios:",font=f(R,24),fill=GREY)
d.text((970,775),"$71.250",font=f(R,24),fill=GREY,anchor="ra")
d.text((px1-30,py1+12),"Ejemplo ilustrativo",font=f(R,20),fill=(90,98,115),anchor="ra")

d.text((80,870),"Lo que SÍ hace y lo que NO:",font=f(B,34),fill=WHITE)
pts=[("✓",GREEN,"Compras más cuando baja, menos cuando sube.","Y te quita la presión de acertar el momento."),
     ("✗",RED,"No evita pérdidas.","Si BTC cae a $60.000, tus $400 valen ≈ $341 (−15%)."),
     ("✗",RED,"No es promediar una operación perdedora.","Y nunca con apalancamiento.")]
for i,(s,c,a,b) in enumerate(pts):
    yy=928+i*92
    d.text((82,yy),s,font=f(B,30),fill=c)
    d.text((125,yy),a,font=f(B,28),fill=WHITE)
    d.text((125,yy+38),b,font=f(R,25),fill=GREY)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-07_am_dca.jpg",quality=92)
