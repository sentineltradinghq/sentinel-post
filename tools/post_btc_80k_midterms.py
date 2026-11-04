from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(18,25,41); LINE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.rounded_rectangle([830,74,1000,118],radius=8,fill=GREEN)
d.text((915,96),"ESPECIAL",font=f(B,22),fill=(11,15,26),anchor="mm")
d.text((80,125),"Midterms en EE. UU. · 4 de noviembre",font=f(R,26),fill=GREY)
d.text((80,190),"BITCOIN SE DA LA VUELTA",font=f(B,52),fill=WHITE)
d.text((80,260),"$80.000",font=f(B,130),fill=GOLD)
d.text((80,410),"De menos de $76K en la madrugada a $81K",font=f(R,32),fill=GREY)
# barra rango del dia
y=480; x0,x1=80,1000
d.rounded_rectangle([x0,y,x1,y+40],radius=10,fill=PANEL)
d.rounded_rectangle([x0,y,x1,y+40],radius=10,fill=GREEN)
d.text((x0,y+60),"Mín. $75.736",font=f(B,26),fill=RED)
d.text((x1,y+60),"Máx. $81.196",font=f(B,26),fill=GREEN,anchor="ra")
d.text((540,y+20),"+7,2% del mínimo al máximo",font=f(B,26),fill=(11,15,26),anchor="mm")
rows=[("QUÉ PASÓ","Los demócratas ganan el Congreso. Primero miedo","y caída; luego Wall Street sube y cripto lo sigue.",GOLD),
      ("$415 MILLONES LIQUIDADOS","Al cruzar $80K, muchos que apostaban a la baja","fueron cerrados a la fuerza (short squeeze).",RED),
      ("ETH Y SOL TAMBIÉN","ETH ~$2.420 (+6%) · SOL ~$95 (+2%).","Pero los ETF de BTC: -$1.160 M en 3 días.",WHITE)]
y=600
for t,l1,l2,c in rows:
    d.rounded_rectangle([80,y,1000,y+150],radius=16,fill=PANEL,outline=LINE,width=2)
    d.rectangle([80,y+18,88,y+132],fill=c)
    d.text((115,y+22),t,font=f(B,28),fill=c)
    d.text((115,y+66),l1,font=f(R,26),fill=WHITE)
    d.text((115,y+104),l2,font=f(R,26),fill=GREY)
    y+=170
d.text((80,1120),"Miedo en la noche, euforia en la tarde.",font=f(R,30),fill=WHITE)
d.text((80,1165),"Un plan no cambia con cada titular.",font=f(B,38),fill=GOLD)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1295),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-04_especial_btc_80k_midterms.jpg",quality=92,subsampling=0)
