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
d.text((80,125),"Educación · Psicología del trading",font=f(R,26),fill=GREY)
d.text((80,200),"Sesgo de confirmación",font=f(B,62),fill=WHITE)
d.text((80,280),"solo ves lo que quieres ver",font=f(B,40),fill=GOLD)

# Espiral
d.rounded_rectangle([80,355,1000,650],radius=20,fill=PANEL)
d.text((110,378),"LA TRAMPA, PASO A PASO",font=f(B,22),fill=GOLD)
steps=[("1","Abres un largo","\"BTC va a subir\""),
       ("2","Lees solo lo","que te da la razón"),
       ("3","Lo contrario","lo llamas \"ruido\""),
       ("4","Mueves el stop","y la pérdida crece")]
bw=205; gap=0
for i,(n,a,b) in enumerate(steps):
    x=110+i*222
    c=RED if i==3 else GOLD
    d.ellipse([x,425,x+56,481],outline=c,width=3)
    d.text((x+28,453),n,font=f(B,28),fill=c,anchor="mm")
    if i<3: d.text((x+90,453),"→",font=f(B,34),fill=GREY,anchor="lm")
    d.text((x,505),a,font=f(B,20),fill=WHITE)
    d.text((x,540),b,font=f(R,19),fill=GREY)
d.text((110,595),"No pierdes por no saber. Pierdes por no querer ver.",font=f(B,25),fill=RED)

# Ejemplo
d.rounded_rectangle([80,680,1000,890],radius=20,fill=PANEL)
d.text((110,702),"EJEMPLO DE ESTAS SEMANAS",font=f(B,22),fill=GOLD)
d.text((110,742),"BTC encadena semanas en rojo y tú estás en largo.",font=f(R,26),fill=WHITE)
d.text((110,782),"Un tuit alcista:",font=f(R,26),fill=GREY)
d.text((970,780),"\"¡La prueba!\"",font=f(B,27),fill=GREEN,anchor="ra")
d.text((110,824),"Salidas de ETF, IPC caliente:",font=f(R,26),fill=GREY)
d.text((970,822),"\"Da igual\"",font=f(B,27),fill=RED,anchor="ra")

d.text((80,925),"Cómo combatirlo:",font=f(B,32),fill=WHITE)
pts=[("Antes de entrar:","escribe qué invalida tu idea."),
     ("Busca a propósito","el argumento contrario."),
     ("El stop decide,","no tu opinión."),
     ("Revisa tu diario:","¿qué señal ignoraste?")]
for i,(a,b) in enumerate(pts):
    y=978+i*50
    d.text((82,y),"•",font=f(B,28),fill=GOLD)
    d.text((115,y),a,font=f(B,27),fill=WHITE)
    w=d.textlength(a,font=f(B,27))
    d.text((115+w+12,y+1),b,font=f(R,27),fill=GREY)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-11_am_sesgo_confirmacion.jpg",quality=92)
