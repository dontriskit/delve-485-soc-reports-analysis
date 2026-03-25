"""
Module 11: Investment Readiness
Thesis: 485 → 19 high scorers → 20 fully mature. The funnel reveals where most companies
fall short and what the cheapest interventions would be.
"""
import matplotlib.pyplot as plt
import numpy as np
from .base_module import BaseModule
from . import theme


class InvestmentReadiness(BaseModule):
    slug = "11_investment_readiness"
    title = "Investment Readiness"
    subtitle = "From 485 companies to the investable few — the quality funnel"

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        # Funnel
        funnel = [
            ('Total Portfolio', N),
            ('Has SOC 2 Report', N),
            ('Type 2 (Operational)', int((df.type == 'Type 2').sum())),
            ('Scored 5+', int((df.score_overall >= 5).sum())),
            ('Scored 7+ (High)', int((df.score_overall >= 7).sum())),
            ('Multi-Region + WAF', int(((df.multi_region) & (df.has_waf)).sum())),
            ('Full Maturity', int(((df.multi_region) & (df.has_waf) & (df.has_pen_testing) & (df.daily_backups) & (df.quarterly_reviews)).sum())),
        ]

        fig, ax = plt.subplots(figsize=(12, 6))
        labels = [f[0] for f in funnel]
        values = [f[1] for f in funnel]
        colors = [theme.CYAN]*2 + [theme.BLUE]*2 + [theme.GREEN]*2 + [theme.PURPLE]
        ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.6)
        for i, v in enumerate(values[::-1]):
            pct = v / N * 100
            ax.text(v + 5, i, f'{v} ({pct:.0f}%)', va='center', fontsize=12, fontweight='bold')
        ax.set_xlabel('Companies')
        ax.set_title('Investment Readiness Funnel', fontsize=16, fontweight='bold')
        ax.set_xlim(0, N * 1.2)
        self.save_chart(fig, 'funnel')

        # Readiness tiers
        def tier(score):
            if score >= 8: return 'HIGH (8-10)'
            if score >= 7: return 'MOD-HIGH (7)'
            if score >= 5: return 'MODERATE (5-6)'
            if score >= 3: return 'LOW (3-4)'
            return 'VERY LOW (1-2)'

        scored_copy = scored.copy()
        scored_copy['tier'] = scored_copy.score_overall.apply(tier)
        tier_order = ['HIGH (8-10)', 'MOD-HIGH (7)', 'MODERATE (5-6)', 'LOW (3-4)', 'VERY LOW (1-2)']
        tier_colors = [theme.GREEN, theme.BLUE, theme.YELLOW, theme.RED, '#7f1d1d']
        tier_counts = scored_copy.tier.value_counts()

        fig, ax = plt.subplots(figsize=(10, 5))
        for t in tier_order:
            if t not in tier_counts: tier_counts[t] = 0
        vals = [tier_counts.get(t, 0) for t in tier_order]
        ax.barh(tier_order[::-1], vals[::-1], color=tier_colors[::-1], height=0.6)
        for i, v in enumerate(vals[::-1]):
            ax.text(v + 1, i, str(v), va='center', fontsize=13, fontweight='bold')
        ax.set_xlabel('Companies')
        ax.set_title('Investment Readiness Tiers (N=121 scored)', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'tiers')

        # Cheapest fixes
        fixes = {
            'Add WAF': int((~df.has_waf).sum()),
            'Add Multi-Region': int((~df.multi_region).sum()),
            'Add Pen Testing': int((~df.has_pen_testing).sum()),
            'Add Quarterly Reviews': int((~df.quarterly_reviews).sum()),
            'Add Daily Backups': int((~df.daily_backups).sum()),
            'Add Cyber Insurance': int((~df.has_cyber_insurance).sum()),
        }
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.barh(list(fixes.keys()), list(fixes.values()), color=theme.YELLOW, height=0.6)
        for i, v in enumerate(fixes.values()):
            ax.text(v + 3, i, f'{v} ({v/N*100:.0f}%)', va='center', fontsize=11)
        ax.set_xlabel('Companies That Would Benefit')
        ax.set_title('Cheapest Security Upgrades — Opportunity Size', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'cheapest_fixes')

    def generate_narrative(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        type2 = int((df.type == 'Type 2').sum())
        score5 = int((df.score_overall >= 5).sum())
        score7 = int((df.score_overall >= 7).sum())
        full_mature = int(((df.multi_region) & (df.has_waf) & (df.has_pen_testing) & (df.daily_backups) & (df.quarterly_reviews)).sum())

        html = self.section('The Investment Funnel', f"""
<p>Starting from {N} companies, each progressive quality filter narrows the pool dramatically.</p>

{self.chart_img('funnel.png')}

{self.table(['Stage', 'Remaining', 'Drop-off', 'What it means'], [
    ['Total Portfolio', str(N), '—', 'All companies with SOC 2 reports'],
    ['Type 2 (Operational)', str(type2), f'{N-type2} lack operational evidence', 'Controls tested over time, not just designed'],
    ['Scored 5+', str(score5), f'{type2-score5} below baseline', 'Minimum acceptable tech maturity'],
    ['Scored 7+', str(score7), f'{score5-score7} adequate but not exceptional', 'Strong tech foundations'],
    ['Full Maturity', str(full_mature), f'{score7-full_mature} missing resilience', 'Multi-region + WAF + pen test + backups + reviews'],
])}

{self.insight_box(f"<strong>Only {full_mature} companies ({full_mature/N*100:.1f}%) meet the full maturity bar.</strong> This means 96% of the portfolio has concrete improvement opportunities — a value creation thesis for PE.")}
""")

        html += self.section('Readiness Tiers', f"""
{self.chart_img('tiers.png')}

<p>Of {len(scored)} scored companies:</p>
<ul>
<li><strong style="color:{theme.GREEN}">HIGH (8-10):</strong> {int((scored.score_overall >= 8).sum())} companies — best-in-class</li>
<li><strong style="color:{theme.BLUE}">MODERATE-HIGH (7):</strong> {int((scored.score_overall == 7).sum())} companies — strong foundations</li>
<li><strong style="color:{theme.YELLOW}">MODERATE (5-6):</strong> {int(((scored.score_overall >= 5) & (scored.score_overall <= 6)).sum())} companies — adequate, undifferentiated</li>
<li><strong style="color:{theme.RED}">LOW (3-4):</strong> {int(((scored.score_overall >= 3) & (scored.score_overall <= 4)).sum())} companies — material gaps</li>
</ul>
""")

        html += self.section('Cheapest Fixes', f"""
<p>These interventions would move the most companies up the maturity ladder with the least effort:</p>

{self.chart_img('cheapest_fixes.png')}

{self.flag_box("<strong>Quick wins:</strong> Adding WAF (Cloudflare/AWS WAF, 1 day) and establishing quarterly access reviews (process change, $0) would benefit 56-78% of the portfolio.", 'green')}
{self.flag_box("<strong>Medium effort:</strong> Multi-region migration and pen testing programs require weeks of work but dramatically reduce portfolio-level risk.", 'yellow')}
""")

        return html


if __name__ == "__main__":
    InvestmentReadiness().run()
