#!/usr/bin/env python3
"""Generate a self-contained single-file HTML Tech DD Viewer dashboard."""

import base64
import json
import glob
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANY_DB = os.path.join(BASE_DIR, "company_db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
CHARTS_DIR = os.path.join(REPORTS_DIR, "charts")
OUTPUT_PATH = os.path.join(REPORTS_DIR, "tech_dd_viewer.html")


def img_to_data_uri(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def collect_companies() -> dict:
    companies = {}
    for f in sorted(glob.glob(os.path.join(COMPANY_DB, "*_tech_extract.json"))):
        doc_id = os.path.basename(f).replace("_tech_extract.json", "")
        with open(f) as fh:
            companies[doc_id] = json.load(fh)
    return companies


def collect_charts() -> dict:
    charts = {}
    for f in sorted(glob.glob(os.path.join(CHARTS_DIR, "*.png"))):
        name = os.path.basename(f)
        charts[name] = img_to_data_uri(f)
    return charts


def collect_diagrams(companies: dict) -> dict:
    diagrams = {}
    # Map doc_ids to diagram files
    diagram_map = {
        "11x": os.path.join(REPORTS_DIR, "11x_infra_diagram.png"),
        "agentmail": os.path.join(REPORTS_DIR, "agentmail_infra_diagram.png"),
    }
    for doc_id, data in companies.items():
        company_name = data.get("company", "").lower()
        for key, path in diagram_map.items():
            if key in company_name or key in doc_id.lower():
                if os.path.exists(path):
                    diagrams[doc_id] = img_to_data_uri(path)
                    break
        # Fallback: try glob patterns
        if doc_id not in diagrams:
            for pattern in [
                os.path.join(REPORTS_DIR, f"*{doc_id}*diagram*.png"),
                os.path.join(REPORTS_DIR, "*infra_diagram.png"),
            ]:
                matches = glob.glob(pattern)
                if matches:
                    diagrams[doc_id] = img_to_data_uri(matches[0])
                    break
    return diagrams


def collect_meta_summary() -> dict:
    path = os.path.join(CHARTS_DIR, "meta_summary.json")
    with open(path) as f:
        return json.load(f)


def build_html(companies: dict, charts: dict, diagrams: dict, meta: dict) -> str:
    return HTML_TEMPLATE.replace(
        "/*__COMPANIES_JSON__*/", json.dumps(companies)
    ).replace(
        "/*__CHARTS_JSON__*/", json.dumps(charts)
    ).replace(
        "/*__DIAGRAMS_JSON__*/", json.dumps(diagrams)
    ).replace(
        "/*__META_JSON__*/", json.dumps(meta)
    )


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tech Due Diligence — Portfolio Analysis</title>
<style>
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1a2332;
  --border: #334155;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --accent-blue: #3b82f6;
  --accent-green: #22c55e;
  --accent-yellow: #f59e0b;
  --accent-red: #ef4444;
  --accent-purple: #a855f7;
  --font-mono: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 15px; }
body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.6;
  display: flex;
  min-height: 100vh;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* Sidebar */
#sidebar {
  position: fixed;
  top: 0; left: 0; bottom: 0;
  width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow: hidden;
}
#sidebar-header {
  padding: 20px 16px 12px;
  border-bottom: 1px solid var(--border);
}
#sidebar-header h1 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-blue);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
#sidebar-header a.overview-link {
  display: block;
  padding: 8px 12px;
  border-radius: 6px;
  color: var(--text-primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 12px;
  transition: background 0.15s;
}
#sidebar-header a.overview-link:hover,
#sidebar-header a.overview-link.active {
  background: var(--accent-blue);
  color: #fff;
}
#search-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  outline: none;
}
#search-input:focus { border-color: var(--accent-blue); }
#search-input::placeholder { color: var(--text-secondary); }

