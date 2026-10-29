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
# The sheet's button carries a darker offset "thickness" layer (with its own dim outline) outside the main
# frame line, visible at the pointed ends and corners. Trace the main line's outer edge instead: per column its
# top/bottom, per row its left/right (gaps in the dashed bottom rail are bridged by interpolation, outliers
# removed by a median), and keep only pixels inside both spans, feathered a pixel.
from PIL import ImageFilter
from statistics import median
W, H = btn.size
line = [[False] * W for _ in range(H)]
for y in range(H):
    for x in range(W):
        r, g, b_, a = px[x, y]
        line[y][x] = a > 150 and r > 220 and g > 22      # main line; the outer layer's outline is dimmer (r < ~200)

def clean(vals, win):
    known = [i for i, v in enumerate(vals) if v is not None]
    out = []
    for i in range(len(vals)):                       # bridge gaps linearly between the nearest known values
        if vals[i] is not None:
            out.append(vals[i]); continue
        lo = max((k for k in known if k < i), default=None); hi = min((k for k in known if k > i), default=None)
        if lo is None: out.append(vals[hi])
        elif hi is None: out.append(vals[lo])
        else: out.append(vals[lo] + (vals[hi] - vals[lo]) * (i - lo) / (hi - lo))
    h = win // 2
    return [median(out[max(0, i - h):i + h + 1]) for i in range(len(out))]

tops = clean([next((y for y in range(H // 2) if line[y][x]), None) for x in range(W)], 9)
bots = clean([next((y for y in range(H - 1, H // 2, -1) if line[y][x]), None) for x in range(W)], 9)
lefts = clean([next((x for x in range(W // 2) if line[y][x]), None) for y in range(H)], 9)
rights = clean([next((x for x in range(W - 1, W // 2, -1) if line[y][x]), None) for y in range(H)], 9)
mask = Image.new("L", btn.size, 0)
mp = mask.load()
for y in range(H):
    for x in range(W):
        if lefts[y] - 0.5 <= x <= rights[y] + 0.5 and tops[x] - 0.5 <= y <= bots[x] + 0.5:
            mp[x, y] = 255
mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))   # keep the rim's full width
from PIL import ImageChops
btn.putalpha(ImageChops.multiply(btn.getchannel("A"), mask))
btn = btn.crop(btn.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
btn.save(os.path.join(ROOT, "assets", "button.png"), optimize=True)
sheet.crop(GLOW).save(os.path.join(ROOT, "assets", "inner-glow.png"), optimize=True)
print("button", btn.size, "glow", (GLOW[2] - GLOW[0], GLOW[3] - GLOW[1]))
