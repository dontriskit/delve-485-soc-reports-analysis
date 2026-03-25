"""
Module 10: Red Flag Analysis
Thesis: Missing RTO/RPO and short audits are most common; flag count inversely correlates with score.
"""
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from .base_module import BaseModule
from . import theme


class RedFlagAnalysis(BaseModule):
    slug = "10_red_flag_analysis"
    title = "Red Flag Analysis"
    subtitle = "Most common risks, what they mean, and which ones matter most"

    def _categorize_flags(self):
        cats = Counter()
        for flag in self.data['all_red_flags']:
            f = flag.lower()
            if 'rto' in f or 'rpo' in f: cats['No RTO/RPO disclosed'] += 1
            elif 'short' in f or '3-month' in f or '3 month' in f or 'minimum' in f: cats['Short audit period (3mo)'] += 1
            elif 'processing integrity' in f or 'privacy' in f: cats['Privacy/PI criteria excluded'] += 1
            elif ('single' in f and 'cloud' in f) or 'concentration' in f: cats['Single cloud dependency'] += 1
            elif 'template' in f or 'placeholder' in f or 'your name' in f: cats['Template artifacts'] += 1
            elif 'untestable' in f or 'no events' in f: cats['Controls untestable'] += 1
            elif 'waf' in f: cats['No WAF'] += 1
            elif 'siem' in f: cats['No SIEM'] += 1
            elif 'team' in f or 'person' in f or 'lean' in f: cats['Small team risk'] += 1
            elif 'tool' in f and 'not' in f: cats['Tools unnamed'] += 1
            else: cats['Other'] += 1
        return cats

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']
        cats = self._categorize_flags()

        # Top red flag categories
        top = dict(sorted(cats.items(), key=lambda x: -x[1])[:12])
        fig, ax = plt.subplots(figsize=(13, 6))
        ax.barh(list(top.keys())[::-1], list(top.values())[::-1], color=theme.RED, height=0.6)
        for i, v in enumerate(list(top.values())[::-1]):
            ax.text(v + 2, i, str(v), va='center', fontsize=11)
        ax.set_xlabel('Frequency')
        ax.set_title('Top Red Flag Categories Across Portfolio', fontsize=16, fontweight='bold')
        self.save_chart(fig, 'red_flag_categories')

        # Flag count distribution
        fig, ax = plt.subplots(figsize=(10, 5))
        df.red_flag_count.hist(bins=range(0, 15), ax=ax, color=theme.RED, edgecolor=theme.BG, alpha=0.8)
        ax.axvline(df.red_flag_count.mean(), color=theme.YELLOW, ls='--', lw=2,
                    label=f'Mean: {df.red_flag_count.mean():.1f}')
        ax.set_xlabel('Red Flags per Company')
        ax.set_ylabel('Companies')
        ax.set_title('Red Flag Count Distribution', fontsize=14, fontweight='bold')
        ax.legend()
        self.save_chart(fig, 'flag_count_dist')

        # Red flags vs score
        if len(scored) > 10:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(scored.red_flag_count, scored.score_overall, alpha=0.5, color=theme.BLUE, s=40)
            z = np.polyfit(scored.red_flag_count, scored.score_overall, 1)
            p = np.poly1d(z)
            x_line = np.linspace(scored.red_flag_count.min(), scored.red_flag_count.max(), 50)
            ax.plot(x_line, p(x_line), color=theme.RED, lw=2, ls='--', label=f'Trend (slope={z[0]:.2f})')
            ax.set_xlabel('Red Flag Count')
            ax.set_ylabel('Overall Score')
            ax.set_title('More Red Flags → Lower Scores', fontsize=14, fontweight='bold')
            ax.legend()
            self.save_chart(fig, 'flags_vs_score')

        # Flag balance (red/yellow/green per score bucket)
        if len(scored) > 0:
            scored_copy = scored.copy()
            scored_copy['bucket'] = scored_copy.score_overall.apply(lambda x: '7+' if x >= 7 else '5-6' if x >= 5 else '3-4')
            balance = scored_copy.groupby('bucket')[['red_flag_count','yellow_flag_count','green_flag_count']].mean()
            balance = balance.reindex(['3-4','5-6','7+'])

            fig, ax = plt.subplots(figsize=(10, 5))
            x = np.arange(len(balance))
            w = 0.25
            ax.bar(x - w, balance.red_flag_count, w, label='Red', color=theme.RED)
            ax.bar(x, balance.yellow_flag_count, w, label='Yellow', color=theme.YELLOW)
            ax.bar(x + w, balance.green_flag_count, w, label='Green', color=theme.GREEN)
            ax.set_xticks(x)
            ax.set_xticklabels(balance.index)
            ax.set_ylabel('Average Flag Count')
            ax.set_xlabel('Score Bucket')
            ax.set_title('Flag Balance by Score Tier', fontsize=14, fontweight='bold')
            ax.legend()
            self.save_chart(fig, 'flag_balance')

    def generate_narrative(self):
        d = self.data
        df, N = d['df'], d['N']
        cats = self._categorize_flags()
        top8 = sorted(cats.items(), key=lambda x: -x[1])[:8]

        html = self.metric_grid([
            (f'{df.red_flag_count.mean():.1f}', 'Avg Red Flags/Company', theme.RED),
            (f'{df.yellow_flag_count.mean():.1f}', 'Avg Yellow Flags', theme.YELLOW),
            (f'{df.green_flag_count.mean():.1f}', 'Avg Green Flags', theme.GREEN),
            (str(len(d['all_red_flags'])), 'Total Red Flags', theme.RED),
        ])

        html += self.section('Top Red Flag Categories', f"""
{self.chart_img('red_flag_categories.png')}

{self.table(['Red Flag', 'Frequency', '% of Portfolio'],
    [[flag, str(cnt), f'{cnt/N*100:.1f}%'] for flag, cnt in top8])}

{self.insight_box("<strong>The top 3 red flags are systemic:</strong> no RTO/RPO disclosure, short 3-month audit periods, and excluded privacy/processing integrity criteria. These aren't company-specific failures — they reflect the compliance automation template's defaults.")}
""")

        html += self.section('Flag Count Distribution', f"""
{self.chart_img('flag_count_dist.png')}
<p>Average company has {df.red_flag_count.mean():.1f} red flags, {df.yellow_flag_count.mean():.1f} yellow flags,
and {df.green_flag_count.mean():.1f} green flags.</p>
""")

        if (self.output_dir / 'flags_vs_score.png').exists():
            html += self.section('Red Flags vs Score', f"""
{self.chart_img('flags_vs_score.png')}
{self.flag_box("There is a negative correlation between red flag count and overall score. However, the relationship is noisy — some high-scoring companies still have many flags (often about audit period length rather than technical gaps).", 'yellow')}
""")

        if (self.output_dir / 'flag_balance.png').exists():
            html += self.section('Flag Balance by Score Tier', f"""
<p>How does the red/yellow/green flag mix change across score tiers?</p>
{self.chart_img('flag_balance.png')}
{self.flag_box("<strong>High scorers (7+) have more green flags and fewer red flags</strong> — but they still have red flags. The difference is in the severity: high scorers' red flags tend to be about audit period length, while low scorers' red flags are about missing controls.", 'green')}
""")
        return html

if __name__ == "__main__":
    RedFlagAnalysis().run()