#company-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.company-entry {
  display: block;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
  margin-bottom: 2px;
}
.company-entry:hover { background: rgba(59,130,246,0.1); }
.company-entry.active { background: rgba(59,130,246,0.15); border-left: 3px solid var(--accent-blue); }
.company-entry .name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.company-entry .meta {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.badge-score-red { background: rgba(239,68,68,0.2); color: var(--accent-red); }
.badge-score-yellow { background: rgba(245,158,11,0.2); color: var(--accent-yellow); }
.badge-score-green { background: rgba(34,197,94,0.2); color: var(--accent-green); }
.badge-cloud { background: rgba(59,130,246,0.15); color: var(--accent-blue); }
.badge-type { background: rgba(168,85,247,0.15); color: var(--accent-purple); }

/* Main content */
main {
  margin-left: 280px;
  flex: 1;
  padding: 32px 40px;
  max-width: 1400px;
}

/* Stat cards */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
}
.stat-card .label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.stat-card .value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
}
.stat-card .value.blue { color: var(--accent-blue); }
.stat-card .value.green { color: var(--accent-green); }
.stat-card .value.yellow { color: var(--accent-yellow); }

/* Chart grid */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}
.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  overflow: hidden;
}
.chart-card.full-width { grid-column: 1 / -1; }
.chart-card img {
  width: 100%;
  height: auto;
  border-radius: 6px;
}
.chart-card .chart-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

/* Scoreboard table */
.table-wrapper {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow-x: auto;
  margin-bottom: 32px;
}
.table-wrapper h2 {
  padding: 16px 20px 0;
  font-size: 1rem;
  color: var(--text-primary);
}
table.scoreboard {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
table.scoreboard th {
  padding: 12px 14px;
  text-align: left;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
table.scoreboard th:hover { color: var(--accent-blue); }
table.scoreboard th .sort-arrow { margin-left: 4px; font-size: 0.65rem; }
table.scoreboard td {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(51,65,85,0.4);
  white-space: nowrap;
}
table.scoreboard tr:hover { background: rgba(59,130,246,0.05); }
table.scoreboard td.company-link {
  color: var(--accent-blue);
  cursor: pointer;
  font-weight: 600;
}
table.scoreboard td.company-link:hover { text-decoration: underline; }
.score-cell { font-family: var(--font-mono); font-weight: 600; }
.score-cell.red { color: var(--accent-red); }
.score-cell.yellow { color: var(--accent-yellow); }
.score-cell.green { color: var(--accent-green); }

/* Company detail */
#company-detail { display: none; }
.detail-header {
  margin-bottom: 28px;
}
.detail-header h2 {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 6px;
}
.detail-header .header-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  color: var(--text-secondary);
  font-size: 0.85rem;
}
.detail-header .header-meta .sep { color: var(--border); }
.detail-header .overall-score {
  font-size: 2.2rem;
  font-weight: 800;
  font-family: var(--font-mono);
}
.detail-header .overall-score span { font-size: 1rem; font-weight: 400; color: var(--text-secondary); }

/* Two-column layout for radar + flags */
.detail-top-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 28px;
}
.radar-card, .flags-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
}
.radar-card h3, .flags-card h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.radar-card svg { display: block; margin: 0 auto; }

.flag-section { margin-bottom: 16px; }
.flag-section h4 {
  font-size: 0.8rem;
  font-weight: 700;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.flag-section h4 .dot {
  width: 8px; height: 8px; border-radius: 50%; display: inline-block;
}
.flag-section.red h4 .dot { background: var(--accent-red); }
.flag-section.red h4 { color: var(--accent-red); }
.flag-section.yellow h4 .dot { background: var(--accent-yellow); }
.flag-section.yellow h4 { color: var(--accent-yellow); }
.flag-section.green h4 .dot { background: var(--accent-green); }
.flag-section.green h4 { color: var(--accent-green); }
.flag-list {
  list-style: none;
  padding: 0;
}
.flag-list li {
  font-size: 0.82rem;
  color: var(--text-secondary);
  padding: 4px 0 4px 16px;
  position: relative;
  line-height: 1.5;
}
.flag-list li::before {
  content: '';
  position: absolute;
  left: 0; top: 10px;
  width: 5px; height: 5px;
  border-radius: 50%;
}
.flag-section.red .flag-list li::before { background: var(--accent-red); }
.flag-section.yellow .flag-list li::before { background: var(--accent-yellow); }
.flag-section.green .flag-list li::before { background: var(--accent-green); }

/* Infra diagram */
.infra-diagram-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 28px;
}
.infra-diagram-card h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 12px;
}
.infra-diagram-card img {
  width: 100%;
  height: auto;
  border-radius: 6px;
}

