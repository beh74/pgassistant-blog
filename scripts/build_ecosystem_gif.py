"""Generate the homepage ecosystem animation and its still alternative with Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'static/images'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(n, bold=False): return ImageFont.truetype(BOLD if bold else FONT, n)
projects = ['pgassistant', 'pg-assistant-collector', 'pgassistant-grafana', 'pg-assistant-autotune']
colors = ['#087eaf', '#009ba8', '#c6721c', '#7155bb']
def frame(active, progress=0):
    im = Image.new('RGB', (960, 650), '#f1f8fa')
    d = ImageDraw.Draw(im)
    d.text((42, 30), 'THE PGASSISTANT ECOSYSTEM', font=font(16, True), fill='#087eaf')
    d.text((42, 65), 'Four projects. One ecosystem.', font=font(37, True), fill='#14344b')
    d.text((42, 119), 'Explore the PostgreSQL improvement toolkit', font=font(20), fill='#627785')
    for i, name in enumerate(projects):
        y = 180 + i * 101
        selected = active == i
        d.rounded_rectangle((42,y,918,y+83), radius=12, fill='white', outline=colors[i] if selected else '#dfe8ed', width=3 if selected else 1)
        d.rounded_rectangle((58,y+18,104,y+64), radius=10, fill=colors[i] if selected else '#eaf1f5')
        d.text((70,y+29), str(i+1).zfill(2), font=font(18,True), fill='white' if selected else '#627785')
        d.text((124,y+25),name,font=font(30,True),fill='#14344b')
        if i == 3:
            d.rounded_rectangle((792,y+25,896,y+57),radius=16,fill='#eee8fa')
            d.text((813,y+32),'NEW',font=font(16,True),fill='#7155bb')
        if selected:
            d.rounded_rectangle((124,y+69,124+int(645*progress),y+73),radius=2,fill=colors[i])
    d.text((42, 610), 'Observe  /  Improve  /  Measure  /  Repeat',font=font(18),fill='#627785')
    return im
frames=[frame(i, (step+1)/8) for i in range(4) for step in range(8)]
frames[0].save(OUT/'pgassistant-ecosystem.gif',save_all=True,append_images=frames[1:],duration=250,loop=0,optimize=True)
frame(-1).save(OUT/'pgassistant-ecosystem.png',optimize=True)
print(f'{len(frames)} frames; {(OUT / "pgassistant-ecosystem.gif").stat().st_size:,} bytes')
