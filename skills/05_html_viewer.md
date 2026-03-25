# SKILL: Generate HTML Tech DD Viewer

## Purpose
Create a self-contained single-file HTML dashboard that provides:
1. **Overview page** — meta-analysis charts, summary stats, portfolio heatmap
2. **Company list** — sortable/filterable table of all analyzed companies with scores
3. **Deep-dive pages** — per-company Tech DD report with infra diagram, scores, flags, vendor map

## Inputs
- `COMPANY_DB`: Path to `company_db/` directory (default: `company_db/`)
- `REPORTS_DIR`: Path to `reports/` directory (default: `reports/`)
- `CHARTS_DIR`: Path to `reports/charts/` directory

## Prerequisites
- `*_tech_extract.json` files in company_db (from Skill 01)
- `*_tech_dd_report.md` files in reports (from Skill 02)
- `*_infra_diagram.png` files in reports (from Skill 03)
- `reports/charts/*.png` and `meta_summary.json` (from Skill 04)

## Procedure

### Step 1: Generate viewer with embedded data
Write a Python script `generate_viewer.py` that:
1. Loads all tech extractions, reports, chart PNGs, and diagram PNGs
2. Embeds everything as base64 data URIs in a single HTML file
3. Outputs `reports/tech_dd_viewer.html`

### Step 2: HTML Structure

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <title>Tech Due Diligence — Portfolio Analysis</title>
  <style>/* Embedded CSS — dark theme, no external deps */</style>
</head>
<body>
  <nav id="sidebar"><!-- Company list --></nav>
  <main>
    <section id="overview"><!-- Meta-analysis --></section>
    <section id="company-detail" hidden><!-- Per-company DD --></section>
  </main>
  <script>/* Embedded JS — routing, filtering, sorting */</script>
</body>
</html>
```

### Step 3: Design Specifications

#### Theme (CSS)
```css
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
  --font-sans: 'Inter', -apple-system, sans-serif;
}
body { background: var(--bg-primary); color: var(--text-primary); }
```

#### Sidebar (Company Navigation)
- Fixed left sidebar, 280px wide
- Search input at top (filters company list in real-time)
- Dropdown filters: Report Type, Cloud Provider, Score Range
- Company list: each entry shows:
  - Company name (bold)
  - Score badge (color-coded: red <5, yellow 5-7, green 8+)
  - Cloud provider icon/tag
  - Report type tag
- Click navigates to company detail
- "Overview" link at top returns to meta-analysis

#### Overview Page (id="overview")
Layout:
```
┌─────────────────────────────────────────────────────┐
│  PORTFOLIO SUMMARY STATS (4 cards in a row)         │
│  [Total Companies] [Avg Score] [Top Cloud] [% MFA]  │
├─────────────┬───────────────────────────────────────┤
│ Score Dist  │  Score by Dimension (box plot)        │
│ (chart 01)  │  (chart 02)                           │
├─────────────┼───────────────────────────────────────┤
│ Cloud Share │  Infra vs Score (chart 04)            │
│ (chart 03)  │                                       │
├─────────────┴───────────────────────────────────────┤
│ Security Heatmap (chart 05) — full width            │
├─────────────────────────────────────────────────────┤
│ Company Scoreboard Table (sortable by any column)   │
│ Columns: Company, Score, Cloud, Type, Infra, App,   │
│          Security, DevOps, BCDR, Vendor, Red Flags   │
└─────────────────────────────────────────────────────┘
```

#### Company Detail Page (id="company-detail")
Layout:
```
┌─────────────────────────────────────────────────────┐
│  COMPANY HEADER                                      │
│  {name} · {score}/10 · {report_type} · {cloud}      │
│  {website} · {audit_period}                          │
├──────────────────────┬──────────────────────────────┤
│  SCORE RADAR         │  RISK ASSESSMENT              │
│  (6 dimensions,      │  🔴 Red flags                 │
│   rendered as SVG    │  🟡 Yellow flags              │
│   radar chart)       │  🟢 Green flags               │
├──────────────────────┴──────────────────────────────┤
│  INFRASTRUCTURE DIAGRAM (embedded PNG, full width)   │
├─────────────────────────────────────────────────────┤
│  TECH STACK DETAILS (collapsible sections)           │
│  ▸ Infrastructure                                    │
│  ▸ Application Architecture                          │
│  ▸ Data Storage                                      │
│  ▸ Authentication & Access                           │
│  ▸ Encryption                                        │
│  ▸ CI/CD & DevOps                                    │
│  ▸ Monitoring & Logging                              │
│  ▸ Security Tools                                    │
│  ▸ BCDR                                              │
├─────────────────────────────────────────────────────┤
│  VENDOR DEPENDENCY TABLE                             │
├─────────────────────────────────────────────────────┤
│  COMPLIANCE CONTROLS SUMMARY                         │
├─────────────────────────────────────────────────────┤
│  RECOMMENDATION + FOLLOW-UP ITEMS                    │
└─────────────────────────────────────────────────────┘
```

### Step 4: JavaScript Features

```javascript
// All company data embedded as JSON
const COMPANIES = {/* all tech extractions */};
const CHARTS = {/* base64 encoded chart PNGs */};
const DIAGRAMS = {/* base64 encoded diagram PNGs */};

