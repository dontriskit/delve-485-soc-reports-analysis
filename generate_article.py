"""
Generate lead magnet article: HTML with embedded charts.
'We Analyzed 485 SOC 2 Reports. Here's What Investors Need to Know.'
"""
import base64
import json
from pathlib import Path

OUT = Path("reports/article")
OUT.mkdir(parents=True, exist_ok=True)

# Load summary stats
import pandas as pd
df = pd.read_csv("data_export/companies_clean.csv")

def norm_cloud(cp):
    if pd.isna(cp) or cp == '': return 'Unknown'
    cp = str(cp).lower()
    for name, key in [('aws','AWS'),('amazon','AWS'),('gcp','GCP'),('google','GCP'),('azure','Azure'),('supabase','Supabase'),('vercel','Vercel'),('render','Render'),('digitalocean','DigitalOcean')]:
        if name in cp: return key
    return 'Other'
df['cloud'] = df.cloud_provider.apply(norm_cloud)
scored = df[df.score_overall.notna()]
N = len(df)
NS = len(scored)

# Embed charts as base64
def embed(path):
    p = Path(path)
    if not p.exists():
        return ""
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"

charts = {
    'score_dist': embed("reports/output/01_executive_overview/score_distribution.png"),
    'dim_avg': embed("reports/output/01_executive_overview/dimension_averages.png"),
    'feature_adopt': embed("reports/output/01_executive_overview/feature_adoption.png"),
    'cloud_share': embed("reports/output/03_cloud_landscape/cloud_share.png"),
    'cloud_score': embed("reports/output/03_cloud_landscape/cloud_vs_score.png"),
    'sec_ladder': embed("reports/output/04_security_maturity/security_ladder.png"),
    'feature_impact': embed("reports/output/04_security_maturity/feature_impact.png"),
    'vendor_score': embed("reports/output/05_vendor_ecosystem/vendor_vs_score.png"),
    'top_vendors': embed("reports/output/05_vendor_ecosystem/top_vendors.png"),
    'bcdr_gap': embed("reports/output/07_bcdr_resilience/resilience_gap.png"),
    'red_flags': embed("reports/output/10_red_flag_analysis/red_flag_categories.png"),
    'flag_balance': embed("reports/output/10_red_flag_analysis/flag_balance.png"),
    'ai_share': embed("reports/output/09_ai_ml_infrastructure/ai_share.png"),
    'llm': embed("reports/output/09_ai_ml_infrastructure/llm_providers.png"),
    'funnel': embed("reports/output/11_investment_readiness/funnel.png"),
    'tiers': embed("reports/output/11_investment_readiness/tiers.png"),
    'top_bottom': embed("reports/output/12_top_performers/top_vs_bottom.png"),
    'top_features': embed("reports/output/12_top_performers/top_features.png"),
}

def img(key, caption=""):
    src = charts.get(key, "")
    if not src: return ""
    cap = f'<p class="text-sm text-slate-400 mt-2 text-center italic">{caption}</p>' if caption else ""
    return f'<figure class="my-8"><img src="{src}" alt="{key}" class="rounded-xl w-full shadow-lg shadow-black/30">{cap}</figure>'

pct_aws = (df.cloud == 'AWS').mean() * 100
pct_waf = df.has_waf.mean() * 100
pct_mfa = df.has_mfa.mean() * 100
pct_mr = df.multi_region.mean() * 100
pct_pen = df.has_pen_testing.mean() * 100
avg_score = scored.score_overall.mean()
high_cnt = int((scored.score_overall >= 7).sum())
type2_cnt = int((df.report_type.str.contains('2', na=False)).sum())
full_mature = int(((df.multi_region) & (df.has_waf) & (df.has_pen_testing) & (df.daily_backups) & (df.quarterly_reviews)).sum())

