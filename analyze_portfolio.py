"""
Meta Tech Due Diligence Analysis — Portfolio of 485 SOC 2 Companies
Generates analysis from PE, VC, Angel, and CTO perspectives.
Creates architecture diagram gallery and comprehensive charts.
"""
import json
import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path

# ============================================================
# SETUP
# ============================================================
OUTPUT = Path("reports/analysis")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Dark theme
plt.rcParams.update({
    'figure.facecolor': '#0f172a',
    'axes.facecolor': '#1e293b',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#e2e8f0',
    'text.color': '#e2e8f0',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#1e3a5f',
    'grid.alpha': 0.3,
    'font.family': 'monospace',
    'font.size': 11,
    'figure.dpi': 150,
})
PAL = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7",
       "#38bdf8", "#10b981", "#ff9900", "#ec4899", "#6366f1"]

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv("data_export/companies_flat.csv")
with open("data_export/tech_extracts_full.json") as f:
    extracts_raw = json.load(f)
with open("data_export/dd_reports.json") as f:
    reports = json.load(f)
with open("data_export/diagrams.json") as f:
    diagrams = json.load(f)

# Normalize report types
df['report_type_clean'] = df.report_type.replace({
    'SOC 2 Type II': 'SOC 2 Type 2',
    'SOC 2 Type I': 'SOC 2 Type 1',
})

# Normalize cloud providers
def normalize_cloud(cp):
    if pd.isna(cp) or cp == '': return 'Unknown'
    cp = str(cp).lower()
    if 'aws' in cp or 'amazon' in cp: return 'AWS'
    if 'gcp' in cp or 'google' in cp: return 'GCP'
    if 'azure' in cp or 'microsoft' in cp: return 'Azure'
    if 'supabase' in cp: return 'Supabase'
    if 'vercel' in cp: return 'Vercel'
    if 'render' in cp: return 'Render'
    if 'digitalocean' in cp or 'digital ocean' in cp: return 'DigitalOcean'
    if 'fly.io' in cp or 'fly' in cp: return 'Fly.io'
    if 'railway' in cp: return 'Railway'
    if 'heroku' in cp: return 'Heroku'
    if 'oracle' in cp: return 'Oracle'
    return 'Other'

df['cloud'] = df.cloud_provider.apply(normalize_cloud)

# Parse vendor data
all_vendors = []
for e in extracts_raw:
    vendors = e.get('third_party_services')
    if isinstance(vendors, str):
        try: vendors = json.loads(vendors)
        except: vendors = []
    if isinstance(vendors, list):
        for v in vendors:
            if isinstance(v, dict):
                all_vendors.append({
                    'doc_id': e['doc_id'],
                    'company': e.get('company', ''),
                    'vendor': v.get('vendor', ''),
                    'purpose': v.get('purpose', ''),
                    'criticality': v.get('criticality', ''),
                })
vendors_df = pd.DataFrame(all_vendors)

# Parse flags
all_flags = {'red': [], 'yellow': [], 'green': []}
for e in extracts_raw:
    for color in all_flags:
        flags = e.get(f'{color}_flags')
        if isinstance(flags, str):
            try: flags = json.loads(flags)
            except: flags = []
        if isinstance(flags, list):
            for f in flags:
                if isinstance(f, str) and len(f) > 10:
                    all_flags[color].append(f)

# Score columns
score_cols = ['score_overall', 'score_infrastructure', 'score_app_architecture',
              'score_data_layer', 'score_security', 'score_devops',
              'score_bcdr', 'score_vendor_diversity']
scored_df = df[df.score_overall.notna()].copy()

print(f"Total companies: {len(df)}")
print(f"Scored: {len(scored_df)}")
print(f"With reports: {df.has_report.sum()}")
print(f"With diagrams: {df.has_diagram.sum()}")
print(f"Vendors tracked: {len(vendors_df)}")

