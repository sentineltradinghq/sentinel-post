from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; I="/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); RED=(231,76,60); GREEN=(46,204,113); CARD=(20,27,43)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,70),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,112),"Hackeo a Binance · 30 oct, mediodía",font=f(R,26),fill=GREY)
d.text((80,175),"Lo que dijo",font=f(B,64),fill=WHITE)
d.text((80,250),"Binance",font=f(B,64),fill=GOLD)
quotes=[("“Los fondos de los usuarios","están seguros.”"),("“Cubriremos todas las pérdidas.”",""),
        ("“No fue un ataque de un solo clic;","fue un proceso más complejo.”")]
y=360
for a,b in quotes:
    h=110 if b else 70
    d.rounded_rectangle([80,y,1000,y+h],radius=16,fill=CARD)
    d.rectangle([80,y,88,y+h],fill=GOLD)
    d.text((110,y+16),a,font=f(I,30),fill=WHITE)
    if b: d.text((110,y+58),b,font=f(I,30),fill=WHITE)
    y+=h+18
rows=[("Robado","≈ $6.300 millones"),("Congelado","≈ $3.000 millones"),
      ("Causa","Laptop comprometida de un ingeniero"),("","  (sin filtración de claves, según Binance)"),
      ("Retiros","Volverían en ~48 h (domingo)"),("Cobertura","Fondo SAFU + reservas de la empresa"),
      ("Ojo","Encontraron más puntos de brecha")]
y+=10
for k,v in rows:
    d.text((80,y),k,font=f(B,28),fill=GOLD); d.text((280,y),v,font=f(R,28),fill=WHITE if k!="Ojo" else RED); y+=50
d.line([(80,1215),(1000,1215)],fill=(40,48,66),width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Información en desarrollo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((80,1110),"Citas traducidas del inglés (Binance y su co-CEO Richard Teng).",font=f(R,24),fill=GREY)
img.save("posts/2026-10/2026-10-30_binance_comunicado_oficial.jpg",quality=92)
print(y)
