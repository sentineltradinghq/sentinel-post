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
d.text((80,200),"Overtrading",font=f(B,66),fill=WHITE)
d.text((80,285),"más operaciones no es más ganancia",font=f(B,38),fill=GOLD)

# Comparativa comisiones
d.rounded_rectangle([80,360,1000,700],radius=20,fill=PANEL)
d.text((110,383),"LO QUE CUESTA OPERAR DE MÁS",font=f(B,22),fill=GOLD)
d.text((110,420),"Ej.: comisión ida y vuelta ≈ 0,1 %, cada operación con todo tu saldo",font=f(R,22),fill=GREY)
cols=[("3 al día",3,GREEN),("20 al día",20,RED)]
for i,(lab,n,c) in enumerate(cols):
    x=110+i*450
    d.text((x,465),lab,font=f(B,30),fill=WHITE)
    d.text((x,510),"Comisiones al mes (22 días):",font=f(R,21),fill=GREY)
    pct=n*22*0.1
    d.text((x,545),f"{pct:.1f} %".replace(".",","),font=f(B,52),fill=c)
    d.text((x,615),"de tu saldo, solo en comisiones" if i==0 else "de tu saldo, antes de ganar nada",font=f(R,21),fill=GREY)
d.line([(540,465),(540,650)],fill=LINE,width=2)

d.text((80,735),"Señales de que operas de más:",font=f(B,32),fill=WHITE)
sig=["Entras por aburrimiento, no por tu plan.",
     "Abres otra justo después de cerrar una.",
     "Operas sin tener tu señal clara."]
for i,s in enumerate(sig):
    y=788+i*46
    d.text((82,y),"•",font=f(B,28),fill=RED)
    d.text((115,y),s,font=f(R,27),fill=GREY)

d.text((80,945),"Cómo frenarlo:",font=f(B,32),fill=WHITE)
pts=[("Límite diario:","máximo de operaciones."),
     ("Solo tu setup:","si no aparece, no entras."),
     ("Pausa tras","2 pérdidas seguidas."),
     ("No operar","también es una decisión.")]
for i,(a,b) in enumerate(pts):
    y=998+i*48
    d.text((82,y),"•",font=f(B,28),fill=GOLD)
    d.text((115,y),a,font=f(B,27),fill=WHITE)
    w=d.textlength(a,font=f(B,27))
    d.text((115+w+12,y+1),b,font=f(R,27),fill=GREY)
d.line([(80,1235),(1000,1235)],fill=LINE,width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-12_am_overtrading.jpg",quality=92)
