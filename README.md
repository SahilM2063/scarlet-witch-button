# Chaos Magic Button

A Scarlet Witch button. Hover it and it lifts. Click it and it burns away from the centre inside churning dark-red hex smoke, while Wanda's tiara grows out of the smoke from the centre to both sides. Click the crown to undo the hex.

**Live:** https://sahilm2063.github.io/scarlet-witch-button/

## How it works

Everything runs live in WebGL (three.js), and `index.html` is one self-contained file.

- **Crown model:** a Tripo PBR model, cut from 2M to 69k triangles with 1024px WebP textures and meshopt compression (18.4 MB → 0.7 MB). It's inlined as base64.
- **Shaders:**
  - **Smoke:** domain-warped fractal noise in two depth layers, one behind the crown and one in front. Each layer is computed into a small offscreen texture every frame, so it stays cheap.
  - **Button burn:** a noise-edged dissolve from the centre outward, with a glowing edge and a charred band. It's injected into three's physical material, and the shadow burns away with it.
  - **Crown reveal:** a dissolve from the centre out to both sides behind a red-hot edge, plus a red Fresnel rim and a slow breathing glow.
  - **Embers:** stateless GPU particles.
- **Smooth playback:** the whole animation is a function of one progress value, so undo is the cast played in reverse. The render loop sleeps when nothing is moving, and pixel ratio, smoke resolution and particle count are capped (lower on touch devices). Shaders are compiled up front, so the first click doesn't stutter. If you have reduced motion turned on, it jumps straight to the end state.

## Rebuild

```bash
cd tools && npm install && cd ..
node tools/optimize_model.mjs model/crown_source.glb model/crown.glb   # only when the model changes
python tools/build_html.py                                             # src/template.html + model -> index.html
```
