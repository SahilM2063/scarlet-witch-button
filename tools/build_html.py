"""Inline the crown model and button assets into src/template.html -> index.html (one self-contained page).

    node tools/optimize_model.mjs model/crown_source.glb model/crown.glb   # when the model changes
    python tools/extract_button.py                                         # when the asset sheet changes
    python tools/build_html.py
"""
import base64, io, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def webp_uri(path):
    buf = io.BytesIO()
    Image.open(path).save(buf, "WEBP", quality=92, alpha_quality=100, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

tpl = open(os.path.join(ROOT, "src", "template.html"), encoding="utf8").read()
glb = open(os.path.join(ROOT, "model", "crown.glb"), "rb").read()
for key in ('"/*__MODEL__*/"', '"/*__BUTTON__*/"', '"/*__GLOW__*/"'):
    assert key in tpl, key
html = (tpl.replace('"/*__MODEL__*/"', '"' + base64.b64encode(glb).decode() + '"')
           .replace('"/*__BUTTON__*/"', '"' + webp_uri(os.path.join(ROOT, "assets", "button.png")) + '"')
           .replace('"/*__GLOW__*/"', '"' + webp_uri(os.path.join(ROOT, "assets", "inner-glow.png")) + '"'))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf8").write(html)
print(f"model {len(glb) / 1e6:.2f} MB -> index.html {len(html) / 1e6:.2f} MB")
