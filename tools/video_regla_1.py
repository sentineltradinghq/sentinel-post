"""Reel educativo: la regla del 1% (texto animado + música sintetizada, sin voz)."""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
DUR=24.0
OUT="videos/2026-10/2026-10-31_reel_regla_1.mp4"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fc={}
def F(p,s):
    if (p,s) not in _fc: _fc[(p,s)]=ImageFont.truetype(p,s)
    return _fc[(p,s)]
BG=(11,15,26); GOLD=(245,166,35); WHITE=(240,242,247); GREY=(150,158,175); GREEN=(46,204,113); RED=(231,76,60); PANEL=(18,25,41); LINE=(40,48,66)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def mix(c,a): return tuple(int(BG[i]+(c[i]-BG[i])*a) for i in range(3))
base=Image.new("RGB",(W,H),BG); d0=ImageDraw.Draw(base)
for x in range(0,W,60): d0.line([(x,0),(x,H)],fill=(16,22,36))
for y in range(0,H,60): d0.line([(0,y),(W,y)],fill=(16,22,36))
d0.text((W//2,150),"SENTINEL TRADING",font=F(B,40),fill=GOLD,anchor="mm")
d0.text((W//2,205),"Educación · Gestión de riesgo",font=F(R,30),fill=GREY,anchor="mm")
d0.line([(90,1700),(990,1700)],fill=LINE,width=2)
d0.text((W//2,1750),"@sentineltradinghq",font=F(B,34),fill=WHITE,anchor="mm")
d0.text((W//2,1800),"Contenido educativo. No es asesoría financiera.",font=F(R,26),fill=GREY,anchor="mm")

def T(d,xy,txt,font,col,a,anchor="mm",dy=0):
    if a<=0: return
    d.text((xy[0],xy[1]+int((1-ease(a))*40)+dy),txt,font=font,fill=mix(col,ease(a)),anchor=anchor)

SC=[0,4,8.5,15.5,20.5,DUR]  # inicios de escena
def scene_alpha(t,i):
    s,e=SC[i],SC[i+1]
    if t<s or t>=e: return 0
    out=1 if i==len(SC)-2 else min(1,(e-t)/0.4)
    return min(1,(t-s)/0.5)*out
RISK=[(1,GREEN),(2,GOLD),(5,RED),(10,RED)]

def frame(t):
    img=base.copy(); d=ImageDraw.Draw(img)
    # 1: gancho
    a=scene_alpha(t,0)
    if a:
        T(d,(W//2,700),"¿Cuánto arriesgas",F(B,78),WHITE,a*min(1,(t-SC[0])/0.5))
        T(d,(W//2,800),"en cada operación?",F(B,78),WHITE,a*min(1,max(0,(t-0.4)/0.5)))
        T(d,(W//2,1000),"Esta respuesta decide",F(R,46),GREY,a*min(1,max(0,(t-1.5)/0.5)))
        T(d,(W//2,1065),"si sigues en el juego.",F(B,50),GOLD,a*min(1,max(0,(t-1.9)/0.5)))
    # 2: la regla
    a=scene_alpha(t,1)
    if a:
        lt=t-SC[1]
        T(d,(W//2,620),"La regla del",F(B,90),WHITE,a)
        s=1+0.08*math.sin(min(1,lt/0.6)*math.pi)
        T(d,(W//2,790),"1%",F(B,int(200*s)),GOLD,a*min(1,lt/0.4))
        T(d,(W//2,1020),"Nunca arriesgues más del 1%",F(R,46),WHITE,a*min(1,max(0,(lt-1.0)/0.5)))
        T(d,(W//2,1085),"de tu cuenta en una sola operación.",F(R,46),WHITE,a*min(1,max(0,(lt-1.3)/0.5)))
    # 3: 10 pérdidas seguidas
    a=scene_alpha(t,2)
    if a:
        lt=t-SC[2]
        n=min(10,max(0,int((lt-1.0)/0.45)+1)) if lt>1.0 else 0
        T(d,(W//2,470),"10 pérdidas seguidas",F(B,70),WHITE,a)
        T(d,(W//2,560),f"Pérdida {n} de 10" if n else "Cuenta inicial: 100%",F(B,42),RED if n else GREY,a,)
        for i,(r,c) in enumerate(RISK):
            y=700+i*200
            v=100*(1-r/100)**n
            T(d,(90,y),f"Arriesgas {r}%",F(B,42),c,a,anchor="lm")
            x0,x1=90,990
            d.rounded_rectangle([x0,y+40,x1,y+110],radius=10,fill=mix(PANEL,a))
            w=int((x1-x0)*v/100)
            d.rounded_rectangle([x0,y+40,x0+max(w,20),y+110],radius=10,fill=mix(c,a))
            txt=f"Te queda {v:.1f}%".replace(".",",")
            tw=d.textlength(txt,font=F(B,38))
            tx=x0+w-tw-20 if w>tw+40 else x0+w+20
            d.text((tx,y+75),txt,font=F(B,38),fill=mix(BG if w>tw+40 else WHITE,a),anchor="lm")
    # 4: cálculo
    a=scene_alpha(t,3)
    if a:
        lt=t-SC[3]
        T(d,(W//2,500),"¿Cómo se calcula?",F(B,72),GOLD,a)
        d.rounded_rectangle([90,600,990,760],radius=20,fill=mix(PANEL,a),outline=mix(LINE,a),width=2)
        T(d,(W//2,650),"Posición =",F(B,46),WHITE,a*min(1,max(0,(lt-0.4)/0.5)))
        T(d,(W//2,712),"Riesgo en $ ÷ Distancia al stop",F(B,44),WHITE,a*min(1,max(0,(lt-0.6)/0.5)))
        steps=[("Cuenta:","$1.000",WHITE),("Riesgo 1%:","$10",GREEN),("Stop a:","5%",RED),("Posición:","$200",GOLD)]
        for i,(k,v,c) in enumerate(steps):
            aa=a*min(1,max(0,(lt-1.2-i*0.6)/0.5))
            T(d,(180,860+i*110),k,F(R,52),GREY,aa,anchor="lm")
            T(d,(900,860+i*110),v,F(B,60),c,aa,anchor="rm")
        T(d,(W//2,1400),"Arriesgar 1% no es meter el 1%.",F(B,40),WHITE,a*min(1,max(0,(lt-3.6)/0.5)))
        T(d,(W//2,1455),"Es lo máximo que pierdes si toca el stop.",F(R,38),GREY,a*min(1,max(0,(lt-3.9)/0.5)))
    # 5: cierre
    a=scene_alpha(t,4)
    if a:
        lt=t-SC[4]
        T(d,(W//2,720),"Primero sobrevivir,",F(B,80),WHITE,a)
        T(d,(W//2,830),"luego ganar.",F(B,80),GOLD,a*min(1,max(0,(lt-0.4)/0.5)))
        T(d,(W//2,1050),"¿Tú cuánto arriesgas?",F(B,50),WHITE,a*min(1,max(0,(lt-1.2)/0.5)))
        T(d,(W//2,1115),"Cuéntanos en comentarios",F(R,42),GREY,a*min(1,max(0,(lt-1.4)/0.5)))
        T(d,(W//2,1300),"Comunidad gratis: link en la bio",F(B,40),GOLD,a*min(1,max(0,(lt-2.0)/0.5)))
    return img

# ---- audio: pad suave + tics en cada pérdida ----
SR=44100; N=int(SR*DUR); tt=np.arange(N)/SR
def note(m): return 440*2**((m-69)/12)
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
aud=np.zeros(N)
for k in range(int(DUR/3)+1):
    s=int(k*3*SR); e=min(N,s+int(3.4*SR))
    if s>=N: break
    seg=tt[:e-s]; env=np.minimum(1,seg/0.6)*np.minimum(1,(3.4-seg)/0.8)
    for m in chords[k%4]:
        f=note(m); aud[s:e]+=0.05*env*(np.sin(2*np.pi*f*seg)+0.3*np.sin(2*np.pi*2*f*seg))
    f=note(chords[k%4][0]-12); aud[s:e]+=0.07*env*np.sin(2*np.pi*f*seg)
for b in np.arange(0,DUR,0.5):  # pulso suave
    s=int(b*SR); seg=tt[:int(0.12*SR)]; e=min(N,s+len(seg))
    aud[s:e]+=0.04*np.random.uniform(-1,1,e-s)*np.exp(-seg[:e-s]*40)
for n in range(10):  # tic por pérdida
    s=int((SC[2]+1.0+n*0.45)*SR); seg=tt[:int(0.15*SR)]
    aud[s:s+len(seg)]+=0.18*np.sin(2*np.pi*(880-n*40)*seg)*np.exp(-seg*30)
fade=np.minimum(1,np.minimum(tt/0.5,(DUR-tt)/1.5)); aud*=fade
aud=aud/np.max(np.abs(aud))*0.6
wav="tools/_regla1_audio.wav"
with wave.open(wav,"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((aud*32767).astype(np.int16).tobytes())

p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
    "-i",wav,"-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",OUT],stdin=subprocess.PIPE)
for i in range(int(DUR*FPS)):
    t=i/FPS; im=frame(t); p.stdin.write(im.tobytes())
    if i in (60,180,400,560,690): im.save(f"/tmp/claude-0/-home-claude-sentinel-post/c7a7fb23-e74a-5ee6-b1c3-83291318cf6e/scratchpad/f{i}.jpg",quality=80)
p.stdin.close(); p.wait(); os.remove(wav)
print("ok",OUT)
