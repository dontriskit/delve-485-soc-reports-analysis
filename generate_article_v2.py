"""
Generate reframed article v2:
"What 500 SOC 2 Reports Reveal About the Technology Foundations of VC-Backed Companies"

Key reframe: SOC 2 ≠ Tech DD. SOC 2 shows operational discipline and security hygiene.
It does NOT show: code quality, SDLC, scalability, team capability, delivery track record.
"""
import base64
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path("reports/article_v2")
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv("data_export/companies_clean.csv")
def norm_cloud(cp):
    if pd.isna(cp) or cp == '': return 'Unknown'
    for name, key in [('aws','AWS'),('amazon','AWS'),('gcp','GCP'),('google','GCP'),('azure','Azure'),('supabase','Supabase'),('vercel','Vercel'),('render','Render'),('digitalocean','DigitalOcean')]:
        if name in str(cp).lower(): return key
    return 'Other'
df['cloud'] = df.cloud_provider.apply(norm_cloud)
scored = df[df.score_overall.notna()]
N = len(df)
NS = len(scored)
with open("data_export/funding_research.json") as f:
    funding = json.load(f)

BG = '#0f172a'
BG2 = '#1e293b'
TEXT = '#e2e8f0'
MUTED = '#94a3b8'
BORDER = '#334155'
GREEN = '#22c55e'
YELLOW = '#f59e0b'
RED = '#ef4444'
BLUE = '#3b82f6'
PURPLE = '#a855f7'

plt.rcParams.update({
    'figure.facecolor': BG, 'axes.facecolor': BG2, 'axes.edgecolor': BORDER,
    'axes.labelcolor': TEXT, 'text.color': TEXT, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'grid.color': '#1e3a5f', 'grid.alpha': 0.3, 'font.family': 'monospace', 'font.size': 11, 'figure.dpi': 150,
})

def save_chart(fig, name):
    path = OUT / f"{name}.png"
    fig.savefig(path, bbox_inches='tight', facecolor=BG, dpi=150)
    plt.close(fig)
    return path

# ============================================================
# NEW CHART 1: What SOC 2 Reveals vs Hides
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# What SOC 2 REVEALS (strong signal)
reveals = {
    'MFA Enforced': 99.4, 'Role-Based Access': 99.0, 'VPC Isolation': 96.9,
    'Multi-AZ Deploy': 88.0, 'Firewalls': 87.8, 'IDS/IPS': 87.4,
    'Vuln Scanning': 87.6, 'Server Hardening': 87.6, 'BCDR Policy': 100.0,
}
ax = axes[0]
r = dict(sorted(reveals.items(), key=lambda x: x[1]))
ax.barh(list(r.keys()), list(r.values()), color=GREEN, height=0.65, alpha=0.8)
for i, v in enumerate(r.values()):
    ax.text(v + 1, i, f'{v:.0f}%', va='center', fontsize=10)
ax.set_xlim(0, 115)
ax.set_title('What SOC 2 REVEALS', fontsize=14, fontweight='bold', color=GREEN)

# What SOC 2 HIDES (weak/no signal)
hides = {
    'Code Quality': 0, 'SDLC Process': 0, 'Team Capability': 0,
    'Deployment Frequency': 0, 'Scalability': 0, 'Tech Debt': 0,
    'AI/ML Practices': 0, 'Cost Efficiency': 0, 'Delivery Track Record': 0,
}
ax = axes[1]
h = list(hides.keys())
ax.barh(h, [100]*len(h), color='#7f1d1d', height=0.65, alpha=0.4)
for i, label in enumerate(h):
    ax.text(50, i, 'NOT MEASURED', ha='center', va='center', fontsize=9, fontweight='bold', color=RED)
ax.set_xlim(0, 115)
ax.set_title('What SOC 2 HIDES', fontsize=14, fontweight='bold', color=RED)
ax.set_xticks([])

