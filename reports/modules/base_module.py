"""
Abstract base class for report modules.
Each module generates charts (.png) and a narrative page (.html).
"""
import matplotlib.pyplot as plt
from pathlib import Path
from . import theme
from . import data_loader


class BaseModule:
    slug = ""
    title = ""
    subtitle = ""

    def __init__(self):
        self.output_dir = Path("reports/output") / self.slug
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts = []
        self.data = data_loader.get()
        theme.apply_theme()

    def save_chart(self, fig, name):
        """Save a matplotlib figure and track it."""
        path = self.output_dir / f"{name}.png"
        fig.savefig(path, bbox_inches='tight', facecolor=theme.BG, dpi=150)
        plt.close(fig)
        self.charts.append(f"{name}.png")
        return path

    def generate_charts(self):
        """Override: create chart PNGs via self.save_chart()."""
        raise NotImplementedError

    def generate_narrative(self) -> str:
        """Override: return body HTML string."""
        raise NotImplementedError

    def run(self):
        """Execute the full module pipeline."""
        print(f"  Generating charts...")
        self.generate_charts()
        print(f"  Generating narrative...")
        body = self.generate_narrative()
        html = theme.html_wrap(self.title, self.subtitle, body, self.charts)
        theme.save_module(self.output_dir, self.slug, html)
        print(f"  Done: {len(self.charts)} charts, 1 HTML")

    # ---- Helpers ----

    def metric_card(self, value, label, color=None):
        c = color or theme.BLUE
        return f'<div class="metric"><div class="value" style="color:{c}">{value}</div><div class="label">{label}</div></div>'

    def metric_grid(self, metrics, cols=4):
        cards = ''.join(self.metric_card(v, l, c) for v, l, c in metrics)
        return f'<div class="grid grid-cols-{cols} gap-4 mb-6">{cards}</div>'

    def insight_box(self, text):
        return f'<div class="insight">{text}</div>'

    def flag_box(self, text, color='blue'):
        cls = f'flag-{color}' if color in ('red','yellow','green') else 'insight'
        return f'<div class="{cls}">{text}</div>'

    def chart_img(self, name, caption=None):
        cap = f'<p class="text-sm text-gray-400 mt-2 text-center">{caption}</p>' if caption else ''
        return f'<div class="my-6"><img src="{name}" class="rounded-lg w-full" alt="{name}">{cap}</div>'

    def table(self, headers, rows):
        ths = ''.join(f'<th>{h}</th>' for h in headers)
        trs = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows)
        return f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>'

    def section(self, title, content):
        return f'<h2>{title}</h2>\n{content}'

    def subsection(self, title, content):
        return f'<h3>{title}</h3>\n{content}'
