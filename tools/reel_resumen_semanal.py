"""Reel del resumen semanal: las imágenes del carrusel en 1080x1920 con transiciones y música suave sintetizada.
Uso: python tools/reel_resumen_semanal.py AAAA-MM-DD
"""
import os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

fecha = sys.argv[1]
mes = fecha[:7]
IMGS = [f"posts/{mes}/{fecha}_resumen_semanal_{i}.jpg" for i in range(1, 6)]
OUT = f"videos/{mes}/{fecha}_reel_resumen_semanal.mp4"
W, H, FPS = 1080, 1920, 30
SEG = [4.5, 3.5, 3.5, 3.0, 4.5]  # duración de cada lámina
FADE = 0.5
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG = (11, 15, 26); GOLD = (245, 166, 35); GREY = (150, 158, 175); GRID = (16, 22, 36)

base = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(base)
for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=GRID)
for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=GRID)
d.text((W // 2, 140), "RESUMEN SEMANAL", font=ImageFont.truetype(B, 52), fill=GOLD, anchor="mm")
d.text((W // 2, 205), "Forward test en vivo, sin capital real", font=ImageFont.truetype(R, 32), fill=GREY, anchor="mm")
d.text((W // 2, 1740), "Comunidad gratis: link en la bio", font=ImageFont.truetype(B, 40), fill=(240, 242, 247), anchor="mm")
d.text((W // 2, 1800), "Contenido educativo. No es asesoría financiera.", font=ImageFont.truetype(R, 28), fill=GREY, anchor="mm")

SCALE = 0.92
cw, ch = int(1080 * SCALE), int(1350 * SCALE)
y0 = (H - ch) // 2 + 10
slides = []
for p in IMGS:
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    fr = base.copy(); fr.paste(im, ((W - cw) // 2, y0))
    ImageDraw.Draw(fr).rectangle([(W - cw) // 2 - 3, y0 - 3, (W + cw) // 2 + 2, y0 + ch + 2], outline=GOLD, width=3)
    slides.append(np.asarray(fr, dtype=np.float32))

DUR = sum(SEG)
starts = np.cumsum([0] + SEG[:-1])
os.makedirs(os.path.dirname(OUT), exist_ok=True)
tmpv = OUT + ".v.mp4"; tmpa = OUT + ".wav"

# música: acordes suaves (pad) + pulso ligero
sr = 44100; t = np.arange(int(DUR * sr)) / sr
chords = [[220.0, 277.18, 329.63], [196.0, 246.94, 293.66], [174.61, 220.0, 261.63], [196.0, 246.94, 329.63]]
aud = np.zeros_like(t)
cl = DUR / len(chords)
for i, ch_ in enumerate(chords):
    m = (t >= i * cl) & (t < (i + 1) * cl)
    lt = t[m] - i * cl
    env = np.minimum(1, lt / 0.6) * np.minimum(1, (cl - lt) / 0.6)
    for f in ch_:
        aud[m] += env * (np.sin(2 * np.pi * f * t[m]) + 0.3 * np.sin(2 * np.pi * 2 * f * t[m]))
beat = 0.5
ph = (t % beat) / beat
aud += 0.6 * np.sin(2 * np.pi * 55 * t) * np.exp(-ph * 8)
aud *= np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 1.5)
aud = aud / np.max(np.abs(aud)) * 0.35
with wave.open(tmpa, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((aud * 32767).astype(np.int16).tobytes())

p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", tmpv],
                     stdin=subprocess.PIPE)
for n in range(int(DUR * FPS)):
    tt = n / FPS
    i = int(np.searchsorted(starts, tt, side="right") - 1)
    fr = slides[i]
    if i + 1 < len(slides):
        rem = starts[i] + SEG[i] - tt
        if rem < FADE:
            a = 1 - rem / FADE
            fr = fr * (1 - a) + slides[i + 1] * a
    p.stdin.write(fr.astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpv, "-i", tmpa, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                "-shortest", "-movflags", "+faststart", OUT], check=True)
os.remove(tmpv); os.remove(tmpa)
print(OUT)
