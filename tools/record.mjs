// Frame-perfect recording of the page: the page clock is driven by hand (exactly 1/FPS per frame), so the
// video is smooth no matter how slow the GPU is.
//   node tools/record.mjs [url] [outDir]   ->  outDir/f_0000.png ...   (then encode with ffmpeg)
import puppeteer from "puppeteer-core";
import { mkdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const URL = process.argv[2] || "https://sahilm2063.github.io/scarlet-witch-button/";
const OUT = process.argv[3] || "recording/frames";
const W = 1920, H = 1080, FPS = 60;
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: EDGE, headless: "new",
  args: [`--window-size=${W},${H}`, "--ignore-gpu-blocklist", "--enable-gpu-rasterization", "--use-angle=d3d11", "--hide-scrollbars"],
});
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
// virtual clock: performance.now and requestAnimationFrame only move when we step them
await page.evaluateOnNewDocument(() => {
  let now = 0;
  const queue = [];
  const realRAF = window.requestAnimationFrame.bind(window);
  performance.now = () => now;
  window.requestAnimationFrame = (cb) => { queue.push(cb); return queue.length; };
  window.__step = (ms) => { now += ms; const cbs = queue.splice(0); for (const cb of cbs) cb(now); };
  window.__present = () => new Promise((r) => realRAF(() => realRAF(r)));
});
await page.goto(URL, { waitUntil: "networkidle0" });
await page.evaluate(() => document.fonts.ready);
// let the model parse and every program warm up before rolling
for (let i = 0; i < 90; i++) { await page.evaluate(() => window.__step(1000 / 60)); await new Promise((r) => setTimeout(r, 20)); }

const move = (x, y) => page.evaluate((x, y) => {
  document.getElementById("c").dispatchEvent(new PointerEvent("pointermove",
    { clientX: x * innerWidth, clientY: y * innerHeight, pointerType: "mouse", bubbles: true }));
}, x, y);
const click = () => page.evaluate(() => document.getElementById("a11y").click());
const ease = (t) => 0.5 - 0.5 * Math.cos(Math.PI * Math.min(1, Math.max(0, t)));

// shot list (seconds)
const CLICK_CAST = 1.2, CLICK_UNDO = 8.6, END = 11.4;
const events = [[CLICK_CAST, click], [CLICK_UNDO, click]];
const total = Math.round(END * FPS);
for (let f = 0; f < total; f++) {
  const t = f / FPS;
  for (const e of events) if (Math.abs(e[0] - t) < 0.5 / FPS) await e[1]();
  // cursor: drifts in, rests during the cast, then sweeps so the crown follows it, and settles back
  let x = 0.5, y = 0.5;
  if (t < CLICK_CAST) { x = 0.5 + 0.08 * (1 - ease(t / CLICK_CAST)); y = 0.62 - 0.12 * ease(t / CLICK_CAST); }
  else if (t > 4.0 && t < 8.2) {
    const k = (t - 4.0) / 4.2;
    x = 0.5 + 0.34 * Math.sin(k * Math.PI * 2) * Math.sin(k * Math.PI);
    y = 0.48 - 0.16 * Math.sin(k * Math.PI * 4) * Math.sin(k * Math.PI);
  }
  await move(x, y);
  await page.evaluate((ms) => window.__step(ms), 1000 / FPS);
  await page.evaluate(() => window.__present());
  await page.screenshot({ path: join(OUT, `f_${String(f).padStart(4, "0")}.png`), type: "png" });
  if (f % 60 === 0) console.log(`frame ${f}/${total}`);
}
await browser.close();
console.log("done", total, "frames");