# ============================================================
# CHART 1: Portfolio Overview — Score Distribution
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Histogram
ax = axes[0]
scored_df.score_overall.hist(bins=range(1, 11), ax=ax, color=PAL[0], edgecolor='#1e293b', alpha=0.8)
ax.axvline(scored_df.score_overall.mean(), color=PAL[2], linestyle='--', label=f'Mean: {scored_df.score_overall.mean():.1f}')
ax.axvline(scored_df.score_overall.median(), color=PAL[1], linestyle='--', label=f'Median: {scored_df.score_overall.median():.0f}')
ax.set_xlabel('Overall Score')
ax.set_ylabel('Count')
ax.set_title('Score Distribution (N=121 scored)', fontsize=14, fontweight='bold')
ax.legend()

# By report type
ax = axes[1]
for i, rt in enumerate(['SOC 2 Type 1', 'SOC 2 Type 2']):
    subset = scored_df[scored_df.report_type_clean == rt]
    if len(subset) > 0:
        ax.hist(subset.score_overall, bins=range(1, 11), alpha=0.6, label=f'{rt} (N={len(subset)})', color=PAL[i])
ax.set_xlabel('Overall Score')
ax.set_ylabel('Count')
ax.set_title('Score by Report Type', fontsize=14, fontweight='bold')
ax.legend()

plt.tight_layout()
plt.savefig(OUTPUT / "01_score_distribution.png", bbox_inches='tight')
plt.close()
print("  01_score_distribution.png")

# ============================================================
# CHART 2: Dimension Scores Box Plot
# ============================================================
fig, ax = plt.subplots(figsize=(14, 7))
dim_data = scored_df[score_cols].melt(var_name='Dimension', value_name='Score')
dim_data['Dimension'] = dim_data.Dimension.str.replace('score_', '').str.replace('_', ' ').str.title()
sns.boxplot(data=dim_data, x='Dimension', y='Score', ax=ax, palette=PAL, showfliers=False)
sns.stripplot(data=dim_data, x='Dimension', y='Score', ax=ax, color='white', alpha=0.3, size=3, jitter=True)
ax.set_title('Score Distribution by Dimension', fontsize=16, fontweight='bold')
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
ax.set_ylim(0, 10.5)
plt.tight_layout()
plt.savefig(OUTPUT / "02_dimension_scores.png", bbox_inches='tight')
plt.close()
print("  02_dimension_scores.png")

# ============================================================
# CHART 3: Cloud Provider Market Share
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

cloud_counts = df.cloud.value_counts()
colors_map = {'AWS': '#ff9900', 'GCP': '#4285f4', 'Azure': '#0078d4', 'Supabase': '#3ecf8e',
              'Vercel': '#ffffff', 'Render': '#46e3b7', 'DigitalOcean': '#0080ff',
              'Fly.io': '#7b3fe4', 'Railway': '#0B0D0E', 'Other': '#666', 'Unknown': '#444'}
colors = [colors_map.get(c, '#666') for c in cloud_counts.index]

ax = axes[0]
wedges, texts, autotexts = ax.pie(cloud_counts.values, labels=cloud_counts.index, autopct='%1.0f%%',
    colors=colors, textprops={'color': '#e2e8f0', 'fontsize': 10})
ax.set_title('Cloud Provider Distribution (N=485)', fontsize=14, fontweight='bold')

# Cloud vs score
ax = axes[1]
cloud_scores = df[df.score_overall.notna()].groupby('cloud').score_overall.agg(['mean', 'count']).reset_index()
cloud_scores = cloud_scores[cloud_scores['count'] >= 3].sort_values('mean', ascending=True)
ax.barh(cloud_scores.cloud, cloud_scores['mean'], color=PAL[0])
for i, row in cloud_scores.iterrows():
    ax.text(row['mean'] + 0.1, row.cloud, f'{row["mean"]:.1f} (N={row["count"]:.0f})', va='center', fontsize=10)
