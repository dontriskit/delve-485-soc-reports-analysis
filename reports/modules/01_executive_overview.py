"""
Module 01: Executive Overview
Thesis: The portfolio's median tech maturity is moderate (5-6/10),
with security as the strongest dimension and vendor diversity as the weakest.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from .base_module import BaseModule
from . import theme


class ExecutiveOverview(BaseModule):
    slug = "01_executive_overview"
    title = "Executive Overview"
    subtitle = "Portfolio-wide summary of 485 SOC 2 compliance reports"

    def generate_charts(self):
        d = self.data
        df, scored, N, NS = d['df'], d['scored'], d['N'], d['NS']

        # Chart 1: Score Distribution
        fig, ax = plt.subplots(figsize=(12, 5))
        bins = np.arange(0.5, 10.5, 1)
        ax.hist(scored.score_overall, bins=bins, color=theme.BLUE, edgecolor=theme.BG, alpha=0.85, rwidth=0.85)
        ax.axvline(scored.score_overall.mean(), color=theme.YELLOW, lw=2, ls='--',
                    label=f'Mean: {scored.score_overall.mean():.1f}')
        ax.axvline(scored.score_overall.median(), color=theme.GREEN, lw=2, ls='--',
                    label=f'Median: {scored.score_overall.median():.0f}')
        ax.set_xlabel('Overall Tech DD Score')
        ax.set_ylabel('Companies')
        ax.set_title(f'Score Distribution (N={NS} scored)', fontsize=16, fontweight='bold')
        ax.legend(fontsize=11)
        ax.set_xlim(0, 10)
        self.save_chart(fig, 'score_distribution')

        # Chart 2: Dimension Averages
        dims = d['SCORE_COLS'][1:]  # skip overall
        labels = d['DIM_LABELS'][1:]
        means = [scored[c].mean() for c in dims]
        stds = [scored[c].std() for c in dims]

        fig, ax = plt.subplots(figsize=(12, 5))
        x = np.arange(len(dims))
        colors = [theme.SCORE_COLOR(m) for m in means]
        ax.bar(x, means, yerr=stds, width=0.6, color=colors,
               capsize=5, error_kw={'color': theme.MUTED, 'lw': 1.5})
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylabel('Average Score')
        ax.set_title('Average Score by Dimension', fontsize=16, fontweight='bold')
        ax.set_ylim(0, 10)
        for i, m in enumerate(means):
            ax.text(i, m + stds[i] + 0.2, f'{m:.1f}', ha='center', fontsize=12, fontweight='bold')
        self.save_chart(fig, 'dimension_averages')

        # Chart 3: Security Feature Adoption
        features = {
            'MFA': df.has_mfa.mean(), 'RBAC': df.has_rbac.mean(), 'VPC': df.has_vpc.mean(),
            'Multi-AZ': df.multi_az.mean(), 'Firewall': df.has_firewall.mean(),
            'Vuln Scan': df.has_vuln_scanning.mean(), 'Branch Prot.': df.branch_protection.mean(),
            'Pen Testing': df.has_pen_testing.mean(), 'Daily Backup': df.daily_backups.mean(),
            'WAF': df.has_waf.mean(), 'Multi-Region': df.multi_region.mean(),
            'Cyber Insur.': df.has_cyber_insurance.mean(),
        }
        features = dict(sorted(features.items(), key=lambda x: x[1]))
        fig, ax = plt.subplots(figsize=(12, 6))
        vals = [v * 100 for v in features.values()]
        colors = [theme.GREEN if v >= 80 else theme.YELLOW if v >= 50 else theme.RED for v in vals]
        ax.barh(list(features.keys()), vals, color=colors, height=0.7)
        for i, v in enumerate(vals):
            ax.text(v + 1.5, i, f'{v:.0f}%', va='center', fontsize=10)
        ax.axvline(80, color=theme.GREEN, ls=':', alpha=0.3)
        ax.axvline(50, color=theme.YELLOW, ls=':', alpha=0.3)
        ax.set_xlabel('Adoption Rate (%)')
        ax.set_title(f'Security & Infrastructure Adoption (N={N})', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 110)
        self.save_chart(fig, 'feature_adoption')

        # Chart 4: Cloud Distribution
        cloud_counts = df.cloud.value_counts().head(8)
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [theme.CLOUD_COLORS.get(c, '#666') for c in cloud_counts.index]
        wedges, texts, autotexts = ax.pie(
            cloud_counts.values, labels=cloud_counts.index, autopct='%1.0f%%',
            colors=colors, textprops={'color': theme.TEXT, 'fontsize': 10})
        ax.set_title(f'Cloud Provider Distribution (N={N})', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'cloud_distribution')

    def generate_narrative(self):
        d = self.data
        df, scored, N, NS = d['df'], d['scored'], d['N'], d['NS']

        mean_s = scored.score_overall.mean()
        median_s = scored.score_overall.median()
        high = int((scored.score_overall >= 7).sum())
        low = int((scored.score_overall <= 4).sum())
        pct_aws = (df.cloud == 'AWS').mean() * 100
        pct_waf = df.has_waf.mean() * 100
        pct_mr = df.multi_region.mean() * 100
        avg_vendors = df.vendor_count.mean()

        html = self.metric_grid([
            (N, 'Companies Analyzed', theme.BLUE),
            (f'{mean_s:.1f}/10', 'Average Score', theme.YELLOW),
            (f'{high}', 'Score 7+ (High)', theme.GREEN),
            (f'{pct_aws:.0f}%', 'AWS Adoption', theme.ORANGE),
            (f'{pct_waf:.0f}%', 'WAF Adoption', theme.RED),
            (f'{pct_mr:.0f}%', 'Multi-Region', theme.PURPLE),
        ], cols=3)

        html += self.section('Score Distribution', f"""