/* Collapsible sections */
.collapsible {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 8px;
  overflow: hidden;
}
.collapsible-header {
  padding: 14px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  user-select: none;
  transition: background 0.15s;
}
.collapsible-header:hover { background: rgba(59,130,246,0.05); }
.collapsible-header h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}
.collapsible-header .arrow {
  color: var(--text-secondary);
  transition: transform 0.2s;
  font-size: 0.8rem;
}
.collapsible.open .collapsible-header .arrow { transform: rotate(90deg); }
.collapsible-body {
  display: none;
  padding: 0 20px 16px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.7;
}
.collapsible.open .collapsible-body { display: block; }

.detail-label {
  font-weight: 600;
  color: var(--text-primary);
  margin-right: 6px;
}
.detail-row {
  padding: 4px 0;
}

/* Vendor table */
.vendor-table-wrap {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow-x: auto;
  margin-bottom: 28px;
  margin-top: 20px;
}
.vendor-table-wrap h3 {
  padding: 16px 20px 0;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}
table.vendor-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
table.vendor-table th {
  padding: 10px 14px;
  text-align: left;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}
table.vendor-table td {
  padding: 8px 14px;
  border-bottom: 1px solid rgba(51,65,85,0.4);
}
.crit-critical { color: var(--accent-red); font-weight: 600; }
.crit-high { color: var(--accent-yellow); font-weight: 600; }
.crit-medium { color: var(--accent-blue); }
.crit-low { color: var(--text-secondary); }

/* Compliance + Recommendations */
.info-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}
.info-card h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 12px;
}
.info-card ul { padding-left: 18px; }
.info-card li {
  font-size: 0.82rem;
  color: var(--text-secondary);
  padding: 3px 0;
  line-height: 1.5;
}
.info-card p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
}
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.info-grid .stat-line {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 0.82rem;
}
.info-grid .stat-line .lbl { color: var(--text-secondary); }
.info-grid .stat-line .val { color: var(--text-primary); font-weight: 600; font-family: var(--font-mono); }

/* Section title */
.section-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  margin: 28px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

