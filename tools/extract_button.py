"""Cut the button + inner-glow streak out of the Ornate Crimson UI asset sheet.

    python tools/extract_button.py   ->  assets/button.png, assets/inner-glow.png

The sheet's assembled button has "CONTINUE" baked in; the lettering is painted out by
interpolating the background gradient across it row by row, so the page can set its own label.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sheet = Image.open(os.path.join(ROOT, "assets", "asset_sheet.png")).convert("RGBA")

BUTTON = (452, 74, 1293, 251)
GLOW = (1233, 680, 1682, 712)
TEXT_X = (655, 1095)        # lettering span inside the button (sheet coords)
TEXT_Y = (120, 205)

btn = sheet.crop(BUTTON)
px = btn.load()
x0, x1 = TEXT_X[0] - BUTTON[0], TEXT_X[1] - BUTTON[0]
for y in range(TEXT_Y[0] - BUTTON[1], TEXT_Y[1] - BUTTON[1]):
    a = [sum(px[x0 - k, y][c] for k in range(1, 6)) / 5 for c in range(4)]
    b = [sum(px[x1 + k, y][c] for k in range(1, 6)) / 5 for c in range(4)]
    for x in range(x0, x1 + 1):
        t = (x - x0) / (x1 - x0)
        px[x, y] = tuple(round(a[c] + (b[c] - a[c]) * t) for c in range(4))
btn.save(os.path.join(ROOT, "assets", "button.png"), optimize=True)
sheet.crop(GLOW).save(os.path.join(ROOT, "assets", "inner-glow.png"), optimize=True)
print("button", btn.size, "glow", (GLOW[2] - GLOW[0], GLOW[3] - GLOW[1]))
