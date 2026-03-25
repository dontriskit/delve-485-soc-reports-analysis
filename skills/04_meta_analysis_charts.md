# SKILL: Meta-Analysis Charts (Seaborn)

## Purpose
Analyze all extracted tech data across the full portfolio of companies and generate publication-quality charts using Seaborn for investor-level meta-analysis.

## Inputs
- `COMPANY_DB`: Path to `company_db/` directory (default: `company_db/`)
- `OUTPUT_DIR`: Path for chart output (default: `reports/charts/`)

## Prerequisites
- Multiple `{COMPANY_DB}/*_tech_extract.json` files must exist (output of Skill 01 run across companies)
- Python packages: `uv add seaborn pandas matplotlib`

## Procedure

### Step 1: Load all extractions
```python
import json, glob, pandas as pd

extracts = []
for f in glob.glob("company_db/*_tech_extract.json"):
    with open(f) as fh:
        extracts.append(json.load(fh))
df = pd.json_normalize(extracts, sep='_')
```

### Step 2: Generate chart suite
Create a Python script `generate_charts.py` that produces these charts. Use a consistent dark theme:

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Global dark theme
plt.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor': '#16213e',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#e2e8f0',
    'text.color': '#e2e8f0',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#1e3a5f',
    'font.family': 'monospace',
    'font.size': 11,
})
PALETTE = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7",
           "#38bdf8", "#10b981", "#ff9900", "#ec4899", "#6366f1"]
```

### Chart 1: Overall Score Distribution
`01_score_distribution.png`
- Histogram + KDE of `scoring.overall.score` across all companies
- Vertical lines at mean and median
- Title: "Tech DD Score Distribution (N={count})"

### Chart 2: Score Radar/Spider by Dimension
`02_score_dimensions_box.png`
- Box plot with individual points (swarm overlay)
- X-axis: each scoring dimension (infrastructure, app_arch, data, security, devops, bcdr, vendor_diversity)
- Y-axis: score 0-10
- Shows distribution spread per dimension

### Chart 3: Cloud Provider Market Share
`03_cloud_provider_share.png`
- Donut chart of `infrastructure.cloud_provider` (extract primary provider)
- Show: AWS, GCP, Azure, Render, Vercel, Supabase, Other
- Annotate with counts

### Chart 4: Infrastructure Provider vs Score
`04_infra_vs_score.png`
- Grouped box plot: X = cloud provider, Y = overall score
- Shows which cloud correlates with higher scores

### Chart 5: Security Posture Heatmap
`05_security_heatmap.png`
- Binary heatmap (present/absent) for key security features per company
- Columns: WAF, IDS/IPS, MFA, RBAC, Vuln Scanning, Pen Testing, Encryption at Rest, Encryption in Transit, SIEM, Server Hardening, Cyber Insurance
- Rows: companies (sorted by overall score)
- Color: green = present, dark = absent

### Chart 6: Vendor Ecosystem
`06_vendor_count_distribution.png`
- Histogram of third_party_services count per company
- Annotation for median vendor count

### Chart 7: Report Type Breakdown
`07_report_type_breakdown.png`
- Stacked bar: SOC 2 Type 1 vs Type 2 vs ISO 27001
- Grouped by overall score bucket (1-4, 5-7, 8-10)

### Chart 8: Architecture Pattern Distribution
`08_architecture_patterns.png`
- Horizontal bar chart of `application_architecture.pattern` categories
- Count of each: Monolith, Microservices, Serverless-heavy, Hybrid, Unknown

### Chart 9: BCDR Readiness
`09_bcdr_readiness.png`
- Stacked horizontal bar showing % of companies with:
  - BCDR policy, Annual review, Annual testing, Multi-AZ, Multi-region, Daily backups, Stated RTO/RPO

### Chart 10: Red/Yellow/Green Flag Frequency
`10_flag_wordcloud_or_bar.png`
- Bar chart of most common red flags (top 15)
- Extracted from `red_flags` field across all companies
- Normalize similar phrases before counting

### Chart 11: Score Correlation Matrix
`11_score_correlations.png`
- Heatmap of Pearson correlations between all scoring dimensions
- Annotated with correlation values

### Chart 12: Investment Readiness Summary
`12_investment_readiness.png`
- Pie/donut chart of investment readiness categories: LOW, MODERATE, MODERATE-HIGH, HIGH
- Based on overall score buckets

### Step 3: Save summary stats
Write `reports/charts/meta_summary.json`:
```json
{
  "total_companies_analyzed": N,
  "mean_overall_score": X.X,
  "median_overall_score": X.X,
  "score_std": X.X,
  "top_cloud_provider": "AWS (N%)",
  "most_common_red_flag": "...",
  "pct_with_waf": X,
  "pct_with_mfa": X,
  "pct_with_multi_az": X,
  "pct_with_stated_rto_rpo": X,
  "dimension_with_lowest_avg_score": "...",
  "dimension_with_highest_avg_score": "..."
}
```

### Step 4: Validate
- All 12 PNGs exist and are non-empty
- Summary JSON is valid
- No charts have empty data (warn if <5 companies analyzed)

## Output
- `reports/charts/01_score_distribution.png` through `12_investment_readiness.png`
- `reports/charts/meta_summary.json`

## Notes
- If fewer than 10 companies have extractions, warn that statistical conclusions may be unreliable
- All charts must have clear titles, axis labels, and source annotation
- Each chart footer: "Source: SOC 2 / ISO 27001 compliance reports · N={count} companies"