@media (max-width: 1100px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
  .detail-top-grid { grid-template-columns: 1fr; }
}
@media (max-width: 800px) {
  #sidebar { width: 220px; }
  main { margin-left: 220px; padding: 20px; }
  .chart-grid { grid-template-columns: 1fr; }
  .stat-cards { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<nav id="sidebar">
  <div id="sidebar-header">
    <h1>Tech DD Viewer</h1>
    <a class="overview-link active" href="#overview">Portfolio Overview</a>
    <input type="text" id="search-input" placeholder="Search companies...">
  </div>
  <div id="company-list"></div>
</nav>

<main>
  <section id="overview"></section>
  <section id="company-detail"></section>
</main>

<script>
// Embedded data
const COMPANIES = /*__COMPANIES_JSON__*/;
const CHARTS = /*__CHARTS_JSON__*/;
const DIAGRAMS = /*__DIAGRAMS_JSON__*/;
const META = /*__META_JSON__*/;

// Chart display names
const CHART_NAMES = {
  '01_score_distribution.png': 'Score Distribution',
  '02_score_dimensions_box.png': 'Score by Dimension',
  '03_cloud_provider_share.png': 'Cloud Provider Share',
  '04_infra_vs_score.png': 'Infrastructure vs Score',
  '05_security_heatmap.png': 'Security Heatmap',
  '06_vendor_count_distribution.png': 'Vendor Count Distribution',
  '07_report_type_breakdown.png': 'Report Type Breakdown',
  '08_architecture_patterns.png': 'Architecture Patterns',
  '09_bcdr_readiness.png': 'BCDR Readiness',
  '10_flag_frequency.png': 'Flag Frequency',
  '11_score_correlations.png': 'Score Correlations',
  '12_investment_readiness.png': 'Investment Readiness'
};

const FULL_WIDTH_CHARTS = ['05_security_heatmap.png', '11_score_correlations.png'];

// Utility functions
function scoreColor(s) {
  if (s < 5) return 'red';
  if (s < 8) return 'yellow';
  return 'green';
}
function scoreBadgeClass(s) {
  if (s < 5) return 'badge-score-red';
  if (s < 8) return 'badge-score-yellow';
  return 'badge-score-green';
}
function escHtml(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function getCloud(c) {
  let cloud = c.infrastructure?.cloud_provider || '';
  // Extract just the provider name
  let m = cloud.match(/^(AWS|GCP|Azure|DigitalOcean|Vercel)/i);
  return m ? m[1] : cloud.split('(')[0].trim().substring(0, 20);
}

// Build company list
const companyEntries = Object.entries(COMPANIES).map(([id, c]) => ({
  id,
  name: c.company || id,
  score: c.scoring?.overall?.score ?? 0,
  cloud: getCloud(c),
  type: c.report_type || '',
  data: c
})).sort((a, b) => a.name.localeCompare(b.name));

// Render sidebar
function renderSidebar(filter) {
  const list = document.getElementById('company-list');
  const q = (filter || '').toLowerCase();
  const filtered = companyEntries.filter(e =>
    !q || e.name.toLowerCase().includes(q) || e.cloud.toLowerCase().includes(q)
  );
  const hash = location.hash;
  list.innerHTML = filtered.map(e => {
    const active = hash === '#company/' + e.id ? ' active' : '';
    return `<a class="company-entry${active}" href="#company/${e.id}">
      <div class="name">
        ${escHtml(e.name)}
        <span class="badge ${scoreBadgeClass(e.score)}">${e.score}/10</span>
      </div>
      <div class="meta">
        <span class="badge badge-cloud">${escHtml(e.cloud)}</span>
        <span class="badge badge-type">${escHtml(e.type)}</span>
      </div>
    </a>`;
  }).join('');
}

// Sort state
let sortCol = null;
let sortDir = 1; // 1 = asc, -1 = desc

function renderOverview() {
  document.getElementById('overview').style.display = 'block';
  document.getElementById('company-detail').style.display = 'none';

  // Update sidebar active state
  document.querySelector('.overview-link').classList.add('active');
  document.querySelectorAll('.company-entry').forEach(e => e.classList.remove('active'));

  const section = document.getElementById('overview');

  // Stat cards
  let statsHtml = `<div class="stat-cards">
    <div class="stat-card">
      <div class="label">Total Companies</div>
      <div class="value blue">${META.total_companies_analyzed}</div>
    </div>
    <div class="stat-card">
      <div class="label">Average Score</div>
      <div class="value ${scoreColor(META.mean_overall_score)}">${META.mean_overall_score.toFixed(1)}/10</div>
    </div>
    <div class="stat-card">
      <div class="label">Top Cloud Provider</div>
      <div class="value blue">${escHtml(META.top_cloud_provider)}</div>
    </div>
    <div class="stat-card">
      <div class="label">With MFA</div>
      <div class="value green">${META.pct_with_mfa.toFixed(0)}%</div>
    </div>
  </div>`;

  // Charts
  let chartsHtml = '<div class="chart-grid">';
  for (const [fname, dataUri] of Object.entries(CHARTS)) {
    const fw = FULL_WIDTH_CHARTS.includes(fname) ? ' full-width' : '';
    const title = CHART_NAMES[fname] || fname.replace(/^\d+_/, '').replace('.png', '').replace(/_/g, ' ');
    chartsHtml += `<div class="chart-card${fw}">
      <div class="chart-title">${escHtml(title)}</div>
      <img src="${dataUri}" alt="${escHtml(title)}" loading="lazy">
    </div>`;
  }
  chartsHtml += '</div>';

  // Scoreboard
  const dims = [
    ['company', 'Company'],
    ['overall', 'Overall'],
    ['cloud', 'Cloud'],
    ['type', 'Type'],
    ['infrastructure', 'Infra'],
    ['application_architecture', 'App Arch'],
    ['data_layer', 'Data'],
    ['security_posture', 'Security'],
    ['devops_maturity', 'DevOps'],
    ['bcdr_readiness', 'BCDR'],
    ['vendor_diversity', 'Vendor Div'],
    ['red_flags', 'Red Flags']
  ];

  let rows = companyEntries.map(e => {
    const s = e.data.scoring || {};
    return {
      id: e.id,
      company: e.name,
      overall: s.overall?.score ?? 0,
      cloud: e.cloud,
      type: e.type,
      infrastructure: s.infrastructure?.score ?? 0,
      application_architecture: s.application_architecture?.score ?? 0,
      data_layer: s.data_layer?.score ?? 0,
      security_posture: s.security_posture?.score ?? 0,
      devops_maturity: s.devops_maturity?.score ?? 0,
      bcdr_readiness: s.bcdr_readiness?.score ?? 0,
      vendor_diversity: s.vendor_diversity?.score ?? 0,
      red_flags: (e.data.red_flags || []).length
    };
  });

  if (sortCol) {
    rows.sort((a, b) => {
      let va = a[sortCol], vb = b[sortCol];
      if (typeof va === 'string') return va.localeCompare(vb) * sortDir;
      return (va - vb) * sortDir;
    });
  }

  let tableHtml = `<div class="table-wrapper"><h2>Company Scoreboard</h2><table class="scoreboard"><thead><tr>`;
  for (const [key, label] of dims) {
    const arrow = sortCol === key ? (sortDir === 1 ? ' &#9650;' : ' &#9660;') : '';
    tableHtml += `<th data-col="${key}">${label}<span class="sort-arrow">${arrow}</span></th>`;
  }
  tableHtml += '</tr></thead><tbody>';
  for (const row of rows) {
    tableHtml += '<tr>';
    for (const [key] of dims) {
      if (key === 'company') {
        tableHtml += `<td class="company-link" data-id="${row.id}">${escHtml(row.company)}</td>`;
      } else if (key === 'cloud' || key === 'type') {
        tableHtml += `<td>${escHtml(row[key])}</td>`;
      } else if (key === 'red_flags') {
        const c = row.red_flags > 3 ? 'red' : row.red_flags > 1 ? 'yellow' : 'green';
        tableHtml += `<td class="score-cell ${c}">${row.red_flags}</td>`;
      } else {
        const c = scoreColor(row[key]);
        tableHtml += `<td class="score-cell ${c}">${row[key]}</td>`;
      }
    }
    tableHtml += '</tr>';
  }
  tableHtml += '</tbody></table></div>';

  section.innerHTML = statsHtml + chartsHtml + tableHtml;

  // Table sorting
  section.querySelectorAll('th[data-col]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.col;
      if (sortCol === col) { sortDir *= -1; }
      else { sortCol = col; sortDir = 1; }
      renderOverview();
    });
  });

  // Company links in table
  section.querySelectorAll('.company-link').forEach(td => {
    td.addEventListener('click', () => {
      location.hash = '#company/' + td.dataset.id;
    });
  });
}

