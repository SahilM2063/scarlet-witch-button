// Shrink the Tripo crown for the web: simplify the 2M-triangle mesh, resize textures to WebP, meshopt-compress.
//   node tools/optimize_model.mjs model/crown_source.glb model/crown.glb [ratio=0.035] [textureSize=1024]
import { NodeIO } from "@gltf-transform/core";
import { ALL_EXTENSIONS, EXTMeshoptCompression, EXTTextureWebP } from "@gltf-transform/extensions";
import { dedup, prune, quantize, reorder, simplify, weld } from "@gltf-transform/functions";
import { MeshoptDecoder, MeshoptEncoder, MeshoptSimplifier } from "meshoptimizer";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [src, dst, ratio = "0.035", size = "1024"] = process.argv.slice(2);
await Promise.all([MeshoptDecoder.ready, MeshoptEncoder.ready, MeshoptSimplifier.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  "meshopt.decoder": MeshoptDecoder,
  "meshopt.encoder": MeshoptEncoder,
});
const doc = await io.read(src);

await doc.transform(
  dedup(),
  weld(),
  simplify({ simplifier: MeshoptSimplifier, ratio: Number(ratio), error: 0.002 }),
  prune(),
);

// textures: Pillow does the resize + WebP encode (sharp/libvips chokes on these files)
const tmp = mkdtempSync(join(tmpdir(), "crowntex-"));
const resize = `
import sys, io
from PIL import Image
im = Image.open(sys.argv[1]); im.load()
im = im.convert("RGBA" if im.mode in ("RGBA", "LA") else "RGB")
s = int(sys.argv[3]); im.thumbnail((s, s), Image.LANCZOS)
im.save(sys.argv[2], "WEBP", quality=int(sys.argv[4]), method=6)
`;
doc.createExtension(EXTTextureWebP).setRequired(true);
const normals = new Set(doc.getRoot().listMaterials().map((m) => m.getNormalTexture()).filter(Boolean));
for (const [i, tex] of doc.getRoot().listTextures().entries()) {
  const a = join(tmp, `in${i}`), b = join(tmp, `out${i}.webp`);
  writeFileSync(a, tex.getImage());
  execFileSync("python", ["-c", resize, a, b, size, normals.has(tex) ? "92" : "84"]);
  tex.setImage(readFileSync(b)).setMimeType("image/webp").setURI("");
}

await doc.transform(reorder({ encoder: MeshoptEncoder }), quantize());
doc.createExtension(EXTMeshoptCompression).setRequired(true)
  .setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.QUANTIZE });
await io.write(dst, doc);

const prim = doc.getRoot().listMeshes()[0].listPrimitives()[0];
console.log(`triangles: ${prim.getIndices().getCount() / 3}, vertices: ${prim.getAttribute("POSITION").getCount()}`);
console.log(`size: ${(readFileSync(dst).length / 1e6).toFixed(2)} MB`);
