"""
Module 03: Cloud Infrastructure Landscape
Thesis: AWS dominates (60%+), but PaaS-first (Supabase/Vercel/Render) is an emerging pattern.
"""
import matplotlib.pyplot as plt
import numpy as np
from .base_module import BaseModule
from . import theme


class CloudLandscape(BaseModule):
    slug = "03_cloud_landscape"
    title = "Cloud Infrastructure Landscape"
    subtitle = "AWS dominance, PaaS-first patterns, and platform concentration risk"

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        cloud = df.cloud.value_counts()
        # Donut
        fig, ax = plt.subplots(figsize=(10, 7))
        top = cloud.head(8)
        colors = [theme.CLOUD_COLORS.get(c, '#666') for c in top.index]
        wedges, texts, autotexts = ax.pie(top.values, labels=top.index, autopct='%1.0f%%',
            colors=colors, textprops={'fontsize': 11, 'color': theme.TEXT}, pctdistance=0.8,
            wedgeprops={'width': 0.5})
        ax.set_title(f'Cloud Provider Market Share (N={N})', fontsize=16, fontweight='bold')
        self.save_chart(fig, 'cloud_share')

        # Cloud vs score
        cs = scored.groupby('cloud').agg(mean=('score_overall','mean'), n=('score_overall','count')).reset_index()
        cs = cs[cs.n >= 3].sort_values('mean')

        fig, ax = plt.subplots(figsize=(12, 5))
        colors = [theme.CLOUD_COLORS.get(c, '#666') for c in cs.cloud]
        ax.barh(cs.cloud, cs['mean'], color=colors, height=0.6)
        for _, row in cs.iterrows():
            ax.text(row['mean'] + 0.1, row.cloud, f'{row["mean"]:.1f} (n={row.n})', va='center', fontsize=11)
        ax.set_xlim(0, 9)
        ax.set_xlabel('Average Overall Score')
        ax.set_title('Cloud Provider vs Average Score (min n=3)', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'cloud_vs_score')

        # Enterprise vs PaaS
        enterprise = ['AWS', 'GCP', 'Azure']
        paas = ['Supabase', 'Vercel', 'Render', 'DigitalOcean', 'Fly.io', 'Railway', 'Heroku']
        df_temp = df.copy()
        df_temp['tier'] = df_temp.cloud.apply(lambda c: 'Enterprise\n(AWS/GCP/Azure)' if c in enterprise else 'PaaS/Startup\n(Supabase/Vercel/etc)' if c in paas else 'Other')
        tier_counts = df_temp.tier.value_counts()

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [theme.BLUE, theme.GREEN, theme.MUTED]
        ax.bar(tier_counts.index, tier_counts.values, color=colors[:len(tier_counts)], width=0.5)
        for i, v in enumerate(tier_counts.values):
            ax.text(i, v + 5, f'{v} ({v/N*100:.0f}%)', ha='center', fontsize=12, fontweight='bold')
        ax.set_ylabel('Companies')
        ax.set_title('Enterprise vs PaaS-First Architecture', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'enterprise_vs_paas')

    def generate_narrative(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']
        cloud = df.cloud.value_counts()

        html = self.metric_grid([
            (f'{cloud.get("AWS",0)}', f'AWS ({cloud.get("AWS",0)/N*100:.0f}%)', theme.ORANGE),
            (f'{cloud.get("GCP",0)}', f'GCP ({cloud.get("GCP",0)/N*100:.0f}%)', theme.BLUE),
            (f'{cloud.get("Supabase",0)}', f'Supabase', theme.GREEN),
            (f'{cloud.get("Vercel",0)}', f'Vercel', theme.TEXT),
        ])

        html += self.section('Market Share', f"""
{self.chart_img('cloud_share.png')}

{self.table(['Provider', 'Companies', 'Share'],
    [[c, str(n), f'{n/N*100:.1f}%'] for c, n in cloud.head(10).items()])}

{self.flag_box(f"<strong>Systemic risk:</strong> {cloud.get('AWS',0)/N*100:.0f}% of the portfolio runs on AWS. A major AWS regional outage would simultaneously impact {cloud.get('AWS',0)} companies.", 'red')}
""")

        html += self.section('Cloud Provider vs Score', f"""
<p>Does cloud provider choice predict tech maturity?</p>
{self.chart_img('cloud_vs_score.png')}
{self.insight_box("Cloud choice alone doesn't determine score — architecture decisions matter more than which cloud you're on. But PaaS-first companies tend to have simpler architectures with fewer disclosed features.")}
""")

        html += self.section('Enterprise vs PaaS-First', f"""
<p>A clear divide exists between companies built on enterprise hyperscalers (AWS/GCP/Azure)
and those using PaaS platforms (Supabase, Vercel, Render) as their primary infrastructure.</p>

{self.chart_img('enterprise_vs_paas.png')}

<h3>PaaS-First Implications</h3>
<ul>
<li><strong>Speed advantage:</strong> PaaS companies deploy faster with less ops overhead</li>
<li><strong>Control trade-off:</strong> Many controls are delegated via carve-out (not audited directly)</li>
<li><strong>Migration risk:</strong> Moving off Supabase/Vercel is harder than migrating between hyperscalers</li>
<li><strong>Scaling ceiling:</strong> PaaS platforms may not scale to enterprise workloads</li>
</ul>
""")
        return html

if __name__ == "__main__":
    CloudLandscape().run()
