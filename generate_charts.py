#!/usr/bin/env python3
"""Skill 04 - Meta-Analysis Charts for Tech DD Pipeline.

Loads all *_tech_extract.json files from company_db/ and generates
12 publication-quality charts plus a meta_summary.json.
"""

import json
import glob
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

# ── Paths ──────────────────────────────────────────────────────────────
COMPANY_DB = "company_db"
OUTPUT_DIR = "reports/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Dark theme ─────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor": "#16213e",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#e2e8f0",
    "text.color": "#e2e8f0",
    "xtick.color": "#94a3b8",
    "ytick.color": "#94a3b8",
    "grid.color": "#1e3a5f",
    "font.family": "monospace",
    "font.size": 11,
})
PALETTE = [
    "#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7",
    "#38bdf8", "#10b981", "#ff9900", "#ec4899", "#6366f1",
]

# ── Load data ──────────────────────────────────────────────────────────
extracts = []
for f in sorted(glob.glob(os.path.join(COMPANY_DB, "*_tech_extract.json"))):
    with open(f) as fh:
        extracts.append(json.load(fh))

N = len(extracts)
print(f"Loaded {N} company extractions")
if N < 5:
    print(f"WARNING: Only {N} companies -- statistical conclusions may be unreliable")

FOOTER = f"Source: SOC 2 / ISO 27001 compliance reports \u00b7 N={N} companies"

# Short company labels
companies = [e["company"].replace(", Inc.", "").replace(" Inc.", "") for e in extracts]

# ── Helpers ────────────────────────────────────────────────────────────
DIMENSIONS = [
    "infrastructure",
    "application_architecture",
    "data_layer",
    "security_posture",
    "devops_maturity",
    "bcdr_readiness",
    "vendor_diversity",
]
DIM_LABELS = [
    "Infra",
    "App Arch",
    "Data",
    "Security",
    "DevOps",
    "BCDR",
    "Vendor Div.",
]


def add_footer(fig, text=FOOTER):
    fig.text(0.5, 0.01, text, ha="center", fontsize=8, color="#64748b", style="italic")


def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {path}")


# ══════════════════════════════════════════════════════════════════════
# Chart 01 – Overall Score Distribution (bar chart for N=2)
# ══════════════════════════════════════════════════════════════════════
scores = [e["scoring"]["overall"]["score"] for e in extracts]
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(companies, scores, color=PALETTE[:N], width=0.5, edgecolor="#334155")
for bar, s in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            str(s), ha="center", va="bottom", fontweight="bold", color="#e2e8f0", fontsize=14)
mean_score = np.mean(scores)
ax.axhline(mean_score, color="#f59e0b", ls="--", lw=1.5, label=f"Mean: {mean_score:.1f}")
ax.set_ylim(0, 10.5)
ax.set_ylabel("Overall Score")
ax.set_title(f"Tech DD Score Distribution (N={N})", fontsize=15, fontweight="bold")
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)
add_footer(fig)
save(fig, "01_score_distribution.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 02 – Score Dimensions Grouped Bar
# ══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(DIMENSIONS))
width = 0.35
for i, (ext, name) in enumerate(zip(extracts, companies)):
    dim_scores = [ext["scoring"][d]["score"] for d in DIMENSIONS]
    offset = (i - (N - 1) / 2) * width
    bars = ax.bar(x + offset, dim_scores, width, label=name, color=PALETTE[i],
                  edgecolor="#334155")
    for bar, s in zip(bars, dim_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(s), ha="center", va="bottom", fontsize=9, color="#e2e8f0")
ax.set_xticks(x)
ax.set_xticklabels(DIM_LABELS, rotation=30, ha="right")
ax.set_ylim(0, 10.5)
ax.set_ylabel("Score (0-10)")
ax.set_title(f"Score by Dimension (N={N})", fontsize=15, fontweight="bold")
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)
add_footer(fig)
save(fig, "02_score_dimensions_box.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 03 – Cloud Provider Market Share (donut)
# ══════════════════════════════════════════════════════════════════════
providers = []
for e in extracts:
    cp = e["infrastructure"]["cloud_provider"]
    # Extract primary provider name
    primary = cp.split("(")[0].strip().split(",")[0].strip()
    providers.append(primary)
    for extra in e["infrastructure"].get("additional_cloud", []):
        providers.append(extra)

provider_counts = Counter(providers)
labels = list(provider_counts.keys())
sizes = list(provider_counts.values())
colors = PALETTE[: len(labels)]

fig, ax = plt.subplots(figsize=(12, 7))
wedges, texts, autotexts = ax.pie(
    sizes, labels=labels, colors=colors, autopct=lambda p: f"{int(round(p * sum(sizes) / 100))}",
    startangle=140, pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor="#1a1a2e"),
    textprops=dict(color="#e2e8f0"),
)
for t in autotexts:
    t.set_fontsize(12)
    t.set_fontweight("bold")
    t.set_color("#e2e8f0")
