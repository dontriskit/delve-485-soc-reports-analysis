"""
Module 06: Architecture Patterns
Thesis: Architecture pattern strongly correlates with score. Microservices and serverless-heavy score highest.
"""
import matplotlib.pyplot as plt
import json
import numpy as np
import pandas as pd
from collections import Counter
from .base_module import BaseModule
from . import theme


class ArchitecturePatterns(BaseModule):
    slug = "06_architecture_patterns"
    title = "Architecture Patterns"
    subtitle = "Monolith, microservices, serverless — what patterns dominate and which score highest"

    def generate_charts(self):
        d = self.data
        df, scored, N = d['df'], d['scored'], d['N']

        # Pattern distribution
        patterns = df.arch_pattern.value_counts().head(10)
        patterns = patterns[patterns.index != '']

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.barh(patterns.index[::-1], patterns.values[::-1], color=theme.CYAN, height=0.6)
        for i, v in enumerate(patterns.values[::-1]):
            ax.text(v + 2, i, str(v), va='center', fontsize=11)
        ax.set_xlabel('Companies')
        ax.set_title('Architecture Pattern Distribution', fontsize=16, fontweight='bold')
        self.save_chart(fig, 'pattern_dist')

        # Pattern vs score
        ps = scored[scored.arch_pattern != ''].groupby('arch_pattern').agg(
            mean=('score_overall','mean'), n=('score_overall','count')
        ).reset_index()
        ps = ps[ps.n >= 3].sort_values('mean')

        if len(ps) > 0:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.barh(ps.arch_pattern, ps['mean'], color=theme.BLUE, height=0.5)
            for _, row in ps.iterrows():
                ax.text(row['mean'] + 0.1, row.arch_pattern, f'{row["mean"]:.1f} (n={row.n})', va='center', fontsize=11)
            ax.set_xlim(0, 9)
            ax.set_xlabel('Average Score')
            ax.set_title('Architecture Pattern vs Score', fontsize=14, fontweight='bold')
            self.save_chart(fig, 'pattern_vs_score')

        # Database landscape
        db_counter = Counter()
        for e in d['extracts']:
            storage = e.get('data_storage')
            if isinstance(storage, str):
                try: storage = json.loads(storage)
                except: storage = {}
            if isinstance(storage, dict):
                dbs = storage.get('databases', [])
                if isinstance(dbs, list):
                    for db in dbs:
                        db_str = str(db).lower()
                        if 'postgres' in db_str: db_counter['PostgreSQL'] += 1
                        elif 'rds' in db_str and 'postgres' not in db_str: db_counter['AWS RDS'] += 1
                        elif 'dynamo' in db_str: db_counter['DynamoDB'] += 1
                        elif 'mongo' in db_str: db_counter['MongoDB'] += 1
                        elif 'redis' in db_str: db_counter['Redis'] += 1
                        elif 'elastic' in db_str or 'opensearch' in db_str: db_counter['ElasticSearch'] += 1
                        elif 'firebase' in db_str or 'firestore' in db_str: db_counter['Firebase/Firestore'] += 1
                        elif 'supabase' in db_str: db_counter['Supabase Postgres'] += 1
                        elif 'aurora' in db_str: db_counter['Aurora'] += 1
                        elif 'mysql' in db_str: db_counter['MySQL'] += 1

        if db_counter:
            top_db = db_counter.most_common(12)
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.barh([d[0] for d in top_db][::-1], [d[1] for d in top_db][::-1], color=theme.ORANGE, height=0.6)
            for i, v in enumerate([d[1] for d in top_db][::-1]):
                ax.text(v + 0.5, i, str(v), va='center', fontsize=10)
            ax.set_xlabel('Companies')
            ax.set_title('Database Technology Landscape', fontsize=14, fontweight='bold')
            self.save_chart(fig, 'databases')

    def generate_narrative(self):
        d = self.data
        df, N = d['df'], d['N']

        patterns = df.arch_pattern.value_counts().head(8)
        patterns = patterns[patterns.index != '']

        html = self.section('Architecture Pattern Distribution', f"""
<p>How companies structure their applications reveals their engineering maturity and scaling strategy.</p>

{self.chart_img('pattern_dist.png')}

{self.table(['Pattern', 'Companies', 'Share'],
    [[p, str(n), f'{n/N*100:.1f}%'] for p, n in patterns.items()])}
""")

        if (self.output_dir / 'pattern_vs_score.png').exists():
            html += self.section('Pattern vs Score', f"""
<p>Architecture pattern correlates with tech DD score — more sophisticated patterns tend to score higher.</p>
{self.chart_img('pattern_vs_score.png')}
{self.insight_box("Microservices and API-first patterns score highest because they require more deliberate infrastructure decisions — VPCs, load balancers, service mesh, etc. — which naturally produce better compliance reports.")}
""")

        if (self.output_dir / 'databases.png').exists():
            html += self.section('Database Technology Landscape', f"""
<p>PostgreSQL dominates, often via managed services (Supabase, AWS RDS, Neon).</p>
{self.chart_img('databases.png')}
{self.flag_box("<strong>For CTOs:</strong> PostgreSQL is the safe default. Redis for caching, DynamoDB for serverless, and Elasticsearch for search are the most common secondary databases.", 'green')}
""")

        return html

if __name__ == "__main__":
    ArchitecturePatterns().run()
