"""Régénère les icônes webOS / Tizen (nécessite Pillow : pip install pillow)."""
import os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def art(w, h):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(255 - 61 * t), int(132 - 71 * t), int(157 - 23 * t)))
    d.polygon([(0, h*.67), (w*.28, h*.39), (w*.47, h*.56), (w*.72, h*.22), (w, h*.61), (w, h), (0, h)], fill=(255, 177, 153))
    r = min(w, h) * .145; cx, cy = w * .5, h * .39
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255)); r2 = r * .54
    d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=(255, 143, 184))
    return im

for name, size in [('icon', (80, 80)), ('largeIcon', (130, 130)), ('splash', (1920, 1080))]:
    art(*size).save(os.path.join(ROOT, 'webos', name + '.png'))
art(512, 512).resize((117, 117)).save(os.path.join(ROOT, 'tizen', 'icon.png'))
print('icônes générées')
