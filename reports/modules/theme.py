"""
Global theme for all report modules.
Shared colors, fonts, chart defaults, HTML template.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================
# COLORS
# ============================================================
BG = '#0f172a'
BG2 = '#1e293b'
CARD = '#1a2332'
BORDER = '#334155'
TEXT = '#e2e8f0'
MUTED = '#94a3b8'
BLUE = '#3b82f6'
GREEN = '#22c55e'
YELLOW = '#f59e0b'
RED = '#ef4444'
PURPLE = '#a855f7'
CYAN = '#38bdf8'
TEAL = '#10b981'
ORANGE = '#ff9900'
PINK = '#ec4899'
INDIGO = '#6366f1'

PAL = [BLUE, GREEN, YELLOW, RED, PURPLE, CYAN, TEAL, ORANGE, PINK, INDIGO]

CLOUD_COLORS = {
    'AWS': '#ff9900', 'GCP': '#4285f4', 'Azure': '#0078d4',
    'Supabase': '#3ecf8e', 'Vercel': '#e2e8f0', 'Render': '#46e3b7',
    'DigitalOcean': '#0080ff', 'Fly.io': '#7b3fe4', 'Railway': '#0B0D0E',
    'Oracle': '#f80000', 'Heroku': '#6762a6', 'Other': '#666', 'Unknown': '#444',
}

SCORE_COLOR = lambda v: GREEN if v >= 7 else YELLOW if v >= 5 else RED if v else MUTED

# ============================================================
# MATPLOTLIB DEFAULTS
# ============================================================
def apply_theme():
    plt.rcParams.update({
        'figure.facecolor': BG,
        'axes.facecolor': BG2,
        'axes.edgecolor': BORDER,
        'axes.labelcolor': TEXT,
        'text.color': TEXT,
        'xtick.color': MUTED,
        'ytick.color': MUTED,
        'grid.color': '#1e3a5f',
        'grid.alpha': 0.3,
        'font.family': 'monospace',
        'font.size': 11,
        'figure.dpi': 150,
        'savefig.facecolor': BG,
        'savefig.bbox': 'tight',
    })

apply_theme()

# ============================================================
# HTML TEMPLATE
# ============================================================
def html_wrap(title, subtitle, body, charts=None):
    """Wrap module content in a Tailwind-styled HTML page."""
    chart_imgs = ''
    if charts:
        chart_imgs = '\n'.join(
            f'<div class="mt-6"><img src="{c}" class="rounded-lg w-full" alt="{c}"></div>'
            for c in charts
        )

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Delve Tech DD</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {{
  darkMode: 'class',
  theme: {{
    extend: {{
      colors: {{
        bg: '{BG}', bg2: '{BG2}', card: '{CARD}', border: '{BORDER}',
      }}
    }}
  }}
}}
</script>
<style>
body {{ background: {BG}; }}
.prose {{ max-width: none; }}
.prose h1 {{ color: {TEXT}; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem; }}
.prose h2 {{ color: {TEXT}; font-size: 1.5rem; font-weight: 700; margin-top: 2rem; margin-bottom: 0.75rem; border-bottom: 1px solid {BORDER}; padding-bottom: 0.5rem; }}
.prose h3 {{ color: {BLUE}; font-size: 1.1rem; font-weight: 600; margin-top: 1.25rem; margin-bottom: 0.5rem; }}
.prose p {{ color: {TEXT}; line-height: 1.7; margin-bottom: 0.75rem; }}
.prose li {{ color: {TEXT}; line-height: 1.6; }}
.prose strong {{ color: {TEXT}; }}
.prose table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
.prose th {{ text-align: left; padding: 8px 12px; background: {BG2}; color: {MUTED}; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid {BORDER}; }}
.prose td {{ padding: 8px 12px; border-bottom: 1px solid {CARD}; color: {TEXT}; font-size: 14px; }}
.prose tr:hover td {{ background: {CARD}; }}
.metric {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: 20px; }}
.metric .value {{ font-size: 2rem; font-weight: 800; }}
.metric .label {{ color: {MUTED}; font-size: 0.75rem; margin-top: 4px; }}
.insight {{ background: {CARD}; border-left: 3px solid {BLUE}; padding: 16px; border-radius: 0 8px 8px 0; margin: 16px 0; }}
.flag-red {{ background: rgba(239,68,68,0.1); border-left: 3px solid {RED}; padding: 12px; border-radius: 0 8px 8px 0; margin: 8px 0; }}
.flag-yellow {{ background: rgba(245,158,11,0.1); border-left: 3px solid {YELLOW}; padding: 12px; border-radius: 0 8px 8px 0; margin: 8px 0; }}
.flag-green {{ background: rgba(34,197,94,0.1); border-left: 3px solid {GREEN}; padding: 12px; border-radius: 0 8px 8px 0; margin: 8px 0; }}
</style>
</head>
<body class="min-h-screen">
<div class="max-w-5xl mx-auto px-6 py-10">

  <!-- Nav -->
  <div class="mb-4">
    <a href="../index.html" class="text-sm text-blue-400 hover:text-blue-300">← Back to Index</a>
  </div>

  <!-- Header -->
  <div class="mb-8">
    <div class="text-sm text-gray-400 mb-1">Delve Tech Due Diligence · Meta-Analysis</div>
    <h1 class="text-3xl font-extrabold text-white">{title}</h1>
    <p class="text-gray-400 mt-1">{subtitle}</p>
  </div>

  <!-- Content -->
  <div class="prose">
    {body}
    {chart_imgs}
  </div>

  <!-- Footer -->
  <div class="mt-12 pt-6 border-t border-gray-700 text-gray-500 text-sm">
    <p>Generated from {title.lower()} module · 485 SOC 2 compliance reports · 2026-03-24</p>
  </div>

</div>
</body>
</html>"""


def save_module(output_dir, name, html_content):
    """Save HTML file."""
    path = output_dir / f"{name}.html"
    with open(path, 'w') as f:
        f.write(html_content)
    print(f"  {path}")
