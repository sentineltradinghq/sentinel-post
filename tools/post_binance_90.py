from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(18,25,41); LINE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.rounded_rectangle([780,74,1000,118],radius=8,fill=RED)
d.text((890,96),"ACTUALIZACIÓN",font=f(B,22),fill=WHITE,anchor="mm")
d.text((80,125),"Hackeo a Binance · 31 de octubre",font=f(R,26),fill=GREY)
d.text((80,200),"90%",font=f(B,150),fill=GOLD)
d.text((500,215),"de los activos",font=f(B,44),fill=WHITE)
d.text((500,270),"robados ya fue",font=f(B,44),fill=WHITE)
d.text((500,325),"repuesto",font=f(B,44),fill=WHITE)
# barra progreso
y=420
d.rounded_rectangle([80,y,1000,y+44],radius=10,fill=PANEL)
d.rounded_rectangle([80,y,80+int(920*0.9),y+44],radius=10,fill=GREEN)
x80=80+int(920*0.8); d.line([(x80,y-8),(x80,y+52)],fill=WHITE,width=3)
d.text((x80,y+80),"Ayer: 80%",font=f(R,24),fill=GREY,anchor="rm")
d.text((100,y+22),"Hoy: 90% repuesto",font=f(B,26),fill=(11,15,26),anchor="lm")
d.text((1000,y+80),"Falta 10%",font=f(R,24),fill=GREY,anchor="rm")
rows=[("RETIROS","Plan: reabrir el domingo 1 de noviembre,","si pasan las revisiones de seguridad.",GOLD),
      ("PRUEBA DE RESERVAS","Nueva foto del 31 oct: 10 tokens al 100%.","Prueba completa esperada hacia el 3 nov.",GREEN),
      ("PÉRDIDAS","Binance dice que las cubre la empresa,","no los usuarios (tesorería y fondo SAFU).",WHITE)]
y=560
for t,l1,l2,c in rows:
    d.rounded_rectangle([80,y,1000,y+150],radius=16,fill=PANEL,outline=LINE,width=2)
    d.rectangle([80,y+18,88,y+132],fill=c)
    d.text((115,y+22),t,font=f(B,28),fill=c)
    d.text((115,y+66),l1,font=f(R,28),fill=WHITE)
    d.text((115,y+104),l2,font=f(R,28),fill=GREY)
    y+=170
d.text((80,1080),"Hackeo de $6.300 M. Aún falta reponer el 10%.",font=f(R,28),fill=GREY)
d.text((80,1130),"La lección no cambia:",font=f(R,32),fill=WHITE)
d.text((80,1172),"no guardes todo en un exchange.",font=f(B,40),fill=GOLD)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1295),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-10/2026-10-31_especial_binance_90.jpg",quality=92,subsampling=0)
