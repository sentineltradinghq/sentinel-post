from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
img=Image.new("RGB",(W,H),(11,15,26)); d=ImageDraw.Draw(img)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=lambda p,s:ImageFont.truetype(p,s)
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); RED=(231,76,60); CARD=(20,27,43)
for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
d.text((80,70),"SENTINEL TRADING",font=f(B,30),fill=GOLD)
d.text((80,112),"Mercado · 29 oct 2026",font=f(R,26),fill=GREY)
d.text((80,185),"Hackeo a Binance:",font=f(B,66),fill=WHITE)
d.text((80,262),"lo que sabemos",font=f(B,66),fill=GOLD)
d.rounded_rectangle([80,365,1000,505],radius=18,fill=CARD)
d.text((110,385),"≈ $5.900 millones",font=f(B,46),fill=RED)
d.text((110,447),"65 tokens · posible mayor robo cripto",font=f(R,28),fill=GREY)
rows=[("BTC","≈ 18.270 BTC","$1.440 M"),("ETH","≈ 460.500 ETH","$1.040 M"),("USDT","≈ 1.770 M USDT","$1.770 M"),
("USDC","≈ 823 M USDC","$823 M"),("TRX","≈ 684,6 M TRX","$241 M"),("XRP","≈ 233,5 M XRP","$297 M"),("SOL","≈ 970.500 SOL","$94 M")]
y=525
for k,q,v in rows:
    d.text((110,y),k,font=f(B,28),fill=GOLD); d.text((250,y),q,font=f(R,28),fill=WHITE); d.text((790,y),v,font=f(R,28),fill=GREY); y+=38
d.text((110,y+2),"+ unos 58 tokens más (ARB, AVAX, ENA, PEPE...)",font=f(R,24),fill=GREY)
d.text((80,840),"Caída de BTC en casos parecidos",font=f(B,34),fill=WHITE)
bars=[("Bitfinex 2016",20,"-20%"),("FTX 2022",17,"-17% (24 h)"),("Bybit 2025",2.1,"-2,1% (día)"),("Binance hoy",4.8,"-4,8%")]
y=890
for name,v,lab in bars:
    d.text((80,y+4),name,font=f(R,28),fill=GREY)
    w=int(v/20*430); d.rectangle([330,y,330+w,y+34],fill=RED if name!="Binance hoy" else GOLD)
    d.text((345+w,y+4),lab,font=f(B,28),fill=WHITE); y+=54
d.text((80,1118),"Retiros pausados · ≈ $2.500 M congelados",font=f(R,28),fill=WHITE)
d.text((80,1158),"Binance dice que cubrirá las pérdidas",font=f(R,28),fill=WHITE)
d.line([(80,1215),(1000,1215)],fill=(40,48,66),width=2)
d.text((80,1240),"@sentineltradinghq",font=f(B,28),fill=WHITE)
d.text((80,1285),"Cifras preliminares on-chain. No es asesoría financiera.",font=f(R,22),fill=GREY)
img.save("posts/2026-10/2026-10-29_pm_hackeo_binance_v2.jpg",quality=92)
