"""Convierte una imagen de post (1080x1350) en historia 1080x1920 para Instagram/Facebook.
Uso: python tools/historia.py entrada.jpg salida.jpg ["Texto de arriba"]"""
import sys
from PIL import Image, ImageDraw, ImageFont
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); BG=(11,15,26)

def historia(entrada, salida, arriba="NUEVO POST"):
    W,H=1080,1920
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    for x in range(0,W,60): d.line([(x,0),(x,H)],fill=(16,22,36))
    for y in range(0,H,60): d.line([(0,y),(W,y)],fill=(16,22,36))
    post=Image.open(entrada).convert("RGB").resize((960,1200))
    d.rounded_rectangle([54,264,1026,1476],radius=28,fill=GOLD)
    img.paste(post,(60,270))
    d.text((W//2,150),arriba,font=ImageFont.truetype(B,54),fill=GOLD,anchor="mm")
    d.text((W//2,212),"@sentineltradinghq",font=ImageFont.truetype(R,32),fill=GREY,anchor="mm")
    d.text((W//2,1600),"Mira el post completo en el perfil",font=ImageFont.truetype(B,40),fill=WHITE,anchor="mm")
    d.text((W//2,1665),"Comunidad gratis: link en la bio",font=ImageFont.truetype(R,32),fill=GREY,anchor="mm")
    img.save(salida,quality=92)

if __name__=="__main__":
    historia(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "NUEVO POST")
