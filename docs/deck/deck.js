const pptxgen = require('pptxgenjs');

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';            // 13.3 x 7.5 — set BEFORE adding slides
pres.author = 'Rui / Pyrenee';
pres.title = 'SpaceX 徹底解剖';

/* ── palette ───────────────────────────────────────────── */
const BG      = '0A0E1F';
const CARD    = '161D36';
const CARD2   = '1E2647';
const FLAME   = 'FF6B35';
const GOLD    = 'FFB627';
const CYAN    = '5FD3F3';
const WHITE   = 'FFFFFF';
const BODY    = 'C5CBDC';
const MUTED   = '858FAB';
const GREEN   = '4ECB8E';
const RED     = 'F4646B';

const H = 'Cambria';      // headings
const B = 'Calibri';      // body

const W = 13.3, HT = 7.5, M = 0.7;

function slide(dark = true) {
  const s = pres.addSlide();
  s.background = { color: dark ? BG : 'F4F6FB' };
  return s;
}

/* circular numbered badge — the deck's repeating motif */
function badge(s, x, y, n, color = FLAME, d = 0.42) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: d, h: d, fill: { color }, line: { color, width: 0 },
  });
  s.addText(String(n), {
    x, y, w: d, h: d, align: 'center', valign: 'middle', margin: 0,
    fontFace: B, fontSize: 13, bold: true, color: BG,
  });
}

function card(s, x, y, w, h, color = CARD) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.09,
    fill: { color }, line: { color: '2A3453', width: 1 },
  });
}

function title(s, text, sub) {
  s.addText(text, {
    x: M, y: 0.44, w: W - M * 2, h: 0.62, margin: 0,
    fontFace: H, fontSize: 30, bold: true, color: WHITE,
  });
  if (sub) {
    s.addText(sub, {
      x: M, y: 1.08, w: W - M * 2, h: 0.36, margin: 0,
      fontFace: B, fontSize: 13.5, color: GOLD,
    });
  }
}

function pageNo(s, n) {
  s.addText(String(n).padStart(2, '0'), {
    x: W - 1.05, y: HT - 0.62, w: 0.5, h: 0.32, margin: 0, align: 'right',
    fontFace: B, fontSize: 11, color: MUTED,
  });
}

