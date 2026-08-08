// Additional original illustrations: a stylized speaker portrait for the quote
// slide, and a wider-aspect orbital data centre so it stops getting cropped.
const sharp = require('sharp');

const BG = '#0A0E1F';
const CARD = '#1E2647';
const FLAME = '#FF6B35';
const GOLD = '#FFB627';

function stars(n, w, h, seedStart = 1) {
  let s = '', seed = seedStart;
  const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
  for (let i = 0; i < n; i++) {
    s += `<circle cx="${(rnd()*w).toFixed(1)}" cy="${(rnd()*h).toFixed(1)}" r="${(rnd()*1.5+0.4).toFixed(2)}" fill="#FFFFFF" opacity="${(rnd()*0.7+0.25).toFixed(2)}"/>`;
  }
  return s;
}

/* ── Caricature of Elon Musk (original flat-vector illustration, not a photo).
   Likeness cues: high hairline with deep temple recession, full lower cheeks
   and a heavy rounded chin, one-sided smirk, black crew-neck tee. ── */
const portrait = `
<svg xmlns="http://www.w3.org/2000/svg" width="620" height="620" viewBox="0 0 620 620">
  <defs>
    <radialGradient id="rim" cx="18%" cy="24%">
      <stop offset="0%" stop-color="#FF6B35" stop-opacity="0.30"/>
      <stop offset="55%" stop-color="#FF6B35" stop-opacity="0.09"/>
      <stop offset="100%" stop-color="#FF6B35" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="disc" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0%" stop-color="#243055"/>
      <stop offset="100%" stop-color="#141B33"/>
    </linearGradient>
    <linearGradient id="tee" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#151B2B"/>
      <stop offset="50%" stop-color="#222A40"/>
      <stop offset="100%" stop-color="#111623"/>
    </linearGradient>
    <linearGradient id="skin" x1="0.1" y1="0" x2="1" y2="0.7">
      <stop offset="0%" stop-color="#F3CFAE"/>
      <stop offset="58%" stop-color="#E2B48C"/>
      <stop offset="100%" stop-color="#BE8E69"/>
    </linearGradient>
    <clipPath id="round"><circle cx="310" cy="310" r="300"/></clipPath>
  </defs>

  <g clip-path="url(#round)">
    <rect width="620" height="620" fill="url(#disc)"/>
    ${stars(55, 620, 620, 13)}
    <rect width="620" height="620" fill="url(#rim)"/>

    <!-- neck -->
    <path d="M264 336 h92 v78 q-46 28 -92 0 Z" fill="#C2916C"/>
    <ellipse cx="310" cy="338" rx="46" ry="14" fill="#A87A57" opacity="0.5"/>

    <!-- broad shoulders in a black crew-neck tee -->
    <path d="M16 620 q10 -182 168 -230 l252 0 q158 48 168 230 Z" fill="url(#tee)"/>

    <!-- neckline + rib -->
    <path d="M238 400 q72 62 144 0 l18 20 q-90 74 -180 0 Z" fill="#0D111C"/>
    <path d="M247 407 q63 52 126 0" fill="none" stroke="#39435F"
          stroke-width="4" stroke-linecap="round" opacity="0.75"/>

    <!-- ears sit outside the face silhouette -->
    <ellipse cx="200" cy="274" rx="15" ry="25" fill="#D7A87F"/>
    <ellipse cx="420" cy="274" rx="15" ry="25" fill="#D7A87F"/>

    <!-- face: wide cheeks tapering to a heavy rounded chin -->
    <path d="M310 152 q106 0 106 120 q0 44 -14 80 q-23 62 -92 62 q-69 0 -92 -62
             q-14 -36 -14 -80 q0 -120 106 -120 Z" fill="url(#skin)"/>
    <!-- jaw weight -->
    <path d="M222 322 q28 82 88 84 q60 -2 88 -84 q-10 72 -88 80 q-78 -8 -88 -80 Z"
          fill="#C99669" opacity="0.38"/>

    <!-- hair: high forehead, deep recession at both temples, combed back -->
    <path d="M204 254 q2 -110 106 -114 q104 4 106 114
             q-24 -66 -74 -72 q-14 22 -32 22 q-18 0 -32 -22 q-50 6 -74 72 Z"
          fill="#3A2E26"/>
    <path d="M204 258 q8 -76 50 -100 q-34 38 -36 100 Z" fill="#2C221B"/>
    <path d="M416 258 q-8 -76 -50 -100 q34 38 36 100 Z" fill="#2C221B"/>
    <!-- sideburns -->
    <path d="M218 258 q7 36 5 56 q-16 -20 -16 -56 Z" fill="#3A2E26"/>
    <path d="M402 258 q-7 36 -5 56 q16 -20 16 -56 Z" fill="#3A2E26"/>

    <!-- heavier brows -->
    <path d="M246 258 q28 -13 56 -2 l0 10 q-28 -9 -56 3 Z" fill="#3A2E26"/>
    <path d="M374 258 q-28 -13 -56 -2 l0 10 q28 -9 56 3 Z" fill="#3A2E26"/>
    <!-- eyes -->
    <ellipse cx="268" cy="286" rx="15" ry="9.5" fill="#FFFFFF"/>
    <ellipse cx="352" cy="286" rx="15" ry="9.5" fill="#FFFFFF"/>
    <circle cx="270" cy="287" r="6" fill="#4A3B2C"/>
    <circle cx="354" cy="287" r="6" fill="#4A3B2C"/>
    <path d="M253 279 q15 -9 30 -3" fill="none" stroke="#C4906A" stroke-width="3"/>
    <path d="M337 276 q15 -6 30 3" fill="none" stroke="#C4906A" stroke-width="3"/>

    <!-- nose -->
    <path d="M310 296 q12 32 -2 43 q-10 6 -19 1" fill="none"
          stroke="#B4835F" stroke-width="5.5" stroke-linecap="round"/>
    <!-- asymmetric smirk: right corner lifts -->
    <path d="M276 360 q30 15 58 -7" fill="none" stroke="#9C6B4C"
          stroke-width="6.5" stroke-linecap="round"/>
    <path d="M332 356 q7 -4 9 -10" fill="none" stroke="#9C6B4C"
          stroke-width="5" stroke-linecap="round"/>
  </g>

  <circle cx="310" cy="310" r="300" fill="none" stroke="${GOLD}" stroke-width="6" opacity="0.85"/>
</svg>`;

