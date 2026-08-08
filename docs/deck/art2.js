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

/* ── Stylized speaker portrait (flat vector, deliberately non-photographic) ── */
const portrait = `
<svg xmlns="http://www.w3.org/2000/svg" width="620" height="620" viewBox="0 0 620 620">
  <defs>
    <radialGradient id="rim" cx="18%" cy="26%">
      <stop offset="0%" stop-color="#FF6B35" stop-opacity="0.30"/>
      <stop offset="55%" stop-color="#FF6B35" stop-opacity="0.09"/>
      <stop offset="100%" stop-color="#FF6B35" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="disc" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0%" stop-color="#243055"/>
      <stop offset="100%" stop-color="#141B33"/>
    </linearGradient>
    <linearGradient id="suit" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#232C48"/>
      <stop offset="52%" stop-color="#2E3A5E"/>
      <stop offset="100%" stop-color="#1B2238"/>
    </linearGradient>
    <linearGradient id="skin" x1="0" y1="0" x2="1" y2="0.6">
      <stop offset="0%" stop-color="#F0C9A8"/>
      <stop offset="62%" stop-color="#DFB08A"/>
      <stop offset="100%" stop-color="#B98A66"/>
    </linearGradient>
    <clipPath id="round"><circle cx="310" cy="310" r="300"/></clipPath>
  </defs>

  <g clip-path="url(#round)">
    <rect width="620" height="620" fill="url(#disc)"/>
    ${stars(55, 620, 620, 13)}
    <!-- soft rim light from the left, ties the portrait to the deck accent -->
    <rect width="620" height="620" fill="url(#rim)"/>

    <!-- shoulders / suit -->
    <path d="M40 620 q4 -186 152 -232 l236 0 q148 46 152 232 Z" fill="url(#suit)"/>
    <!-- collar + open shirt -->
    <path d="M252 404 l58 74 58 -74 32 14 -90 118 -90 -118 Z" fill="#E9EDF6"/>
    <path d="M262 400 l48 78 -22 26 -66 -84 Z" fill="#151C31"/>
    <path d="M358 400 l-48 78 22 26 66 -84 Z" fill="#151C31"/>

    <!-- neck -->
    <path d="M276 334 h68 v70 q-34 24 -68 0 Z" fill="#C08F6B"/>
    <ellipse cx="310" cy="336" rx="34" ry="12" fill="#A97B58" opacity="0.55"/>
    <!-- head -->
    <path d="M310 118 q88 0 88 106 q0 22 -6 44 q-14 66 -82 66 q-68 0 -82 -66 q-6 -22 -6 -44 q0 -106 88 -106 Z" fill="url(#skin)"/>
    <!-- ears -->
    <ellipse cx="222" cy="252" rx="13" ry="19" fill="#D5A67F"/>
    <ellipse cx="398" cy="252" rx="13" ry="19" fill="#D5A67F"/>
    <!-- hair: short, swept -->
    <path d="M310 104 q94 0 96 100 q-10 -34 -40 -44 q-56 20 -118 4 q-24 8 -34 40 q2 -100 96 -100 Z" fill="#2B2622"/>
    <path d="M222 214 q10 -46 46 -58 q-30 24 -32 60 Z" fill="#221E1A"/>

    <!-- brows -->
    <rect x="252" y="228" width="42" height="7" rx="3.5" fill="#2B2622"/>
    <rect x="326" y="228" width="42" height="7" rx="3.5" fill="#2B2622"/>
    <!-- eyes -->
    <ellipse cx="273" cy="252" rx="13" ry="9" fill="#FFFFFF"/>
    <ellipse cx="347" cy="252" rx="13" ry="9" fill="#FFFFFF"/>
    <circle cx="275" cy="252" r="5.4" fill="#3B3229"/>
    <circle cx="349" cy="252" r="5.4" fill="#3B3229"/>
    <!-- nose + mouth -->
    <path d="M310 262 q9 26 -2 34 q-7 5 -14 1" fill="none" stroke="#B4835F" stroke-width="5" stroke-linecap="round"/>
    <path d="M288 322 q22 11 44 0" fill="none" stroke="#9C6B4C" stroke-width="5.5" stroke-linecap="round"/>
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
