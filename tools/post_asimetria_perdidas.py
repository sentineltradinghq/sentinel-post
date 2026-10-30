from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26))
d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Educación · Gestión de riesgo",font=f(R,26),fill=GREY)
d.text((80,215),"Si pierdes el 50%,",font=f(B,72),fill=WHITE)
d.text((80,300),"necesitas ganar",font=f(B,72),fill=WHITE)
d.text((80,385),"el 100%",font=f(B,72),fill=GOLD)
d.text((420,385),"para volver",font=f(B,72),fill=WHITE)
# table header
y0=520
d.text((80,y0),"Pierdes",font=f(B,28),fill=RED)
d.text((330,y0),"Para recuperarte necesitas ganar",font=f(B,28),fill=GREEN)
rows=[(10,11.1),(20,25),(30,42.9),(50,100),(75,300)]
maxbar=640; scale=maxbar/300
for i,(l,g) in enumerate(rows):
    y=y0+60+i*78
    d.text((80,y),f"−{l}%",font=f(B,40),fill=RED)
    w=max(int(g*scale),8)
    c=GOLD if l==50 else GREEN
    d.rounded_rectangle([330,y+4,330+w,y+44],radius=6,fill=c)
    txt=f"+{g:g}%"
    tw=d.textlength(txt,font=f(B,32))
    tx=330+w+16 if 330+w+16+tw<1010 else 330+w-tw-16
    d.text((tx,y+6),txt,font=f(B,32),fill=WHITE if tx>330+w else (11,15,26))
lines=["Las pérdidas pesan más que las ganancias.",
       "Por eso lo primero no es ganar mucho:"]
for i,l in enumerate(lines): d.text((80,990+i*42),l,font=f(R,30),fill=WHITE)
d.text((80,1080),"es no perder mucho.",font=f(B,40),fill=GOLD)
d.text((80,1148),"✔ Riesgo pequeño por operación  ✔ Stop siempre",font=f(B,26),fill=GREY)
d.line([(80,1215),(1000,1215)],fill=(40,48,66),width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-10/2026-10-30_am_asimetria_perdidas.jpg",quality=92)