plt.suptitle('SOC 2 Coverage: Operational Discipline ≠ Tech Maturity', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
save_chart(fig, 'reveals_vs_hides')

# ============================================================
# NEW CHART 2: The Cyber Insurance Paradox
# ============================================================
fig, ax = plt.subplots(figsize=(8, 5))
insured = df.has_cyber_insurance.sum()
not_insured = N - insured
ax.pie([insured, not_insured],
       labels=[f'Have Cyber Insurance\n({insured}, {insured/N*100:.0f}%)',
               f'No Cyber Insurance\n({not_insured}, {not_insured/N*100:.0f}%)'],
       colors=[GREEN, RED], autopct='', startangle=90,
       textprops={'color': TEXT, 'fontsize': 12})
ax.set_title('The Cyber Insurance Paradox\n78% pass SOC 2 without insuring against breach', fontsize=13, fontweight='bold')
save_chart(fig, 'cyber_insurance_paradox')

# ============================================================
# NEW CHART 3: The Compliance-to-Maturity Gap
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5))
stages = [
    ('SOC 2 Compliant\n(passed audit)', 100),
    ('Multi-AZ\n(cloud default)', 88),
    ('Branch Protection\n(code review)', 69),
    ('Pen Testing\n(annual external)', 63),
    ('Daily Backups\n(data protection)', 54),
    ('WAF\n(app firewall)', 44),
    ('Quarterly Reviews\n(access audit)', 43),
    ('Multi-Region\n(geographic DR)', 28),
    ('Cyber Insurance\n(risk transfer)', 22),
]
labels = [s[0] for s in stages]
vals = [s[1] for s in stages]
colors = [GREEN if v >= 80 else YELLOW if v >= 50 else RED for v in vals]
bars = ax.bar(range(len(stages)), vals, color=colors, width=0.7)
ax.set_xticks(range(len(stages)))
ax.set_xticklabels(labels, fontsize=8, rotation=30, ha='right')
for i, v in enumerate(vals):
    ax.text(i, v + 2, f'{v}%', ha='center', fontsize=10, fontweight='bold')
    if i > 0:
        drop = vals[i-1] - v
        if drop > 5:
            ax.annotate(f'↓{drop}%', xy=(i-0.3, (vals[i-1]+v)/2),
                       fontsize=8, color=RED, alpha=0.7)
ax.set_ylabel('% of Companies')
ax.set_title('From Compliance to Maturity — The Drop-Off', fontsize=16, fontweight='bold')
ax.set_ylim(0, 115)
save_chart(fig, 'compliance_to_maturity')

print("New charts generated")