ax.set_title(f"Cloud Provider Share (N={N})", fontsize=15, fontweight="bold")
add_footer(fig)
save(fig, "03_cloud_provider_share.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 04 – Infrastructure Provider vs Score
# ══════════════════════════════════════════════════════════════════════
primary_providers = []
for e in extracts:
    cp = e["infrastructure"]["cloud_provider"]
    primary_providers.append(cp.split("(")[0].strip().split(",")[0].strip())

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(companies, scores, color=[PALETTE[list(set(primary_providers)).index(p) % len(PALETTE)]
              for p in primary_providers], width=0.5, edgecolor="#334155")
for bar, s, p in zip(bars, scores, primary_providers):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            f"{s} ({p})", ha="center", va="bottom", fontsize=11, color="#e2e8f0")
ax.set_ylim(0, 10.5)
ax.set_ylabel("Overall Score")
ax.set_title(f"Cloud Provider vs Overall Score (N={N})", fontsize=15, fontweight="bold")
ax.grid(axis="y", alpha=0.3)
add_footer(fig)
save(fig, "04_infra_vs_score.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 05 – Security Posture Heatmap
# ══════════════════════════════════════════════════════════════════════
SEC_FEATURES = [
    ("WAF", lambda e: bool(e["security_tools"].get("waf"))),
    ("IDS/IPS", lambda e: bool(e["security_tools"].get("ids_ips"))),
    ("MFA", lambda e: bool(e["authentication_access_control"].get("mfa"))),
    ("RBAC", lambda e: bool(e["authentication_access_control"].get("rbac"))),
    ("VulnScan", lambda e: bool(e["security_tools"].get("vulnerability_scanning"))),
    ("PenTest", lambda e: bool(e["security_tools"].get("penetration_testing"))),
    ("EncRest", lambda e: bool(e["encryption"].get("at_rest"))),
    ("EncTransit", lambda e: bool(e["encryption"].get("in_transit"))),
    ("SIEM", lambda e: bool(e["monitoring_logging"].get("siem") and
                             e["monitoring_logging"]["siem"] != "Not explicitly named" and
                             e["monitoring_logging"]["siem"] != "Not named")),
    ("Hardening", lambda e: bool(e["security_tools"].get("server_hardening"))),
    ("CyberIns", lambda e: bool(e["security_tools"].get("cybersecurity_insurance"))),
]

# Sort companies by overall score descending
sorted_idx = sorted(range(N), key=lambda i: extracts[i]["scoring"]["overall"]["score"], reverse=True)
sorted_companies = [companies[i] for i in sorted_idx]
sorted_extracts = [extracts[i] for i in sorted_idx]

heat_data = []
for e in sorted_extracts:
    row = []
    for _, fn in SEC_FEATURES:
        row.append(1 if fn(e) else 0)
    heat_data.append(row)

heat_df = pd.DataFrame(heat_data, index=sorted_companies, columns=[f[0] for f in SEC_FEATURES])

fig, ax = plt.subplots(figsize=(12, 7))
cmap = sns.color_palette(["#1e293b", "#22c55e"], as_cmap=True)
sns.heatmap(heat_df, ax=ax, cmap=cmap, linewidths=2, linecolor="#1a1a2e",
            cbar=False, annot=heat_df.replace({1: "\u2714", 0: "\u2718"}),
            fmt="s", annot_kws={"fontsize": 14, "fontweight": "bold"})
ax.set_title(f"Security Posture Heatmap (N={N})", fontsize=15, fontweight="bold")
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
# Legend
present = mpatches.Patch(color="#22c55e", label="Present")
absent = mpatches.Patch(color="#1e293b", label="Absent")
ax.legend(handles=[present, absent], loc="upper right", framealpha=0.8,
          facecolor="#16213e", edgecolor="#334155")
add_footer(fig)
save(fig, "05_security_heatmap.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 06 – Vendor Count Distribution
# ══════════════════════════════════════════════════════════════════════
vendor_counts = [len(e.get("third_party_services", [])) for e in extracts]
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(companies, vendor_counts, color=PALETTE[:N], width=0.5, edgecolor="#334155")
median_vc = np.median(vendor_counts)
ax.axhline(median_vc, color="#f59e0b", ls="--", lw=1.5, label=f"Median: {median_vc:.0f}")
for bar, v in zip(bars, vendor_counts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
            str(v), ha="center", va="bottom", fontweight="bold", color="#e2e8f0", fontsize=14)
ax.set_ylabel("Number of Third-Party Vendors")
ax.set_title(f"Vendor Count per Company (N={N})", fontsize=15, fontweight="bold")
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.3)
add_footer(fig)
save(fig, "06_vendor_count_distribution.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 07 – Report Type Breakdown
# ══════════════════════════════════════════════════════════════════════
report_types = Counter(e["report_type"] for e in extracts)
fig, ax = plt.subplots(figsize=(12, 7))
rt_labels = list(report_types.keys())
rt_values = list(report_types.values())
bars = ax.bar(rt_labels, rt_values, color=PALETTE[: len(rt_labels)], width=0.4, edgecolor="#334155")
for bar, v in zip(bars, rt_values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
            str(v), ha="center", va="bottom", fontweight="bold", color="#e2e8f0", fontsize=14)
ax.set_ylabel("Count")
ax.set_title(f"Report Type Breakdown (N={N})", fontsize=15, fontweight="bold")
ax.set_ylim(0, max(rt_values) + 1)
ax.grid(axis="y", alpha=0.3)
add_footer(fig)
save(fig, "07_report_type_breakdown.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 08 – Architecture Patterns
# ══════════════════════════════════════════════════════════════════════
patterns = []
for e in extracts:
    pat = e["application_architecture"]["pattern"]
    # Normalize: take first word if it contains extra description
    pat_clean = pat.split("(")[0].strip().split("/")[0].strip()
    patterns.append(pat_clean)

pattern_counts = Counter(patterns)
fig, ax = plt.subplots(figsize=(12, 7))
p_labels = list(pattern_counts.keys())
p_values = list(pattern_counts.values())
y_pos = np.arange(len(p_labels))
bars = ax.barh(y_pos, p_values, color=PALETTE[: len(p_labels)], height=0.5, edgecolor="#334155")
for bar, v in zip(bars, p_values):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
            str(v), va="center", fontweight="bold", color="#e2e8f0", fontsize=14)
ax.set_yticks(y_pos)
ax.set_yticklabels(p_labels)
ax.set_xlabel("Count")
ax.set_title(f"Architecture Patterns (N={N})", fontsize=15, fontweight="bold")
ax.set_xlim(0, max(p_values) + 1)
ax.grid(axis="x", alpha=0.3)
add_footer(fig)
save(fig, "08_architecture_patterns.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 09 – BCDR Readiness (stacked horizontal bar)
# ══════════════════════════════════════════════════════════════════════
BCDR_FEATURES = [
    ("BCDR Policy", "bcdr_policy"),
    ("Annual Review", "annual_review"),
    ("Annual Testing", "annual_testing"),
    ("Multi-AZ", "multi_az_failover"),
    ("Multi-Region", "multi_region_failover"),
    ("Daily Backups", "daily_backups"),
    ("Stated RTO/RPO", None),  # special
]


def has_rto_rpo(e):
    rto = e["bcdr"].get("rto", "Not disclosed")
    rpo = e["bcdr"].get("rpo", "Not disclosed")
    return rto not in ("Not disclosed", None, "") or rpo not in ("Not disclosed", None, "")


fig, ax = plt.subplots(figsize=(12, 7))
y_pos = np.arange(N)
feature_labels = [f[0] for f in BCDR_FEATURES]
n_features = len(BCDR_FEATURES)
# Build matrix: companies x features
bcdr_matrix = []
for e in extracts:
    row = []
    for label, key in BCDR_FEATURES:
        if key is None:
            row.append(1 if has_rto_rpo(e) else 0)
        else:
            row.append(1 if e["bcdr"].get(key) else 0)
    bcdr_matrix.append(row)

bcdr_df = pd.DataFrame(bcdr_matrix, index=companies, columns=feature_labels)

# Stacked horizontal bar
left = np.zeros(N)
for j, feat in enumerate(feature_labels):
    vals = bcdr_df[feat].values.astype(float)
    ax.barh(y_pos, vals, left=left, height=0.5, label=feat,
            color=PALETTE[j % len(PALETTE)], edgecolor="#1a1a2e")
    left += vals

ax.set_yticks(y_pos)
ax.set_yticklabels(companies)
ax.set_xlabel("Number of BCDR Features Present")
ax.set_title(f"BCDR Readiness (N={N})", fontsize=15, fontweight="bold")
ax.legend(loc="lower right", fontsize=8, framealpha=0.8, facecolor="#16213e", edgecolor="#334155")
ax.grid(axis="x", alpha=0.3)
add_footer(fig)
save(fig, "09_bcdr_readiness.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 10 – Red Flag Frequency
# ══════════════════════════════════════════════════════════════════════
# Bar chart of red flag count per company
red_flag_counts = [len(e.get("red_flags", [])) for e in extracts]
fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(companies, red_flag_counts, color=["#ef4444"] * N, width=0.5, edgecolor="#334155")
for bar, v in zip(bars, red_flag_counts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
            str(v), ha="center", va="bottom", fontweight="bold", color="#e2e8f0", fontsize=14)
ax.set_ylabel("Red Flag Count")
ax.set_title(f"Red Flag Count per Company (N={N})", fontsize=15, fontweight="bold")
ax.set_ylim(0, max(red_flag_counts) + 2)
ax.grid(axis="y", alpha=0.3)
add_footer(fig)
save(fig, "10_flag_frequency.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 11 – Score Correlation Matrix
# ══════════════════════════════════════════════════════════════════════
dim_data = {dl: [e["scoring"][d]["score"] for e in extracts] for d, dl in zip(DIMENSIONS, DIM_LABELS)}
dim_df = pd.DataFrame(dim_data)
corr = dim_df.corr()

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            linewidths=1, linecolor="#1a1a2e", ax=ax, vmin=-1, vmax=1,
            cbar_kws={"shrink": 0.8})
ax.set_title(f"Score Dimension Correlations (N={N})", fontsize=15, fontweight="bold")
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
if N < 5:
    ax.text(0.5, -0.12, "Note: N<5 -- correlations are not statistically meaningful",
            transform=ax.transAxes, ha="center", fontsize=9, color="#f59e0b", style="italic")
add_footer(fig)
save(fig, "11_score_correlations.png")

# ══════════════════════════════════════════════════════════════════════
# Chart 12 – Investment Readiness (donut)
# ══════════════════════════════════════════════════════════════════════

def readiness_bucket(score):
    if score <= 3:
        return "LOW"
    elif score <= 5:
        return "MODERATE"
    elif score <= 7:
        return "MODERATE-HIGH"
    else:
        return "HIGH"


readiness = [readiness_bucket(s) for s in scores]
readiness_counts = Counter(readiness)
# Ensure consistent order
order = ["LOW", "MODERATE", "MODERATE-HIGH", "HIGH"]
r_labels = [o for o in order if o in readiness_counts]
r_values = [readiness_counts[o] for o in r_labels]
r_colors = {"LOW": "#ef4444", "MODERATE": "#f59e0b", "MODERATE-HIGH": "#3b82f6", "HIGH": "#22c55e"}

fig, ax = plt.subplots(figsize=(12, 7))
wedges, texts, autotexts = ax.pie(
    r_values, labels=r_labels,
    colors=[r_colors[l] for l in r_labels],
    autopct=lambda p: f"{int(round(p * sum(r_values) / 100))}",
    startangle=140, pctdistance=0.75,
    wedgeprops=dict(width=0.4, edgecolor="#1a1a2e"),
    textprops=dict(color="#e2e8f0"),
)
for t in autotexts:
    t.set_fontsize(14)
    t.set_fontweight("bold")
    t.set_color("#e2e8f0")
ax.set_title(f"Investment Readiness Summary (N={N})", fontsize=15, fontweight="bold")
add_footer(fig)
save(fig, "12_investment_readiness.png")

# ══════════════════════════════════════════════════════════════════════
# Meta Summary JSON
# ══════════════════════════════════════════════════════════════════════
all_red_flags = []
for e in extracts:
    all_red_flags.extend(e.get("red_flags", []))
flag_counter = Counter(all_red_flags)
most_common_flag = flag_counter.most_common(1)[0][0] if flag_counter else "N/A"

# Dimension averages
dim_avgs = {}
for d, dl in zip(DIMENSIONS, DIM_LABELS):
    dim_avgs[dl] = np.mean([e["scoring"][d]["score"] for e in extracts])
lowest_dim = min(dim_avgs, key=dim_avgs.get)
highest_dim = max(dim_avgs, key=dim_avgs.get)

# Security percentages
pct_waf = 100 * sum(1 for e in extracts if e["security_tools"].get("waf")) / N
pct_mfa = 100 * sum(1 for e in extracts if e["authentication_access_control"].get("mfa")) / N
pct_multi_az = 100 * sum(1 for e in extracts if e["bcdr"].get("multi_az_failover")) / N
pct_rto_rpo = 100 * sum(1 for e in extracts if has_rto_rpo(e)) / N

# Top cloud provider
top_provider = Counter(primary_providers).most_common(1)[0]

summary = {
    "total_companies_analyzed": N,
    "mean_overall_score": round(float(np.mean(scores)), 1),
    "median_overall_score": round(float(np.median(scores)), 1),
    "score_std": round(float(np.std(scores, ddof=1)) if N > 1 else 0.0, 1),
    "top_cloud_provider": f"{top_provider[0]} ({100 * top_provider[1] / N:.0f}%)",
    "most_common_red_flag": most_common_flag,
    "pct_with_waf": round(pct_waf, 1),
    "pct_with_mfa": round(pct_mfa, 1),
    "pct_with_multi_az": round(pct_multi_az, 1),
    "pct_with_stated_rto_rpo": round(pct_rto_rpo, 1),
    "dimension_with_lowest_avg_score": lowest_dim,
    "dimension_with_highest_avg_score": highest_dim,
}

summary_path = os.path.join(OUTPUT_DIR, "meta_summary.json")
with open(summary_path, "w") as fh:
    json.dump(summary, fh, indent=2)
print(f"  Saved {summary_path}")

# ── Validation ─────────────────────────────────────────────────────────
expected = [
    "01_score_distribution.png",
    "02_score_dimensions_box.png",
    "03_cloud_provider_share.png",
    "04_infra_vs_score.png",
    "05_security_heatmap.png",
    "06_vendor_count_distribution.png",
    "07_report_type_breakdown.png",
    "08_architecture_patterns.png",
    "09_bcdr_readiness.png",
    "10_flag_frequency.png",
    "11_score_correlations.png",
    "12_investment_readiness.png",
]
print("\nValidation:")
all_ok = True
for fname in expected:
    path = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  OK  {fname} ({os.path.getsize(path):,} bytes)")
    else:
        print(f"  FAIL  {fname}")
        all_ok = False

if os.path.exists(summary_path):
    with open(summary_path) as fh:
        json.loads(fh.read())
    print(f"  OK  meta_summary.json (valid JSON)")
else:
    print(f"  FAIL  meta_summary.json")
    all_ok = False

if all_ok:
    print(f"\nAll 12 charts + summary generated successfully.")
else:
    print(f"\nSome outputs are missing or empty!")
