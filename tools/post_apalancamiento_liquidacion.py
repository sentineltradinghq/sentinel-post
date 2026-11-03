from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26))
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(20,27,43); BG=(11,15,26)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Educación · Gestión de riesgo",font=f(R,26),fill=GREY)
d.text((80,205),"Apalancamiento:",font=f(B,72),fill=WHITE)
d.text((80,290),"¿a cuánto estás",font=f(B,72),fill=WHITE)
d.text((80,375),"de la liquidación?",font=f(B,72),fill=RED)
# panel bars
d.rounded_rectangle([80,485,1000,905],radius=22,fill=PANEL)
d.text((115,508),"Movimiento en contra que borra tu margen",font=f(B,28),fill=WHITE)
d.text((115,548),"(aprox., margen aislado)",font=f(R,22),fill=GREY)
rows=[("2x",50),("5x",20),("10x",10),("20x",5),("50x",2),("100x",1)]
maxw=600
for i,(lev,pct) in enumerate(rows):
    y=595+i*50
    d.text((115,y+18),lev,font=f(B,28),fill=GOLD,anchor="lm")
    w=max(8,int(maxw*pct/50))
    c=GREEN if pct>=20 else (GOLD if pct>=10 else RED)
    d.rounded_rectangle([215,y+4,215+w,y+32],radius=8,fill=c)
    d.text((215+w+15,y+18),f"−{pct}%",font=f(B,26),fill=WHITE,anchor="lm")
# key lesson
d.text((80,945),"Lo que importa:",font=f(B,36),fill=GOLD)
rules=[("1","Bitcoin se mueve 5% en un día sin avisar."),
       ("2","Tu stop debe estar ANTES de la liquidación."),
       ("3","Calcula el tamaño por riesgo, no por la x."),]
for i,(n,t) in enumerate(rules):
    y=995+i*60
    d.ellipse([82,y,128,y+46],fill=GOLD)
    d.text((105,y+23),n,font=f(B,26),fill=BG,anchor="mm")
    d.text((150,y+23),t,font=f(R,30),fill=WHITE,anchor="lm")
d.text((80,1180),"El apalancamiento no es el enemigo. El tamaño sí.",font=f(B,30),fill=GREEN)
d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-03_am_apalancamiento_liquidacion.jpg",quality=92)