// Radar chart SVG renderer
function renderRadarSVG(scores) {
  // scores: array of {label, value} where value is 0-10
  const n = scores.length;
  const cx = 150, cy = 150, R = 120;
  const levels = [2, 4, 6, 8, 10];

  let svg = `<svg width="300" height="320" viewBox="0 0 300 320" xmlns="http://www.w3.org/2000/svg">`;

  // Background
  function pointOnAxis(i, r) {
    const angle = (Math.PI * 2 * i / n) - Math.PI / 2;
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
  }

  // Grid
  for (const lvl of levels) {
    const r = (lvl / 10) * R;
    let pts = [];
    for (let i = 0; i < n; i++) pts.push(pointOnAxis(i, r).join(','));
    svg += `<polygon points="${pts.join(' ')}" fill="none" stroke="#334155" stroke-width="0.5"/>`;
  }

  // Axes
  for (let i = 0; i < n; i++) {
    const [x, y] = pointOnAxis(i, R);
    svg += `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="#334155" stroke-width="0.5"/>`;
  }

  // Data polygon
  let dataPts = [];
  for (let i = 0; i < n; i++) {
    const r = (scores[i].value / 10) * R;
    dataPts.push(pointOnAxis(i, r).join(','));
  }
  svg += `<polygon points="${dataPts.join(' ')}" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" stroke-width="2"/>`;

  // Data points and labels
  for (let i = 0; i < n; i++) {
    const r = (scores[i].value / 10) * R;
    const [dx, dy] = pointOnAxis(i, r);
    svg += `<circle cx="${dx}" cy="${dy}" r="4" fill="#3b82f6"/>`;

    // Label
    const [lx, ly] = pointOnAxis(i, R + 22);
    const anchor = lx < cx - 10 ? 'end' : lx > cx + 10 ? 'start' : 'middle';
    svg += `<text x="${lx}" y="${ly}" text-anchor="${anchor}" fill="#94a3b8" font-size="10" font-family="Inter, sans-serif">${escHtml(scores[i].label)}</text>`;
    // Score value
    svg += `<text x="${lx}" y="${ly + 13}" text-anchor="${anchor}" fill="#e2e8f0" font-size="11" font-weight="bold" font-family="monospace">${scores[i].value}/10</text>`;
  }

  // Grid level labels
  for (const lvl of [2, 4, 6, 8, 10]) {
    const r = (lvl / 10) * R;
    svg += `<text x="${cx + 3}" y="${cy - r - 2}" fill="#475569" font-size="8" font-family="monospace">${lvl}</text>`;
  }

  svg += '</svg>';
  return svg;
}