ax.set_xlabel('Average Score')
ax.set_title('Cloud Provider vs Avg Score', fontsize=14, fontweight='bold')
ax.set_xlim(0, 10)

plt.tight_layout()
plt.savefig(OUTPUT / "03_cloud_providers.png", bbox_inches='tight')
plt.close()
print("  03_cloud_providers.png")

# ============================================================
# CHART 4: Security Posture Heatmap
# ============================================================
security_features = ['has_vpc', 'has_waf', 'has_firewall', 'has_ids_ips', 'has_mfa', 'has_rbac',
                     'has_vuln_scanning', 'has_pen_testing', 'has_server_hardening', 'has_cyber_insurance',
                     'has_bcdr_policy', 'daily_backups', 'multi_az', 'multi_region', 'branch_protection',
                     'quarterly_reviews', 'per_tenant_segregation']

fig, ax = plt.subplots(figsize=(14, 5))
adoption = df[security_features].mean() * 100
adoption = adoption.sort_values(ascending=True)
labels = [s.replace('has_', '').replace('_', ' ').title() for s in adoption.index]
colors = [PAL[1] if v >= 80 else PAL[2] if v >= 50 else PAL[3] for v in adoption.values]
ax.barh(labels, adoption.values, color=colors)
for i, v in enumerate(adoption.values):
    ax.text(v + 1, i, f'{v:.0f}%', va='center', fontsize=10)
ax.set_xlabel('Adoption Rate (%)')
ax.set_title('Security & Infrastructure Feature Adoption (N=485)', fontsize=14, fontweight='bold')
ax.set_xlim(0, 110)
plt.tight_layout()
plt.savefig(OUTPUT / "04_security_adoption.png", bbox_inches='tight')
plt.close()
print("  04_security_adoption.png")

# ============================================================
# CHART 5: Vendor Ecosystem
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Top vendors
ax = axes[0]
top_vendors = vendors_df.vendor.value_counts().head(20)
ax.barh(top_vendors.index[::-1], top_vendors.values[::-1], color=PAL[0])
ax.set_xlabel('Companies Using')
ax.set_title('Top 20 Vendors Across Portfolio', fontsize=14, fontweight='bold')

# Vendor count distribution
ax = axes[1]
df.vendor_count.hist(bins=range(0, 20), ax=ax, color=PAL[4], edgecolor='#1e293b')
ax.axvline(df.vendor_count.mean(), color=PAL[2], linestyle='--', label=f'Mean: {df.vendor_count.mean():.1f}')
ax.set_xlabel('Number of Vendors')
ax.set_ylabel('Companies')
ax.set_title('Vendor Count Distribution', fontsize=14, fontweight='bold')
ax.legend()

plt.tight_layout()
plt.savefig(OUTPUT / "05_vendor_ecosystem.png", bbox_inches='tight')
plt.close()
print("  05_vendor_ecosystem.png")

# ============================================================
# CHART 6: Red Flag Frequency
# ============================================================
fig, ax = plt.subplots(figsize=(14, 8))

# Categorize red flags
flag_categories = Counter()
for flag in all_flags['red']:
    f = flag.lower()
    if 'rto' in f or 'rpo' in f: flag_categories['No RTO/RPO disclosed'] += 1
    elif 'short' in f or '3-month' in f or '3 month' in f or 'minimum' in f: flag_categories['Short audit period (3 months)'] += 1
    elif 'processing integrity' in f or 'privacy' in f: flag_categories['Processing Integrity/Privacy excluded'] += 1
    elif 'single' in f and 'cloud' in f or 'concentration' in f: flag_categories['Single cloud dependency'] += 1
    elif 'template' in f or 'placeholder' in f or 'your name' in f: flag_categories['Template placeholders in report'] += 1
    elif 'untestable' in f or 'no events' in f: flag_categories['Controls untestable (no events)'] += 1
    elif 'waf' in f: flag_categories['No WAF'] += 1
    elif 'siem' in f: flag_categories['No SIEM'] += 1
    elif 'tool' in f and 'not named' in f or 'not disclosed' in f: flag_categories['Tooling not disclosed'] += 1
    elif 'small team' in f or 'key-person' in f or 'lean' in f: flag_categories['Key-person / small team risk'] += 1
    else: flag_categories['Other'] += 1

