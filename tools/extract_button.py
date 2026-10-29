"""Build the button image from the Scarlet Witch frame + pill sheet.

    python tools/extract_button.py   ->  assets/button.png, assets/inner-glow.png

assets/scarlet_frame_sheet.png holds the ornate frame (top) and the glowing pill background (bottom),
both already cut out. The pill is fitted behind the frame's opening so its edge tucks under the rails.
The inner-glow streak (press flash) still comes from the crimson asset sheet.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sheet = Image.open(os.path.join(ROOT, "assets", "scarlet_frame_sheet.png")).convert("RGBA")

FRAME = (276, 12, 1896, 395)        # frame piece (sheet coords)
PILL = (367, 408, 1801, 692)        # pill piece
OPENING = (384, 142, 1788, 348)     # transparent inside of the frame
TUCK = 12                           # how far the pill reaches under the rails

frame = sheet.crop(FRAME)
pill = sheet.crop(PILL)
w = OPENING[2] - OPENING[0] + TUCK * 2
h = OPENING[3] - OPENING[1] + TUCK * 2
pill = pill.resize((w, h), Image.LANCZOS)

out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
out.alpha_composite(pill, (OPENING[0] - TUCK - FRAME[0], OPENING[1] - TUCK - FRAME[1]))
out.alpha_composite(frame)
out.save(os.path.join(ROOT, "assets", "button.png"), optimize=True)

crimson = Image.open(os.path.join(ROOT, "assets", "asset_sheet.png")).convert("RGBA")
crimson.crop((1233, 680, 1682, 712)).save(os.path.join(ROOT, "assets", "inner-glow.png"), optimize=True)

# where the label goes, as fractions of the button image (used by src/template.html)
cx = ((OPENING[0] + OPENING[2]) / 2 - FRAME[0]) / frame.width
cy = ((OPENING[1] + OPENING[3]) / 2 - FRAME[1]) / frame.height
print("button", out.size, f"label centre ({cx:.3f}, {cy:.3f})",
      f"rails at y {(OPENING[1] - FRAME[1]) / frame.height:.3f} / {(OPENING[3] - FRAME[1]) / frame.height:.3f}")
