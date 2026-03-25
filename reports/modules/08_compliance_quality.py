"""
Module 08: Compliance Quality
Thesis: Type 2 > Type 1; template artifacts undermine audit credibility. Auditor landscape is concentrated.
"""
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import Counter
from .base_module import BaseModule
from . import theme


class ComplianceQuality(BaseModule):
    slug = "08_compliance_quality"
    title = "Compliance Quality"
    subtitle = "Type 1 vs Type 2, auditor landscape, and template artifact detection"

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        # Type 1 vs Type 2 count + score
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        tc = df.type.value_counts()
        ax = axes[0]
        ax.bar(tc.index, tc.values, color=[theme.BLUE, theme.PURPLE], width=0.5)
        for i, v in enumerate(tc.values):
            ax.text(i, v + 5, f'{v} ({v/N*100:.0f}%)', ha='center', fontsize=12, fontweight='bold')
        ax.set_title('Report Type Distribution', fontsize=14, fontweight='bold')
        ax.set_ylabel('Companies')

        ax = axes[1]
        for i, t in enumerate(['Type 1', 'Type 2']):
            sub = scored[scored.type == t]
            if len(sub) > 0:
                ax.hist(sub.score_overall, bins=np.arange(0.5, 10.5, 1), alpha=0.6,
                        label=f'{t} (n={len(sub)}, μ={sub.score_overall.mean():.1f})', color=theme.PAL[i])
        ax.legend()
        ax.set_xlabel('Overall Score')
        ax.set_title('Score by Report Type', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self.save_chart(fig, 'type_comparison')

        # Auditor landscape
        auditors = df[df.auditor.notna()].auditor.value_counts().head(10)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.barh(auditors.index[::-1], auditors.values[::-1], color=theme.TEAL, height=0.6)
        for i, v in enumerate(auditors.values[::-1]):
            ax.text(v + 1, i, f'{v} ({v/N*100:.0f}%)', va='center', fontsize=10)
        ax.set_xlabel('Companies')
        ax.set_title('Top 10 Auditors', fontsize=14, fontweight='bold')
        self.save_chart(fig, 'auditor_landscape')

        # Template artifact detection
        template_count = 0
        for flag in d['all_red_flags']:
            fl = flag.lower()
            if any(w in fl for w in ['template', 'placeholder', 'your name', 'sample', 'boilerplate']):
                template_count += 1

        fig, ax = plt.subplots(figsize=(8, 4))
        vals = [template_count, len(d['all_red_flags']) - template_count]
        ax.pie(vals, labels=['Template Artifacts', 'Other Red Flags'], autopct='%1.0f%%',
               colors=[theme.RED, theme.MUTED], textprops={'color': theme.TEXT})
        ax.set_title(f'Template Artifacts in Red Flags ({template_count} instances)', fontsize=13, fontweight='bold')
        self.save_chart(fig, 'template_artifacts')

    def generate_narrative(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']
        t1 = int((df.type == 'Type 1').sum())
        t2 = int((df.type == 'Type 2').sum())
        t1_score = scored[scored.type == 'Type 1'].score_overall.mean()
        t2_score = scored[scored.type == 'Type 2'].score_overall.mean()

        html = self.metric_grid([
            (t1, 'Type 1 (Design Only)', theme.BLUE),
            (t2, 'Type 2 (Operational)', theme.PURPLE),
            (f'{t1_score:.1f}' if not np.isnan(t1_score) else '—', 'Type 1 Avg Score', theme.BLUE),
            (f'{t2_score:.1f}' if not np.isnan(t2_score) else '—', 'Type 2 Avg Score', theme.PURPLE),
        ])

        html += self.section('Type 1 vs Type 2', f"""
<p><strong>Type 1</strong> reports evaluate control design at a point in time.
<strong>Type 2</strong> reports test operating effectiveness over a period (typically 3-12 months).
Type 2 is significantly more valuable for due diligence.</p>

{self.chart_img('type_comparison.png')}

{self.insight_box(f"<strong>{t2} companies ({t2/N*100:.0f}%)</strong> have Type 2 reports with operational evidence. The remaining {t1} ({t1/N*100:.0f}%) have only Type 1 — their controls may be well-designed but unproven in practice.")}
""")

        html += self.section('Auditor Landscape', f"""
<p>The auditor ecosystem is highly concentrated. A single auditor dominates the portfolio.</p>

{self.chart_img('auditor_landscape.png')}

{self.flag_box("<strong>Concentration risk:</strong> When one auditor handles the majority of reports, template re-use is inevitable. This explains the striking similarity across reports — identical control descriptions, same structure, same boilerplate.", 'yellow')}
""")

        html += self.section('Template Artifact Detection', f"""
<p>Many reports contain visible template artifacts — placeholder text, sample diagrams,
'Your Name Here' in signing authority, or highlighted instructions that were never removed.</p>

{self.chart_img('template_artifacts.png')}

{self.flag_box("<strong>What template artifacts mean:</strong> A published SOC 2 report with placeholder text suggests the company rushed through compliance without thorough review. It doesn't necessarily mean controls are absent — but it undermines confidence in the audit's rigor.", 'red')}
""")
        return html

if __name__ == "__main__":
    ComplianceQuality().run()
