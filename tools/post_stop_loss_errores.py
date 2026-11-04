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
d.text((80,205),"El stop loss:",font=f(B,80),fill=WHITE)
d.text((80,295),"3 errores que salen caros",font=f(B,56),fill=GOLD)
d.text((80,380),"Tu stop es el seguro de tu cuenta. Úsalo bien.",font=f(R,30),fill=GREY)

errs=[("1","Operar sin stop","\"Si baja, espero a que vuelva\".",
       "Así una pérdida pequeña se vuelve enorme."),
      ("2","Moverlo en contra","Lo alejas cuando el precio se acerca.",
       "Rompes tu plan y agrandas la pérdida."),
      ("3","Ponerlo demasiado pegado","El ruido normal del precio te saca.",
       "Pierdes aunque tu idea fuera correcta.")]
y0=450
for i,(n,t,a,b) in enumerate(errs):
    y=y0+i*190
    d.rounded_rectangle([80,y,1000,y+170],radius=20,fill=PANEL)
    d.rounded_rectangle([80,y,90,y+170],radius=4,fill=RED)
    d.ellipse([115,y+28,165,y+78],outline=RED,width=4)
    d.text((140,y+53),"✕",font=f(B,28),fill=RED,anchor="mm")
    d.text((190,y+53),t,font=f(B,36),fill=WHITE,anchor="lm")
    d.text((190,y+100),a,font=f(R,27),fill=GREY)
    d.text((190,y+134),b,font=f(R,27),fill=WHITE)

d.text((80,1035),"Cómo hacerlo bien:",font=f(B,34),fill=GREEN)
ok=["Decide el stop ANTES de entrar, donde tu idea queda invalidada.",
    "Ajusta el tamaño de la posición, no la distancia del stop.",
    "Solo muévelo a favor (para proteger ganancias), nunca en contra."]
for i,t in enumerate(ok):
    yy=1088+i*42
    d.text((82,yy),"✓",font=f(B,28),fill=GREEN)
    d.text((120,yy),t,font=f(R,26),fill=WHITE)
d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-04_am_stop_loss_errores.jpg",quality=92)