// Client-side rendering
function renderOverview() { /* ... */ }
function renderCompanyDetail(docId) { /* ... */ }
function renderRadarChart(scores) { /* SVG radar chart */ }

// Filtering and sorting
function filterCompanies(query, filters) { /* ... */ }
function sortTable(column, direction) { /* ... */ }

// Navigation (hash-based routing)
window.addEventListener('hashchange', route);
function route() {
  const hash = location.hash;
  if (hash.startsWith('#company/')) {
    renderCompanyDetail(hash.split('/')[1]);
  } else {
    renderOverview();
  }
}
```

### Step 5: Radar Chart (inline SVG)
Generate a radar/spider chart for each company's 6 dimension scores using inline SVG:
- Axes: Infrastructure, App Arch, Data, Security, DevOps, BCDR
- Fill with semi-transparent accent color
- Grid lines at 2, 4, 6, 8, 10
- Score labels at each vertex

### Step 6: Build script
The Python build script (`generate_viewer.py`) should:
1. Collect all data files
2. Convert PNGs to base64 data URIs
3. Render the complete HTML with embedded CSS/JS/data
4. Output a single file: `reports/tech_dd_viewer.html`

```python
import base64, json, glob, os

def img_to_data_uri(path):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.rsplit('.', 1)[-1]
    return f"data:image/{ext};base64,{b64}"

# Collect data
companies = {}
for f in glob.glob("company_db/*_tech_extract.json"):
    doc_id = os.path.basename(f).replace("_tech_extract.json", "")
    with open(f) as fh:
        companies[doc_id] = json.load(fh)

# Collect charts
charts = {}
for f in sorted(glob.glob("reports/charts/*.png")):
    name = os.path.basename(f)
    charts[name] = img_to_data_uri(f)

# Collect diagrams
diagrams = {}
for doc_id in companies:
    # Find matching diagram
    for pattern in [f"reports/*{doc_id}*diagram*.png", ...]:
        matches = glob.glob(pattern)
        if matches:
            diagrams[doc_id] = img_to_data_uri(matches[0])
            break

# Build HTML
html = HTML_TEMPLATE.format(
    companies_json=json.dumps(companies),
    charts_json=json.dumps(charts),
    diagrams_json=json.dumps(diagrams),
)
with open("reports/tech_dd_viewer.html", "w") as f:
    f.write(html)
```

### Step 7: Validate
- Open the HTML and verify:
  - Overview page loads with charts
  - Company list populates and is searchable
  - Clicking a company shows detail view
  - Radar chart renders correctly
  - Infra diagram displays
  - All sections expand/collapse
  - Sorting works on the scoreboard table

## Output
- `reports/tech_dd_viewer.html` — self-contained, no external dependencies
- `generate_viewer.py` — build script (rerunnable)

## Size Considerations
- With 576 companies, each with a ~100KB diagram PNG, the HTML file could be ~60MB+
- If total exceeds 50MB, implement lazy loading: embed only chart PNGs and summary data; load company diagrams on-demand via separate files in `reports/diagrams/`
- Alternative: generate a lightweight version without diagrams (~5MB) and a full version with diagrams
