from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26))
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(18,25,41)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Educación · Gestión de riesgo",font=f(R,26),fill=GREY)
d.text((80,205),"La regla del",font=f(B,72),fill=WHITE)
d.text((80+d.textlength("La regla del ",font=f(B,72)),205),"1%",font=f(B,72),fill=GOLD)
d.text((80,295),"¿Cuánto arriesgar por operación?",font=f(B,38),fill=WHITE)
# chart
y0=395
d.text((80,y0),"Tu cuenta después de 10 pérdidas seguidas",font=f(B,28),fill=GREY)
rows=[(1,90.4),(2,81.7),(5,59.9),(10,34.9)]
x0=350; maxbar=650
for i,(r,left) in enumerate(rows):
    y=y0+60+i*80
    c=GREEN if r==1 else (GOLD if r==2 else RED)
    lab=f"Arriesgas {r}%"
    d.text((80,y+6),lab,font=f(B,29),fill=c)
    w=int(left/100*maxbar)
    d.rounded_rectangle([x0,y+2,x0+maxbar,y+46],radius=6,fill=PANEL)
    d.rounded_rectangle([x0,y+2,x0+w,y+46],radius=6,fill=c)
    t=f"{left:.1f}%".replace(".",",")
    tw=d.textlength(t,font=f(B,30))
    d.text((x0+w-tw-14,y+8),t,font=f(B,30),fill=(11,15,26))
# formula panel
py=790
d.rounded_rectangle([80,py,1000,py+250],radius=18,fill=PANEL,outline=(40,48,66),width=2)
d.text((110,py+28),"Cómo calcular tu posición",font=f(B,32),fill=GOLD)
d.text((110,py+80),"Posición = Riesgo en $ ÷ Distancia al stop",font=f(B,30),fill=WHITE)
d.text((110,py+135),"Ejemplo: cuenta de $1.000 · riesgo 1% = $10",font=f(R,28),fill=GREY)
d.text((110,py+178),"Stop a 5% de la entrada  →  posición de $200",font=f(R,28),fill=GREY)
lines=["Con 1% puedes equivocarte muchas veces",
       "y seguir en el juego."]
for i,l in enumerate(lines): d.text((80,1075+i*42),l,font=f(R,30),fill=WHITE)
d.text((80,1160),"Primero sobrevivir, luego ganar.",font=f(B,38),fill=GOLD)
d.line([(80,1225),(1000,1225)],fill=(40,48,66),width=2)
d.text((80,1245),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1288),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-10/2026-10-31_am_regla_1_por_ciento.jpg",quality=92,subsampling=0)
