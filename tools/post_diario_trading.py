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
d.text((80,125),"Educación · Hábitos de trading",font=f(R,26),fill=GREY)
d.text((80,205),"Tu diario de trading:",font=f(B,64),fill=WHITE)
d.text((80,285),"lo que no se anota, se repite",font=f(B,48),fill=GOLD)
d.text((80,355),"Una ficha por operación. Así se ve una:",font=f(R,29),fill=GREY)

px0,py0,px1,py1=80,415,1000,845
d.rounded_rectangle([px0,py0,px1,py1],radius=20,fill=PANEL)
d.text((110,440),"OPERACIÓN #27",font=f(B,26),fill=GOLD)
d.text((px1-30,442),"Ejemplo ilustrativo",font=f(R,20),fill=(90,98,115),anchor="ra")
rows=[("Activo / dirección","BTC · Largo",WHITE),
      ("Por qué entré","Estaba en mi plan, no por impulso",WHITE),
      ("Stop / objetivo","Definidos ANTES de entrar",WHITE),
      ("Riesgo","1% de la cuenta",WHITE),
      ("Resultado","−1R  (tocó el stop)",RED),
      ("Cómo me sentí","Ansioso: quise mover el stop",GREY),
      ("Lección","Lo respeté. Pérdida controlada.",GREEN)]
for i,(k,v,c) in enumerate(rows):
    y=490+i*49
    d.text((110,y),k,font=f(R,26),fill=GREY)
    d.text((470,y),v,font=f(B,26),fill=c)
    if i<len(rows)-1: d.line([(110,y+40),(970,y+40)],fill=LINE,width=1)

d.text((80,880),"Por qué funciona:",font=f(B,36),fill=GREEN)
ok=[("Ves tus errores repetidos con datos.","No con la memoria, que siempre te favorece."),
    ("Separas mala suerte de mala decisión.","Perder siguiendo el plan no es un error."),
    ("Revísalo cada semana.","Busca un patrón y corrige una sola cosa.")]
for i,(a,b) in enumerate(ok):
    yy=938+i*90
    d.text((82,yy),"✓",font=f(B,30),fill=GREEN)
    d.text((125,yy),a,font=f(B,28),fill=WHITE)
    d.text((125,yy+38),b,font=f(R,25),fill=GREY)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-06_am_diario_trading.jpg",quality=92)
