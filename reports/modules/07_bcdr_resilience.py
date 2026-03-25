"""
Module 07: BCDR & Resilience
Thesis: The gap between "has BCDR policy" (100%) and "has tested DR" (51%) is the single biggest risk.
"""
import matplotlib.pyplot as plt
import numpy as np
from .base_module import BaseModule
from . import theme


class BCDRResilience(BaseModule):
    slug = "07_bcdr_resilience"
    title = "BCDR & Resilience"
    subtitle = "Business continuity, disaster recovery, and the policy-vs-practice gap"

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        # BCDR feature adoption
        features = {
            'BCDR Policy': df.has_bcdr_policy.mean(),
            'Multi-AZ': df.multi_az.mean(),
            'Vuln Scanning': df.has_vuln_scanning.mean(),
            'Pen Testing': df.has_pen_testing.mean(),
            'Daily Backups': df.daily_backups.mean(),
            'Annual DR Testing': df.annual_dr_testing.mean(),
            'Tenant Isolation': df.per_tenant_segregation.mean(),
            'Multi-Region': df.multi_region.mean(),
            'Cyber Insurance': df.has_cyber_insurance.mean(),
        }
        features = dict(sorted(features.items(), key=lambda x: x[1]))

        fig, ax = plt.subplots(figsize=(12, 6))
        vals = [v * 100 for v in features.values()]
        colors = [theme.GREEN if v >= 80 else theme.YELLOW if v >= 50 else theme.RED for v in vals]
        ax.barh(list(features.keys()), vals, color=colors, height=0.65)
        for i, v in enumerate(vals):
            ax.text(v + 1.5, i, f'{v:.0f}%', va='center', fontsize=11)
        ax.set_xlabel('Adoption Rate (%)')
        ax.set_title(f'Resilience Feature Adoption (N={N})', fontsize=16, fontweight='bold')
        ax.set_xlim(0, 115)
        self.save_chart(fig, 'resilience_adoption')

        # The gap waterfall
        stages = [
            ('Has Policy', df.has_bcdr_policy.mean() * 100),
            ('Multi-AZ', df.multi_az.mean() * 100),
            ('Daily Backups', df.daily_backups.mean() * 100),
            ('Annual DR Test', df.annual_dr_testing.mean() * 100),
            ('Multi-Region', df.multi_region.mean() * 100),
            ('Cyber Insurance', df.has_cyber_insurance.mean() * 100),
        ]

        fig, ax = plt.subplots(figsize=(12, 5))
        x = range(len(stages))
        vals = [s[1] for s in stages]
        colors = [theme.GREEN if v >= 80 else theme.YELLOW if v >= 50 else theme.RED for v in vals]
        ax.bar(x, vals, color=colors, width=0.6)
        ax.set_xticks(x)
        ax.set_xticklabels([s[0] for s in stages], rotation=20, ha='right')
        for i, v in enumerate(vals):
            ax.text(i, v + 2, f'{v:.0f}%', ha='center', fontsize=11, fontweight='bold')
            if i > 0:
                drop = vals[i-1] - v
                if drop > 5:
                    ax.annotate(f'−{drop:.0f}%', xy=(i-0.5, (vals[i-1]+v)/2),
                               fontsize=9, color=theme.RED, ha='center')
        ax.set_ylabel('Adoption %')
        ax.set_title('The Resilience Gap — from Policy to Practice', fontsize=16, fontweight='bold')
        ax.set_ylim(0, 115)
        self.save_chart(fig, 'resilience_gap')

    def generate_narrative(self):
        d = self.data
        df, N = d['df'], d['N']

        html = self.metric_grid([
            ('100%', 'Have BCDR Policy', theme.GREEN),
            (f'{df.multi_az.mean()*100:.0f}%', 'Multi-AZ', theme.GREEN),
            (f'{df.annual_dr_testing.mean()*100:.0f}%', 'Annual DR Testing', theme.YELLOW),
            (f'{df.multi_region.mean()*100:.0f}%', 'Multi-Region', theme.RED),
        ])

        html += self.section('Resilience Feature Adoption', f"""
{self.chart_img('resilience_adoption.png')}
""")

        html += self.section('The Policy-vs-Practice Gap', f"""
<p>Every company has a BCDR policy (100%). But the drop-off from policy to practice is dramatic:</p>

{self.chart_img('resilience_gap.png')}

{self.insight_box(f"<strong>The critical gap:</strong> 100% have a BCDR policy, but only {df.annual_dr_testing.mean()*100:.0f}% test it annually and only {df.multi_region.mean()*100:.0f}% have multi-region failover. Most companies have a plan they've never tested for a disaster they can't recover from quickly.")}

<h3>What this means for investors:</h3>
{self.flag_box("A BCDR policy without annual testing is a checkbox, not a capability. Ask to see DR test results — the date, the scenario, the recovery time, and what was fixed afterward.", 'red')}
{self.flag_box(f"Only {df.has_cyber_insurance.mean()*100:.0f}% have cyber insurance. For companies handling sensitive data, this is a material gap in financial risk transfer.", 'yellow')}
{self.flag_box(f"Multi-AZ ({df.multi_az.mean()*100:.0f}%) is nearly universal — the industry has standardized on AZ-level redundancy. Multi-region ({df.multi_region.mean()*100:.0f}%) remains expensive and rare.", 'green')}
""")
        return html

if __name__ == "__main__":
    BCDRResilience().run()
