"""Run all report modules and generate index."""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib

def _load(module_name, class_name):
    mod = importlib.import_module(f"reports.modules.{module_name}")
    return getattr(mod, class_name)

ALL_MODULES = [
    _load("01_executive_overview", "ExecutiveOverview"),
    _load("02_score_deep_dive", "ScoreDeepDive"),
    _load("03_cloud_landscape", "CloudLandscape"),
    _load("04_security_maturity", "SecurityMaturity"),
    _load("05_vendor_ecosystem", "VendorEcosystem"),
    _load("06_architecture_patterns", "ArchitecturePatterns"),
    _load("07_bcdr_resilience", "BCDRResilience"),
    _load("08_compliance_quality", "ComplianceQuality"),
    _load("09_ai_ml_infrastructure", "AIMLInfrastructure"),
    _load("10_red_flag_analysis", "RedFlagAnalysis"),
    _load("11_investment_readiness", "InvestmentReadiness"),
    _load("12_top_performers", "TopPerformers"),
    _load("13_funding_signals", "FundingSignals"),
]


def main():
    start = time.time()
    print(f"=== Running {len(ALL_MODULES)} Report Modules ===\n")

    for cls in ALL_MODULES:
        print(f"\n{'='*50}")
        print(f"  {cls.slug}: {cls.title}")
        print(f"{'='*50}")
        mod = cls()
        mod.run()

    # Generate index
    generate_index()

    elapsed = time.time() - start
    print(f"\n=== All done in {elapsed:.1f}s ===")
    print(f"Open: reports/output/index.html")


def generate_index():
    """Build the index.html navigator."""
    from reports.modules import theme

    output = Path("reports/output")
    output.mkdir(exist_ok=True)

    cards = ""
    for cls in ALL_MODULES:
        # Find first chart for thumbnail
        mod_dir = output / cls.slug
        charts = list(mod_dir.glob("*.png")) if mod_dir.exists() else []
        thumb = f'{cls.slug}/{charts[0].name}' if charts else ''
        thumb_img = f'<img src="{thumb}" class="w-full h-40 object-cover rounded-t-lg">' if thumb else '<div class="w-full h-40 bg-gray-800 rounded-t-lg flex items-center justify-center text-gray-500">No preview</div>'

        cards += f"""
<a href="{cls.slug}/{cls.slug}.html" class="block bg-gray-800 border border-gray-700 rounded-lg hover:border-blue-500 transition-colors overflow-hidden">
  {thumb_img}
  <div class="p-4">
    <h3 class="text-white font-semibold text-lg">{cls.title}</h3>
    <p class="text-gray-400 text-sm mt-1">{cls.subtitle}</p>
  </div>
</a>"""

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Delve — Tech DD Meta-Analysis</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body {{ background: {theme.BG}; }}</style>
</head>
<body class="min-h-screen text-gray-200">
<div class="max-w-6xl mx-auto px-6 py-12">
  <div class="text-center mb-12">
    <h1 class="text-4xl font-extrabold text-white mb-2">Tech Due Diligence</h1>
    <h2 class="text-xl text-gray-400">Meta-Analysis of 485 SOC 2 Compliance Reports</h2>
    <p class="text-gray-500 mt-4 max-w-2xl mx-auto">
      Quantitative analysis of security maturity, cloud infrastructure, vendor ecosystems,
      and investment readiness across a portfolio of early-stage technology companies.
    </p>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {cards}
  </div>

  <div class="mt-12 pt-6 border-t border-gray-700 text-center text-gray-500 text-sm">
    <p>Generated from 485 SOC 2 compliance reports · Delve Tech DD Pipeline · 2026-03-24</p>
  </div>
</div>
</body>
</html>"""

    with open(output / "index.html", "w") as f:
        f.write(html)
    print(f"\n  Index: reports/output/index.html")


if __name__ == "__main__":
    main()