// Render company detail
function renderCompanyDetail(docId) {
  const c = COMPANIES[docId];
  if (!c) { location.hash = '#overview'; return; }

  document.getElementById('overview').style.display = 'none';
  document.getElementById('company-detail').style.display = 'block';

  // Update sidebar
  document.querySelector('.overview-link').classList.remove('active');
  document.querySelectorAll('.company-entry').forEach(e => {
    e.classList.toggle('active', e.getAttribute('href') === '#company/' + docId);
  });

  const section = document.getElementById('company-detail');
  const s = c.scoring || {};
  const overall = s.overall?.score ?? 0;

  // Header
  let html = `<div class="detail-header">
    <h2>${escHtml(c.company)}</h2>
    <div class="header-meta">
      <span class="overall-score ${scoreColor(overall)}">${overall}<span>/10</span></span>
      <span class="sep">|</span>
      <span>${escHtml(c.report_type)}</span>
      <span class="sep">|</span>
      <span>${escHtml(getCloud(c))}</span>
      ${c.hq ? `<span class="sep">|</span><span>${escHtml(c.hq)}</span>` : ''}
      ${c.audit_period ? `<span class="sep">|</span><span>${escHtml(c.audit_period)}</span>` : ''}
    </div>
  </div>`;

  // Radar + Flags
  const radarScores = [
    { label: 'Infrastructure', value: s.infrastructure?.score ?? 0 },
    { label: 'App Arch', value: s.application_architecture?.score ?? 0 },
    { label: 'Data', value: s.data_layer?.score ?? 0 },
    { label: 'Security', value: s.security_posture?.score ?? 0 },
    { label: 'DevOps', value: s.devops_maturity?.score ?? 0 },
    { label: 'BCDR', value: s.bcdr_readiness?.score ?? 0 }
  ];

  html += `<div class="detail-top-grid">
    <div class="radar-card">
      <h3>Dimension Scores</h3>
      ${renderRadarSVG(radarScores)}
    </div>
    <div class="flags-card">
      <h3>Risk Assessment</h3>`;

  // Red flags
  if (c.red_flags?.length) {
    html += `<div class="flag-section red"><h4><span class="dot"></span> Red Flags (${c.red_flags.length})</h4><ul class="flag-list">`;
    c.red_flags.forEach(f => { html += `<li>${escHtml(f)}</li>`; });
    html += '</ul></div>';
  }
  if (c.yellow_flags?.length) {
    html += `<div class="flag-section yellow"><h4><span class="dot"></span> Yellow Flags (${c.yellow_flags.length})</h4><ul class="flag-list">`;
    c.yellow_flags.forEach(f => { html += `<li>${escHtml(f)}</li>`; });
    html += '</ul></div>';
  }
  if (c.green_flags?.length) {
    html += `<div class="flag-section green"><h4><span class="dot"></span> Green Flags (${c.green_flags.length})</h4><ul class="flag-list">`;
    c.green_flags.forEach(f => { html += `<li>${escHtml(f)}</li>`; });
    html += '</ul></div>';
  }
  html += '</div></div>';

  // Infrastructure diagram
  if (DIAGRAMS[docId]) {
    html += `<div class="infra-diagram-card">
      <h3>Infrastructure Diagram</h3>
      <img src="${DIAGRAMS[docId]}" alt="Infrastructure diagram for ${escHtml(c.company)}">
    </div>`;
  }

  // Tech stack collapsible sections
  html += '<div class="section-title">Tech Stack Details</div>';

  const sections = [
    { key: 'infrastructure', title: 'Infrastructure', render: () => renderKV(c.infrastructure) },
    { key: 'application_architecture', title: 'Application Architecture', render: () => renderKV(c.application_architecture) },
    { key: 'network_architecture', title: 'Network Architecture', render: () => renderKV(c.network_architecture) },
    { key: 'data_storage', title: 'Data Storage', render: () => renderKV(c.data_storage) },
    { key: 'authentication_access_control', title: 'Authentication & Access Control', render: () => renderKV(c.authentication_access_control) },
    { key: 'encryption', title: 'Encryption', render: () => renderKV(c.encryption) },
    { key: 'ci_cd_devops', title: 'CI/CD & DevOps', render: () => renderKV(c.ci_cd_devops) },
    { key: 'monitoring_logging', title: 'Monitoring & Logging', render: () => renderKV(c.monitoring_logging) },
    { key: 'security_tools', title: 'Security Tools', render: () => renderKV(c.security_tools) },
    { key: 'bcdr', title: 'BCDR', render: () => renderKV(c.bcdr) }
  ];

  for (const sec of sections) {
    if (!c[sec.key]) continue;
    html += `<div class="collapsible">
      <div class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">
        <h3>${sec.title}</h3>
        <span class="arrow">&#9654;</span>
      </div>
      <div class="collapsible-body">${sec.render()}</div>
    </div>`;
  }

  // Scoring rationales
  html += '<div class="section-title">Scoring Rationales</div>';
  const scoreDims = ['infrastructure', 'application_architecture', 'data_layer', 'security_posture', 'devops_maturity', 'bcdr_readiness', 'vendor_diversity', 'overall'];
  const dimLabels = {
    infrastructure: 'Infrastructure',
    application_architecture: 'Application Architecture',
    data_layer: 'Data Layer',
    security_posture: 'Security Posture',
    devops_maturity: 'DevOps Maturity',
    bcdr_readiness: 'BCDR Readiness',
    vendor_diversity: 'Vendor Diversity',
    overall: 'Overall'
  };
  for (const dim of scoreDims) {
    if (!s[dim]) continue;
    html += `<div class="collapsible">
      <div class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">
        <h3>${dimLabels[dim] || dim} &mdash; <span class="score-cell ${scoreColor(s[dim].score)}">${s[dim].score}/10</span></h3>
        <span class="arrow">&#9654;</span>
      </div>
      <div class="collapsible-body"><p>${escHtml(s[dim].rationale)}</p></div>
    </div>`;
  }

  // Vendor dependency table
  if (c.third_party_services?.length) {
    html += `<div class="vendor-table-wrap"><h3>Vendor Dependencies</h3>
      <table class="vendor-table"><thead><tr><th>Vendor</th><th>Purpose</th><th>Criticality</th></tr></thead><tbody>`;
    for (const v of c.third_party_services) {
      const cc = (v.criticality || '').toLowerCase();
      const cls = cc === 'critical' ? 'crit-critical' : cc === 'high' ? 'crit-high' : cc === 'medium' ? 'crit-medium' : 'crit-low';
      html += `<tr><td style="font-weight:600">${escHtml(v.vendor)}</td><td>${escHtml(v.purpose)}</td><td class="${cls}">${escHtml(v.criticality)}</td></tr>`;
    }
    html += '</tbody></table></div>';
  }

  // Compliance controls
  if (c.compliance_controls) {
    const cc = c.compliance_controls;
    html += `<div class="info-card"><h3>Compliance Controls Summary</h3>
      <div class="info-grid">
        <div class="stat-line"><span class="lbl">Controls Tested</span><span class="val">${cc.total_controls_tested ?? 'N/A'}</span></div>
        <div class="stat-line"><span class="lbl">Exceptions</span><span class="val">${cc.exceptions ?? 'N/A'}</span></div>
      </div>`;
    if (cc.untestable?.length) {
      html += `<div style="margin-top:12px"><strong style="color:var(--text-primary);font-size:0.8rem">Untestable Controls:</strong><ul>`;
      cc.untestable.forEach(u => { html += `<li>${escHtml(u)}</li>`; });
      html += '</ul></div>';
    }
    if (cc.excluded_criteria?.length) {
      html += `<div style="margin-top:12px"><strong style="color:var(--text-primary);font-size:0.8rem">Excluded Criteria:</strong><ul>`;
      cc.excluded_criteria.forEach(e => { html += `<li>${escHtml(e)}</li>`; });
      html += '</ul></div>';
    }
    if (cc.notable_controls?.length) {
      html += `<div style="margin-top:12px"><strong style="color:var(--text-primary);font-size:0.8rem">Notable Controls:</strong><ul>`;
      cc.notable_controls.forEach(n => { html += `<li>${escHtml(n)}</li>`; });
      html += '</ul></div>';
    }
    html += '</div>';
  }

  // Key observations / recommendations
  if (c.key_observations?.length) {
    html += `<div class="info-card"><h3>Key Observations &amp; Recommendations</h3><ul>`;
    c.key_observations.forEach(o => { html += `<li>${escHtml(o)}</li>`; });
    html += '</ul></div>';
  }

  section.innerHTML = html;
}