# ============================================================
# EMBED CHARTS
# ============================================================
def embed(path):
    p = Path(path)
    if not p.exists(): return ""
    with open(p, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

charts = {
    'reveals_hides': embed(OUT / 'reveals_vs_hides.png'),
    'cyber_insurance': embed(OUT / 'cyber_insurance_paradox.png'),
    'compliance_maturity': embed(OUT / 'compliance_to_maturity.png'),
    'sec_ladder': embed("reports/output/04_security_maturity/security_ladder.png"),
    'feature_impact': embed("reports/output/04_security_maturity/feature_impact.png"),
    'bcdr_gap': embed("reports/output/07_bcdr_resilience/resilience_gap.png"),
    'cloud_share': embed("reports/output/03_cloud_landscape/cloud_share.png"),
    'pattern_dist': embed("reports/output/06_architecture_patterns/pattern_dist.png"),
    'type_comparison': embed("reports/output/08_compliance_quality/type_comparison.png"),
    'funding_score': embed("reports/output/13_funding_signals/funding_vs_score.png"),
    'red_flags': embed("reports/output/10_red_flag_analysis/red_flag_categories.png"),
    'vendor_score': embed("reports/output/05_vendor_ecosystem/vendor_vs_score.png"),
}

def img(key, caption=""):
    src = charts.get(key, "")
    if not src: return ""
    cap = f'<p class="text-sm text-slate-400 mt-2 text-center italic">{caption}</p>' if caption else ""
    return f'<figure class="my-8"><img src="{src}" alt="{key}" class="rounded-xl w-full shadow-lg shadow-black/30">{cap}</figure>'

pct_aws = (df.cloud == 'AWS').mean() * 100
pct_mfa = df.has_mfa.mean() * 100
pct_waf = df.has_waf.mean() * 100
pct_mr = df.multi_region.mean() * 100
pct_pen = df.has_pen_testing.mean() * 100
pct_ci = df.has_cyber_insurance.mean() * 100
pct_qr = df.quarterly_reviews.mean() * 100
pct_bp = df.branch_protection.mean() * 100
type2_cnt = int(df.report_type.str.contains('2', na=False).sum())

# ============================================================
# BUILD HTML
# ============================================================
html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>What 500 SOC 2 Reports Reveal About VC-Backed Companies</title>
<meta name="description" content="An analysis of 500 funded startups: what SOC 2 compliance actually tells investors about security, operations, and discipline — and what it doesn't.">
<meta property="og:title" content="What 500 SOC 2 Reports Reveal About VC-Backed Companies">
<meta property="og:description" content="SOC 2 shows discipline, not maturity. We analyzed 500 reports to separate security signals from actual operational maturity.">
<meta name="author" content="Jacek Podoba, Maksym Huczyński">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script>tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ fontFamily: {{ sans: ['Inter', 'system-ui', 'sans-serif'] }} }} }} }}</script>
<style>html {{ scroll-behavior: smooth; }} body {{ background: #0f172a; }}</style>
</head>
<body class="bg-slate-950 text-slate-200 font-sans">

<nav class="fixed top-0 left-0 right-0 z-50 bg-slate-950/90 backdrop-blur border-b border-slate-800">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
    <span class="font-bold text-lg text-white">Altimi × WhiteContext</span>
    <div class="hidden md:flex gap-5 text-sm text-slate-400">
      <a href="#security" class="hover:text-white">Security</a>
      <a href="#availability" class="hover:text-white">Availability</a>
      <a href="#infrastructure" class="hover:text-white">Infrastructure</a>
      <a href="#process" class="hover:text-white">Process</a>
      <a href="#gap" class="hover:text-white">The Gap</a>
      <a href="#investors" class="hover:text-white">For Investors</a>
    </div>
  </div>
</nav>

<div class="max-w-4xl mx-auto px-6 pt-24 pb-20">

<!-- HERO -->
<header class="mb-16">
  <div class="text-blue-400 text-sm font-medium mb-3">RESEARCH · {N} COMPANIES · $291M+ IN TRACKED FUNDING</div>
  <h1 class="text-4xl md:text-5xl font-black text-white leading-tight mb-6">
    What 500 SOC 2 Reports Reveal About the Technology Foundations of VC-Backed Companies
  </h1>
  <p class="text-xl text-slate-300 leading-relaxed mb-4">
    <strong class="text-white">SOC 2 is not a measure of tech maturity.</strong> It's a signal of operational
    discipline in a narrow domain — controls and security. We analyzed {N} SOC 2 compliance reports from
    VC-backed companies (a16z, Benchmark, Kleiner Perkins, Lightspeed, Y Combinator) to understand exactly
    what these reports reveal about security posture and operational discipline — and where they fall completely silent.
  </p>
  <p class="text-lg text-slate-400 leading-relaxed mb-6">
    A proper Tech Due Diligence is still absolutely required. But SOC 2 reports, read correctly,
    contain valuable signals about whether a company has moved past the chaotic startup phase into
    structured operations. Here's what we found.
  </p>

  <div class="flex flex-wrap items-center gap-6 mt-6 mb-8">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">JP</div>
      <div>
        <div class="text-white font-semibold">Jacek Podoba</div>
        <div class="text-slate-400 text-sm">CEO, <a href="https://altimi.com" class="text-blue-400">Altimi.com</a></div>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">MH</div>
      <div>
        <div class="text-white font-semibold">Maksym Huczyński</div>
        <div class="text-slate-400 text-sm">CTO, <a href="https://whitecontext.com" class="text-blue-400">WhiteContext.com</a></div>
      </div>
    </div>
    <div class="text-slate-500 text-sm">March 2026</div>
  </div>

  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-white">{N}</div>
      <div class="text-slate-400 text-sm">SOC 2 Reports Analyzed</div>
    </div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-purple-400">$291M+</div>
      <div class="text-slate-400 text-sm">Tracked Funding</div>
    </div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-green-400">{pct_mfa:.0f}%</div>
      <div class="text-slate-400 text-sm">Have MFA (hygiene)</div>
    </div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-red-400">{pct_ci:.0f}%</div>
      <div class="text-slate-400 text-sm">Have Cyber Insurance</div>
    </div>
  </div>
</header>

<article>

<!-- SECTION 1: EXECUTIVE SUMMARY -->
<h2 id="summary" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6">1. Signals vs Reality</h2>

<div class="bg-amber-950/20 border-l-4 border-amber-500 rounded-r-xl p-6 my-6">
  <p class="text-lg text-slate-200 font-semibold mb-2">The core finding:</p>
  <p class="text-slate-300">SOC 2 compliance validates how a company <em>operates</em>, not what it has <em>built</em>.
  It tells you whether they wash their hands — not whether they can cook.
  For investors, it's a signal of organizational discipline, not engineering capability.</p>
</div>

<p class="text-slate-300 leading-relaxed mb-4">
After analyzing {N} SOC 2 reports from funded startups, five core insights emerged:
</p>

<ol class="space-y-4 mb-6">
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
    <span class="text-white font-semibold">1. Security hygiene is near-universal.</span>
    <span class="text-slate-400"> {pct_mfa:.0f}% have MFA, 99% have RBAC, 97% use VPCs. This is the floor, not the ceiling.</span>
  </li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
    <span class="text-white font-semibold">2. Policy exceeds practice by a wide margin.</span>
    <span class="text-slate-400"> 100% have BCDR policies, but only 51% test them. 88% have multi-AZ (cloud default), but only {pct_mr:.0f}% chose multi-region.</span>
  </li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
    <span class="text-white font-semibold">3. Template-driven compliance is the norm.</span>
    <span class="text-slate-400"> 70%+ of control descriptions are identical boilerplate. The unique signal lives in architecture diagrams and vendor lists — nowhere else.</span>
  </li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
    <span class="text-white font-semibold">4. Funding does not predict operational maturity.</span>
    <span class="text-slate-400"> A company that raised $75M has the same SOC 2 profile as one that raised $500K. Money buys speed, not discipline.</span>
  </li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
    <span class="text-white font-semibold">5. SOC 2 is completely silent on what matters most for Tech DD.</span>
    <span class="text-slate-400"> Code quality, SDLC process, team capability, deployment frequency, scalability, tech debt, AI practices — zero signal.</span>
  </li>
</ol>

{img('reveals_hides', 'SOC 2 covers security controls and operational policy. It does not measure engineering capability.')}

<!-- SECTION 2: SECURITY CONTROLS -->
<h2 id="security" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">2. Security Controls — Strong Signals, Limited Depth</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Security is where SOC 2 reports provide the most reliable signal. The data is clear: VC-backed companies
overwhelmingly adopt baseline security controls.
</p>

<h3 class="text-lg font-semibold text-blue-400 mt-6 mb-3">What you can expect in VC-backed companies:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• <strong class="text-white">MFA everywhere</strong> — {pct_mfa:.0f}% enforce multi-factor authentication on admin access, source code, and email</li>
  <li>• <strong class="text-white">Role-based access</strong> — 99% implement RBAC with defined permission boundaries</li>
  <li>• <strong class="text-white">Network isolation</strong> — 97% use VPCs with segmented subnets and ACLs</li>
  <li>• <strong class="text-white">Formalized policies</strong> — often template-driven, but the documentation exists</li>
</ul>

{img('sec_ladder', 'Security feature adoption across {0} companies, color-coded by maturity tier'.format(N))}

<h3 class="text-lg font-semibold text-red-400 mt-6 mb-3">What this likely hides:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• <strong class="text-white">Weak multi-tenant isolation</strong> — SOC 2 confirms per-tenant segregation exists (53%) but not how it's implemented</li>
  <li>• <strong class="text-white">Over-permissioning in practice</strong> — quarterly access reviews happen at only {pct_qr:.0f}%, meaning 57% may have stale permissions</li>
  <li>• <strong class="text-white">Gaps between policy and enforcement</strong> — WAF adoption is only {pct_waf:.0f}% despite internet-facing services</li>
</ul>

<div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>The Cyber Insurance Paradox:</strong> {100-pct_ci:.0f}% of these companies pass SOC 2
  without purchasing cybersecurity insurance. If they truly trusted their security controls to prevent breach,
  insurance would be cheap and obvious. Its absence suggests that passing SOC 2 is not the same as
  feeling secure.</p>
</div>

{img('cyber_insurance', '')}

<!-- SECTION 3: AVAILABILITY & RELIABILITY -->
<h2 id="availability" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">3. Availability & Reliability — Process Over Engineering</h2>

<p class="text-slate-300 leading-relaxed mb-4">
SOC 2 provides a window into backup procedures, monitoring claims, and disaster recovery commitments.
The picture that emerges: processes exist on paper, but resilience engineering is thin.
</p>

<h3 class="text-lg font-semibold text-blue-400 mt-6 mb-3">What to expect:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• <strong class="text-white">Backups exist</strong> — 54% do daily backups, virtually all have some backup policy</li>
  <li>• <strong class="text-white">Multi-AZ is the default</strong> — 88% deploy across multiple availability zones (this is a cloud provider default, not an architectural choice)</li>
  <li>• <strong class="text-white">Incident response is defined on paper</strong> — 100% have a BCDR policy</li>
</ul>

<h3 class="text-lg font-semibold text-red-400 mt-6 mb-3">What this likely hides:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• <strong class="text-white">Fragile architecture under scale</strong> — multi-AZ is a checkbox, multi-region is a choice. Only {pct_mr:.0f}% make that choice.</li>
  <li>• <strong class="text-white">Manual recovery processes</strong> — ~85% don't state RTO/RPO targets. They have a plan but no measurable recovery commitment.</li>
  <li>• <strong class="text-white">Limited resilience testing</strong> — only 51% test DR plans annually. The other 49% have a plan they've never rehearsed.</li>
</ul>

{img('compliance_maturity', 'The drop-off from compliance to operational maturity')}

<div class="bg-blue-950/30 border-l-4 border-blue-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>Key insight:</strong> The 60-point gap between multi-AZ (88%) and multi-region ({pct_mr:.0f}%)
  is the clearest illustration of compliance vs. maturity. Multi-AZ is what the cloud gives you by default.
  Multi-region is what you build by choice. SOC 2 counts both as "available."</p>
</div>

{img('bcdr_gap', 'The resilience gap from policy to practice')}

<!-- SECTION 4: INFRASTRUCTURE & OPERATIONS -->
<h2 id="infrastructure" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">4. Infrastructure & Operations — Indirect Signals Only</h2>

<p class="text-slate-300 leading-relaxed mb-4">
SOC 2 reports provide indirect clues about infrastructure, but they are <strong class="text-white">never sufficient
for a technical assessment.</strong> The signal is thin and heavily filtered through compliance boilerplate.
</p>

<h3 class="text-lg font-semibold text-blue-400 mt-6 mb-3">What you can infer:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• <strong class="text-white">Some CI/CD exists</strong> — {pct_bp:.0f}% have branch protection, implying merge-based deployment</li>
  <li>• <strong class="text-white">Environment separation</strong> — most companies mention dev/staging/prod separation</li>
  <li>• <strong class="text-white">Cloud provider choice</strong> — AWS ({pct_aws:.0f}%), GCP, Azure, or PaaS platforms (Supabase, Vercel)</li>
  <li>• <strong class="text-white">Architecture diagrams</strong> — the ONLY genuine technical signal in most reports, showing actual services and data flows</li>
</ul>

{img('cloud_share', 'AWS dominates at {0:.0f}%, creating portfolio-level concentration risk'.format(pct_aws))}

<h3 class="text-lg font-semibold text-red-400 mt-6 mb-3">What remains completely unclear:</h3>

<div class="grid md:grid-cols-2 gap-4 my-6">
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30">
    <h4 class="text-red-400 font-semibold mb-2">Scalability</h4>
    <p class="text-slate-400 text-sm">Can this architecture handle 10x traffic? SOC 2 doesn't test load, latency, or auto-scaling behavior.</p>
  </div>
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30">
    <h4 class="text-red-400 font-semibold mb-2">Cost Efficiency</h4>
    <p class="text-slate-400 text-sm">Is infrastructure spending appropriate for the stage? No financial or resource efficiency data exists in SOC 2.</p>
  </div>
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30">
    <h4 class="text-red-400 font-semibold mb-2">Technical Debt</h4>
    <p class="text-slate-400 text-sm">How much legacy code or architectural shortcuts exist? SOC 2 evaluates controls, not code quality.</p>
  </div>
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30">
    <h4 class="text-red-400 font-semibold mb-2">Cloud Architecture Quality</h4>
    <p class="text-slate-400 text-sm">Is the architecture well-designed or spaghetti? The compliance report can't distinguish a monolith on a single VM from a well-orchestrated microservices platform.</p>
  </div>
</div>

<p class="text-slate-300 leading-relaxed mb-4">
The template boilerplate problem is severe: 70%+ of control descriptions across different companies are
word-for-word identical. When every company has "firewalls configured on the application gateway and production
network to limit unnecessary ports, protocols and services," the control description becomes noise.
The signal lives in the architecture diagram and the vendor list — the parts the auditor didn't write.
</p>

<!-- SECTION 5: PROCESS & ORGANIZATIONAL DISCIPLINE -->
<h2 id="process" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">5. Process & Organizational Discipline — The Strongest Signal</h2>

<p class="text-slate-300 leading-relaxed mb-4">
This is where SOC 2 actually shines. If there's one thing a compliance report genuinely measures,
it's whether a company has <strong class="text-white">repeatable, documented processes</strong> for managing access,
handling incidents, and governing change.
</p>

<h3 class="text-lg font-semibold text-green-400 mt-6 mb-3">What to expect:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• <strong class="text-white">Defined ownership structures</strong> — org charts, named CTO/CISO, governance committees</li>
  <li>• <strong class="text-white">Repeatable processes</strong> — change management, access provisioning, incident response</li>
  <li>• <strong class="text-white">Audit trails</strong> — logging of admin activities, access changes, security events</li>
  <li>• <strong class="text-white">Access revocation SLA</strong> — most companies commit to 1-business-day termination revocation</li>
</ul>

{img('type_comparison', 'Type 2 reports (operational evidence over time) provide stronger signals than Type 1 (design only)')}

<h3 class="text-lg font-semibold text-blue-400 mt-6 mb-3">What this suggests:</h3>
<ul class="text-slate-300 space-y-2 ml-4 mb-4">
  <li>• The company is <strong class="text-white">past the "chaotic startup phase"</strong> — they've formalized how work gets done</li>
  <li>• Some <strong class="text-white">operational maturity</strong> is present — the ability to pass an audit implies process discipline</li>
  <li>• Type 2 reports ({type2_cnt} of {N} companies) provide evidence that controls <em>operated effectively</em> over time, not just that they were designed</li>
</ul>

<div class="bg-green-950/20 border-l-4 border-green-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>The strongest investor signal in SOC 2:</strong> A company with a Type 2 report,
  quarterly access reviews, annual penetration testing, and a vendor management program has demonstrated
  that it can execute structured processes. That's the organizational capability that SOC 2 validates —
  not the technology itself, but the <em>discipline to operate technology systematically.</em></p>
</div>

<!-- SECTION 6: THE MATURITY GAP -->
<h2 id="gap" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">6. The Maturity Gap — Where SOC 2 Misleads</h2>

<p class="text-slate-300 leading-relaxed mb-4">
SOC 2 can create false confidence when investors treat it as a proxy for technical quality.
Three archetypes emerge from our data:
</p>

<div class="space-y-4 my-6">
  <div class="bg-red-950/20 border border-red-800/30 rounded-xl p-5">
    <h4 class="text-red-400 font-semibold mb-2">"Compliant but Fragile"</h4>
    <p class="text-slate-300 text-sm">Clean SOC 2 opinion, zero exceptions — but the report contains template placeholders,
    sample diagrams, and "Your Name Here" in the signing authority. The audit passed because the controls
    are designed correctly on paper. Whether they're enforced in practice is unknowable from the report alone.
    ~15% of our dataset fits this profile.</p>
  </div>
  <div class="bg-amber-950/20 border border-amber-800/30 rounded-xl p-5">
    <h4 class="text-amber-400 font-semibold mb-2">"Process-Heavy but Slow"</h4>
    <p class="text-slate-300 text-sm">Comprehensive processes, multiple governance committees, detailed change management.
    But the 3-month audit window, 4 untestable controls (no incidents occurred), and generic tool descriptions
    suggest a young company that layered compliance onto a small team. The processes may be creating overhead
    rather than value. SOC 2 can't distinguish efficient processes from bureaucratic ones.</p>
  </div>
  <div class="bg-blue-950/20 border border-blue-800/30 rounded-xl p-5">
    <h4 class="text-blue-400 font-semibold mb-2">"Genuinely Mature"</h4>
    <p class="text-slate-300 text-sm">Detailed architecture diagrams naming specific services, 5+ vendors disclosed transparently,
    multi-region deployment, named monitoring tools, and a 6-12 month audit window. These reports read like
    technical documentation, not compliance templates. Only ~15% of the portfolio reaches this level.</p>
  </div>
</div>

<h3 class="text-lg font-semibold text-white mt-8 mb-3">Funding ≠ Maturity</h3>

<p class="text-slate-300 leading-relaxed mb-4">
Our funding research across 27 top companies confirms: <strong class="text-white">there is no meaningful correlation
between funding raised and SOC 2 quality.</strong> A company at $75M+ with a $350M valuation (backed by a16z
and Benchmark) produces a SOC 2 report indistinguishable from a $500K seed-stage startup.
</p>

{img('funding_score', 'Funding vs operational maturity — no correlation')}

<div class="bg-slate-800 rounded-xl p-6 border border-slate-700 my-6">
  <p class="text-slate-200"><strong>Key statement:</strong> <em>SOC 2 validates how you operate, not what you've built.</em>
  A company can have impeccable access controls, tested DR plans, and quarterly security reviews —
  and still have a fragile monolith running on a single VM with no automated tests.
  The compliance report would give them a clean opinion in both cases.</p>
</div>

{img('red_flags', 'Most common red flags — note how many are about disclosure gaps, not control failures')}

<!-- SECTION 7: WHAT INVESTORS SHOULD INFER -->
<h2 id="investors" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">7. What Investors Should Infer — and What They Should Ignore</h2>

<div class="grid md:grid-cols-3 gap-4 my-6">
  <div class="bg-green-950/20 border border-green-800 rounded-xl p-5">
    <h4 class="text-green-400 font-semibold text-sm mb-3 uppercase">✓ Signals to Trust</h4>
    <ul class="text-slate-300 text-sm space-y-2">
      <li>• Basic security hygiene (MFA, RBAC, encryption)</li>
      <li>• Organizational discipline (defined processes, audit trails)</li>
      <li>• Enterprise-readiness (the company can produce compliance artifacts)</li>
      <li>• Vendor management maturity (if vendors are named and managed)</li>
      <li>• Past the chaos phase (formalized operations exist)</li>
    </ul>
  </div>
  <div class="bg-red-950/20 border border-red-800 rounded-xl p-5">
    <h4 class="text-red-400 font-semibold text-sm mb-3 uppercase">✗ Signals to Discount</h4>
    <ul class="text-slate-300 text-sm space-y-2">
      <li>• Architecture quality or scalability</li>
      <li>• Codebase health or technical debt</li>
      <li>• Engineering team capability</li>
      <li>• Deployment frequency or delivery speed</li>
      <li>• AI/ML practices or data governance</li>
      <li>• Product-market fit or revenue trajectory</li>
    </ul>
  </div>
  <div class="bg-purple-950/20 border border-purple-800 rounded-xl p-5">
    <h4 class="text-purple-400 font-semibold text-sm mb-3 uppercase">→ Where to Go Deeper</h4>
    <ul class="text-slate-300 text-sm space-y-2">
      <li>• System design & architecture review</li>
      <li>• Data model & database design</li>
      <li>• Team capability assessment (SDLC)</li>
      <li>• Delivery track record (deploy frequency, DORA)</li>
      <li>• AI practices & model governance</li>
      <li>• Cost structure & unit economics</li>
    </ul>
  </div>
</div>

<h3 class="text-lg font-semibold text-white mt-8 mb-3">10 Questions for Real Tech DD (Beyond SOC 2)</h3>

<div class="bg-slate-800 rounded-xl p-6 border border-slate-700 my-6">
  <ol class="text-slate-300 space-y-3 list-decimal ml-4">
    <li><strong class="text-white">Walk me through your deployment pipeline.</strong> <span class="text-slate-400">How code goes from commit to production — tools, steps, time.</span></li>
    <li><strong class="text-white">Show me your monitoring dashboard.</strong> <span class="text-slate-400">What do you see when something breaks? How quickly do you know?</span></li>
    <li><strong class="text-white">What's your test coverage and testing strategy?</strong> <span class="text-slate-400">Unit, integration, E2E — what exists and what's missing?</span></li>
    <li><strong class="text-white">Describe your last production incident.</strong> <span class="text-slate-400">What happened, how long to detect, how long to resolve, what changed?</span></li>
    <li><strong class="text-white">What happens at 10x your current traffic?</strong> <span class="text-slate-400">Where does the architecture break? What's the plan?</span></li>
    <li><strong class="text-white">Show me the architecture — the real one, not the SOC 2 version.</strong> <span class="text-slate-400">Services, databases, queues, external APIs, data flows.</span></li>
    <li><strong class="text-white">How does your team do code review?</strong> <span class="text-slate-400">Process, turnaround time, who reviews what, quality bar.</span></li>
    <li><strong class="text-white">What's your relationship with AI in development?</strong> <span class="text-slate-400">Code generation, testing, operations — how and where?</span></li>
    <li><strong class="text-white">What would you rebuild if you started today?</strong> <span class="text-slate-400">This reveals tech debt awareness and architectural honesty.</span></li>
    <li><strong class="text-white">What's your biggest technical risk right now?</strong> <span class="text-slate-400">The answer reveals self-awareness more than the risk itself.</span></li>
  </ol>
</div>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6 my-6">
  <p class="text-slate-300 leading-relaxed">
    <strong class="text-white">Bottom line:</strong> SOC 2 compliance is a necessary signal of hygiene,
    not a sufficient signal of tech quality. It tells you a company can operate with discipline.
    It does not tell you whether what they built is any good. For that, you need a proper Tech Due Diligence —
    one that evaluates system design, team capability, delivery track record, and engineering culture.
    SOC 2 is the starting line, not the finish.
  </p>
</div>

<!-- RESOURCES -->
<div class="grid md:grid-cols-3 gap-4 my-12">
  <a href="modules/" class="block bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition">
    <div class="text-2xl mb-2">📊</div>
    <h3 class="text-white font-bold mb-1">Deep Dive Modules</h3>
    <p class="text-slate-400 text-sm">13 detailed analysis modules with charts — security, vendors, BCDR, AI stack, funding signals.</p>
  </a>
  <a href="diagrams/" class="block bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition">
    <div class="text-2xl mb-2">🏗️</div>
    <h3 class="text-white font-bold mb-1">Architecture Gallery</h3>
    <p class="text-slate-400 text-sm">479 infrastructure diagrams — the one genuine technical signal in SOC 2 reports.</p>
  </a>
  <a href="https://delve-vision-extract.whitecontext.workers.dev/" class="block bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition">
    <div class="text-2xl mb-2">🔍</div>
    <h3 class="text-white font-bold mb-1">Searchable Database</h3>
    <p class="text-slate-400 text-sm">Search {N} companies by technology, vendor, cloud. Full extraction data.</p>
  </a>
</div>

<!-- CTA -->
<div class="bg-gradient-to-br from-blue-950 to-slate-900 rounded-2xl p-10 my-12 border border-blue-800/50 text-center">
  <h2 class="text-3xl font-black text-white mb-4">SOC 2 is the Starting Line.<br>Real Tech DD is the Race.</h2>
  <p class="text-slate-300 text-lg mb-6 max-w-2xl mx-auto">
    This analysis shows what compliance reports can tell you. For the full picture —
    system design, team capability, delivery track record, AI practices —
    you need a proper technical due diligence.
  </p>
  <div class="flex flex-col sm:flex-row gap-4 justify-center">
    <a href="mailto:hello@altimi.com" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-8 py-3 rounded-lg transition">
      Talk to Altimi →
    </a>
    <a href="https://whitecontext.com" class="bg-slate-700 hover:bg-slate-600 text-white font-bold px-8 py-3 rounded-lg transition">
      Talk to WhiteContext →
    </a>
  </div>
</div>

</article>

<footer class="text-center text-slate-500 text-sm py-8 border-t border-slate-800">
  <p>© 2026 <a href="https://altimi.com" class="text-blue-400">Altimi</a> ×
  <a href="https://whitecontext.com" class="text-blue-400">WhiteContext</a> ·
  {N} SOC 2 reports analyzed · By Jacek Podoba &amp; Maksym Huczyński</p>
</footer>

</div>
</body>
</html>"""

with open(OUT / "article.html", "w") as f:
    f.write(html)

import re
text_parts = re.findall(r'>([^<]+)<', html)
visible_text = ' '.join(t.strip() for t in text_parts if t.strip() and 'data:image' not in t)
visible_text = re.sub(r'[A-Za-z0-9+/=]{{100,}}', '', visible_text)
words = [w for w in visible_text.split() if len(w) > 0]
print(f"Article v2: {len(words)} words, {len(html)/1024/1024:.1f} MB, {html.count('<h2')} sections")
print(f"Output: {OUT / 'article.html'}")
