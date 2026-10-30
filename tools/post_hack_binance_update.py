from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); RED=(231,76,60); GREEN=(46,204,113); CARD=(20,27,43)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,70),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,112),"Actualización · 30 oct 2026",font=f(R,26),fill=GREY)
d.text((80,180),"Hackeo a Binance:",font=f(B,64),fill=WHITE)
d.text((80,255),"lo nuevo",font=f(B,64),fill=GOLD)
d.rounded_rectangle([80,355,1000,480],radius=18,fill=CARD)
d.text((110,372),"$6.300 millones",font=f(B,52),fill=RED)
d.text((110,437),"confirmado por Binance · récord histórico",font=f(R,27),fill=GREY)
rows=[("¿Cómo?","Laptop comprometida de un ingeniero"),
      ("¿Quién?","Corea del Norte (TraderTraitor/Lazarus),"),
      ("","  según la firma TRM"),
      ("Congelado","≈ $2.500 – 3.000 millones"),
      ("Retiros","Suspendidos por ahora"),
      ("Usuarios","Binance promete cubrir las pérdidas"),
      ("Fondo SAFU","≈ $1.000 M en BTC"),
      ("1 de nov.","Nueva prueba de reservas")]
y=520
for k,v in rows:
    d.text((80,y),k,font=f(B,29),fill=GOLD); d.text((300,y),v,font=f(R,29),fill=WHITE); y+=58
d.rounded_rectangle([80,1000,1000,1150],radius=18,fill=CARD)
d.text((110,1020),"Mercado",font=f(B,30),fill=WHITE)
d.text((110,1070),"BTC ≈ -5%  (< $77.000)   ·   ETH ≈ $2.230",font=f(R,30),fill=RED)
d.line([(80,1215),(1000,1215)],fill=(40,48,66),width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Información en desarrollo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-10/2026-10-30_hackeo_binance_actualizacion.jpg",quality=92)