// Render key-value pairs from a flat object
function renderKV(obj) {
  if (!obj) return '<p>No data available.</p>';
  let html = '';
  for (const [k, v] of Object.entries(obj)) {
    const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    let val;
    if (v === true) val = '<span style="color:var(--accent-green)">Yes</span>';
    else if (v === false) val = '<span style="color:var(--accent-red)">No</span>';
    else if (v === null) val = '<span style="color:var(--text-secondary)">Not mentioned</span>';
    else if (Array.isArray(v)) {
      if (v.length === 0) val = '<span style="color:var(--text-secondary)">None</span>';
      else val = v.map(x => typeof x === 'object' ? JSON.stringify(x) : escHtml(x)).join(', ');
    } else val = escHtml(v);
    html += `<div class="detail-row"><span class="detail-label">${escHtml(label)}:</span> ${val}</div>`;
  }
  return html;
}

// Router
function route() {
  const hash = location.hash || '#overview';
  if (hash.startsWith('#company/')) {
    const docId = hash.substring(9);
    renderCompanyDetail(docId);
  } else {
    renderOverview();
  }
  renderSidebar(document.getElementById('search-input').value);
}

// Events
window.addEventListener('hashchange', route);
document.getElementById('search-input').addEventListener('input', function() {
  renderSidebar(this.value);
});

// Initial render
route();
</script>
</body>
</html>'''


def main():
    print("Collecting company data...")
    companies = collect_companies()
    print(f"  Found {len(companies)} companies")

    print("Collecting charts...")
    charts = collect_charts()
    print(f"  Found {len(charts)} charts")

    print("Collecting diagrams...")
    diagrams = collect_diagrams(companies)
    print(f"  Found {len(diagrams)} diagrams")

    print("Loading meta summary...")
    meta = collect_meta_summary()

    print("Building HTML...")
    html = build_html(companies, charts, diagrams, meta)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"Output: {OUTPUT_PATH}")
    print(f"Size: {size_mb:.2f} MB")
    print("Done.")


if __name__ == "__main__":
    main()