/* ════════════════════════════════════════════════════════
   1. COVER
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  s.addImage({
    path: 'art-launch.png', x: 8.35, y: 0, w: 4.95, h: HT,
    sizing: { type: 'cover', w: 4.95, h: HT },
  });
  // soft blend so the artwork edge doesn't cut hard against the text column
  s.addShape(pres.ShapeType.rect, {
    x: 8.35, y: 0, w: 1.5, h: HT, fill: { color: BG, transparency: 35 }, line: { width: 0 },
  });

  s.addText('SPACE EXPLORATION TECHNOLOGIES  |  NASDAQ: SPCX', {
    x: M, y: 1.55, w: 7.3, h: 0.3, margin: 0,
    fontFace: B, fontSize: 11, bold: true, color: FLAME, charSpacing: 1.6,
  });
  s.addText('SpaceX 徹底解剖', {
    x: M, y: 2.0, w: 7.4, h: 1.0, margin: 0,
    fontFace: H, fontSize: 46, bold: true, color: WHITE,
  });
  s.addText('打ち上げ経済圏・Starlink・そして電力戦争へ', {
    x: M, y: 3.05, w: 7.4, h: 0.45, margin: 0,
    fontFace: B, fontSize: 17, color: BODY,
  });
  s.addText('2026年8月8日  |  Q2 2026決算・ロックアップ解除を踏まえて', {
    x: M, y: 3.6, w: 7.4, h: 0.32, margin: 0,
    fontFace: B, fontSize: 12, color: MUTED,
  });

  const stats = [
    ['$7.81B', '四半期売上 (+92%)'],
    ['12,400機', 'Starlink累計打上'],
    ['$15-20M', '打上1回の社内原価'],
  ];
  stats.forEach(([v, l], i) => {
    const x = M + i * 2.5;
    card(s, x, 4.62, 2.25, 1.15);
    s.addText(v, {
      x: x + 0.16, y: 4.76, w: 1.95, h: 0.42, margin: 0,
      fontFace: H, fontSize: 21, bold: true, color: GOLD,
    });
    s.addText(l, {
      x: x + 0.16, y: 5.2, w: 1.95, h: 0.44, margin: 0,
      fontFace: B, fontSize: 10.5, color: MUTED,
    });
  });
  s.addNotes('表紙。右のロケットは著作権フリーの自作ベクター。SpaceX公式写真はCC0のため差し替え可。');
}

/* ════════════════════════════════════════════════════════
   2. EXECUTIVE SUMMARY
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, 'エグゼクティブサマリー', '本資料の結論');

  const items = [
    [FLAME, 'Starlinkが全社を養う',
     '3事業のうち唯一の黒字。営業利益$1.66B。売上の55%を占め、利益は事実上100%。契約数1,200万件は前年比2倍。'],
    [GOLD, '打ち上げは「強いが赤字」',
     'Falcon 9の粗利率は約75%。部門赤字-$542Mの正体はStarship開発費で、四半期あたり約$1B。事業の弱さではない。'],
    [CYAN, '次の主戦場は電力',
     '2030年のDC需要219GWに地上の送電網が追いつかない。SpaceXはFCCに軌道DC衛星100万機を申請済み。'],
  ];

  items.forEach(([c, h, body], i) => {
    const y = 1.72 + i * 1.78;
    card(s, M, y, W - M * 2, 1.40);
    badge(s, M + 0.36, y + 0.34, i + 1, c, 0.46);
    s.addText(h, {
      x: M + 1.05, y: y + 0.26, w: 4.3, h: 0.42, margin: 0,
      fontFace: H, fontSize: 18, bold: true, color: c,
    });
    s.addText(body, {
      x: M + 1.05, y: y + 0.74, w: 10.4, h: 0.62, margin: 0,
      fontFace: B, fontSize: 13, color: BODY, lineSpacingMultiple: 1.12,
    });
  });
  pageNo(s, 2);
  s.addNotes('3つの結論。以降のスライドはこの3点を裏付ける構成。');
}

/* ════════════════════════════════════════════════════════
   3. HISTORY TIMELINE
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, '24年の軌跡', '倒産寸前から史上最大のIPOまで');

  const events = [
    ['2002', '創業', 'ロシアでICBM購入を断られ「自分で作る」と決断'],
    ['2008', '崖っぷち', 'Falcon 1が4回目で初成功。NASA CRS契約$1.6Bで倒産回避'],
    ['2010', 'Falcon 9初飛行', '開発費$390M。NASA試算($3.6-4B)の約1/9で完成'],
    ['2015', '着陸成功', '第1段の地上帰還に世界初成功。再利用時代が始まる'],
    ['2019', 'Starlink開始', '衛星量産と打ち上げの垂直統合が回り出す'],
    ['2023', 'Starship初飛行', '完全再利用への挑戦。累計開発費は$15B超へ'],
    ['2026.6', 'IPO', 'NASDAQ上場。公開価格$135、時価総額$1.75兆'],
    ['2026.8', '初決算', '売上$7.81B(+92%)。同時にロックアップ解除が開始'],
  ];

  events.forEach(([yr, h, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.05;
    const y = 1.72 + row * 1.35;
    card(s, x, y, 5.85, 1.18, row % 2 === 0 ? CARD : CARD2);
    s.addText(yr, {
      x: x + 0.2, y: y + 0.16, w: 1.15, h: 0.34, margin: 0,
      fontFace: H, fontSize: 16, bold: true, color: FLAME,
    });
    s.addText(h, {
      x: x + 1.32, y: y + 0.16, w: 4.3, h: 0.34, margin: 0,
      fontFace: H, fontSize: 15, bold: true, color: WHITE,
    });
    s.addText(d, {
      x: x + 0.2, y: y + 0.58, w: 5.45, h: 0.48, margin: 0,
      fontFace: B, fontSize: 11.5, color: BODY,
    });
  });
  pageNo(s, 3);
  s.addNotes('Falcon 9の開発費$390Mは、NASAが同じものを従来型調達で作った場合の試算$3.6-4Bの約1/9。これが後の全ての原資になる。');
}

/* ════════════════════════════════════════════════════════
   4. Q2 2026 RESULTS
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, 'Q2 2026決算 — 3事業の実像', '売上$7.81B (+92% YoY) / 純損失 -$541M');

  s.addChart(pres.ChartType.bar, [{
    name: '売上高 ($B)',
    labels: ['Connectivity\n(Starlink)', 'AI\n(クラウド)', 'Space\n(打ち上げ)'],
    values: [4.30, 2.56, 0.96],
  }], {
    x: M, y: 1.72, w: 5.9, h: 4.25,
    barDir: 'col', barGapWidthPct: 60,
    chartColors: [CYAN, GOLD, FLAME],
    varyColors: true,
    chartArea: { fill: { color: CARD } },
    plotArea: { fill: { color: CARD } },
    showTitle: true, title: 'セグメント別 売上高 ($B)',
    titleColor: WHITE, titleFontFace: B, titleFontSize: 13,
    showValue: true, dataLabelPosition: 'outEnd',
    dataLabelColor: WHITE, dataLabelFontFace: B, dataLabelFontSize: 12,
    dataLabelFormatCode: '$0.00"B"',
    catAxisLabelColor: BODY, catAxisLabelFontFace: B, catAxisLabelFontSize: 11,
    valAxisLabelColor: MUTED, valAxisLabelFontFace: B, valAxisLabelFontSize: 10,
    valGridLine: { color: '2A3453', size: 1 },
    catGridLine: { style: 'none' },
    valAxisMaxVal: 5,
    showLegend: false,
  });

  const rows = [
    ['Connectivity', '+66%', '+$1.66B', GREEN, '唯一の黒字。契約1,200万件'],
    ['AI', '+247%', '-$1.26B', RED, '設備投資$15.8B/四半期'],
    ['Space', '+29%', '-$0.54B', RED, 'Starship開発費が重い'],
  ];
  s.addText('営業損益で見ると構図が反転する', {
    x: 6.95, y: 1.72, w: 5.65, h: 0.34, margin: 0,
    fontFace: H, fontSize: 16, bold: true, color: WHITE,
  });
  rows.forEach(([n, g, op, c, note], i) => {
    const y = 2.2 + i * 1.28;
    card(s, 6.95, y, 5.65, 1.12);
    s.addText(n, {
      x: 7.15, y: y + 0.14, w: 2.4, h: 0.32, margin: 0,
      fontFace: B, fontSize: 14, bold: true, color: WHITE,
    });
    s.addText(`成長率 ${g}`, {
      x: 7.15, y: y + 0.55, w: 2.4, h: 0.3, margin: 0,
      fontFace: B, fontSize: 11.5, color: MUTED,
    });
    s.addText(op, {
      x: 9.5, y: y + 0.14, w: 1.6, h: 0.36, margin: 0, align: 'right',
      fontFace: H, fontSize: 18, bold: true, color: c,
    });
    s.addText(note, {
      x: 9.5, y: y + 0.58, w: 2.95, h: 0.3, margin: 0, align: 'right',
      fontFace: B, fontSize: 10.5, color: BODY,
    });
  });
  s.addText('決算は大幅ビート。それでも株価が下げたのは、四半期capex $18.4B（うちAIに$15.8B）への警戒。', {
    x: M, y: 6.28, w: W - M * 2, h: 0.36, margin: 0,
    fontFace: B, fontSize: 12, italic: true, color: GOLD,
  });
  pageNo(s, 4);
  s.addNotes('売上ではStarlinkが55%。営業利益では実質100%。AI部門は成長率247%だが赤字。');
}

/* ════════════════════════════════════════════════════════
   5. LAUNCH ECONOMICS
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, '打ち上げ経済学', '同じ仕事を、他社の1/4〜1/10のコストでやる');

  s.addChart(pres.ChartType.bar, [{
    name: '1回あたり費用 ($M)',
    labels: ['SpaceX\n社内原価', 'SpaceX\n外販価格', 'Ariane 6\n(欧州)', 'ULA Vulcan\n(米)'],
    values: [17.5, 74, 100, 155],
  }], {
    x: M, y: 1.78, w: 7.15, h: 4.05,
    barDir: 'bar', barGapWidthPct: 50,
    chartColors: [FLAME, GOLD, '5A6685', '3E4763'],
    varyColors: true,
    chartArea: { fill: { color: CARD } },
    plotArea: { fill: { color: CARD } },
    showTitle: true, title: '打ち上げ1回あたりの費用 ($M)',
    titleColor: WHITE, titleFontFace: B, titleFontSize: 13,
    showValue: true, dataLabelPosition: 'outEnd',
    dataLabelColor: WHITE, dataLabelFontFace: B, dataLabelFontSize: 11.5,
    catAxisLabelColor: BODY, catAxisLabelFontFace: B, catAxisLabelFontSize: 11,
    valAxisLabelColor: MUTED, valAxisLabelFontFace: B, valAxisLabelFontSize: 10,
    valGridLine: { color: '2A3453', size: 1 },
    catGridLine: { style: 'none' },
    showLegend: false,
  });

  card(s, 8.2, 1.78, 4.4, 1.62);
  s.addText('約75%', {
    x: 8.42, y: 1.92, w: 3.95, h: 0.72, margin: 0,
    fontFace: H, fontSize: 38, bold: true, color: FLAME,
  });
  s.addText('Falcon 9の粗利率（外販$74M − 社内原価$17.5M）', {
    x: 8.42, y: 2.6, w: 3.95, h: 0.6, margin: 0,
    fontFace: B, fontSize: 12, color: BODY,
  });

  const notes = [
    ['再利用', '1機のブースターを20回以上使い回す。整備費は約$1M'],
    ['使い捨ての壁', 'Ariane 6もVulcanも毎回ロケットを新造している'],
    ['売り手市場', '2026年2月に$70M→$74Mへ値上げ。それでも席が足りない'],
  ];
  notes.forEach(([h, d], i) => {
    const y = 3.62 + i * 0.78;
    s.addShape(pres.ShapeType.ellipse, {
      x: 8.2, y: y + 0.08, w: 0.16, h: 0.16, fill: { color: GOLD }, line: { width: 0 },
    });
    s.addText(h, {
      x: 8.48, y: y, w: 4.1, h: 0.3, margin: 0,
      fontFace: B, fontSize: 13, bold: true, color: WHITE,
    });
    s.addText(d, {
      x: 8.48, y: y + 0.3, w: 4.1, h: 0.44, margin: 0,
      fontFace: B, fontSize: 10.5, color: MUTED,
    });
  });
  s.addText('※ 社内原価は非公開。Musk発言と業界推定に基づく推定値', {
    x: M, y: 6.32, w: 7.15, h: 0.3, margin: 0,
    fontFace: B, fontSize: 10, color: MUTED,
  });
  pageNo(s, 5);
  s.addNotes('外に売れば$74M取れるロケットを、自社Starlink用には$17.5Mで使える。この差が縦統合の威力。');
}

/* ════════════════════════════════════════════════════════
   6. WHY THE SPACE SEGMENT LOSES MONEY
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, 'なぜ「粗利75%」なのに部門は赤字なのか', 'Space部門 Q2 2026 の分解（推定込み）');

  const steps = [
    ['外部売上', '+$962M', GOLD, '商業・NASA・国防ミッション'],
    ['打ち上げ粗利', '+$450〜500M', GREEN, 'ここは黒字。事業として健全'],
    ['Starship開発費', '−$1,000M', RED, '赤字の正体。四半期あたり約$1B'],
    ['部門営業損益', '−$542M', RED, '「弱さ」ではなく未来への投資'],
  ];
  steps.forEach(([h, v, c, d], i) => {
    const x = M + i * 3.06;
    card(s, x, 1.85, 2.85, 2.15, i === 3 ? CARD2 : CARD);
    s.addText(h, {
      x: x + 0.2, y: 2.05, w: 2.45, h: 0.34, margin: 0,
      fontFace: B, fontSize: 12.5, bold: true, color: MUTED,
    });
    s.addText(v, {
      x: x + 0.2, y: 2.5, w: 2.45, h: 0.62, margin: 0,
      fontFace: H, fontSize: 25, bold: true, color: c,
    });
    s.addText(d, {
      x: x + 0.2, y: 3.24, w: 2.45, h: 0.72, margin: 0,
      fontFace: B, fontSize: 11, color: BODY, lineSpacingMultiple: 1.1,
    });
    if (i < 3) {
      s.addText('▶', {
        x: x + 2.85, y: 2.9, w: 0.21, h: 0.4, margin: 0, align: 'center',
        fontFace: B, fontSize: 13, color: FLAME,
      });
    }
  });

  const facts = [
    ['38倍', 'Starship累計開発費$15B ÷ Falcon 9の$390M'],
    ['2/3', '打ち上げの2/3は自社Starlink向け。社内取引なので売上に計上されない'],
    ['$4B超', 'NASA HLS契約。Starship開発費の一部は政府が負担している'],
  ];
  facts.forEach(([v, d], i) => {
    const x = M + i * 4.07;
    card(s, x, 4.45, 3.86, 1.35, CARD2);
    s.addText(v, {
      x: x + 0.2, y: 4.61, w: 3.46, h: 0.4, margin: 0,
      fontFace: H, fontSize: 19, bold: true, color: GOLD,
    });
    s.addText(d, {
      x: x + 0.2, y: 5.03, w: 3.46, h: 0.66, margin: 0,
      fontFace: B, fontSize: 10.5, color: BODY, lineSpacingMultiple: 1.1,
    });
  });
  s.addText('監視すべきは1点 — Starshipの年間支出が減り始めたら開発完了が近い。増え続けるなら回収は後ろ倒し。', {
    x: M, y: 6.3, w: W - M * 2, h: 0.34, margin: 0,
    fontFace: B, fontSize: 12, italic: true, color: GOLD,
  });
  pageNo(s, 6);
  s.addNotes('Falcon 9事業は儲かっている。赤字はStarshipへの意図的な投資。2025年の支出は$3B（前年$1.84B）と加速中。');
}

/* ════════════════════════════════════════════════════════
   7. STARLINK
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, 'Starlink — 利益エンジンの正体', '打ち上げ1回が13ヶ月で元を取る構造');

  s.addImage({
    path: 'art-constellation.png', x: 6.9, y: 1.78, w: 5.7, h: 4.25,
    sizing: { type: 'cover', w: 5.7, h: 4.25 },
  });

  const stats = [
    ['12,400機', '累計打ち上げ', CYAN],
    ['10,800機', '現在軌道上で稼働', CYAN],
    ['1,200万', '契約数（前年比2倍）', GOLD],
  ];
  stats.forEach(([v, l, c], i) => {
    const y = 1.78 + i * 1.03;
    card(s, M, y, 5.85, 0.88);
    s.addText(v, {
      x: M + 0.22, y: y + 0.16, w: 2.5, h: 0.56, margin: 0, valign: 'middle',
      fontFace: H, fontSize: 24, bold: true, color: c,
    });
    s.addText(l, {
      x: M + 2.85, y: y + 0.16, w: 2.75, h: 0.56, margin: 0, valign: 'middle', align: 'right',
      fontFace: B, fontSize: 12, color: BODY,
    });
  });

  card(s, M, 4.92, 5.85, 1.42, CARD2);
  s.addText('13ヶ月で回収', {
    x: M + 0.22, y: 5.06, w: 5.4, h: 0.4, margin: 0,
    fontFace: H, fontSize: 18, bold: true, color: FLAME,
  });
  s.addText('1回$40M（ロケット＋衛星24機）→ 約2.6万契約分の容量 → 月$3.1Mの収入。衛星寿命5年のうち最初の1年で元が取れる。', {
    x: M + 0.22, y: 5.5, w: 5.4, h: 0.74, margin: 0,
    fontFace: B, fontSize: 11.5, color: BODY, lineSpacingMultiple: 1.12,
  });
  s.addText('競合は外部からロケットを買うため1回$70〜100M。回収に2〜3年かかり、衛星寿命とのマージンが薄い。', {
    x: M, y: 6.5, w: W - M * 2, h: 0.34, margin: 0,
    fontFace: B, fontSize: 11.5, italic: true, color: MUTED,
  });
  pageNo(s, 7);
  s.addNotes('人類の稼働衛星の過半数がStarlink。2〜4日に1回のペースで打ち上げ続けている。');
}

/* ════════════════════════════════════════════════════════
   8. POWER — THE NEXT BATTLEGROUND
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, '次の主戦場は「電力」', 'AIデータセンター需要が地球側の限界に当たる');

  s.addChart(pres.ChartType.bar, [{
    name: 'DC電力需要 (GW)',
    labels: ['2025年', '2026年', '2030年予測'],
    values: [82, 88, 219],
  }], {
    x: M, y: 1.78, w: 5.5, h: 3.15,
    barDir: 'col', barGapWidthPct: 70,
    chartColors: ['3E4763', '5A6685', FLAME],
    varyColors: true,
    chartArea: { fill: { color: CARD } },
    plotArea: { fill: { color: CARD } },
    showTitle: true, title: '世界のデータセンター電力需要 (GW)',
    titleColor: WHITE, titleFontFace: B, titleFontSize: 12.5,
    showValue: true, dataLabelPosition: 'outEnd',
    dataLabelColor: WHITE, dataLabelFontFace: B, dataLabelFontSize: 12,
    catAxisLabelColor: BODY, catAxisLabelFontFace: B, catAxisLabelFontSize: 11,
    valAxisLabelColor: MUTED, valAxisLabelFontFace: B, valAxisLabelFontSize: 10,
    valGridLine: { color: '2A3453', size: 1 },
    catGridLine: { style: 'none' },
    showLegend: false,
  });
  s.addText('2030年にはAIが全需要の70%を占める（McKinsey）', {
    x: M, y: 5.02, w: 5.5, h: 0.3, margin: 0,
    fontFace: B, fontSize: 11, color: MUTED,
  });

  s.addText('土地は足りる。電気が足りない。', {
    x: 6.6, y: 1.78, w: 6.0, h: 0.38, margin: 0,
    fontFace: H, fontSize: 18, bold: true, color: WHITE,
  });

  const comp = [
    ['建物・キャンパスの土地', '東京都 1個分', '2030年の219GW分でも約1,300〜2,700km²。陸地のわずか0.002%', GREEN],
    ['それを太陽光で賄う土地', '長野県 1個分', '約13,000km²のパネルが要る。しかも稼働率は20〜35%', RED],
  ];
  comp.forEach(([h, v, d, c], i) => {
    const y = 2.32 + i * 1.5;
    card(s, 6.6, y, 6.0, 1.32);
    s.addText(h, {
      x: 6.82, y: y + 0.14, w: 3.3, h: 0.3, margin: 0,
      fontFace: B, fontSize: 11.5, color: MUTED,
    });
    s.addText(v, {
      x: 6.82, y: y + 0.44, w: 3.3, h: 0.4, margin: 0,
      fontFace: H, fontSize: 19, bold: true, color: c,
    });
    s.addText(d, {
      x: 6.82, y: y + 0.86, w: 5.55, h: 0.4, margin: 0,
      fontFace: B, fontSize: 10.5, color: BODY,
    });
  });

  card(s, 6.6, 5.32, 6.0, 1.28, CARD2);
  s.addText('本当の壁は送電網', {
    x: 6.82, y: 5.44, w: 5.55, h: 0.32, margin: 0,
    fontFace: B, fontSize: 13, bold: true, color: GOLD,
  });
  s.addText('電力網への接続待ちは5年超。冷却水は1日数百万リットル。土地を買っても電気が引けない — これが軌道データセンター構想の出発点。', {
    x: 6.82, y: 5.78, w: 5.55, h: 0.72, margin: 0,
    fontFace: B, fontSize: 11, color: BODY, lineSpacingMultiple: 1.12,
  });
  pageNo(s, 8);
  s.addNotes('発表済みのDC計画は合計190GW・777件。日本全国の電力ピーク需要を超える規模。');
}

/* ════════════════════════════════════════════════════════
   9. THE POWER WAR + MUSK QUOTE
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, 'なぜ核融合ではなく「宇宙」なのか', 'AI電力戦争の三つ巴と、Muskの一貫した論理');

  // quote block
  card(s, M, 1.75, 7.3, 1.72, CARD2);
  s.addText('“', {
    x: M + 0.18, y: 1.70, w: 0.6, h: 0.95, margin: 0,
    fontFace: H, fontSize: 54, bold: true, color: FLAME,
  });
  s.addText('空にすでに巨大な核融合炉が浮かんでいる。\n太陽という名前で、無料で、メンテナンス不要だ。', {
    x: M + 0.78, y: 1.98, w: 6.3, h: 0.86, margin: 0,
    fontFace: H, fontSize: 15.5, italic: true, color: WHITE, lineSpacingMultiple: 1.2,
  });
  s.addText('— Elon Musk（宇宙太陽光をめぐる持論より）', {
    x: M + 0.78, y: 2.92, w: 6.3, h: 0.3, margin: 0,
    fontFace: B, fontSize: 11, color: GOLD,
  });

  s.addImage({
    path: 'art-orbital-dc.png', x: 8.3, y: 1.75, w: 4.3, h: 1.72,
    sizing: { type: 'cover', w: 4.3, h: 1.72 },
  });

  const camps = [
    ['SpaceX / xAI', '軌道太陽光', FLAME,
     'FCCに衛星DC 100万機を申請。夜も雲もない軌道なら発電量は地上の約8倍。急所はStarshipのコストカーブ。'],
    ['Google', '両張り', CYAN,
     'CFSと核融合200MWの購電契約を結びつつ、Suncatcher衛星でTPUを2027年に軌道投入。最もリスク分散が効く。'],
    ['OpenAI / MSFT', '核融合', GOLD,
     'Helionと2028年50MWの購電契約。ただし商用炉は世界にまだゼロで、必要規模には3桁足りない。'],
  ];
  camps.forEach(([n, bet, c, d], i) => {
    const x = M + i * 4.07;
    card(s, x, 3.68, 3.86, 1.92);
    s.addText(n, {
      x: x + 0.2, y: 3.84, w: 3.46, h: 0.32, margin: 0,
      fontFace: B, fontSize: 12, color: MUTED,
    });
    s.addText(bet, {
      x: x + 0.2, y: 4.16, w: 3.46, h: 0.44, margin: 0,
      fontFace: H, fontSize: 20, bold: true, color: c,
    });
    s.addText(d, {
      x: x + 0.2, y: 4.68, w: 3.46, h: 0.92, margin: 0,
      fontFace: B, fontSize: 10.5, color: BODY, lineSpacingMultiple: 1.14,
    });
  });

  s.addText('移行期の現実解はTesla Megapack — 2025年売上$12.8B(+27%)。AIデータセンターが送電網を待つ間の緩衝材として売れている。', {
    x: M, y: 6.18, w: W - M * 2, h: 0.34, margin: 0,
    fontFace: B, fontSize: 11.5, italic: true, color: GOLD,
  });
  s.addText('※ 引用は発言の主旨を日本語に要約したもの', {
    x: M, y: 6.56, w: 6.0, h: 0.28, margin: 0,
    fontFace: B, fontSize: 9.5, color: MUTED,
  });
  pageNo(s, 9);
  s.addNotes('Muskの理屈では宇宙太陽光は核融合の代替ではなく「完成済みの核融合炉から直接電気を引く方法」。核融合が成功してもTeslaの電池が売れるので彼は困らない。');
}

/* ════════════════════════════════════════════════════════
   10. INVESTMENT VIEW
   ════════════════════════════════════════════════════════ */
{
  const s = slide();
  title(s, '投資判断 — 3シナリオと降りる線', '保有: SPCX 3株 @ $135 / 現在値 $108〜115');

  const sc = [
    ['Bull', '25%', '$145〜160', GREEN, 'Starlink単独IPOの発表、またはStarship商業運用の開始'],
    ['Base', '50%', '$105〜130', GOLD, '材料難。ロックアップ消化が続き現水準でのもみ合い'],
    ['Bear', '25%', '$100割れ', RED, '政治リスクがNASA・国防契約に波及。Starshipの重大事故'],
  ];
  sc.forEach(([n, p, tgt, c, d], i) => {
    const x = M + i * 4.07;
    card(s, x, 1.85, 3.86, 2.05);
    s.addText(n, {
      x: x + 0.2, y: 2.0, w: 1.8, h: 0.38, margin: 0,
      fontFace: H, fontSize: 20, bold: true, color: c,
    });
    s.addText(`確率 ${p}`, {
      x: x + 2.0, y: 2.06, w: 1.66, h: 0.32, margin: 0, align: 'right',
      fontFace: B, fontSize: 12, color: MUTED,
    });
    s.addText(tgt, {
      x: x + 0.2, y: 2.48, w: 3.46, h: 0.5, margin: 0,
      fontFace: H, fontSize: 24, bold: true, color: WHITE,
    });
    s.addText(d, {
      x: x + 0.2, y: 3.06, w: 3.46, h: 0.82, margin: 0,
      fontFace: B, fontSize: 10.5, color: BODY, lineSpacingMultiple: 1.14,
    });
  });

  card(s, M, 4.4, 5.85, 1.95, CARD2);
  s.addText('監視すべき先行指標', {
    x: M + 0.22, y: 4.54, w: 5.4, h: 0.32, margin: 0,
    fontFace: B, fontSize: 13, bold: true, color: CYAN,
  });
  [
    'Starshipの年間支出 — 減少なら開発完了が近い',
    'Starlink契約の純増数 — 利益エンジンの健全性',
    '政府契約の新規受注と見直しの動き',
  ].forEach((t, i) => {
    s.addText(t, {
      x: M + 0.22, y: 4.9 + i * 0.4, w: 5.4, h: 0.36, margin: 0,
      fontFace: B, fontSize: 11, color: BODY, bullet: true,
    });
  });

  card(s, 6.75, 4.4, 5.85, 1.95);
  s.addText('Kill Criteria（降りる線）', {
    x: 6.97, y: 4.54, w: 5.4, h: 0.32, margin: 0,
    fontFace: B, fontSize: 13, bold: true, color: RED,
  });
  [
    '$100を明確に下抜けたら損切りを実行する',
    'Starshipの重大事故で開発が長期停止',
    '政府契約が実際に見直し・剥奪された時点',
  ].forEach((t, i) => {
    s.addText(t, {
      x: 6.97, y: 4.9 + i * 0.4, w: 5.4, h: 0.36, margin: 0,
      fontFace: B, fontSize: 11, color: BODY, bullet: true,
    });
  });

  s.addText('本資料は情報提供を目的としたもので、投資勧誘ではありません。数値には推定を含み、最終判断はご自身の責任で行ってください。', {
    x: M, y: 6.62, w: W - M * 2, h: 0.3, margin: 0,
    fontFace: B, fontSize: 9.5, color: MUTED,
  });
  pageNo(s, 10);
  s.addNotes('感情で判断しないためにKill Criteriaを事前に決めておくことが目的。特に$100割れは機械的に実行する。');
}

pres.writeFile({ fileName: 'SpaceX-徹底解剖.pptx' })
  .then(f => console.log('created:', f));