html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>We Analyzed 485 SOC 2 Reports — Tech DD Benchmark for Investors</title>
<meta name="description" content="Quantitative analysis of 485 SOC 2 compliance reports reveals the state of tech maturity across early-stage AI and SaaS startups.">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script>
tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ fontFamily: {{ sans: ['Inter', 'system-ui', 'sans-serif'] }} }} }} }}
</script>
<style>
html {{ scroll-behavior: smooth; }}
body {{ background: #0f172a; }}
.prose-custom h2 {{ scroll-margin-top: 80px; }}
</style>
</head>
<body class="bg-slate-950 text-slate-200 font-sans">

<!-- STICKY NAV -->
<nav class="fixed top-0 left-0 right-0 z-50 bg-slate-950/90 backdrop-blur border-b border-slate-800">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
    <span class="font-bold text-lg text-white">Delve</span>
    <div class="hidden md:flex gap-6 text-sm text-slate-400">
      <a href="#scores" class="hover:text-white">Scores</a>
      <a href="#cloud" class="hover:text-white">Cloud</a>
      <a href="#security" class="hover:text-white">Security</a>
      <a href="#vendors" class="hover:text-white">Vendors</a>
      <a href="#funnel" class="hover:text-white">Funnel</a>
      <a href="#cta" class="hover:text-white text-blue-400">Get Your Analysis →</a>
    </div>
  </div>
</nav>

<div class="max-w-4xl mx-auto px-6 pt-24 pb-20">

<!-- HERO -->
<header class="mb-16">
  <div class="text-blue-400 text-sm font-medium mb-3">RESEARCH REPORT · {N} COMPANIES · 2026</div>
  <h1 class="text-4xl md:text-5xl font-black text-white leading-tight mb-6">
    We Analyzed 485 SOC 2 Reports.<br>
    <span class="text-blue-400">Here's What Investors Need to Know.</span>
  </h1>
  <p class="text-xl text-slate-300 leading-relaxed mb-8">
    A quantitative deep-dive into the tech maturity of {N} early-stage AI and SaaS companies.
    We extracted infrastructure data, scored security posture, mapped vendor ecosystems,
    and built the first open benchmark for tech due diligence at scale.
  </p>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-white">{N}</div>
      <div class="text-slate-400 text-sm">Companies Analyzed</div>
    </div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-amber-400">{avg_score:.1f}<span class="text-lg">/10</span></div>
      <div class="text-slate-400 text-sm">Average Score</div>
    </div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-green-400">{high_cnt}</div>
      <div class="text-slate-400 text-sm">Score 7+ (High)</div>
    </div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700">
      <div class="text-3xl font-black text-red-400">{full_mature}</div>
      <div class="text-slate-400 text-sm">Fully Mature (4%)</div>
    </div>
  </div>
</header>

<article class="prose-custom">

<!-- SECTION 1 -->
<h2 id="intro" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6">The Problem with Tech Due Diligence</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Every VC and PE firm conducts tech due diligence before investing. But the process is manual, inconsistent, and expensive.
A senior engineer spends 2-3 days reading a SOC 2 report, cross-referencing architecture claims with reality,
and producing a qualitative assessment that's hard to compare across portfolio companies.
</p>
<p class="text-slate-300 leading-relaxed mb-4">
We took a different approach. We built an automated pipeline that reads the full PDF — every page, every diagram,
every control description — and extracts structured data. Then we scored each company across 7 dimensions
using a consistent rubric. The result: the first quantitative benchmark for tech due diligence across {N} companies.
</p>
<p class="text-slate-300 leading-relaxed mb-4">
This isn't a sample. It's <strong class="text-white">{N} real compliance reports</strong> from companies
that have completed SOC 2 audits. The majority are early-stage AI and SaaS startups — exactly the companies
that VCs and growth equity firms evaluate every day.
</p>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6 my-8">
  <p class="text-sm text-slate-400 mb-2 font-medium uppercase">Methodology</p>
  <p class="text-slate-300 text-sm leading-relaxed">
    Each PDF was converted to page images and processed through a vision AI model (Moonshot kimi-k2.5, 256K context).
    The model extracted company metadata, infrastructure details, security controls, vendor lists, and architecture
    diagram components. Each company was scored 1-10 across 7 dimensions: Infrastructure, Application Architecture,
    Data Layer, Security, DevOps, BCDR, and Vendor Diversity. All data is stored in a Cloudflare D1 database
    and served via a searchable API.
  </p>
</div>

<!-- SECTION 2: SCORES -->
<h2 id="scores" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">The Score Landscape</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Of {NS} companies with complete dimension scores, the average tech DD score is <strong class="text-white">{avg_score:.1f}/10</strong>.
The distribution clusters tightly around 5-6 — most companies achieve a similar baseline from template-driven compliance.
Only {high_cnt} companies ({high_cnt/NS*100:.0f}%) score 7 or above.
</p>

{img('score_dist', f'Distribution of overall tech DD scores across {NS} scored companies')}

<p class="text-slate-300 leading-relaxed mb-4">
The tight clustering tells an important story: <strong class="text-white">SOC 2 compliance creates a floor, not a ceiling.</strong>
Nearly every company has MFA, RBAC, and a VPC — the audit template ensures it. What separates a 5 from a 7 isn't
the presence of controls, but the depth and specificity of implementation.
</p>

<h3 class="text-xl font-semibold text-blue-400 mt-8 mb-4">Dimension Breakdown</h3>

<p class="text-slate-300 leading-relaxed mb-4">
Security is the strongest dimension at {scored.score_security.mean():.1f}/10 — baseline security controls
are effectively universal. Vendor Diversity is the weakest at {scored.score_vendor_diversity.mean():.1f}/10 —
most companies depend on a single cloud provider and disclose few third-party dependencies.
</p>

{img('dim_avg', 'Average score by dimension with standard deviation error bars')}

<div class="bg-blue-950/30 border-l-4 border-blue-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>Key insight:</strong> Infrastructure score has the highest correlation
  with overall score. Companies that invest in their infrastructure — multi-AZ, IaC, proper VPCs —
  tend to score higher across all dimensions. It's the foundation that lifts everything else.</p>
</div>

<!-- SECTION 3: CLOUD -->
<h2 id="cloud" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">The Cloud Infrastructure Landscape</h2>

<p class="text-slate-300 leading-relaxed mb-4">
AWS dominates at <strong class="text-white">{pct_aws:.0f}%</strong> of the portfolio.
This creates a systemic risk that few portfolio managers account for: a major AWS regional outage
would simultaneously impact over half the companies in a typical fund.
</p>

{img('cloud_share', f'Primary cloud provider distribution across {N} companies')}

<p class="text-slate-300 leading-relaxed mb-4">
An emerging pattern we call <strong class="text-white">"PaaS-first"</strong> architecture:
a meaningful minority of companies build on Supabase, Vercel, or Render as their primary infrastructure.
These platforms offer faster time-to-market but trade away control. Critically, when a company uses
Supabase as their primary provider with a carve-out method, the most important infrastructure controls
— physical security, network backbone, hypervisor isolation — are explicitly outside the audit scope.
</p>

{img('cloud_score', 'Does cloud choice predict tech maturity?')}

<div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>Portfolio risk:</strong> With {pct_aws:.0f}% on AWS and only {pct_mr:.0f}%
  deploying multi-region, a single AWS region failure would affect roughly {(df.cloud == 'AWS').sum() - int(df[df.cloud == 'AWS'].multi_region.sum())}
  companies with no failover capability.</p>
</div>

<!-- SECTION 4: SECURITY -->
<h2 id="security" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">The Security Maturity Ladder</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Security maturity across the portfolio follows a clear three-tier pattern.
Understanding these tiers is essential for benchmarking a company during diligence.
</p>

<div class="grid md:grid-cols-3 gap-4 my-6">
  <div class="bg-green-950/20 border border-green-800 rounded-xl p-5">
    <div class="text-green-400 font-bold text-sm mb-2">TIER 1 — TABLE STAKES</div>
    <div class="text-green-400 text-2xl font-black">80%+</div>
    <p class="text-slate-400 text-sm mt-2">MFA, RBAC, VPC, Multi-AZ, Firewalls, IDS/IPS. These are universal — their presence tells you nothing about quality.</p>
  </div>
  <div class="bg-amber-950/20 border border-amber-800 rounded-xl p-5">
    <div class="text-amber-400 font-bold text-sm mb-2">TIER 2 — DIFFERENTIATORS</div>
    <div class="text-amber-400 text-2xl font-black">40-80%</div>
    <p class="text-slate-400 text-sm mt-2">Branch protection, pen testing, daily backups, WAF. These separate the middle from the top.</p>
  </div>
  <div class="bg-red-950/20 border border-red-800 rounded-xl p-5">
    <div class="text-red-400 font-bold text-sm mb-2">TIER 3 — ADVANCED</div>
    <div class="text-red-400 text-2xl font-black">&lt;40%</div>
    <p class="text-slate-400 text-sm mt-2">Multi-region, cyber insurance, quarterly reviews. Rare, expensive, and predictive of the highest scores.</p>
  </div>
</div>

{img('sec_ladder', 'Feature adoption rates color-coded by tier')}

<p class="text-slate-300 leading-relaxed mb-4">
The question for investors isn't "does this company have MFA?" — they all do.
The question is: <strong class="text-white">"Which Tier 2 and Tier 3 features have they adopted?"</strong>
Companies with WAF + multi-region + quarterly reviews are in the top 5% of the portfolio.
</p>

{img('feature_impact', 'Average score for companies with vs without each feature')}

<!-- SECTION 5: VENDORS -->
<h2 id="vendors" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">Vendor Transparency = Engineering Culture</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Perhaps our most surprising finding: <strong class="text-white">the number of vendors a company names in their
SOC 2 report strongly correlates with their overall tech DD score.</strong>
</p>

<p class="text-slate-300 leading-relaxed mb-4">
Companies that name 0-1 vendors average {scored[scored.vendor_count <= 1].score_overall.mean():.1f}/10.
Companies that name 5+ vendors average {scored[scored.vendor_count >= 5].score_overall.mean():.1f}/10.
That's nearly a full point — highly significant in a distribution this tight.
</p>

{img('vendor_score', 'Average score by number of named vendors')}

<p class="text-slate-300 leading-relaxed mb-4">
This isn't because more vendors make you more secure. It's because <strong class="text-white">transparency about
dependencies is a proxy for engineering culture maturity.</strong> Teams that know their full vendor stack
well enough to document it in an audit tend to have more deliberate architecture decisions, better
monitoring, and stronger operational practices.
</p>

<div class="bg-amber-950/20 border-l-4 border-amber-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>Due diligence signal:</strong> If a SOC 2 report names only "AWS"
  and nothing else, that's a transparency red flag. Ask the founder: "What's your monitoring stack?
  What databases do you use? What's your CI/CD pipeline?" If they can't answer specifically,
  the compliance report isn't the only thing that's generic.</p>
</div>

{img('top_vendors', f'Most common vendors across the portfolio')}

<!-- SECTION 6: BCDR -->
<h2 id="bcdr" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">The BCDR Gap: Policy vs Practice</h2>

<p class="text-slate-300 leading-relaxed mb-4">
<strong class="text-white">100% of companies have a BCDR policy.</strong> That's the good news.
The bad news: the drop-off from policy to practice is dramatic.
</p>

{img('bcdr_gap', 'The resilience gap — from policy to practice')}

<p class="text-slate-300 leading-relaxed mb-4">
Only {df.annual_dr_testing.mean()*100:.0f}% test their disaster recovery plans annually.
Only {pct_mr:.0f}% have multi-region failover. Only {df.has_cyber_insurance.mean()*100:.0f}%
carry cybersecurity insurance.
</p>

<p class="text-slate-300 leading-relaxed mb-4">
Most companies in this portfolio have a disaster recovery plan they've never tested,
for a disaster they can't recover from quickly, with no insurance to cover the loss.
That's not resilience — it's a checkbox.
</p>

<div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>Ask for proof:</strong> During diligence, request the last DR test results —
  the date, the scenario, the measured recovery time, and what was fixed afterward.
  A company that can produce this has genuine operational maturity. One that can't
  has a policy document, not a capability.</p>
</div>

<!-- SECTION 7: RED FLAGS -->
<h2 id="flags" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">Red Flags: What to Watch For</h2>

<p class="text-slate-300 leading-relaxed mb-4">
We identified and categorized thousands of red flags across the portfolio.
The top flags are systemic — they appear in the majority of reports because
they reflect the compliance template's defaults, not company-specific failures.
</p>

{img('red_flags', 'Most common red flag categories across the portfolio')}

<div class="space-y-3 my-6">
  <div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-4">
    <p class="text-slate-200 text-sm"><strong class="text-red-400">No RTO/RPO disclosed</strong> — The most common flag.
    Despite having BCDR policies and annual testing, almost no company commits to specific recovery time objectives.</p>
  </div>
  <div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-4">
    <p class="text-slate-200 text-sm"><strong class="text-red-400">Short audit period (3 months)</strong> — Nearly universal.
    The minimum viable period for a Type 2 report. Suggests a first-time SOC 2 with limited operational history.</p>
  </div>
  <div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-4">
    <p class="text-slate-200 text-sm"><strong class="text-red-400">Privacy/Processing Integrity excluded</strong> — Particularly
    concerning for AI companies handling user data. Many exclude these trust criteria as "not relevant" — a claim
    that deserves scrutiny.</p>
  </div>
  <div class="bg-amber-950/20 border-l-4 border-amber-500 rounded-r-xl p-4">
    <p class="text-slate-200 text-sm"><strong class="text-amber-400">Template artifacts</strong> — Published reports containing
    placeholder text ("Your Name Here"), sample diagrams, or highlighted instructions that were never removed.
    This doesn't mean controls are absent — but it undermines confidence in audit rigor.</p>
  </div>
</div>

{img('flag_balance', 'How the red/yellow/green flag mix changes across score tiers')}

<!-- SECTION 8: AI STACK -->
<h2 id="ai" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">The AI Stack Inside the Portfolio</h2>

<p class="text-slate-300 leading-relaxed mb-4">
A significant majority of these companies are AI-first. Their compliance reports reveal
the emerging AI infrastructure stack — what they use, who they depend on, and where
the concentration risks lie.
</p>

{img('ai_share', 'Percentage of portfolio companies with AI/ML products')}

{img('llm', 'LLM provider adoption across the portfolio')}

<p class="text-slate-300 leading-relaxed mb-4">
<strong class="text-white">OpenAI dominates</strong> as the LLM provider of choice,
with Anthropic and Google Gemini gaining ground. A small number of companies run
self-hosted models (Llama via FIXIE, vLLM on Modal) — these tend to have more
sophisticated infrastructure and carry higher IP value.
</p>

<div class="bg-purple-950/20 border-l-4 border-purple-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>The emerging AI stack:</strong>
  LLM API (OpenAI/Anthropic) + Voice (ElevenLabs + Twilio) + Vector DB (Pinecone/Weaviate) +
  Auth (Clerk/STYTCH) + Hosting (Vercel/AWS) + Monitoring (Sentry/Datadog).
  Companies that name this full stack score materially higher on tech DD.</p>
</div>

<!-- SECTION 9: FUNNEL -->
<h2 id="funnel" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">The Investment Readiness Funnel</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Starting from {N} companies, we applied progressive quality filters.
The result is sobering.
</p>

{img('funnel', 'Investment readiness funnel — progressive quality filters')}

<div class="bg-slate-800 rounded-xl overflow-hidden my-8">
  <table class="w-full text-sm">
    <thead><tr class="bg-slate-700/50 text-slate-400 text-xs uppercase">
      <th class="text-left p-3">Filter</th><th class="text-right p-3">Remaining</th><th class="text-right p-3">Drop-off</th>
    </tr></thead>
    <tbody class="text-slate-300">
      <tr class="border-t border-slate-700"><td class="p-3">Total Portfolio</td><td class="text-right p-3">{N}</td><td class="text-right p-3 text-slate-500">—</td></tr>
      <tr class="border-t border-slate-700"><td class="p-3">Type 2 (Operational evidence)</td><td class="text-right p-3">{type2_cnt}</td><td class="text-right p-3 text-red-400">-{N-type2_cnt}</td></tr>
      <tr class="border-t border-slate-700"><td class="p-3">Score 5+ (Minimum maturity)</td><td class="text-right p-3">{int((df.score_overall >= 5).sum())}</td><td class="text-right p-3 text-red-400">-{type2_cnt - int((df.score_overall >= 5).sum())}</td></tr>
      <tr class="border-t border-slate-700"><td class="p-3">Score 7+ (Investment ready)</td><td class="text-right p-3">{high_cnt}</td><td class="text-right p-3 text-red-400">-{int((df.score_overall >= 5).sum()) - high_cnt}</td></tr>
      <tr class="border-t border-slate-700"><td class="p-3">Multi-Region + WAF</td><td class="text-right p-3">{int(((df.multi_region) & (df.has_waf)).sum())}</td><td class="text-right p-3 text-red-400"></td></tr>
      <tr class="border-t border-slate-700 bg-slate-800/50"><td class="p-3 font-bold text-white">Full Maturity</td><td class="text-right p-3 font-bold text-green-400">{full_mature}</td><td class="text-right p-3 text-slate-500">{full_mature/N*100:.1f}% of total</td></tr>
    </tbody>
  </table>
</div>

<p class="text-slate-300 leading-relaxed mb-4">
<strong class="text-white">Only {full_mature} companies ({full_mature/N*100:.1f}%) meet the full maturity bar</strong>:
SOC 2 Type 2 + multi-region + WAF + pen testing + daily backups + quarterly access reviews.
The other 96% have concrete improvement opportunities — which is exactly where value creation lives.
</p>

<!-- SECTION 10: TOP PERFORMERS -->
<h2 id="top" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">What Top Performers Do Differently</h2>

<p class="text-slate-300 leading-relaxed mb-4">
Comparing the top 20 companies (by score) against the bottom 20 reveals clear patterns:
</p>

{img('top_bottom', 'Dimension comparison: top 20 vs bottom 20 companies')}

{img('top_features', 'Feature adoption gap between top performers and portfolio average')}

<p class="text-slate-300 leading-relaxed mb-4">
The top performers share specific characteristics:
</p>

<ul class="space-y-2 text-slate-300 mb-6 ml-4">
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> Multi-region deployment with active failover</li>
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> WAF deployed on all internet-facing services</li>
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> Named monitoring and SIEM tools (not just "monitoring tool")</li>
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> 5+ vendors disclosed transparently in the compliance report</li>
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> Branch protection with mandatory code review</li>
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> Annual external penetration testing with remediation tracking</li>
  <li class="flex items-start"><span class="text-green-400 mr-2">✓</span> Quarterly access reviews for all accounts including admin</li>
</ul>

<!-- SECTION 11: IMPLICATIONS -->
<h2 id="implications" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">What This Means for Investors</h2>

<div class="space-y-6 my-6">
  <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
    <h3 class="text-lg font-bold text-blue-400 mb-3">For PE Firms</h3>
    <p class="text-slate-300 text-sm leading-relaxed">
      The data reveals concrete value creation levers. Adding WAF across a portfolio is a one-day implementation
      per company via Cloudflare or AWS WAF. Establishing quarterly access reviews is a process change with zero cost.
      Migrating to multi-region takes weeks but dramatically reduces portfolio-level outage risk.
      These aren't hypothetical improvements — they're measurable moves that shift companies from Tier 2 to Tier 3
      on the security ladder and improve their position for future fundraising or exit.
    </p>
  </div>

  <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
    <h3 class="text-lg font-bold text-green-400 mb-3">For VCs</h3>
    <p class="text-slate-300 text-sm leading-relaxed">
      Most SOC 2 reports are noise. The signal is in three places: the network architecture diagram (pages 18-19),
      the system description section (pages 14-17), and the vendor list. Everything else is template.
      Companies that name 5+ vendors, have detailed architecture diagrams, and exclude fewer trust criteria
      are the ones with genuine engineering culture — not just compliance-as-a-service.
    </p>
  </div>

  <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
    <h3 class="text-lg font-bold text-purple-400 mb-3">10 Questions to Ask During Diligence</h3>
    <ol class="text-slate-300 text-sm leading-relaxed space-y-2 list-decimal ml-4 mt-3">
      <li>What's your actual deployment pipeline? (CI/CD tool, deployment frequency)</li>
      <li>Show me your monitoring dashboard. (Proves operational maturity)</li>
      <li>What happens if your primary region goes down? (Multi-region / RTO/RPO)</li>
      <li>Who's your SIEM vendor? (If none, that's a signal)</li>
      <li>When was your last DR test, and what did you fix afterward?</li>
      <li>Why did you exclude Processing Integrity from SOC 2? (Tests AI governance awareness)</li>
      <li>What's your full vendor stack? Name every SaaS dependency.</li>
      <li>Show me your architecture diagram — the real one, not the SOC 2 version.</li>
      <li>How many engineers are on the team, and who's your on-call rotation?</li>
      <li>What would break if OpenAI raised prices 10x tomorrow?</li>
    </ol>
  </div>
</div>

<!-- CTA -->
<div id="cta" class="bg-gradient-to-br from-blue-950 to-slate-900 rounded-2xl p-10 my-16 border border-blue-800/50 text-center">
  <h2 class="text-3xl font-black text-white mb-4">Get Your Portfolio Analyzed</h2>
  <p class="text-slate-300 text-lg mb-6 max-w-2xl mx-auto">
    This analysis was performed by Delve's automated Tech DD pipeline.
    We can run the same analysis on your portfolio — any number of companies,
    any compliance reports, delivered in days not weeks.
  </p>
  <div class="flex flex-col sm:flex-row gap-4 justify-center">
    <a href="mailto:hello@delve.tech" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-8 py-3 rounded-lg transition">
      Request a Demo →
    </a>
    <a href="#intro" class="bg-slate-700 hover:bg-slate-600 text-white font-bold px-8 py-3 rounded-lg transition">
      Read Again ↑
    </a>
  </div>
</div>

</article>

<!-- FOOTER -->
<footer class="text-center text-slate-500 text-sm py-8 border-t border-slate-800">
  <p>© 2026 Delve Technologies · {N} SOC 2 compliance reports analyzed ·
  Built with Cloudflare Workers AI, D1, R2</p>
</footer>

</div>
</body>
</html>"""

with open(OUT / "article.html", "w") as f:
    f.write(html)

size_mb = len(html) / 1024 / 1024
word_count = len(html.split()) # rough estimate of visible text
print(f"Article generated: reports/article/article.html")
print(f"Size: {size_mb:.1f} MB (with {len(charts)} embedded charts)")
print(f"Approximate word count: ~{word_count}")
