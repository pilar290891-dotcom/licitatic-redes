// Memes «Estoy a esto» LicitaTIC: 3 slides con zoom progresivo + slide de marca, en 4:5 y 9:16, y reel animado.
// Uso: node build.js <id> <carpetaSalida> [--reel]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path'); const { execSync } = require('child_process');
const { hand, TX, TY } = require('./hand');
const D = __dirname; const f = p => 'file://' + path.join(D, p);
const FM = 'node_modules/@fontsource/montserrat/files/montserrat-latin';

const MEMES = {
  pliego:      { lines: ['de leer el pliego', 'entero'], sub: '(voy por la página 4 de 187)' },
  aclaraciones:{ lines: ['de pedir aclaraciones', 'sobre las aclaraciones'] },
  bar:         { lines: ['de dejar las licitaciones', 'y montar un bar'] },
  ganarla:     { lines: ['de ganarla'], sub: '(me faltaron 0,02 puntos)' },
  tiempo:      { lines: ['de presentar la oferta', 'con tiempo'], sub: '(quedan 3 minutos)' },
  subsanar:    { lines: ['de subsanar', 'mi vida entera'] },
};

const CSS = H => `
@font-face{font-family:M;font-weight:400;src:url(${f(FM + '-400-normal.woff2')})}
@font-face{font-family:M;font-weight:600;src:url(${f(FM + '-600-normal.woff2')})}
@font-face{font-family:M;font-weight:800;src:url(${f(FM + '-800-normal.woff2')})}
@font-face{font-family:S;font-style:italic;src:url(${f('node_modules/@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:${H}px;overflow:hidden}
body{font-family:M;position:relative;background:#F2F6F9;color:#03214F}
#stage{position:absolute;left:0;top:0;width:1080px;height:${H}px;transform-origin:0 0}
.grid{position:absolute;inset:-2000px;background-image:linear-gradient(rgba(3,33,79,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(3,33,79,.055) 1px,transparent 1px);background-size:54px 54px}
.dot{position:absolute;border-radius:50%;background:#0CA8AC;box-shadow:0 0 10px 3px rgba(12,168,172,.55)}
.title{position:absolute;left:0;right:0;text-align:center;font-weight:800;font-size:${H === 1920 ? 150 : 132}px;line-height:1.12;letter-spacing:.01em}
.hl{background:#0CA8AC;color:#fff;padding:0 22px;border-radius:12px}
.hand{position:absolute;width:1000px;height:1000px}
.brand{position:absolute;left:70px;display:flex;align-items:center;gap:16px;font-weight:600;font-size:26px;color:#08777A}
.brand img{height:44px}
/* slide de marca */
.dark{background:radial-gradient(900px 700px at 100% 0%,rgba(12,168,172,.28),transparent 60%),radial-gradient(800px 700px at 0% 100%,rgba(8,119,122,.35),transparent 60%),#03214F;color:#fff}
.dark .grid{inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px)}
.wrap{position:absolute;left:90px;right:90px;top:${H === 1920 ? 250 : 110}px;bottom:${H === 1920 ? 420 : 200}px;display:flex;flex-direction:column;justify-content:center}
.h1{font-weight:800;font-size:${H === 1920 ? 104 : 92}px;line-height:1.22}
.serif{font-family:S;font-style:italic;color:#0CA8AC;font-size:${H === 1920 ? 80 : 70}px;line-height:1.12;margin-top:44px}
.p{font-size:${H === 1920 ? 40 : 34}px;line-height:1.45;margin-top:40px;color:#DCE6F2}
.foot{position:absolute;left:90px;bottom:${H === 1920 ? 300 : 90}px;display:flex;align-items:center}
.foot img{height:60px}.foot span{font-size:27px;color:#C3CFDE;margin-left:28px}
.mini{position:absolute;right:90px;top:${H === 1920 ? 250 : 110}px;width:150px;opacity:.9}
`;

let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

function layout(H) {
  const hx = 70, hy = H === 1920 ? 800 : H - 990;               // posición de la mano en la página
  const fx = hx + TX, fy = hy + TY;           // punto de zoom (texto diminuto)
  const titleTop = H === 1920 ? 400 : 150;
  return { hx, hy, fx, fy, titleTop };
}

function memePage(m, H) {
  const L = layout(H); seed = 7;
  const dots = Array.from({ length: 12 }, () => { const s = 5 + rnd() * 7; return `<div class="dot" style="left:${(rnd() * 1040) | 0}px;top:${(rnd() * (L.hy + 300)) | 0}px;width:${s}px;height:${s}px;opacity:${(0.3 + rnd() * 0.5).toFixed(2)}"></div>`; }).join('');
  const brandTop = H === 1920 ? 150 : H - 100;
  return `<div id="stage"><div class="grid"></div>${dots}
    <div class="title" style="top:${L.titleTop}px">ESTOY<br>A <span class="hl">ESTO</span></div>
    <div class="hand" style="left:${L.hx}px;top:${L.hy}px">${hand({ lines: m.lines, textSub: m.sub })}</div></div>
    <div class="brand" style="top:${brandTop}px"><img src="${f('iso-color.png')}">licitatic.es</div>`;
}

