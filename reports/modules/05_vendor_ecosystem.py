"""
Module 05: Vendor Ecosystem
Thesis: Transparency about vendor dependencies correlates with engineering culture maturity.
Companies naming 5+ vendors score significantly higher than opaque ones.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .base_module import BaseModule
from . import theme


class VendorEcosystem(BaseModule):
    slug = "05_vendor_ecosystem"
    title = "Vendor Ecosystem"
    subtitle = "Who powers these companies — and what vendor transparency reveals"

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        # Top 25 vendors
        top = d['all_vendors'].most_common(25)
        fig, ax = plt.subplots(figsize=(13, 8))
        ax.barh([v[0][:30] for v in top][::-1], [v[1] for v in top][::-1], color=theme.BLUE, height=0.65)
        for i, v in enumerate([v[1] for v in top][::-1]):
            ax.text(v + 0.5, i, str(v), va='center', fontsize=10)
        ax.set_xlabel('Companies Using')
        ax.set_title(f'Top 25 Vendors Across Portfolio (N={N})', fontsize=16, fontweight='bold')
        self.save_chart(fig, 'top_vendors')

        # Vendor count distribution
        fig, ax = plt.subplots(figsize=(10, 5))
        df.vendor_count.hist(bins=range(0, 25), ax=ax, color=theme.PURPLE, edgecolor=theme.BG)
        ax.axvline(df.vendor_count.mean(), color=theme.YELLOW, ls='--', lw=2,
                    label=f'Mean: {df.vendor_count.mean():.1f}')
        ax.set_xlabel('Number of Named Vendors')
        ax.set_ylabel('Companies')
        ax.set_title('Vendor Count Distribution', fontsize=14, fontweight='bold')
        ax.legend()
        self.save_chart(fig, 'vendor_count_dist')

        # Vendor count vs score
        bins_v = [0, 1, 3, 5, 8, 15, 30]
        labels_v = ['0-1', '2-3', '4-5', '6-8', '9-15', '16+']
        df_temp = df.copy()
        df_temp['vbin'] = pd.cut(df_temp.vendor_count, bins=bins_v, labels=labels_v)
        vsc = df_temp[df_temp.score_overall.notna()].groupby('vbin', observed=True).score_overall.agg(['mean','count']).reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(vsc.vbin.astype(str), vsc['mean'], color=theme.CYAN, width=0.6)
        for i, row in vsc.iterrows():
            ax.text(i, row['mean'] + 0.15, f'{row["mean"]:.1f}\n(n={row["count"]:.0f})', ha='center', fontsize=10)
        ax.set_xlabel('Named Vendor Count')
        ax.set_ylabel('Average Score')
        ax.set_title('Vendor Transparency Predicts Higher Scores', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 9)
        self.save_chart(fig, 'vendor_vs_score')

    def generate_narrative(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']
        top10 = d['all_vendors'].most_common(10)

        low_v = scored[scored.vendor_count <= 1].score_overall.mean()
        high_v = scored[scored.vendor_count >= 5].score_overall.mean()

        html = self.metric_grid([
            (len(d['all_vendors']), 'Unique Vendors', theme.BLUE),
            (f'{df.vendor_count.mean():.1f}', 'Avg Vendors/Company', theme.YELLOW),
            (f'{low_v:.1f}/10', 'Score (0-1 vendors)', theme.RED),
            (f'{high_v:.1f}/10', 'Score (5+ vendors)', theme.GREEN),
        ])

        html += self.section('Vendor Landscape', f"""
<p>Across {N} companies, we identified {len(d['all_vendors'])} unique technology vendors.
The average company names {df.vendor_count.mean():.1f} vendors in their compliance report.</p>

{self.chart_img('top_vendors.png')}

{self.table(['Rank', 'Vendor', 'Companies', '% of Portfolio'],
    [[str(i+1), v, str(c), f'{c/N*100:.1f}%'] for i, (v, c) in enumerate(top10)])}
""")

        html += self.section('Transparency = Maturity', f"""
<p>A striking pattern: companies that name more vendors in their SOC 2 reports score
significantly higher. This isn't because more vendors = better architecture. It's because
<strong>transparency about dependencies is a proxy for engineering culture maturity</strong>.</p>

{self.chart_img('vendor_vs_score.png')}

{self.insight_box(f"Companies with 0-1 named vendors average <strong>{low_v:.1f}/10</strong>. Companies with 5+ vendors average <strong>{high_v:.1f}/10</strong>. The difference is nearly a full point — meaningful in a tight distribution.")}
""")

        html += self.section('Distribution', f"""
{self.chart_img('vendor_count_dist.png')}

{self.flag_box("<strong>Due diligence signal:</strong> If a SOC 2 report names only the cloud provider and nothing else, that's a transparency red flag. Ask the founder to disclose the full vendor stack.", 'yellow')}
""")

        return html


if __name__ == "__main__":
    VendorEcosystem().run()
