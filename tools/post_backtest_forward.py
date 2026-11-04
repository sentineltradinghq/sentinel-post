from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60)
PANEL=(20,27,44); EDGE=(40,48,66)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,80),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,125),"Proyecto · Cómo probamos",font=f(R,26),fill=GREY)
d.text((80,215),"Backtest vs",font=f(B,80),fill=WHITE)
d.text((80,308),"forward test",font=f(B,80),fill=GOLD)
d.text((80,418),"Por qué el pasado no basta.",font=f(R,34),fill=GREY)
# two panels
def panel(x0,title,sub,col,items,curve):
    d.rounded_rectangle([x0,500,x0+440,1050],radius=22,fill=PANEL,outline=col,width=3)
    d.text((x0+30,525),title,font=f(B,36),fill=col)
    d.text((x0+30,572),sub,font=f(R,24),fill=GREY)
    # mini curve
    pts=[(x0+40+i*(360/(len(curve)-1)),800-v) for i,v in enumerate(curve)]
    d.line([(x0+40,800),(x0+400,800)],fill=EDGE,width=2)
    d.line(pts,fill=col,width=5,joint="curve")
    y=835
    for it in items:
        d.text((x0+30,y),"• "+it[0],font=f(B,25),fill=WHITE)
        d.text((x0+56,y+33),it[1],font=f(R,22),fill=GREY)
        y+=70
panel(80,"BACKTEST","Datos del pasado",GREY,
      [("Rápido y barato","años en minutos"),("Riesgo: sobreajuste","perfecto solo en el pasado"),("Sin fricción real","ni deslizamientos ni fallos")],
      [10,40,35,70,90,85,120,150,145,180,200])
panel(560,"FORWARD","Mercado en vivo",GOLD,
      [("Lento: día a día","señales en tiempo real"),("Mercado que no vio","la prueba de verdad"),("Gana y pierde","y todo se publica")],
      [30,60,25,70,40,85,35,55,90,45,65])
d.text((80,1085),"Sentinel está en forward test hoy.",font=f(B,32),fill=GOLD)
d.text((80,1132),"En vivo, sin capital real.",font=f(R,27),fill=GREY)
d.line([(80,1215),(1000,1215)],fill=EDGE,width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-04_pm_backtest_forward.jpg",quality=92)