function brandPage(H) {
  return `<div class="grid"></div>
  <div class="wrap">
    <div class="h1">¿Tú también estás <span class="hl" style="padding:0 16px">a esto</span>?</div>
    <div class="serif">Para eso estamos: te echamos una mano.</div>
    <div class="p">Guárdalo y etiqueta a quien le haya pasado.</div>
  </div>
  <div class="foot"><img src="${f('logo-blanco.png')}"><span>www.licitatic.es</span></div>`;
}

// Transformación de zoom: z=1 sin mover; z>1 centra el punto del texto
let FOC = null; // {x,y,w} foco calculado en la página: texto diminuto + puntas de los dedos
async function measure(pg) {
  FOC = await pg.evaluate(() => {
    const t = document.getElementById('tiny').getBoundingClientRect();
    const h = document.querySelector('.hand').getBoundingClientRect();
    const tipX = h.left + 300, x0 = t.left, x1 = Math.max(t.right, tipX);
    return { x: (x0 + x1) / 2, y: t.top + t.height / 2, w: x1 - x0 };
  });
}
function zoomCss(z, H, t = 1) {
  const L = { fx: FOC.x, fy: FOC.y };
  const cx = 540, cy = H * 0.5;
  const tx = (cx - L.fx * z) * t + 0 * (1 - t), ty = (cy - L.fy * z) * t;
  return `translate(${tx}px,${ty}px) scale(${z})`;
}

async function render(id, out, doReel) {
  const m = MEMES[id]; fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  for (const [tag, H] of [['ig', 1350], ['tt', 1920]]) {
    const pg = await b.newPage({ viewport: { width: 1080, height: H } });
    const tmp = path.join(D, 'tmp.html');
    const load = async (body, cls = '') => { fs.writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"><style>${CSS(H)}</style></head><body class="${cls}">${body}</body></html>`); await pg.goto('file://' + tmp); await pg.evaluate(() => document.fonts.ready); };
    await load(memePage(m, H));
    await measure(pg); const ZMAX = Math.min(6.4, 860 / FOC.w);
    const zooms = [[1, 0], [ZMAX / 2.4, 1], [ZMAX, 1]];
    for (const [i, [z, t]] of zooms.entries()) {
      await pg.evaluate(c => { document.getElementById('stage').style.transform = c; }, zoomCss(z, H, t));
      await pg.waitForTimeout(150);
      await pg.screenshot({ path: path.join(out, `${tag}_${id}_${i + 1}.jpg`), type: 'jpeg', quality: 92 });
    }
    await load(brandPage(H), 'dark');
    await pg.screenshot({ path: path.join(out, `${tag}_${id}_4.jpg`), type: 'jpeg', quality: 92 });
    if (doReel && H === 1920) await reel(pg, m, id, out, load);
    await pg.close();
  }
  await b.close();
}

async function reel(pg, m, id, out, load) {
  const H = 1920, FPS = 30, fr = path.join(D, 'frames'); fs.rmSync(fr, { recursive: true, force: true }); fs.mkdirSync(fr);
  let n = 0; const shot = async () => pg.screenshot({ path: path.join(fr, String(n++).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 90 });
  const ease = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  await load(memePage(m, H)); await measure(pg);
  const ZMAX = Math.min(6.4, 860 / FOC.w), hold1 = 1.6, zoom = 3.4, hold2 = 3.2;
  const total = Math.round((hold1 + zoom + hold2) * FPS);
  for (let k = 0; k < total; k++) {
    const s = k / FPS; let z = 1, t = 0;
    if (s > hold1) { const p = ease(Math.min(1, (s - hold1) / zoom)); z = Math.exp(Math.log(ZMAX) * p); t = Math.min(1, p * 1.6); }
    await pg.evaluate(c => { document.getElementById('stage').style.transform = c; }, zoomCss(z, H, t));
    await shot();
  }
  await load(brandPage(H), 'dark');
  for (let k = 0; k < 3 * FPS; k++) await shot();
  const mp4 = path.join(out, `reel_${id}.mp4`);
  execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${fr}/%05d.jpg -f lavfi -i anullsrc=r=44100:cl=stereo -shortest -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 20 -c:a aac -b:a 128k -movflags +faststart ${mp4}`);
  fs.copyFileSync(path.join(fr, '00000.jpg'), path.join(out, `reel_${id}_portada.jpg`));
  fs.rmSync(fr, { recursive: true, force: true });
}

const [id, out, flag] = process.argv.slice(2);
render(id, out || path.join(D, 'out'), flag === '--reel').catch(e => { console.error(e); process.exit(1); });
