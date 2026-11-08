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
d.text((80,125),"Educación · Ejecución de órdenes",font=f(R,26),fill=GREY)
d.text((80,200),"Orden de mercado vs límite",font=f(B,58),fill=WHITE)
d.text((80,275),"y el costo invisible: el slippage",font=f(B,40),fill=GOLD)

def panel(x0,title,sub,items):
    d.rounded_rectangle([x0,350,x0+445,720],radius=20,fill=PANEL)
    d.text((x0+28,375),title,font=f(B,34),fill=GOLD)
    d.text((x0+28,422),sub,font=f(R,24),fill=GREY)
    for i,(s,c,a,b) in enumerate(items):
        y=478+i*78
        d.text((x0+28,y),s,font=f(B,26),fill=c)
        d.text((x0+62,y),a,font=f(B,24),fill=WHITE)
        d.text((x0+62,y+33),b,font=f(R,21),fill=GREY)
panel(80,"MERCADO","Entras YA, al precio que haya.",
      [("✓",GREEN,"Se ejecuta seguro","Ideal para salir rápido."),
       ("✗",RED,"Puedes pagar más","Eso es el slippage."),
       ("✗",RED,"Comisión más alta","Suele ser tarifa taker.")])
panel(555,"LÍMITE","Tú fijas el precio y esperas.",
      [("✓",GREEN,"Precio exacto o mejor","Sin sorpresas."),
       ("✓",GREEN,"Comisión más baja","Suele ser tarifa maker."),
       ("✗",RED,"Puede no ejecutarse","Si el precio no llega.")])

d.rounded_rectangle([80,750,1000,1000],radius=20,fill=PANEL)
d.text((110,772),"EJEMPLO EN UN MOVIMIENTO RÁPIDO",font=f(B,22),fill=GOLD)
d.text((110,812),"Quieres comprar BTC a $75.000.",font=f(R,27),fill=WHITE)
d.text((110,852),"Con orden de mercado te llenan a $75.150.",font=f(R,27),fill=WHITE)
d.text((110,900),"Slippage:",font=f(R,27),fill=GREY)
d.text((970,898),"0,2 % peor",font=f(B,30),fill=RED,anchor="ra")
d.text((110,945),"Con 10x de apalancamiento:",font=f(R,27),fill=GREY)
d.text((970,943),"−2 % de tu margen",font=f(B,30),fill=RED,anchor="ra")
d.text((1000-30,1012),"Ejemplo ilustrativo",font=f(R,20),fill=(90,98,115),anchor="ra")

d.text((80,1045),"Regla práctica:",font=f(B,32),fill=WHITE)
pts=[("Entradas planeadas:","orden límite, con calma."),
     ("Salir por tu stop:","prioriza salir (mercado)."),
     ("Noticias o poco volumen:","evita la orden de mercado.")]
for i,(a,b) in enumerate(pts):
    y=1095+i*42
    d.text((82,y),"•",font=f(B,28),fill=GOLD)
    d.text((115,y),a,font=f(B,26),fill=WHITE)
    w=d.textlength(a,font=f(B,26))
    d.text((115+w+12,y+1),b,font=f(R,26),fill=GREY)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-08_am_orden_mercado_limite.jpg",quality=92)
