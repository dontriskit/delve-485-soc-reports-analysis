"""
Module 13: Funding Signals
Thesis: Funding level does NOT predict tech maturity. The highest-funded company (11x, $75M)
scores 6/10 while a bootstrapped company (Scribeberry) scores 8/10. YC dominates the cohort.
"""
import matplotlib.pyplot as plt
import numpy as np
import json
import re
from collections import Counter
from .base_module import BaseModule
from . import theme


class FundingSignals(BaseModule):
    slug = "13_funding_signals"
    title = "Funding Signals"
    subtitle = "Does more money mean better tech? Investor patterns across 27 researched companies"

    def _load_funding(self):
        with open("data_export/funding_research.json") as f:
            return json.load(f)

    def _parse_funding_amount(self, f):
        if not f or f in ('Undisclosed', 'Undisclosed/Bootstrapped', 'Undisclosed Pre-Seed'):
            return 0
        nums = re.findall(r'[\d.]+', f.replace(',', ''))
        if nums:
            val = float(nums[0])
            if 'M' in f.upper() or val >= 1:
                return val
            if 'K' in f.upper():
                return val / 1000
        return 0

    def generate_charts(self):
        funding = self._load_funding()

        # Score vs Funding scatter
        companies_with_both = [(c['company'][:20], c['tech_score'], self._parse_funding_amount(c.get('total_funding','')))
                                for c in funding if c.get('tech_score') and self._parse_funding_amount(c.get('total_funding','')) > 0]

        fig, ax = plt.subplots(figsize=(12, 7))
        names = [c[0] for c in companies_with_both]
        scores = [c[1] for c in companies_with_both]
        funds = [c[2] for c in companies_with_both]

        scatter = ax.scatter(funds, scores, s=100, c=scores, cmap='RdYlGn', vmin=3, vmax=8,
                            edgecolors=theme.BORDER, linewidths=1, zorder=5)
        for name, score, fund in companies_with_both:
            if fund > 10 or score >= 7:  # Label notable companies
                ax.annotate(name, (fund, score), textcoords="offset points",
                           xytext=(8, 5), fontsize=8, color=theme.MUTED)
        ax.set_xscale('log')
        ax.set_xlabel('Total Funding ($M, log scale)', fontsize=12)
        ax.set_ylabel('Tech DD Score', fontsize=12)
        ax.set_title('Funding vs Tech Maturity — No Correlation', fontsize=16, fontweight='bold')
        ax.set_ylim(2, 9)
        ax.axhline(7, color=theme.GREEN, ls=':', alpha=0.3, label='Investment Ready (7+)')
        ax.legend()
        plt.colorbar(scatter, label='Score')
        self.save_chart(fig, 'funding_vs_score')

        # Top funded bar chart
        sorted_by_funding = sorted(funding, key=lambda c: -self._parse_funding_amount(c.get('total_funding','')))
        top_funded = [(c['company'][:25], self._parse_funding_amount(c['total_funding']), c.get('tech_score',0))
                      for c in sorted_by_funding if self._parse_funding_amount(c.get('total_funding','')) > 0][:15]

        fig, ax = plt.subplots(figsize=(13, 7))
        names = [t[0] for t in top_funded]
        funds = [t[1] for t in top_funded]
        scores = [t[2] for t in top_funded]
        colors = [theme.SCORE_COLOR(s) for s in scores]
        ax.barh(names[::-1], funds[::-1], color=colors[::-1], height=0.6)
        for i, (f, s) in enumerate(zip(funds[::-1], scores[::-1])):
            ax.text(f + 0.5, i, f'${f:.0f}M (score: {s}/10)', va='center', fontsize=10)
        ax.set_xlabel('Total Funding ($M)')
        ax.set_title('Top Funded Companies — Color = Tech DD Score', fontsize=16, fontweight='bold')
        self.save_chart(fig, 'top_funded')

        # Investor frequency
        investor_counts = Counter()
        for c in funding:
            for inv in c.get('investors', []):
                if inv and inv != 'Undisclosed':
                    investor_counts[inv] += 1

        top_inv = investor_counts.most_common(15)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh([i[0][:25] for i in top_inv][::-1], [i[1] for i in top_inv][::-1],
                color=theme.PURPLE, height=0.6)
        for i, v in enumerate([i[1] for i in top_inv][::-1]):
            ax.text(v + 0.1, i, str(v), va='center', fontsize=11)
        ax.set_xlabel('Portfolio Companies Backed')
        ax.set_title('Most Active Investors in This Portfolio', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'investor_landscape')

        # Stage distribution
        stages = Counter()
        for c in funding:
            lr = c.get('last_round', '') or ''
            if 'Series B' in lr: stages['Series B'] += 1
            elif 'Series A' in lr: stages['Series A'] += 1
            elif 'Seed' in lr or 'seed' in lr: stages['Seed'] += 1
            elif 'Pre-Seed' in lr or 'pre-seed' in lr.lower(): stages['Pre-Seed'] += 1
            elif 'Speedrun' in lr or 'Grant' in lr: stages['Grant/Program'] += 1
            elif lr: stages['Other'] += 1
            else: stages['Undisclosed'] += 1

        fig, ax = plt.subplots(figsize=(8, 5))
        labels = list(stages.keys())
        vals = list(stages.values())
        ax.pie(vals, labels=labels, autopct='%1.0f%%', colors=theme.PAL[:len(labels)],
               textprops={'color': theme.TEXT, 'fontsize': 11})
        ax.set_title('Funding Stage Distribution', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'stage_distribution')

    def generate_narrative(self):
        funding = self._load_funding()
        n = len(funding)

        yc_count = sum(1 for c in funding if 'Y Combinator' in str(c.get('investors', [])))
        a16z_count = sum(1 for c in funding if 'Andreessen Horowitz' in str(c.get('investors', [])))
        kp_count = sum(1 for c in funding if 'Kleiner Perkins' in str(c.get('investors', [])))

        top3 = sorted(funding, key=lambda c: -self._parse_funding_amount(c.get('total_funding', '')))[:3]

        html = self.metric_grid([
            (n, 'Companies Researched', theme.BLUE),
            (yc_count, 'YC-Backed', theme.ORANGE),
            (a16z_count, 'a16z-Backed', theme.PURPLE),
            (f'${sum(self._parse_funding_amount(c.get("total_funding","")) for c in funding):.0f}M', 'Total Identifiable Funding', theme.GREEN),
        ])

        html += self.section('Funding Does NOT Predict Tech Maturity', f"""
<p>Perhaps the most counterintuitive finding of this analysis: <strong>there is no meaningful correlation
between funding level and tech DD score.</strong></p>

{self.chart_img('funding_vs_score.png', 'Each dot is a company. Color = tech DD score. X-axis is log scale.')}

{self.insight_box("<strong>The highest-scoring company (Scribeberry, 8/10) appears to be bootstrapped.</strong> The highest-funded company (11x AI, $75M+) scores 6/10. Money buys speed, marketing, and headcount — but it doesn't automatically buy infrastructure maturity or security depth.")}

<p>This has practical implications for diligence: a company's fundraising history tells you about
market validation and investor confidence, but it tells you nothing about whether they have WAF,
multi-region failover, or named monitoring tools. Tech DD and funding DD are orthogonal signals
that must be evaluated independently.</p>
""")

        html += self.section('Top Funded Companies', f"""
{self.chart_img('top_funded.png', 'Bar color indicates tech DD score (green = 7+, yellow = 5-6, red = 3-4)')}

{self.table(['Company', 'Funding', 'Score', 'Product'], [
    [c['company'][:30], c.get('total_funding','—'), f'{c.get("tech_score","—")}/10', c.get('product','')[:40]]
    for c in top3
])}
""")

        html += self.section('Investor Landscape', f"""
<p>Y Combinator dominates this cohort with {yc_count} of {n} researched companies.
a16z backs {a16z_count} companies (11x AI and Cluely). Kleiner Perkins backs {kp_count}
(Conway and Antes AI).</p>

{self.chart_img('investor_landscape.png')}

{self.chart_img('stage_distribution.png')}

<h3>Key Patterns</h3>
<ul>
<li><strong>YC is the common thread</strong> — {yc_count}/{n} companies are YC alumni. The YC network effect is visible in both deal flow and compliance timing (many get SOC 2 within months of demo day).</li>
<li><strong>a16z bets on GTM AI</strong> — both 11x (AI SDR) and Cluely (AI coaching) are sales/productivity tools</li>
<li><strong>Kleiner Perkins goes vertical</strong> — Conway (risk ops) and Antes AI (manufacturing compliance) are vertical AI plays</li>
<li><strong>Revenue-funded outliers</strong> — AfterQuery ($6.5M revenue on $500K funding) and Afterword (deliberately non-VC) show that some of the best-architected companies don't need venture capital</li>
</ul>

{self.flag_box("<strong>For LPs and fund managers:</strong> When a portfolio company presents a clean SOC 2, ask what it actually contains. Our analysis shows that the highest-funded companies don't necessarily have the best compliance reports — they just get them faster. The compliance automation tools (Vanta, Drata, Delve) have made it possible to achieve SOC 2 in weeks, but speed doesn't equal depth.", 'yellow')}
""")

        return html


if __name__ == "__main__":
    FundingSignals().run()