top_flags = dict(sorted(flag_categories.items(), key=lambda x: -x[1])[:12])
ax.barh(list(top_flags.keys())[::-1], list(top_flags.values())[::-1], color=PAL[3])
ax.set_xlabel('Frequency')
ax.set_title('Most Common Red Flags Across Portfolio', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT / "06_red_flags.png", bbox_inches='tight')
plt.close()
print("  06_red_flags.png")

# ============================================================
# CHART 7: Architecture Pattern Distribution
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))
patterns = df.arch_pattern.value_counts().head(10)
patterns = patterns[patterns.index != '']
ax.barh(patterns.index[::-1], patterns.values[::-1], color=PAL[5])
for i, v in enumerate(patterns.values[::-1]):
    ax.text(v + 1, i, str(v), va='center')
ax.set_xlabel('Companies')
ax.set_title('Architecture Patterns', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT / "07_architecture_patterns.png", bbox_inches='tight')
plt.close()
print("  07_architecture_patterns.png")

# ============================================================
# CHART 8: Report Type vs Score Heatmap
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))
type_scores = scored_df.groupby('report_type_clean')[score_cols].mean()
type_scores.columns = [c.replace('score_', '').replace('_', ' ').title() for c in type_scores.columns]
sns.heatmap(type_scores, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax, vmin=3, vmax=8,
            linewidths=0.5, linecolor='#334155')
ax.set_title('Average Score by Report Type and Dimension', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT / "08_type_vs_score.png", bbox_inches='tight')
plt.close()
print("  08_type_vs_score.png")

# ============================================================
# CHART 9: Score Correlation Matrix
# ============================================================
fig, ax = plt.subplots(figsize=(10, 8))
corr = scored_df[score_cols].corr()
corr.columns = [c.replace('score_', '').replace('_', '\n') for c in corr.columns]
corr.index = corr.columns
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax,
            linewidths=0.5, linecolor='#334155', vmin=-0.5, vmax=1)
ax.set_title('Score Dimension Correlations', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT / "09_score_correlations.png", bbox_inches='tight')
plt.close()
print("  09_score_correlations.png")

# ============================================================
# CHART 10: BCDR Readiness Breakdown
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5))
bcdr_features = {
    'BCDR Policy': df.has_bcdr_policy.mean(),
    'Multi-AZ': df.multi_az.mean(),
    'Daily Backups': df.daily_backups.mean(),
    'Branch Protection': df.branch_protection.mean(),
    'Vuln Scanning': df.has_vuln_scanning.mean(),
    'Pen Testing': df.has_pen_testing.mean(),
    'Multi-Region': df.multi_region.mean(),
    'Per-Tenant Isolation': df.per_tenant_segregation.mean(),
}
labels = list(bcdr_features.keys())
values = [v * 100 for v in bcdr_features.values()]
colors = [PAL[1] if v >= 80 else PAL[2] if v >= 50 else PAL[3] for v in values]
ax.bar(labels, values, color=colors)
for i, v in enumerate(values):
    ax.text(i, v + 1, f'{v:.0f}%', ha='center', fontsize=10)
ax.set_ylabel('Adoption %')
ax.set_title('Resilience & Security Adoption Rates', fontsize=14, fontweight='bold')
ax.set_xticklabels(labels, rotation=30, ha='right')
ax.set_ylim(0, 110)
plt.tight_layout()
plt.savefig(OUTPUT / "10_bcdr_readiness.png", bbox_inches='tight')
plt.close()
print("  10_bcdr_readiness.png")

