"""Inline the optimised crown model into src/template.html -> index.html (one self-contained page).

    node tools/optimize_model.mjs model/crown_source.glb model/crown.glb   # once, when the model changes
    python tools/build_html.py
"""
import base64, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, "src", "template.html"), encoding="utf8").read()
glb = open(os.path.join(ROOT, "model", "crown.glb"), "rb").read()
assert '"/*__MODEL__*/"' in tpl
html = tpl.replace('"/*__MODEL__*/"', '"' + base64.b64encode(glb).decode() + '"')
open(os.path.join(ROOT, "index.html"), "w", encoding="utf8").write(html)
print(f"model {len(glb) / 1e6:.2f} MB -> index.html {len(html) / 1e6:.2f} MB")
