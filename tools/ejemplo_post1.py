from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26))
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60)
# grid
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Educación · Trading algorítmico",font=f(R,26),fill=GREY)
d.text((80,230),"¿Qué es una",font=f(B,78),fill=WHITE)
d.text((80,320),"vela de volumen",font=f(B,78),fill=WHITE)
d.text((80,410),"climático?",font=f(B,78),fill=GOLD)
# volume bars
base=900; x=90
vals=[60,75,55,80,65,70,58,72,260,90,70]
for i,v in enumerate(vals):
    c=GOLD if v>200 else (60,70,95)
    d.rectangle([x+i*82,base-v,x+i*82+56,base],fill=c)
avg=base-70
for xx in range(80,1000,24): d.line([(xx,avg),(xx+12,avg)],fill=GREY,width=3)
d.text((80,avg-40),"promedio de volumen",font=f(R,24),fill=GREY)
d.text((700,base-330),"3–4× el promedio",font=f(B,30),fill=GOLD)
lines=["Ese volumen incluye compras Y ventas chocando.",
       "Lo clave es qué venía haciendo el precio antes:"]
for i,l in enumerate(lines): d.text((80,945+i*42),l,font=f(R,30),fill=WHITE)
d.text((80,1040),"▼ Tras una caída: posible capitulación",font=f(B,28),fill=GREEN)
d.text((118,1076),"vendedores se rinden → podría rebotar",font=f(R,26),fill=GREY)
d.text((80,1118),"▲ Tras una subida: posible euforia",font=f(B,28),fill=RED)
d.text((118,1154),"compradores tarde → podría girar abajo",font=f(R,26),fill=GREY)
d.line([(80,1215),(1000,1215)],fill=(40,48,66),width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("post1_volumen_climatico.png")