<p>Across {NS} scored companies, the average tech DD score is <strong>{mean_s:.1f}/10</strong>
(median: {median_s:.0f}). The distribution clusters tightly at 5-6, with {high} companies
({high/NS*100:.0f}%) scoring 7+ and {low} ({low/NS*100:.0f}%) scoring 4 or below.</p>

{self.chart_img('score_distribution.png', f'N={NS} companies with dimension scores')}

{self.insight_box(f"<strong>Key insight:</strong> The tight clustering at 5-6/10 suggests most companies achieve a similar baseline from template-driven SOC 2 compliance. The differentiators that push a company to 7+ are specific: multi-region deployment, WAF, named monitoring tools, and vendor transparency.")}
""")

        html += self.section('Dimension Analysis', f"""
<p>Security is the strongest dimension ({scored.score_security.mean():.1f}/10) — MFA, RBAC, and basic firewalls
are near-universal. Vendor Diversity is the weakest ({scored.score_vendor_diversity.mean():.1f}/10) — most companies
depend on a single cloud provider with minimal third-party disclosure.</p>

{self.chart_img('dimension_averages.png', 'Error bars show standard deviation')}

<h3>Dimension Ranking</h3>
""")

        # Dimension table
        rows = []
        for col, label in zip(d['SCORE_COLS'][1:], d['DIM_LABELS'][1:]):
            s = scored[col]
            rows.append([label, f'{s.mean():.1f}', f'{s.median():.0f}', f'{s.std():.1f}',
                        f'{s.min():.0f}', f'{s.max():.0f}'])
        html += self.table(['Dimension', 'Mean', 'Median', 'Std', 'Min', 'Max'], rows)

        html += self.section('Security & Infrastructure Adoption', f"""
<p>The portfolio shows a clear three-tier security maturity pattern:</p>
<ul>
<li><strong style="color:{theme.GREEN}">Table Stakes (80%+):</strong> MFA, RBAC, VPC, Multi-AZ, Firewalls — essentially universal</li>
<li><strong style="color:{theme.YELLOW}">Differentiators (40-80%):</strong> Vulnerability scanning, branch protection, pen testing, WAF</li>
<li><strong style="color:{theme.RED}">Rare (&lt;40%):</strong> Multi-region, cyber insurance, quarterly access reviews</li>
</ul>

{self.chart_img('feature_adoption.png', f'N={N} companies')}
""")

        html += self.section('Cloud Provider Landscape', f"""
<p>AWS dominates at {pct_aws:.0f}%, creating systemic portfolio-level concentration risk.
A major AWS outage would simultaneously impact over half the portfolio.</p>

{self.chart_img('cloud_distribution.png')}
""")

        html += self.section('Key Takeaways', f"""
{self.flag_box(f"<strong>For PE:</strong> {pct_mr:.0f}% multi-region adoption means 72% of the portfolio has single-region risk. Migrating companies to multi-region is a concrete value creation lever.", 'red')}
{self.flag_box(f"<strong>For VC:</strong> Vendor transparency (naming 5+ third-party services) correlates with higher scores. Ask founders to name their full stack — opacity is a red flag.", 'yellow')}
{self.flag_box(f"<strong>For CTO:</strong> Security ({scored.score_security.mean():.1f}/10) outpaces DevOps ({scored.score_devops.mean():.1f}/10). Most companies have security controls but lack CI/CD maturity.", 'green')}
""")

        return html


if __name__ == "__main__":
    mod = ExecutiveOverview()
    mod.run()
