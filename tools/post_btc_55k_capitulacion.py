from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(20,27,43); BG=(11,15,26)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
# datos diarios BTCUSDT (Binance), últimos 45 días
o=[83321.81,81754.46,82635.56,82988.35,83773.12,81850.01,83169.01,81682.02,82245.93,81615.91,81491.04,82116,81938.39,83028.14,84093.42,81416.09,81189.44,80888.15,80154.09,80150.56,80909.77,81343.51,77991.89,77368.76,77582.02,78354.01,76816.01,77453.85,80504.01,76088.01,75844,75867.58,74851.44,75368.41,73796.06,74015.2,71460,68314.01,64150.01,65351.05,64882.88,64947.36,63068.21,61986.73,58951.51,60215.78]
h=[85598.22,83521.15,83528.98,83173.29,84199,84352,84168,84146.72,82634.3,82940.81,81770.01,82295.47,83158,83439,84898,84377.21,82060.88,81213.64,81033.69,80844.7,81300,81823,81971,78804.01,77796.01,78422.23,78878.01,78063.3,81196.01,80918.01,76416.24,76249.99,76200,75599.22,75442.01,74811.45,74217.49,71514.01,68446.21,66132.01,65696.16,65447,65002,64080.8,62639.52,60996,60352.16]
l=[82787.25,80393.56,81603.52,82545.82,82804.65,81750.09,81033.66,81444.42,79800,80809.25,80819.66,80684.36,81748.85,81200,82635.32,80939.54,80513,79220.74,79845.86,79368.67,79506,80397.14,77910,76325.98,77114.01,77517.2,76705,76388.88,75736.38,75208.42,74888,75571.08,73510,73750,72727.27,73209.12,71113.06,67568,63320,62006,63905.01,63336,62062.97,61428.26,57778.35,55130,60180]
c=[81754.45,82635.55,82988.36,83773.12,81850,83169,81682.01,82245.93,81615.64,81491.04,82116,81938.4,83028.15,84093.42,81416.09,81189.43,80888.16,80154.09,80150.56,80909.77,81343.5,77991.89,77368.77,77582.02,78354,76816,77453.86,80504.01,76088.01,75844,75867.59,74851.44,75368.41,73796.06,74015.19,71460,68314,64150,65351.05,64882.87,64947.35,63068.22,61986.73,58951.51,60215.77,60296.44]
n=min(len(o),len(h),len(l),len(c)); o,h,l,c=o[-n:],h[-n:],l[-n:],c[-n:]
d.text((80,70),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,112),"Mercado · Bitcoin diario",font=f(R,26),fill=GREY)
d.text((80,180),"Bitcoin toca $55K:",font=f(B,68),fill=WHITE)
d.text((80,262),"¿capitulación o pausa?",font=f(B,62),fill=GOLD)
# gráfico
X0,X1,Y0,Y1=80,1000,370,800
d.rounded_rectangle([X0-20,Y0-25,X1+20,Y1+25],radius=22,fill=PANEL)
pmin,pmax=53000,87000
py=lambda p: Y1-(p-pmin)/(pmax-pmin)*(Y1-Y0)
lv=[(65000,GREY,"65.000"),(62300,GREY,"62.000-62.600"),(57800,GOLD,"57.800"),(55130,RED,"55.130")]
for p,col,t in lv:
    y=py(p)
    for x in range(X0,X1-168,18): d.line([(x,y),(x+9,y)],fill=col,width=2)
    d.text((X1-158,y),t,font=f(B,19),fill=col,anchor="lm")
cw=(X1-170-X0)/n
for i in range(n):
    x=X0+i*cw+cw/2; col=GREEN if c[i]>=o[i] else RED
    d.line([(x,py(h[i])),(x,py(l[i]))],fill=col,width=2)
    a,b=sorted([py(o[i]),py(c[i])]); d.rectangle([x-cw*0.35,a,x+cw*0.35,max(b,a+2)],fill=col)
d.text((X0,Y0-10),"BTC/USDT · 1D",font=f(B,22),fill=GREY)
# cifras
stats=[("Precio","~$60.100"),("Mínimo","$55.130"),("30 días","-26%")]
for i,(k,v) in enumerate(stats):
    x=80+i*315
    d.rounded_rectangle([x,850,x+290,970],radius=18,fill=PANEL)
    d.text((x+145,885),k,font=f(R,24),fill=GREY,anchor="mm")
    d.text((x+145,932),v,font=f(B,38),fill=RED if v.startswith("-") else WHITE,anchor="mm")
pts=[("1","Mínimo en más de 2 años y bajo la media de 200 semanas."),
     ("2","Mecha larga + volumen récord del mes: posible capitulación."),
     ("3","Sigue bajista mientras no recupere $65.000.")]
for i,(k,t) in enumerate(pts):
    y=1005+i*55
    d.ellipse([82,y,124,y+42],fill=GOLD); d.text((103,y+21),k,font=f(B,24),fill=BG,anchor="mm")
    d.text((142,y+21),t,font=f(R,26),fill=WHITE,anchor="lm")
d.text((80,1185),"Una mecha no confirma un suelo: espera el cierre.",font=f(B,29),fill=GREEN)
d.line([(80,1235),(1000,1235)],fill=(40,48,66),width=2)
d.text((80,1252),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1292),"Contenido educativo. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-11/2026-11-21_pm_btc_55k_capitulacion.jpg",quality=92)
