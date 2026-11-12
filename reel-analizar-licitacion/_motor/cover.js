const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'reel.html')); await p.evaluate(() => window.ready);
  await p.evaluate(() => {
    window.render(13.5);
    const $ = id => document.getElementById(id);
    const s = 1.95, cy = 900; $('world').style.transform = `translate(${540 - 437.5 * s}px,${cy - 471.5 * s}px) scale(${s})`;
    document.querySelectorAll('.dim').forEach(e => e.style.opacity = 0.45);
    $('hook').style.opacity = 1; $('hook').style.transform = 'none';
    $('todavia').style.opacity = 1; $('todavia').style.transform = 'none'; $('tdm').style.backgroundSize = '100% 100%';
    $('hdr').style.opacity = 0;
    const C = $('cap'); C.style.opacity = 1; C.style.transform = 'none'; C.style.top = '1250px';
    $('capn').textContent = '8'; $('capl').textContent = 'Antes de presentarte';
    $('capq').textContent = 'Las 8 cosas que tienes que subrayar'; $('capd').textContent = 'Con un pliego real';
  });
  await p.screenshot({ path: path.join(__dirname, 'portada.jpg'), type: 'jpeg', quality: 92 });
  await b.close();
})();
