const rowsEl = document.getElementById("rows");
const statusEl = document.getElementById("status");
const btnEl = document.getElementById("loadBtn");
const themeEl = document.getElementById("theme");
const prefEl = document.getElementById("pref");
const chartEl = document.getElementById("chart");

const FALLBACK_THEMES = [
  { key: "population", label: "人口" },
  { key: "employment", label: "雇用" },
  { key: "households", label: "世帯" },
  { key: "cpi", label: "消費者物価" },
  { key: "tourism", label: "観光" },
  { key: "wage", label: "賃金" },
];

function escapeHtml(v) {
  return String(v)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function setThemeOptions(themes) {
  if (!themeEl || !themes.length) return;
  themeEl.innerHTML = themes
    .map((t) => `<option value="${escapeHtml(t.key)}">${escapeHtml(t.label)}</option>`)
    .join("");
}

function drawChart(data) {
  if (!chartEl) return;

  if (!Array.isArray(data) || data.length < 2) {
    chartEl.innerHTML = '<div class="chart-empty">折れ線グラフ表示には2年分以上のデータが必要です</div>';
    return;
  }

  const sorted = [...data].sort((a, b) => Number(a.year) - Number(b.year));
  const values = sorted.map((d) => Number(d.value) || 0);
  const years = sorted.map((d) => Number(d.year));

  const w = 920;
  const h = 280;
  const padL = 56;
  const padR = 20;
  const padT = 16;
  const padB = 34;

  const minV = Math.min(...values);
  const maxV = Math.max(...values);
  const spanV = Math.max(maxV - minV, 1);
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;

  const points = values.map((v, i) => {
    const x = padL + (i / (values.length - 1)) * plotW;
    const y = padT + ((maxV - v) / spanV) * plotH;
    return { x, y, v, year: years[i] };
  });

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(" ");

  const yTicks = 4;
  const yLabels = Array.from({ length: yTicks + 1 }, (_, i) => {
    const ratio = i / yTicks;
    const y = padT + ratio * plotH;
    const v = maxV - ratio * spanV;
    return `<text class="line-label" x="8" y="${y + 4}">${Math.round(v).toLocaleString()}</text>`;
  }).join("");

  const xStep = Math.max(1, Math.floor(points.length / 5));
  const xLabels = points
    .filter((_, i) => i % xStep === 0 || i === points.length - 1)
    .map((p) => `<text class="line-label" x="${p.x}" y="${h - 8}" text-anchor="middle">${p.year}</text>`)
    .join("");

  const pointMarks = points
    .map((p) => `<circle class="line-point" cx="${p.x}" cy="${p.y}" r="2.8"><title>${p.year}: ${Math.round(p.v).toLocaleString()}</title></circle>`)
    .join("");

  chartEl.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" role="img" aria-label="直近20年の折れ線グラフ">
      <line class="line-axis" x1="${padL}" y1="${h - padB}" x2="${w - padR}" y2="${h - padB}" />
      <line class="line-axis" x1="${padL}" y1="${padT}" x2="${padL}" y2="${h - padB}" />
      ${yLabels}
      ${xLabels}
      <path class="line-path" d="${path}" />
      ${pointMarks}
    </svg>
  `;
}

async function loadThemes() {
  try {
    const res = await fetch("/api/themes");
    if (!res.ok) throw new Error(`テーマ取得失敗: ${res.status}`);
    const themes = await res.json();
    if (Array.isArray(themes) && themes.length) {
      setThemeOptions(themes);
      return;
    }
  } catch {
    // fall through
  }
  setThemeOptions(FALLBACK_THEMES);
}

async function load() {
  if (!themeEl || !prefEl) return;

  const theme = themeEl.value;
  const prefCode = prefEl.value;

  const params = new URLSearchParams({ theme, years: "20" });
  if (prefCode) params.set("pref", prefCode);

  statusEl.textContent = "読み込み中...";
  rowsEl.innerHTML = "";

  let res;
  try {
    res = await fetch(`/api/stats?${params.toString()}`);
  } catch {
    statusEl.textContent = "APIに接続できません。バックエンド起動を確認してください。";
    drawChart([]);
    return;
  }

  if (!res.ok) {
    statusEl.textContent = `取得失敗: ${res.status}（/api/stats）`;
    drawChart([]);
    return;
  }

  const data = await res.json();
  if (!Array.isArray(data) || !data.length) {
    statusEl.textContent = "データがありません。";
    drawChart([]);
    return;
  }

  const sorted = [...data].sort((a, b) => Number(a.year) - Number(b.year));
  rowsEl.innerHTML = sorted
    .map(
      (r) => `
      <tr>
        <td>${escapeHtml(r.source)}</td>
        <td>${escapeHtml(r.theme)}</td>
        <td>${escapeHtml(r.label)}</td>
        <td>${escapeHtml(r.prefecture_name)} (${escapeHtml(r.prefecture_code)})</td>
        <td>${Number(r.value).toLocaleString()}</td>
        <td>${escapeHtml(r.unit)}</td>
        <td>${escapeHtml(r.year)}</td>
      </tr>
    `
    )
    .join("");

  drawChart(sorted);
  const source = sorted[0]?.source || "";
  if (source === "mock") {
    statusEl.textContent = `${sorted.length}件表示（直近20年 / サンプルデータ）`;
  } else {
    statusEl.textContent = `${sorted.length}件表示（直近20年）`;
  }
}

if (btnEl) {
  btnEl.addEventListener("click", () => {
    load().catch((e) => {
      statusEl.textContent = `エラー: ${e.message}`;
      drawChart([]);
    });
  });
}

loadThemes()
  .then(() => load())
  .catch((e) => {
    statusEl.textContent = `エラー: ${e.message}`;
    drawChart([]);
  });
