from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26))
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(20,27,43)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Educación · Gestión de riesgo",font=f(R,26),fill=GREY)
d.text((80,215),"Puedes fallar",font=f(B,76),fill=WHITE)
d.text((80,303),"6 de cada 10",font=f(B,76),fill=GOLD)
d.text((80,391),"y aun así ganar",font=f(B,76),fill=WHITE)
d.text((80,490),"La clave: la relación riesgo / beneficio (R:B)",font=f(R,30),fill=GREY)
# panel: 10 trades
d.rounded_rectangle([80,560,1000,850],radius=22,fill=PANEL)
d.text((115,585),"10 operaciones · arriesgas 1 para ganar 2",font=f(B,30),fill=WHITE)
res=["W","L","L","W","L","W","L","L","W","L"]
for i,r in enumerate(res):
    x=118+i*86; c=GREEN if r=="W" else RED
    d.rounded_rectangle([x,645,x+68,725],radius=12,fill=c)
    d.text((x+34,685),"+2" if r=="W" else "−1",font=f(B,28),fill=(11,15,26),anchor="mm")
d.text((115,760),"4 ganadas × 2 = +8",font=f(B,30),fill=GREEN)
d.text((480,760),"6 perdidas × 1 = −6",font=f(B,30),fill=RED)
d.text((115,802),"Resultado: +2 aunque perdiste la mayoría",font=f(R,28),fill=WHITE)
# table
d.text((80,885),"Acierto mínimo para no perder (sin comisiones):",font=f(B,30),fill=WHITE)
rows=[("R:B 1:1","50%"),("R:B 1:2","33%"),("R:B 1:3","25%")]
for i,(a,b) in enumerate(rows):
    y=940+i*62
    d.text((110,y),a,font=f(B,32),fill=GOLD)
    for xx in range(330,800,18): d.line([(xx,y+20),(xx+8,y+20)],fill=(60,70,95),width=2)
    d.text((960,y),b,font=f(B,32),fill=WHITE,anchor="ra")
d.text((80,1135),"Ojo: un R:B alto no sirve si el objetivo es irreal.",font=f(R,27),fill=GREY)
d.text((80,1172),"Define stop y objetivo ANTES de entrar.",font=f(B,27),fill=GOLD)
d.line([(80,1225),(1000,1225)],fill=(40,48,66),width=2)
d.text((80,1245),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1288),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-01_am_riesgo_beneficio.jpg",quality=92)
