from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60)
PANEL=(20,27,44); EDGE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Proyecto · Transparencia",font=f(R,26),fill=GREY)
d.text((80,215),"Cada cierre,",font=f(B,80),fill=WHITE)
d.text((80,308),"a la vista.",font=f(B,80),fill=GOLD)
d.text((80,418),"Ganadas y perdidas. Sin filtro.",font=f(R,34),fill=GREY)
steps=[("1","El bot cierra una operación","Solo cierres, nunca entradas."),
       ("2","Su tarjeta llega al Discord","Resultado en %, gane o pierda."),
       ("3","Resumen semanal cada domingo","7:00 p. m. en nuestras redes.")]
y=505
for n,t,s in steps:
    d.rounded_rectangle([80,y,1000,y+128],radius=20,fill=PANEL,outline=EDGE,width=2)
    d.ellipse([110,y+29,180,y+99],fill=GOLD)
    d.text((145,y+64),n,font=f(B,38),fill=(11,15,26),anchor="mm")
    d.text((210,y+30),t,font=f(B,34),fill=WHITE)
    d.text((210,y+76),s,font=f(R,27),fill=GREY)
    y+=150
# result tags
y=965
d.rounded_rectangle([80,y,520,y+90],radius=18,outline=GREEN,width=3)
d.text((300,y+45),"GANADA: se publica",font=f(B,30),fill=GREEN,anchor="mm")
d.rounded_rectangle([560,y,1000,y+90],radius=18,outline=RED,width=3)
d.text((780,y+45),"PERDIDA: también",font=f(B,30),fill=RED,anchor="mm")
d.text((80,1085),"Mañana domingo: primer resumen semanal.",font=f(B,32),fill=GOLD)
d.text((80,1132),"Forward test en vivo, sin capital real.",font=f(R,27),fill=GREY)
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-10/2026-10-31_pm_transparencia_cierres.jpg",quality=92)
