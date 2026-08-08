// Generate original vector illustrations (copyright-safe) as PNGs for the deck.
const sharp = require('sharp');
const fs = require('fs');

const BG = '#0A0E1F';
const FLAME = '#FF6B35';
const GOLD = '#FFB627';
const STEEL = '#C9D2E8';
const STEEL_D = '#8A93A8';
const CYAN = '#5FD3F3';

function stars(n, w, h, seedStart = 1) {
  let s = '';
  let seed = seedStart;
  const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
  for (let i = 0; i < n; i++) {
    const x = rnd() * w, y = rnd() * h * 0.85;
    const r = rnd() * 1.6 + 0.4;
    const o = rnd() * 0.7 + 0.25;
    s += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(2)}" fill="#FFFFFF" opacity="${o.toFixed(2)}"/>`;
  }
  return s;
}

/* ── 1. Rocket launch (cover) ───────────────────────────────── */
const launch = `
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200" viewBox="0 0 900 1200">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#05070F"/>
      <stop offset="55%" stop-color="#0A0E1F"/>
      <stop offset="100%" stop-color="#1A1330"/>
    </linearGradient>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#6E7893"/>
      <stop offset="28%" stop-color="#F2F5FB"/>
      <stop offset="72%" stop-color="#D2D9EA"/>
      <stop offset="100%" stop-color="#59627C"/>
    </linearGradient>
    <linearGradient id="fl" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFF4D6"/>
      <stop offset="22%" stop-color="#FFB627"/>
      <stop offset="60%" stop-color="#FF6B35"/>
      <stop offset="100%" stop-color="#B32F12" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="50%">
      <stop offset="0%" stop-color="#FF8A4C" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#FF6B35" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="edgeFade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#000000"/>
      <stop offset="20%" stop-color="#FFFFFF"/>
    </linearGradient>
    <mask id="fadeLeft"><rect width="900" height="1200" fill="url(#edgeFade)"/></mask>
    <radialGradient id="plume" cx="50%" cy="10%">
      <stop offset="0%" stop-color="#FFD9A8" stop-opacity="0.55"/>
      <stop offset="55%" stop-color="#9AA4BF" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#5A6480" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <g mask="url(#fadeLeft)">
  <rect width="900" height="1200" fill="url(#sky)"/>
  ${stars(170, 900, 1200, 7)}

  <!-- exhaust plume billowing at base -->
  <ellipse cx="450" cy="1080" rx="330" ry="150" fill="url(#plume)"/>
  <ellipse cx="330" cy="1120" rx="180" ry="90" fill="url(#plume)" opacity="0.8"/>
  <ellipse cx="580" cy="1110" rx="200" ry="95" fill="url(#plume)" opacity="0.7"/>

  <!-- glow behind engines -->
  <ellipse cx="450" cy="900" rx="260" ry="230" fill="url(#glow)"/>

  <!-- flame -->
  <path d="M408 866 Q450 1060 450 1150 Q450 1060 492 866 Z" fill="url(#fl)"/>
  <path d="M424 866 Q450 990 450 1058 Q450 990 476 866 Z" fill="#FFF1CC" opacity="0.92"/>

  <!-- rocket body -->
  <rect x="405" y="300" width="90" height="566" fill="url(#body)"/>
  <!-- nose cone -->
  <path d="M405 300 Q450 168 495 300 Z" fill="url(#body)"/>
  <!-- interstage band -->
  <rect x="405" y="556" width="90" height="30" fill="#2B3450"/>
  <rect x="405" y="596" width="90" height="9" fill="#39435F"/>
  <!-- grid fins -->
  <g fill="#39435F">
    <rect x="374" y="342" width="31" height="52" rx="3"/>
    <rect x="495" y="342" width="31" height="52" rx="3"/>
  </g>
  <g stroke="#5A6685" stroke-width="2" opacity="0.9">
    <line x1="374" y1="358" x2="405" y2="358"/><line x1="374" y1="376" x2="405" y2="376"/>
    <line x1="495" y1="358" x2="526" y2="358"/><line x1="495" y1="376" x2="526" y2="376"/>
  </g>
  <!-- landing legs stowed -->
  <path d="M405 800 L382 866 L397 866 L412 806 Z" fill="#4A5472"/>
  <path d="M495 800 L518 866 L503 866 L488 806 Z" fill="#4A5472"/>
  <!-- engine skirt -->
  <path d="M400 848 L500 848 L492 872 L408 872 Z" fill="#232B44"/>
  <!-- accent stripe on hull (part of the rocket, not slide decor) -->
  <rect x="405" y="668" width="90" height="6" fill="#FF6B35" opacity="0.85"/>
  <circle cx="450" cy="470" r="15" fill="none" stroke="#8A93A8" stroke-width="3"/>
  </g>
</svg>`;

