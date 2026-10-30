from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); CARD=(20,27,44); EDGE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Mercado cripto · 30 oct 2026",font=f(R,26),fill=GREY)
d.text((80,210),"Viernes de miedo",font=f(B,76),fill=WHITE)
d.text((80,300),"en cripto.",font=f(B,76),fill=WHITE)
d.text((80,390),"¿Y la disciplina?",font=f(B,76),fill=GOLD)
# tarjetas
cards=[("BITCOIN","$76.870","−5,6% en 7 días",RED),
       ("LIQUIDACIONES","$1.570 M","tras el hackeo a Binance",RED),
       ("ETHEREUM","$2.239","−6,8% en 7 días",RED)]
cw=293; y0=510
for i,(t,v,s,c) in enumerate(cards):
    x=80+i*(cw+20)
    d.rounded_rectangle([x,y0,x+cw,y0+170],radius=18,fill=CARD,outline=EDGE,width=2)
    d.text((x+22,y0+22),t,font=f(B,20),fill=GREY)
    d.text((x+22,y0+58),v,font=f(B,44),fill=WHITE)
    d.text((x+22,y0+122),s,font=f(R,20),fill=c)
# medidor miedo/codicia
gy=760
d.text((80,gy),"Índice de Miedo y Codicia",font=f(B,28),fill=WHITE)
d.text((1000,gy),"30 · MIEDO",font=f(B,28),fill=RED,anchor="ra")
by=gy+60; bx0,bx1=80,1000
for i in range(bx1-bx0):
    t=i/(bx1-bx0)
    if t<0.5: c=tuple(int(RED[k]+(GOLD[k]-RED[k])*t*2) for k in range(3))
    else: c=tuple(int(GOLD[k]+(GREEN[k]-GOLD[k])*(t-0.5)*2) for k in range(3))
    d.line([(bx0+i,by),(bx0+i,by+22)],fill=c)
def mark(val,col,lab,up):
    x=bx0+(bx1-bx0)*val/100
    d.polygon([(x-12,by-16),(x+12,by-16),(x,by-2)] if up else [(x-12,by+40),(x+12,by+40),(x,by+24)],fill=col)
    d.text((x,by-24 if up else by+46),lab,font=f(B,22),fill=col,anchor="md" if up else "ma")
mark(30,WHITE,"hoy 30",False); mark(51,GREY,"ayer 51",False)
d.text((80,by+90),"BTC en mínimos de 6 semanas · soporte clave: $75.000",font=f(R,26),fill=GREY)
# disciplina
d.text((80,985),"En días así, un sistema no improvisa:",font=f(B,32),fill=GOLD)
items=["Riesgo por operación definido antes de entrar","Stop puesto de antemano, no por nervios","Cero decisiones por pánico ni por FOMO"]
for i,t in enumerate(items):
    yy=1045+i*48
    d.text((80,yy),"✓",font=f(B,30),fill=GREEN); d.text((125,yy+2),t,font=f(R,28),fill=WHITE)
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
d.text((1000,1287),"Datos: Yahoo Finance, alternative.me",font=f(R,18),fill=GREY,anchor="ra")
img.save("posts/2026-10/2026-10-30_pm_mercado_miedo_disciplina.jpg",quality=92)