/* ── Orbital data centre, wider aspect so the slide crop stops cutting it ── */
const orbitalWide = `
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">
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
  <rect width="1200" height="560" fill="${BG}"/>
  ${stars(110, 1200, 560, 41)}

  <circle cx="130" cy="120" r="150" fill="url(#sun)"/>
  <circle cx="130" cy="120" r="46" fill="#FFF6D8"/>
  <g stroke="${GOLD}" stroke-width="2.5" opacity="0.32" stroke-linecap="round">
    <line x1="228" y1="182" x2="392" y2="248"/>
    <line x1="208" y1="216" x2="372" y2="288"/>
    <line x1="246" y1="150" x2="418" y2="212"/>
  </g>

  <g transform="translate(640 285)">
    <g transform="translate(-470 -58) skewY(8)">
      <rect x="0" y="0" width="320" height="116" rx="4" fill="url(#panel)"/>
      <g stroke="#0A1B33" stroke-width="2" opacity="0.7">
        <line x1="80" y1="0" x2="80" y2="116"/><line x1="160" y1="0" x2="160" y2="116"/>
        <line x1="240" y1="0" x2="240" y2="116"/><line x1="0" y1="58" x2="320" y2="58"/>
      </g>
    </g>
    <g transform="translate(150 -58) skewY(-8)">
      <rect x="0" y="0" width="320" height="116" rx="4" fill="url(#panel)"/>
      <g stroke="#0A1B33" stroke-width="2" opacity="0.7">
        <line x1="80" y1="0" x2="80" y2="116"/><line x1="160" y1="0" x2="160" y2="116"/>
        <line x1="240" y1="0" x2="240" y2="116"/><line x1="0" y1="58" x2="320" y2="58"/>
      </g>
    </g>
    <rect x="-152" y="-6" width="304" height="12" fill="#6E7893"/>

    <rect x="-88" y="-70" width="176" height="146" rx="7" fill="url(#rack)"/>
    <g fill="#2B3450">
      <rect x="-74" y="-54" width="148" height="19" rx="2.5"/>
      <rect x="-74" y="-27" width="148" height="19" rx="2.5"/>
      <rect x="-74" y="0" width="148" height="19" rx="2.5"/>
      <rect x="-74" y="27" width="148" height="19" rx="2.5"/>
    </g>
    <g fill="${FLAME}">
      <circle cx="58" cy="-44" r="4.3"/><circle cx="58" cy="-17" r="4.3"/>
      <circle cx="58" cy="10" r="4.3"/><circle cx="58" cy="37" r="4.3"/>
    </g>
    <g fill="#5FD3F3">
      <circle cx="43" cy="-44" r="4.3"/><circle cx="43" cy="-17" r="4.3"/>
      <circle cx="43" cy="10" r="4.3"/><circle cx="43" cy="37" r="4.3"/>
    </g>
    <g fill="#39435F">
      <rect x="-62" y="80" width="124" height="9" rx="2"/>
      <rect x="-52" y="94" width="104" height="9" rx="2"/>
      <rect x="-40" y="108" width="80" height="9" rx="2"/>
    </g>
  </g>

  <g stroke="#5FD3F3" stroke-width="2" opacity="0.5" stroke-dasharray="5 7">
    <line x1="640" y1="400" x2="900" y2="512"/>
  </g>
  <ellipse cx="990" cy="536" rx="230" ry="42" fill="#16406B" opacity="0.85"/>
</svg>`;

(async () => {
  for (const [name, svg, w] of [
    ['art-portrait.png', portrait, 620],
    ['art-orbital-dc.png', orbitalWide, 1200],
  ]) {
    await sharp(Buffer.from(svg)).resize({ width: w }).png().toFile(name);
    console.log('wrote', name);
  }
})();