/* ── 2. Starlink constellation over Earth limb ───────────────── */
function sat(x, y, s = 1, rot = 0) {
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
    <rect x="-7" y="-11" width="14" height="22" rx="2.5" fill="${STEEL}"/>
    <rect x="7" y="-8" width="42" height="16" rx="1.5" fill="${CYAN}" opacity="0.82"/>
    <rect x="-49" y="-8" width="42" height="16" rx="1.5" fill="${CYAN}" opacity="0.82"/>
    <line x1="7" y1="0" x2="49" y2="0" stroke="${BG}" stroke-width="1.4" opacity="0.6"/>
    <line x1="-49" y1="0" x2="-7" y2="0" stroke="${BG}" stroke-width="1.4" opacity="0.6"/>
  </g>`;
}

const constellation = `
<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="820" viewBox="0 0 1100 820">
  <defs>
    <radialGradient id="earth" cx="50%" cy="30%">
      <stop offset="0%" stop-color="#2E6FA8"/>
      <stop offset="62%" stop-color="#16406B"/>
      <stop offset="100%" stop-color="#0C2340"/>
    </radialGradient>
    <linearGradient id="atmo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#5FD3F3" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#5FD3F3" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="1100" height="820" fill="${BG}"/>
  ${stars(150, 1100, 700, 23)}

  <!-- orbital shells -->
  <ellipse cx="550" cy="900" rx="690" ry="455" fill="none" stroke="#39435F" stroke-width="1.5" stroke-dasharray="6 9" opacity="0.75"/>
  <ellipse cx="550" cy="900" rx="580" ry="380" fill="none" stroke="#39435F" stroke-width="1.5" stroke-dasharray="6 9" opacity="0.6"/>

  <!-- atmosphere halo + earth limb -->
  <ellipse cx="550" cy="960" rx="520" ry="330" fill="url(#atmo)" opacity="0.5"/>
  <ellipse cx="550" cy="985" rx="500" ry="315" fill="url(#earth)"/>
  <path d="M180 880 q120 -55 250 -18 q90 26 170 -6 q110 -44 210 4" fill="none" stroke="#3E8F6E" stroke-width="16" opacity="0.35" stroke-linecap="round"/>

  <!-- inter-satellite laser links -->
  <g stroke="${GOLD}" stroke-width="1.6" opacity="0.5">
    <line x1="215" y1="470" x2="430" y2="360"/>
    <line x1="430" y1="360" x2="672" y2="392"/>
    <line x1="672" y1="392" x2="880" y2="300"/>
    <line x1="430" y1="360" x2="560" y2="560"/>
    <line x1="672" y1="392" x2="560" y2="560"/>
    <line x1="880" y1="300" x2="955" y2="520"/>
  </g>

  ${sat(215, 470, 1.0, -14)}
  ${sat(430, 360, 1.15, 8)}
  ${sat(672, 392, 1.05, -6)}
  ${sat(880, 300, 0.92, 12)}
  ${sat(560, 560, 0.85, -4)}
  ${sat(955, 520, 0.78, 16)}
</svg>`;

/* ── 3. Orbital data center powered by the sun ───────────────── */
const orbitalDC = `
<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700" viewBox="0 0 1000 700">
  <defs>
    <radialGradient id="sun" cx="50%" cy="50%">
      <stop offset="0%" stop-color="#FFF6D8"/>
      <stop offset="38%" stop-color="#FFB627"/>
      <stop offset="100%" stop-color="#FF6B35" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1B3A6B"/>
      <stop offset="50%" stop-color="#2E6FA8"/>
      <stop offset="100%" stop-color="#16406B"/>
    </linearGradient>
    <linearGradient id="rack" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E8EDF7"/>
      <stop offset="100%" stop-color="#98A2BC"/>
    </linearGradient>
  </defs>
  <rect width="1000" height="700" fill="${BG}"/>
  ${stars(120, 1000, 700, 41)}

  <!-- sun -->
  <circle cx="130" cy="130" r="165" fill="url(#sun)"/>
  <circle cx="130" cy="130" r="52" fill="#FFF6D8"/>
  <!-- light rays toward panels -->
  <g stroke="${GOLD}" stroke-width="2.5" opacity="0.34" stroke-linecap="round">
    <line x1="235" y1="205" x2="400" y2="300"/>
    <line x1="215" y1="245" x2="380" y2="345"/>
    <line x1="252" y1="168" x2="425" y2="258"/>
  </g>

  <!-- solar panel wings -->
  <g transform="translate(500 360)">
    <g transform="translate(-430 -60) skewY(9)">
      <rect x="0" y="0" width="300" height="120" rx="4" fill="url(#panel)"/>
      <g stroke="#0A1B33" stroke-width="2" opacity="0.7">
        <line x1="75" y1="0" x2="75" y2="120"/><line x1="150" y1="0" x2="150" y2="120"/>
        <line x1="225" y1="0" x2="225" y2="120"/><line x1="0" y1="60" x2="300" y2="60"/>
      </g>
    </g>
    <g transform="translate(130 -60) skewY(-9)">
      <rect x="0" y="0" width="300" height="120" rx="4" fill="url(#panel)"/>
      <g stroke="#0A1B33" stroke-width="2" opacity="0.7">
        <line x1="75" y1="0" x2="75" y2="120"/><line x1="150" y1="0" x2="150" y2="120"/>
        <line x1="225" y1="0" x2="225" y2="120"/><line x1="0" y1="60" x2="300" y2="60"/>
      </g>
    </g>
    <rect x="-135" y="-6" width="270" height="12" fill="#6E7893"/>

    <!-- compute core: server racks -->
    <rect x="-92" y="-72" width="184" height="150" rx="7" fill="url(#rack)"/>
    <g fill="#2B3450">
      <rect x="-78" y="-56" width="156" height="20" rx="2.5"/>
      <rect x="-78" y="-28" width="156" height="20" rx="2.5"/>
      <rect x="-78" y="0" width="156" height="20" rx="2.5"/>
      <rect x="-78" y="28" width="156" height="20" rx="2.5"/>
    </g>
    <g fill="${FLAME}">
      <circle cx="62" cy="-46" r="4.5"/><circle cx="62" cy="-18" r="4.5"/>
      <circle cx="62" cy="10" r="4.5"/><circle cx="62" cy="38" r="4.5"/>
    </g>
    <g fill="#5FD3F3">
      <circle cx="46" cy="-46" r="4.5"/><circle cx="46" cy="-18" r="4.5"/>
      <circle cx="46" cy="10" r="4.5"/><circle cx="46" cy="38" r="4.5"/>
    </g>
    <!-- radiator fins (heat rejection into vacuum) -->
    <g fill="#39435F">
      <rect x="-66" y="82" width="132" height="9" rx="2"/>
      <rect x="-56" y="96" width="112" height="9" rx="2"/>
      <rect x="-44" y="110" width="88" height="9" rx="2"/>
    </g>
  </g>

  <!-- downlink beam to earth -->
  <g stroke="#5FD3F3" stroke-width="2" opacity="0.5" stroke-dasharray="5 7">
    <line x1="500" y1="450" x2="760" y2="640"/>
  </g>
  <ellipse cx="820" cy="668" rx="200" ry="46" fill="#16406B" opacity="0.8"/>
</svg>`;

const jobs = [
  ['art-launch.png', launch, 900],
  ['art-constellation.png', constellation, 1100],
  // art-orbital-dc.png is generated by art2.js (wider aspect) — do not emit here
];

(async () => {
  for (const [name, svg, w] of jobs) {
    await sharp(Buffer.from(svg)).resize({ width: w }).png().toFile(name);
    console.log('wrote', name);
  }
})();
