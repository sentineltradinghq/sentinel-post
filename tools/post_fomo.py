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
d.text((80,125),"Educación · Psicología del trading",font=f(R,26),fill=GREY)
d.text((80,205),"FOMO:",font=f(B,80),fill=WHITE)
d.text((80,295),"perseguir la vela verde",font=f(B,56),fill=GOLD)
d.text((80,380),"Cuando todos ya ganaron, tú entras... y el precio gira.",font=f(R,29),fill=GREY)

# Panel con gráfico ilustrativo de velas
px0,py0,px1,py1=80,440,1000,820
d.rounded_rectangle([px0,py0,px1,py1],radius=20,fill=PANEL)
# (open, close, high, low) en escala 0-100
velas=[(30,28,33,25),(28,31,33,26),(31,30,34,28),(30,34,36,29),(34,40,42,33),(40,52,54,39),
       (52,68,70,51),(68,88,95,66),(88,80,92,76),(80,66,82,62),(66,58,68,54),(58,61,63,55)]
cx0,cy_top,cy_bot=184,470,790
def Y(v): return cy_bot-(v/100)*(cy_bot-cy_top)
step=62
for i,(o,c,h,l) in enumerate(velas):
    x=cx0+i*step
    col=GREEN if c>=o else RED
    d.line([(x+15,Y(h)),(x+15,Y(l))],fill=col,width=3)
    d.rectangle([x,Y(max(o,c)),x+30,Y(min(o,c))],fill=col)
# marcadores
ix=cx0+7*step+15
d.ellipse([ix-14,Y(90)-14,ix+14,Y(90)+14],outline=GOLD,width=4)
d.text((ix-30,Y(90)-8),"Entras aquí",font=f(B,26),fill=GOLD,anchor="rm")
d.text((ix-30,Y(90)+26),"(por miedo a quedarte fuera)",font=f(R,22),fill=GREY,anchor="rm")
ex=cx0+10*step+15
d.text((ex+10,Y(52)+22),"Corrección",font=f(B,24),fill=RED,anchor="mm")
d.text((cx0-10,Y(12)),"Aquí nadie hablaba de esto",font=f(R,22),fill=GREY,anchor="lm")
d.text((px1-20,py1-14),"Ejemplo ilustrativo",font=f(R,18),fill=(90,98,115),anchor="rd")

d.text((80,850),"Cómo frenarlo:",font=f(B,36),fill=GREEN)
ok=[("Si no estaba en tu plan, no es tu operación.","Entrar por impulso no es una estrategia."),
    ("Pregúntate: ¿dónde va mi stop?","Si no lo sabes, no entres."),
    ("Después de un salto, espera un retroceso.","El mercado suele dar otra oportunidad."),
    ("Perderte una subida no te cuesta dinero.","Entrar mal en el techo, sí.")]
for i,(a,b) in enumerate(ok):
    yy=905+i*80
    d.text((82,yy),"✓",font=f(B,30),fill=GREEN)
    d.text((125,yy),a,font=f(B,28),fill=WHITE)
    d.text((125,yy+36),b,font=f(R,25),fill=GREY)
d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-05_am_fomo.jpg",quality=92)