# ============================================================
# CHART 11: Investment Readiness Tiers
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))
def tier(score):
    if pd.isna(score): return 'Unscored'
    if score >= 8: return 'HIGH (8-10)'
    if score >= 7: return 'MODERATE-HIGH (7)'
    if score >= 5: return 'MODERATE (5-6)'
    if score >= 3: return 'LOW (3-4)'
    return 'VERY LOW (1-2)'

df['tier'] = df.score_overall.apply(tier)
tier_counts = df.tier.value_counts()
tier_order = ['HIGH (8-10)', 'MODERATE-HIGH (7)', 'MODERATE (5-6)', 'LOW (3-4)', 'VERY LOW (1-2)', 'Unscored']
tier_colors = [PAL[1], PAL[0], PAL[2], PAL[3], '#7f1d1d', '#333']
for t in tier_order:
    if t not in tier_counts.index:
        tier_counts[t] = 0
tier_counts = tier_counts.reindex(tier_order)
ax.barh(tier_order[::-1], tier_counts.values[::-1], color=tier_colors[::-1])
for i, v in enumerate(tier_counts.values[::-1]):
    ax.text(v + 2, i, str(v), va='center', fontsize=12, fontweight='bold')
ax.set_xlabel('Companies')
ax.set_title('Investment Readiness Tiers', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT / "11_investment_tiers.png", bbox_inches='tight')
plt.close()
print("  11_investment_tiers.png")

# ============================================================
# CHART 12: Extraction Method Coverage
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
method_counts = df.extraction_method.value_counts()
ax.pie(method_counts.values, labels=method_counts.index, autopct='%1.0f%%',
       colors=PAL[:len(method_counts)], textprops={'color': '#e2e8f0'})
ax.set_title('Extraction Method Coverage', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT / "12_extraction_coverage.png", bbox_inches='tight')
plt.close()
print("  12_extraction_coverage.png")

# ============================================================
# SAVE SUMMARY STATS
# ============================================================
summary = {
    'total_companies': len(df),
    'scored': len(scored_df),
    'with_reports': int(df.has_report.sum()),
    'with_diagrams': int(df.has_diagram.sum()),
    'mean_score': round(scored_df.score_overall.mean(), 1) if len(scored_df) > 0 else None,
    'median_score': round(scored_df.score_overall.median(), 1) if len(scored_df) > 0 else None,
    'top_cloud': df.cloud.value_counts().index[0],
    'pct_aws': round(df.cloud.value_counts().get('AWS', 0) / len(df) * 100, 1),
    'pct_mfa': round(df.has_mfa.mean() * 100, 1),
    'pct_waf': round(df.has_waf.mean() * 100, 1),
    'pct_multi_region': round(df.multi_region.mean() * 100, 1),
    'pct_pen_testing': round(df.has_pen_testing.mean() * 100, 1),
    'avg_vendor_count': round(df.vendor_count.mean(), 1),
    'total_unique_vendors': vendors_df.vendor.nunique(),
    'type_1_count': int((df.report_type_clean == 'SOC 2 Type 1').sum()),
    'type_2_count': int((df.report_type_clean == 'SOC 2 Type 2').sum()),
    'high_scorers': int((scored_df.score_overall >= 7).sum()),
    'low_scorers': int((scored_df.score_overall <= 3).sum()),
    'dimension_scores': {
        c.replace('score_', ''): round(scored_df[c].mean(), 1)
        for c in score_cols if scored_df[c].notna().sum() > 0
    },
    'cloud_distribution': df.cloud.value_counts().to_dict(),
    'security_adoption': {
        f.replace('has_', ''): round(df[f].mean() * 100, 1)
        for f in security_features
    },
}

with open(OUTPUT / "meta_summary.json", 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n=== Analysis Complete ===")
print(f"Charts: {len(list(OUTPUT.glob('*.png')))} PNGs")
print(f"Summary: {OUTPUT / 'meta_summary.json'}")
print(f"Output: {OUTPUT}")
