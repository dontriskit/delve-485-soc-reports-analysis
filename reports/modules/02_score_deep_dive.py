"""
Module 02: Score Deep Dive
Thesis: Infrastructure investment drives all other scores; vendor diversity is weakest and most independent.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from .base_module import BaseModule
from . import theme


class ScoreDeepDive(BaseModule):
    slug = "02_score_deep_dive"
    title = "Score Deep Dive"
    subtitle = "What drives high scores — dimension analysis of 121 scored companies"

    def generate_charts(self):
        d = self.data
        scored = d['scored']
        dims = d['SCORE_COLS'][1:]
        labels = d['DIM_LABELS'][1:]

        # Box plots
        fig, ax = plt.subplots(figsize=(13, 6))
        data = scored[dims].melt(var_name='dim', value_name='score')
        data['dim'] = data.dim.map(dict(zip(dims, labels)))
        sns.boxplot(data=data, x='dim', y='score', hue='dim', ax=ax, palette=theme.PAL[:len(dims)], legend=False, showfliers=True)
        sns.stripplot(data=data, x='dim', y='score', ax=ax, color='white', alpha=0.2, size=3, jitter=True)
        ax.set_xlabel('')
        ax.set_ylabel('Score')
        ax.set_title('Score Distribution by Dimension', fontsize=16, fontweight='bold')
        ax.set_ylim(0, 10.5)
        plt.xticks(rotation=20, ha='right')
        self.save_chart(fig, 'dimension_boxplots')

        # Correlation matrix
        corr = scored[d['SCORE_COLS']].corr()
        fig, ax = plt.subplots(figsize=(9, 8))
        short = [l.replace('\n',' ') for l in d['DIM_LABELS']]
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn', center=0.5, ax=ax,
                    xticklabels=short, yticklabels=short, linewidths=0.5,
                    linecolor=theme.BORDER, vmin=0, vmax=1)
        ax.set_title('Dimension Score Correlations', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_chart(fig, 'correlations')

        # Strongest vs weakest dimension per company
        dim_df = scored[dims].copy()
        dim_df.columns = labels
        strongest = dim_df.idxmax(axis=1).value_counts()
        weakest = dim_df.idxmin(axis=1).value_counts()

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        for ax, data, title, color in [(axes[0], strongest, 'Most Common Strongest Dimension', theme.GREEN),
                                        (axes[1], weakest, 'Most Common Weakest Dimension', theme.RED)]:
            ax.barh(data.index, data.values, color=color, height=0.6)
            for i, v in enumerate(data.values):
                ax.text(v + 0.5, i, str(v), va='center', fontsize=11)
            ax.set_title(title, fontsize=13, fontweight='bold')
        plt.tight_layout()
        self.save_chart(fig, 'strongest_weakest')

    def generate_narrative(self):
        d = self.data
        scored = d['scored']
        dims = d['SCORE_COLS'][1:]
        labels = d['DIM_LABELS'][1:]

        rows = []
        for col, label in zip(dims, labels):
            s = scored[col]
            rows.append([label, f'{s.mean():.1f}', f'{s.median():.0f}', f'{s.std():.1f}', f'{s.min():.0f}', f'{s.max():.0f}'])

        html = self.section('Dimension Distributions', f"""
<p>Each company is scored across 7 dimensions on a 1-10 scale. The box plots reveal how tightly or broadly
each dimension varies across the portfolio.</p>

{self.chart_img('dimension_boxplots.png', 'Box = IQR, whiskers = 1.5×IQR, dots = individual companies')}

{self.table(['Dimension', 'Mean', 'Median', 'Std Dev', 'Min', 'Max'], rows)}

{self.insight_box(f"<strong>Security ({scored.score_security.mean():.1f}/10)</strong> is the highest and tightest — most companies achieve a similar level via template SOC 2 controls. <strong>Vendor Diversity ({scored.score_vendor_diversity.mean():.1f}/10)</strong> is the lowest and widest — it's the dimension that most differentiates companies.")}
""")

        html += self.section('Dimension Correlations', f"""
<p>How do dimensions relate to each other? Strong correlations suggest shared underlying drivers.</p>

{self.chart_img('correlations.png')}

<h3>Key findings:</h3>
<ul>
<li><strong>Infrastructure ↔ Overall</strong> has the strongest correlation — investing in infrastructure lifts all boats</li>
<li><strong>Vendor Diversity</strong> is the most independent dimension — a company can score high on everything else but low on vendor diversity (single-cloud dependency)</li>
<li><strong>Security ↔ DevOps</strong> are moderately correlated — mature ops teams tend to have better security practices</li>
</ul>
""")

        html += self.section('Strongest vs Weakest', f"""
<p>For each company, which dimension is their strongest and weakest?</p>

{self.chart_img('strongest_weakest.png')}

{self.flag_box("<strong>Pattern:</strong> Security is most often the strongest dimension, while Vendor Diversity is most often the weakest. This aligns with the template-driven compliance model — security controls are prescribed, but vendor choices are company-specific.", 'yellow')}
""")

        return html


if __name__ == "__main__":
    ScoreDeepDive().run()
