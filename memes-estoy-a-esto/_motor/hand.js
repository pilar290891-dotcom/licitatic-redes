// Mano propia LicitaTIC haciendo el gesto «estoy a esto» (índice y pulgar casi juntos).
// Técnica: cada forma se pinta dos veces (contorno azul marino grueso y relleno blanco encima)
// para que el contorno quede unido sin líneas internas. Coordenadas en un lienzo 1000x1000.
const NAVY = '#03214F', TEAL = '#0CA8AC';
const OUT = 15; // grosor del contorno

// Dedos como trazos redondeados [puntos, grosor]
const fingers = [
  { d: 'M 330 438 C 450 418, 600 440, 720 500', w: 96 },   // índice
  { d: 'M 345 566 C 450 580, 540 625, 620 710', w: 100 },  // pulgar
];
// Palma + muñeca (polígono relleno)
const palm = 'M 600 468 C 760 440, 860 470, 900 560 C 930 640, 900 760, 880 860 L 870 1010 L 600 1010 L 610 880 C 560 800, 545 700, 565 600 C 572 540, 585 495, 600 468 Z';

const TX = 256, TY = 503; // centro del texto diminuto (punto de zoom)
function hand({ lines = [], textSub = '' } = {}) {
  const outerF = fingers.map(f => `<path d="${f.d}" stroke="${NAVY}" stroke-width="${f.w + OUT * 2}" stroke-linecap="round" fill="none"/>`).join('');
  const innerF = fingers.map(f => `<path d="${f.d}" stroke="#fff" stroke-width="${f.w}" stroke-linecap="round" fill="none"/>`).join('');
  return `<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <defs><filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter></defs>
  <!-- halo turquesa -->
  <g filter="url(#glow)" opacity=".45">
    ${fingers.map(f => `<path d="${f.d}" stroke="${TEAL}" stroke-width="${f.w + 70}" stroke-linecap="round" fill="none"/>`).join('')}
    <path d="${palm}" fill="${TEAL}" stroke="${TEAL}" stroke-width="70" stroke-linejoin="round"/>
  </g>
  <!-- contorno -->
  <path d="${palm}" fill="${NAVY}" stroke="${NAVY}" stroke-width="${OUT * 2}" stroke-linejoin="round"/>
  ${outerF}
  <!-- relleno -->
  <path d="${palm}" fill="#fff"/>
  ${innerF}
  <!-- dedos doblados (corazón, anular, meñique) -->
  <g stroke="${NAVY}" stroke-width="13" fill="none" stroke-linecap="round">
    <path d="M 690 530 C 640 540, 600 575, 610 610 C 618 640, 660 640, 690 615"/>
    <path d="M 700 600 C 650 615, 615 650, 628 685 C 638 712, 676 712, 704 688"/>
    <path d="M 712 668 C 668 684, 642 716, 655 748 C 665 772, 698 770, 720 750"/>
    <!-- arruga del nudillo del índice y uña -->
    <path d="M 380 420 C 372 438, 372 452, 380 466" stroke-width="9"/>
    <path d="M 400 548 C 394 562, 396 578, 404 590" stroke-width="9"/>
  </g>
  <!-- puño de camisa con detalle turquesa -->
  <path d="M 585 905 L 895 905 L 905 1500 L 575 1500 Z" fill="${NAVY}" stroke="${NAVY}" stroke-width="20" stroke-linejoin="round"/>
  <rect x="595" y="928" width="300" height="10" rx="5" fill="${TEAL}"/>
  <circle cx="850" cy="968" r="13" fill="#fff"/>
  <!-- texto diminuto entre los dedos -->
  <g font-family="M" fill="${NAVY}" text-anchor="end" id="tiny">
    ${lines.map((l, i) => `<text x="${TX}" y="${TY + (i - (lines.length - 1) / 2) * 14 + 4}" font-size="12" font-weight="600">${l}</text>`).join('')}
    ${textSub ? `<text x="${TX}" y="${TY + lines.length * 7 + 11}" font-size="6.6" font-weight="400" fill="#08777A">${textSub}</text>` : ''}
  </g>
</svg>`;
}
module.exports = { hand, TX, TY };
