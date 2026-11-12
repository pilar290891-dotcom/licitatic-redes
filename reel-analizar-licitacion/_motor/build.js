const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 30, END = 54;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'reel.html'));
  await p.evaluate(() => window.ready);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(__dirname, 'musica.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
    '-profile:v', 'high', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', path.join(__dirname, 'reel.mp4')], { stdio: ['pipe', 'ignore', 'inherit'] });
  const total = FPS * END;
  for (let f = 0; f < total; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log('frame', f);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  // portada
  await p.evaluate(() => window.render(1.7));
  await p.screenshot({ path: path.join(__dirname, 'portada.jpg'), type: 'jpeg', quality: 92 });
  await b.close();
})();
