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
d.text((80,125),"Educación · Psicología del trading",font=f(R,26),fill=GREY)
d.text((80,210),"Operar por",font=f(B,80),fill=WHITE)
d.text((80,300),"venganza",font=f(B,80),fill=RED)
d.text((80,400),"El error que convierte una pérdida en diez",font=f(R,30),fill=GREY)
# spiral panel
d.rounded_rectangle([80,465,1000,745],radius=22,fill=PANEL)
d.text((115,488),"La espiral",font=f(B,30),fill=WHITE)
steps=[("Pérdida","−1%"),("Rabia","\"la recupero ya\""),("Más tamaño","sin plan"),("Pérdida","−5%")]
xs=[115,340,565,790]
for i,((a,b),x) in enumerate(zip(steps,xs)):
    c=RED if i in (0,3) else GOLD
    d.rounded_rectangle([x,545,x+195,655],radius=14,outline=c,width=3)
    d.text((x+97,580),a,font=f(B,25 if len(a)>8 else 27),fill=c,anchor="mm")
    d.text((x+97,622),b,font=f(R,21),fill=WHITE,anchor="mm")
    if i<3:
        ax=x+200; d.polygon([(ax,592),(ax+20,600),(ax,608)],fill=GREY)
d.text((115,690),"Y vuelve a empezar, cada vez más grande.",font=f(R,26),fill=GREY)
# rules
d.text((80,790),"Cómo cortarla:",font=f(B,36),fill=GOLD)
rules=[("1","Límite diario: llegas a él y cierras por hoy."),
       ("2","Pausa obligatoria después de cada pérdida."),
       ("3","Nunca subas el tamaño para recuperar."),
       ("4","Pregúntate: ¿esta entrada estaba en mi plan?")]
for i,(n,t) in enumerate(rules):
    y=855+i*68
    d.ellipse([82,y,128,y+46],fill=GOLD)
    d.text((105,y+23),n,font=f(B,26),fill=BG,anchor="mm")
    d.text((150,y+23),t,font=f(R,30),fill=WHITE,anchor="lm")
d.text((80,1140),"El mercado no te debe nada.",font=f(B,32),fill=WHITE)
d.text((80,1182),"Mañana también habrá oportunidades.",font=f(B,32),fill=GREEN)
d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-02_am_trading_venganza.jpg",quality=92)
