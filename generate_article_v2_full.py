"""
Generate article v2 (4000+ words):
"What 500 SOC 2 Reports Reveal About the Technology Foundations of VC-Backed Companies"

Reframed: SOC 2 ≠ Tech DD. SOC 2 shows operational discipline, not tech maturity.
"""
import base64, json, re
import pandas as pd
from pathlib import Path

OUT = Path("reports/article_v2")

# Load data
df = pd.read_csv("data_export/companies_clean.csv")
def nc(cp):
    if pd.isna(cp) or cp=='': return 'Unknown'
    for n,k in [('aws','AWS'),('amazon','AWS'),('gcp','GCP'),('google','GCP'),('azure','Azure'),('supabase','Supabase'),('vercel','Vercel'),('render','Render'),('digitalocean','DigitalOcean')]:
        if n in str(cp).lower(): return k
    return 'Other'
df['cloud'] = df.cloud_provider.apply(nc)
N = len(df)

def embed(path):
    p = Path(path)
    if not p.exists(): return ""
    with open(p,"rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

def img(src, cap=""):
    if not src: return ""
    c = f'<p class="text-sm text-slate-400 mt-2 text-center italic">{cap}</p>' if cap else ""
    return f'<figure class="my-8"><img src="{src}" alt="" class="rounded-xl w-full shadow-lg shadow-black/30">{c}</figure>'

ch = {
    'reveals_hides': embed(OUT/'reveals_vs_hides.png'),
    'cyber_ins': embed(OUT/'cyber_insurance_paradox.png'),
    'comp_mat': embed(OUT/'compliance_to_maturity.png'),
    'sec_ladder': embed("reports/output/04_security_maturity/security_ladder.png"),
    'feat_impact': embed("reports/output/04_security_maturity/feature_impact.png"),
    'bcdr_gap': embed("reports/output/07_bcdr_resilience/resilience_gap.png"),
    'cloud': embed("reports/output/03_cloud_landscape/cloud_share.png"),
    'patterns': embed("reports/output/06_architecture_patterns/pattern_dist.png"),
    'types': embed("reports/output/08_compliance_quality/type_comparison.png"),
    'funding': embed("reports/output/13_funding_signals/funding_vs_score.png"),
    'redflags': embed("reports/output/10_red_flag_analysis/red_flag_categories.png"),
    'vendors': embed("reports/output/05_vendor_ecosystem/vendor_vs_score.png"),
}

# Build the article body as sections
body = ""

# ============================================================
# HERO
# ============================================================
body += f"""
<header class="mb-16">
  <div class="text-blue-400 text-sm font-medium mb-3">RESEARCH · {N} COMPANIES · $291M+ IN TRACKED FUNDING</div>
  <h1 class="text-4xl md:text-5xl font-black text-white leading-tight mb-6">What 500 SOC 2 Reports Reveal About the Technology Foundations of VC-Backed Companies</h1>
  <p class="text-xl text-slate-300 leading-relaxed mb-4"><strong class="text-white">SOC 2 is not a measure of tech maturity.</strong> It's a signal of operational discipline in a narrow domain — controls and security. We analyzed {N} SOC 2 compliance reports from VC-backed companies to understand exactly what these reports reveal about security posture and operational discipline — and where they fall completely silent.</p>
  <p class="text-lg text-slate-400 leading-relaxed mb-6">Companies backed by Andreessen Horowitz, Benchmark, Kleiner Perkins, Lightspeed, and Y Combinator. Total tracked funding: $291M+. The finding that shaped this entire analysis: <em>a proper Tech Due Diligence is still absolutely required.</em> SOC 2 is the starting line, not the finish.</p>

  <div class="flex flex-wrap items-center gap-6 mt-6 mb-8">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">JP</div>
      <div><div class="text-white font-semibold">Jacek Podoba</div><div class="text-slate-400 text-sm">CEO, <a href="https://altimi.com" class="text-blue-400">Altimi.com</a></div></div>
    </div>
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">MH</div>
      <div><div class="text-white font-semibold">Maksym Huczyński</div><div class="text-slate-400 text-sm">CTO, <a href="https://whitecontext.com" class="text-blue-400">WhiteContext.com</a></div></div>
    </div>
    <div class="text-slate-500 text-sm">March 2026</div>
  </div>

  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700"><div class="text-3xl font-black text-white">{N}</div><div class="text-slate-400 text-sm">SOC 2 Reports</div></div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700"><div class="text-3xl font-black text-purple-400">$291M+</div><div class="text-slate-400 text-sm">Tracked Funding</div></div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700"><div class="text-3xl font-black text-green-400">99%</div><div class="text-slate-400 text-sm">Have MFA</div></div>
    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700"><div class="text-3xl font-black text-red-400">22%</div><div class="text-slate-400 text-sm">Have Cyber Insurance</div></div>
  </div>
</header>
"""

# ============================================================
# SECTION 1: EXECUTIVE SUMMARY
# ============================================================
body += f"""
<h2 id="summary" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6">1. Executive Summary — Signals vs Reality</h2>

<div class="bg-amber-950/20 border-l-4 border-amber-500 rounded-r-xl p-6 my-6">
  <p class="text-lg text-slate-200 font-semibold mb-2">The core finding:</p>
  <p class="text-slate-300">SOC 2 compliance validates how a company <em>operates</em>, not what it has <em>built</em>. It tells you whether they wash their hands — not whether they can cook. For investors, it's a signal of organizational discipline, not engineering capability.</p>
</div>

<p class="text-slate-300 leading-relaxed mb-4">SOC 2 (System and Organization Controls 2) is a compliance framework developed by the AICPA that evaluates how a company manages data security, availability, processing integrity, confidentiality, and privacy. It's become table stakes for B2B SaaS companies selling to enterprises — procurement teams require it, and compliance automation platforms like Vanta, Drata, and Secureframe have made achieving it faster than ever.</p>

<p class="text-slate-300 leading-relaxed mb-4">But speed of compliance is not depth of capability. When a company achieves SOC 2 in 8 weeks using an automation platform and a template-driven auditor, the resulting report tells you about their <em>control design</em> — not their <em>engineering quality</em>. The overlap between SOC 2 and a real Tech Due Diligence is roughly 10%: some security controls, some infrastructure indicators, and some process documentation. The other 90% — codebase quality, SDLC maturity, team capability, scalability, technical debt, AI practices — is completely absent from every report we analyzed.</p>

<p class="text-slate-300 leading-relaxed mb-4">After processing all {N} reports through a vision AI pipeline (every page of every PDF, including architecture diagrams), five core insights emerged:</p>

<ol class="space-y-4 mb-6">
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700"><span class="text-white font-semibold">1. Security hygiene is near-universal — and therefore uninformative.</span><span class="text-slate-400"> 99% have MFA, 99% have RBAC, 97% use VPCs. These are the floor, not the ceiling. A company <em>without</em> MFA would be the signal — its presence tells you nothing.</span></li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700"><span class="text-white font-semibold">2. Policy exceeds practice by a dramatic margin.</span><span class="text-slate-400"> 100% have BCDR policies, but only 51% test them annually. 88% have multi-AZ (a cloud provider default), but only 28% chose multi-region (an architectural decision). The gap between what's documented and what's implemented is the real story.</span></li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700"><span class="text-white font-semibold">3. Template-driven compliance is the dominant pattern.</span><span class="text-slate-400"> A single auditor (Accorp Partners) appears across the vast majority of reports, using identical boilerplate. 70%+ of control descriptions are word-for-word the same across different companies. The unique signal lives in architecture diagrams and vendor lists — the parts the auditor didn't write.</span></li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700"><span class="text-white font-semibold">4. Funding does not predict operational maturity.</span><span class="text-slate-400"> A company that raised $75M from a16z and Benchmark produces a SOC 2 report indistinguishable from a $500K seed-stage startup. Money buys market access and headcount — not process discipline.</span></li>
  <li class="bg-slate-800/50 rounded-lg p-4 border border-slate-700"><span class="text-white font-semibold">5. SOC 2 is completely silent on what matters most for Tech DD.</span><span class="text-slate-400"> Code quality, SDLC process, team capability, deployment frequency, scalability analysis, technical debt assessment, AI/ML practices — zero signal in any report we analyzed.</span></li>
</ol>

{img(ch['reveals_hides'], 'SOC 2 covers operational controls (left). It is completely silent on engineering capability (right).')}
"""

# ============================================================
# SECTION 2: SECURITY CONTROLS
# ============================================================
body += f"""
<h2 id="security" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">2. Security Controls — Strong Signals, Limited Depth</h2>

<p class="text-slate-300 leading-relaxed mb-4">Security is where SOC 2 reports provide their most reliable signal. The framework was designed to evaluate security controls, and the data confirms that VC-backed companies overwhelmingly adopt baseline protections. If you're evaluating a funded startup's <em>security stance</em>, the SOC 2 report has genuine value.</p>

<p class="text-slate-300 leading-relaxed mb-4">But "security controls exist" and "security is robust" are different claims. SOC 2 confirms the first. It cannot confirm the second.</p>

<h3 class="text-lg font-semibold text-green-400 mt-6 mb-3">What you can expect in VC-backed companies:</h3>
<p class="text-slate-300 leading-relaxed mb-4">Generally good hygiene. 99.4% enforce MFA on administrative access — this is effectively universal. 99% implement role-based access control. 97% use network isolation via VPCs. 88% deploy firewalls and IDS/IPS systems. 88% perform vulnerability scanning. These numbers are so high that their presence is uninformative — a company <em>without</em> MFA would be the actual signal worth noting.</p>
<p class="text-slate-300 leading-relaxed mb-4">Formalized security policies exist across the board, though they are often template-driven. The same compliance automation platforms that help companies achieve SOC 2 quickly also generate standardized policy documents. The policy exists; whether it reflects the company's actual security posture is a separate question that the audit format doesn't always answer.</p>

{img(ch['sec_ladder'], 'Security feature adoption rates across {0} companies. Green = near-universal (80%+), Yellow = differentiator (40-80%), Red = rare (<40%).'.format(N))}

<h3 class="text-lg font-semibold text-red-400 mt-6 mb-3">What this likely hides:</h3>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Weak multi-tenant isolation in practice.</strong> SOC 2 confirms that per-tenant data segregation exists in 53% of companies. But it doesn't test the implementation — whether database-level row isolation, schema-level separation, or application-level filtering. For a SaaS company where data leakage between tenants is existential, the SOC 2 assurance is paper-thin.</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Over-permissioning between reviews.</strong> Only 43% conduct quarterly access reviews. For the remaining 57%, user permissions set during onboarding may persist unchanged for months or years — through role changes, project rotations, and scope creep. SOC 2 confirms the review process exists; it doesn't confirm that permissions are appropriate at any given moment.</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Gaps between policy and real enforcement.</strong> WAF adoption sits at just 44% — meaning 56% of internet-facing SaaS applications lack a web application firewall. For API-first products handling sensitive data, this is a material gap that the SOC 2 report doesn't flag as a deficiency because WAF isn't a required control.</p>

<div class="bg-red-950/20 border-l-4 border-red-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>The Cyber Insurance Paradox:</strong> 78% of these companies pass SOC 2 without purchasing cybersecurity insurance. This is revealing: if management genuinely believed their security controls were sufficient to prevent breach, cyber insurance would be cheap and an obvious purchase. Its widespread absence suggests that passing SOC 2 is not the same as feeling secure — or that the insurance market sees risks that the audit doesn't measure.</p>
</div>

{img(ch['cyber_ins'], '78% of SOC 2-compliant companies do not insure against the risks SOC 2 is supposed to address.')}
"""

# ============================================================
# SECTION 3: AVAILABILITY
# ============================================================
body += f"""
<h2 id="availability" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">3. Availability & Reliability — Process Over Engineering</h2>

<p class="text-slate-300 leading-relaxed mb-4">SOC 2 reports provide a window into how companies think about uptime, backup, and disaster recovery. The Availability trust criteria — when included in scope — evaluates whether the company has procedures to maintain system availability commitments. What we found is a consistent pattern: <strong class="text-white">processes are defined on paper, but resilience engineering is thin.</strong></p>

<h3 class="text-lg font-semibold text-green-400 mt-6 mb-3">What to expect:</h3>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Backups exist.</strong> 54% perform daily backups; virtually all have some backup policy. This is table stakes for any SaaS company. <strong class="text-white">Multi-AZ deployment is the default.</strong> 88% deploy across multiple availability zones — but this is a cloud provider default in AWS, GCP, and Azure, not an architectural choice. Selecting "multi-AZ" during RDS setup takes one click. <strong class="text-white">Incident response is defined.</strong> 100% have a BCDR (Business Continuity and Disaster Recovery) policy documented. Many include communication plans, role assignments, and escalation procedures.</p>

<h3 class="text-lg font-semibold text-red-400 mt-6 mb-3">What this likely hides:</h3>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Fragile architecture under scale.</strong> The 60-point gap between multi-AZ (88%) and multi-region (28%) is the clearest illustration of compliance vs. maturity. Multi-AZ is what the cloud gives you automatically. Multi-region is what you build intentionally — it requires cross-region data replication, routing decisions, and tested failover procedures. SOC 2 counts both as "available" with no distinction.</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Manual recovery processes.</strong> Approximately 85% of companies don't state specific RTO (Recovery Time Objective) or RPO (Recovery Point Objective) targets anywhere in their SOC 2 report. They have a disaster recovery plan but no measurable commitment for how quickly they can recover or how much data they can afford to lose. This is the difference between "we have a plan" and "we've committed to recovering in 4 hours with less than 1 hour of data loss."</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Limited real resilience testing.</strong> Only 51% test their DR plans annually. The other 49% have a disaster recovery plan they've never rehearsed — for a disaster they can't recover from quickly, with no insurance to cover the loss.</p>

{img(ch['comp_mat'], 'The compliance-to-maturity drop-off: from 100% policy to 22% insurance.')}

<div class="bg-blue-950/30 border-l-4 border-blue-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>Key insight:</strong> When an investor reads "multi-AZ deployment" in a SOC 2 report, they should mentally translate that to "used the cloud provider's default settings." When they read "multi-region deployment," they should understand that as "made a deliberate, expensive architectural decision to build geographic redundancy." The SOC 2 report doesn't distinguish between a $20/month checkbox and a $20,000/month infrastructure decision.</p>
</div>

{img(ch['bcdr_gap'], 'The resilience gap from BCDR policy (100%) to actual multi-region deployment (28%).')}
"""

# ============================================================
# SECTION 4: INFRASTRUCTURE
# ============================================================
body += f"""
<h2 id="infrastructure" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">4. Infrastructure & Operations — Indirect Signals Only</h2>

<p class="text-slate-300 leading-relaxed mb-4">This is where SOC 2 reports begin to fail as a source of technical insight. Infrastructure is mentioned — cloud providers are named, network diagrams are included, change management processes are described — but the information is <strong class="text-white">never sufficient for a genuine technical assessment.</strong> The signal is indirect, heavily filtered through compliance boilerplate, and often misleading in its apparent specificity.</p>

<h3 class="text-lg font-semibold text-green-400 mt-6 mb-3">What you can infer:</h3>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Some CI/CD pipeline exists.</strong> 69% of companies have branch protection configured — meaning code changes require approval before merging to production. This implies a merge-based deployment model and at least rudimentary code review. But SOC 2 doesn't tell you which CI/CD tool, how fast deployments happen, what percentage of deployments succeed, or how rollbacks work.</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Production/non-production separation is present.</strong> Most companies describe separate environments for development, staging, and production. SOC 2 auditors verify that these environments exist and that production deployments follow a defined process. But they don't assess whether the environments are equivalent (many staging environments bear no resemblance to production).</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Architecture diagrams are the one genuine signal.</strong> In our analysis, the network/architecture diagrams included in SOC 2 reports (typically pages 18-19) are the most valuable technical artifacts. They name specific services, show data flows, reveal vendor dependencies, and — critically — are the one part of the report that the compliance template can't auto-generate. When a diagram shows AWS ECS Fargate clusters with Aurora Serverless, ElastiCache Redis, and Lambda functions in VPC, that's real architectural signal. When it's a sample placeholder that was never replaced, that's signal too — just a different kind.</p>

{img(ch['cloud'], 'AWS dominates at 59%, creating portfolio-level concentration risk.')}

<h3 class="text-lg font-semibold text-red-400 mt-6 mb-3">What remains completely unclear:</h3>

<div class="grid md:grid-cols-2 gap-4 my-6">
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30"><h4 class="text-red-400 font-semibold mb-2">Scalability</h4><p class="text-slate-400 text-sm">Can this architecture handle 10x traffic? SOC 2 doesn't test load, measure latency, or evaluate auto-scaling. A single EC2 instance and a fully orchestrated Kubernetes cluster both pass.</p></div>
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30"><h4 class="text-red-400 font-semibold mb-2">Cost Efficiency</h4><p class="text-slate-400 text-sm">Is infrastructure spending appropriate? Is the company over-provisioned or running on fumes? No financial data exists in SOC 2.</p></div>
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30"><h4 class="text-red-400 font-semibold mb-2">Technical Debt</h4><p class="text-slate-400 text-sm">How much legacy code, architectural shortcuts, or unmaintained dependencies exist? SOC 2 evaluates operational controls, not codebase health.</p></div>
  <div class="bg-slate-800 rounded-xl p-5 border border-red-800/30"><h4 class="text-red-400 font-semibold mb-2">Cloud Architecture Quality</h4><p class="text-slate-400 text-sm">Is this a well-designed system or spaghetti? The compliance report can't distinguish a monolith on a single VM from a well-orchestrated microservices platform. Both can pass SOC 2 with identical control descriptions.</p></div>
</div>

<p class="text-slate-300 leading-relaxed mb-4">The template boilerplate problem deserves emphasis: when 70%+ of control descriptions across different companies use the exact same language — "system firewalls are configured on the application gateway and production network to limit unnecessary ports, protocols and services" — the control description becomes noise. The auditor is confirming a template was filled in, not that the firewall configuration is appropriate, tested, or maintained.</p>
"""

# ============================================================
# SECTION 5: PROCESS
# ============================================================
body += f"""
<h2 id="process" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">5. Process & Organizational Discipline — The Strongest Signal</h2>

<p class="text-slate-300 leading-relaxed mb-4">If there's one domain where SOC 2 genuinely earns its keep, it's here. The framework excels at evaluating whether a company has <strong class="text-white">repeatable, documented processes</strong> for managing access, handling incidents, governing changes, and overseeing vendors. This is valuable signal — not about technology, but about organizational maturity.</p>

<h3 class="text-lg font-semibold text-green-400 mt-6 mb-3">What to expect:</h3>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Defined ownership structures.</strong> Companies that achieve SOC 2 have org charts with named roles (CTO, CISO or equivalent), governance committees, and documented responsibility assignments. This doesn't mean the structure is effective, but its existence is a prerequisite for organizational scaling.</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Repeatable processes.</strong> Change management, access provisioning, incident response, and vendor evaluation all follow documented procedures. The audit verifies that these procedures exist and — in Type 2 reports — that they operated consistently over the audit period.</p>
<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">Audit trails.</strong> Logging of administrative activities, access changes, and security events is confirmed. This is foundational for accountability and incident investigation.</p>

{img(ch['types'], 'Type 2 reports provide operational evidence over time; Type 1 evaluates design only.')}

<h3 class="text-lg font-semibold text-blue-400 mt-6 mb-3">What this suggests about the company:</h3>
<p class="text-slate-300 leading-relaxed mb-4">A company with a SOC 2 Type 2 report, quarterly access reviews, annual penetration testing, and a vendor management program has demonstrated something real: <strong class="text-white">it can execute structured processes consistently over time.</strong> That's the organizational capability that SOC 2 validates. It doesn't tell you the technology is good — but it tells you the <em>organization</em> can operate with discipline. For an investor, this is the signal that the company has moved past the chaotic startup phase into something more repeatable.</p>

<div class="bg-green-950/20 border-l-4 border-green-500 rounded-r-xl p-5 my-6">
  <p class="text-slate-200"><strong>The honest statement:</strong> SOC 2 compliance is best understood as enterprise-readiness certification. It tells prospective customers: "We can operate your data responsibly, and we can prove it to an auditor." For investors, the corresponding signal is: "This company can execute structured processes" — which is a necessary but not sufficient condition for building great technology.</p>
</div>

<p class="text-slate-300 leading-relaxed mb-4"><strong class="text-white">What SOC 2 does NOT tell you about process:</strong> Execution speed. Engineering productivity. Sprint velocity. Feature delivery cadence. Bug resolution time. Code review turnaround. Deployment frequency. These are the SDLC (Software Development Lifecycle) metrics that actually predict engineering effectiveness — and they're entirely absent from every SOC 2 report we analyzed. A company can have perfect change management processes that take 3 weeks to ship a one-line fix. SOC 2 would report this as "controls operating effectively."</p>
"""

# ============================================================
# SECTION 6: THE GAP
# ============================================================
body += f"""
<h2 id="gap" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">6. The Maturity Gap — Where SOC 2 Misleads</h2>

<p class="text-slate-300 leading-relaxed mb-4">SOC 2 can create false confidence when investors — or procurement teams — treat it as a proxy for overall technical quality. Three archetypes emerge from our analysis of {N} reports, and understanding them is essential for calibrating how much weight to give a SOC 2 opinion.</p>

<div class="space-y-4 my-6">
  <div class="bg-red-950/20 border border-red-800/30 rounded-xl p-5">
    <h4 class="text-red-400 font-semibold mb-2">"Compliant but Fragile" (~15% of portfolio)</h4>
    <p class="text-slate-300 text-sm leading-relaxed">Clean SOC 2 opinion, zero exceptions — but the report contains template placeholders, sample diagrams that were never replaced, "Your Name Here" in the signing authority, and highlighted template instructions visible in the published PDF. The company used a compliance automation tool to generate a SOC 2 report in weeks, and the auditor confirmed the controls are "suitably designed." Whether those controls exist beyond the documentation is unknowable from the report alone. These companies passed the audit because the template was filled in correctly — not because the controls were validated in depth.</p>
  </div>
  <div class="bg-amber-950/20 border border-amber-800/30 rounded-xl p-5">
    <h4 class="text-amber-400 font-semibold mb-2">"Process-Heavy but Slow" (~70% of portfolio)</h4>
    <p class="text-slate-300 text-sm leading-relaxed">The largest archetype. These companies have real processes — change management, access reviews, incident response — but the 3-month audit window, generic tool descriptions, and identical boilerplate control language suggest a young compliance program. The processes exist to pass the audit; whether they accelerate or impede engineering velocity is unclear. A Risk and Governance Executive Committee meeting semiannually sounds impressive for a 5-person startup, but may represent overhead rather than value. SOC 2 cannot distinguish efficient discipline from bureaucratic compliance theater.</p>
  </div>
  <div class="bg-blue-950/20 border border-blue-800/30 rounded-xl p-5">
    <h4 class="text-blue-400 font-semibold mb-2">"Genuinely Mature" (~15% of portfolio)</h4>
    <p class="text-slate-300 text-sm leading-relaxed">Detailed architecture diagrams naming specific services (ECS Fargate, Aurora Serverless v2, CloudFront CDN with WAF rules). Five or more vendors disclosed transparently. Multi-region deployment with tested failover. Named monitoring tools (Datadog, Sentry, Grafana). A 6-12 month audit window. CDK v2 TypeScript IaC mentioned by name. These reports read like technical documentation — the compliance template was a vehicle for genuine disclosure, not a substitute for it. These are the companies where SOC 2 provides real signal, precisely because the engineering team used it as an opportunity to document what they actually built.</p>
  </div>
</div>

<h3 class="text-lg font-semibold text-white mt-8 mb-3">Funding Does Not Predict Operational Maturity</h3>
<p class="text-slate-300 leading-relaxed mb-4">We tracked funding data across 27 companies in our top-scoring cohort. The finding is clear: there is no meaningful correlation between capital raised and SOC 2 quality. 11x AI ($75M+, $350M valuation, backed by a16z and Benchmark) produces a report in the same tier as companies that raised $500K from Y Combinator. Meanwhile, Scribeberry — a bootstrapped Canadian healthtech with no disclosed venture funding — produces the most architecturally detailed report in the entire dataset.</p>

{img(ch['funding'], 'Funding vs operational discipline as measured by SOC 2. No correlation.')}

<div class="bg-slate-800 rounded-xl p-6 border border-slate-700 my-6">
  <p class="text-slate-200 text-lg"><strong>The key statement:</strong> <em>SOC 2 validates how you operate, not what you've built.</em> A company can have impeccable access controls, tested DR plans, and quarterly security reviews — and still have a fragile monolith running on a single VM with no automated tests, no staging environment that mirrors production, and technical debt accumulated over years. The compliance report would give them a clean opinion in both cases.</p>
</div>

{img(ch['redflags'], 'Most common red flags in SOC 2 reports — many are about disclosure gaps, not control failures.')}
"""

# ============================================================
# SECTION 7: FOR INVESTORS
# ============================================================
body += f"""
<h2 id="investors" class="text-2xl font-bold text-white border-b border-slate-700 pb-3 mb-6 mt-16">7. What Investors Should Infer — and What They Should Ignore</h2>

<p class="text-slate-300 leading-relaxed mb-4">The purpose of this analysis is not to diminish SOC 2 — it serves its intended purpose well. The purpose is to calibrate what investors can and cannot learn from it, so they invest their diligence time where it matters most.</p>

<div class="grid md:grid-cols-3 gap-4 my-6">
  <div class="bg-green-950/20 border border-green-800 rounded-xl p-5">
    <h4 class="text-green-400 font-semibold text-sm mb-3 uppercase">✓ Signals to Trust</h4>
    <ul class="text-slate-300 text-sm space-y-2">
      <li>• <strong>Basic security hygiene</strong> — MFA, RBAC, encryption at rest/transit are confirmed</li>
      <li>• <strong>Organizational discipline</strong> — defined processes, audit trails, role-based governance</li>
      <li>• <strong>Enterprise-readiness</strong> — the company can produce compliance artifacts for procurement</li>
      <li>• <strong>Vendor management maturity</strong> — if vendors are named and evaluated, not just listed</li>
      <li>• <strong>Past the chaos phase</strong> — formalized operations suggest scaling readiness</li>
    </ul>
  </div>
  <div class="bg-red-950/20 border border-red-800 rounded-xl p-5">
    <h4 class="text-red-400 font-semibold text-sm mb-3 uppercase">✗ Signals to Discount</h4>
    <ul class="text-slate-300 text-sm space-y-2">
      <li>• <strong>Architecture quality</strong> — SOC 2 can't distinguish good design from bad</li>
      <li>• <strong>Scalability</strong> — no load testing, no performance data</li>
      <li>• <strong>Codebase health</strong> — test coverage, tech debt, code quality unmeasured</li>
      <li>• <strong>Engineering velocity</strong> — deployment frequency, lead time invisible</li>
      <li>• <strong>AI/ML practices</strong> — model governance, data pipelines, evaluation frameworks absent</li>
      <li>• <strong>Product-market fit</strong> — revenue, retention, user growth not in scope</li>
    </ul>
  </div>
  <div class="bg-purple-950/20 border border-purple-800 rounded-xl p-5">
    <h4 class="text-purple-400 font-semibold text-sm mb-3 uppercase">→ Where Real Tech DD Goes Deeper</h4>
    <ul class="text-slate-300 text-sm space-y-2">
      <li>• <strong>System design review</strong> — architecture walkthrough with the CTO</li>
      <li>• <strong>Data model assessment</strong> — schema complexity, migration strategy</li>
      <li>• <strong>Team capability</strong> — hiring quality, SDLC maturity, collaboration patterns</li>
      <li>• <strong>Delivery track record</strong> — deploy frequency, DORA metrics, incident history</li>
      <li>• <strong>AI practices audit</strong> — model evaluation, prompt engineering, data governance</li>
      <li>• <strong>Cost structure analysis</strong> — infrastructure spend, unit economics</li>
    </ul>
  </div>
</div>

<h3 class="text-lg font-semibold text-white mt-8 mb-3">10 Questions for Real Tech DD (Beyond SOC 2)</h3>
<p class="text-slate-300 leading-relaxed mb-4">If SOC 2 gives you the compliance picture, these questions give you the engineering picture. Every one of them addresses a dimension that SOC 2 is structurally incapable of measuring:</p>

<div class="bg-slate-800 rounded-xl p-6 border border-slate-700 my-6">
  <ol class="text-slate-300 space-y-3 list-decimal ml-4">
    <li><strong class="text-white">Walk me through your deployment pipeline.</strong> <span class="text-slate-400">How code goes from commit to production — tools, steps, time, failure rate. This reveals CI/CD maturity.</span></li>
    <li><strong class="text-white">Show me your monitoring dashboard.</strong> <span class="text-slate-400">What metrics do you watch? How quickly do you know when something breaks? This reveals operational awareness.</span></li>
    <li><strong class="text-white">What's your test coverage and testing strategy?</strong> <span class="text-slate-400">Unit, integration, E2E — what exists and what's missing. This reveals code quality culture.</span></li>
    <li><strong class="text-white">Describe your last production incident.</strong> <span class="text-slate-400">Timeline, detection, resolution, post-mortem, what changed. This reveals incident maturity better than any policy document.</span></li>
    <li><strong class="text-white">What happens at 10x your current load?</strong> <span class="text-slate-400">Where does the architecture break? What's the plan? This reveals scalability awareness and honesty.</span></li>
    <li><strong class="text-white">Show me the real architecture — not the SOC 2 version.</strong> <span class="text-slate-400">Services, databases, queues, external APIs, data flows. SOC 2 diagrams are often simplified or outdated.</span></li>
    <li><strong class="text-white">How does your team do code review?</strong> <span class="text-slate-400">Process, turnaround time, who reviews what, quality bar. This reveals engineering culture.</span></li>
    <li><strong class="text-white">What's your relationship with AI in development?</strong> <span class="text-slate-400">Code generation, testing, operations — how and where. This reveals adaptability and modernization pace.</span></li>
    <li><strong class="text-white">What would you rebuild if you started today?</strong> <span class="text-slate-400">This reveals tech debt awareness and architectural honesty — the willingness to admit what isn't working.</span></li>
    <li><strong class="text-white">What's your biggest technical risk right now?</strong> <span class="text-slate-400">The answer reveals self-awareness. A CTO who says "nothing" is either dishonest or unaware — both are concerning.</span></li>
  </ol>
</div>

<div class="bg-slate-800/50 border border-slate-700 rounded-xl p-6 my-6">
  <p class="text-slate-300 leading-relaxed"><strong class="text-white">Bottom line:</strong> SOC 2 compliance is a necessary signal of operational hygiene, not a sufficient signal of tech quality. It tells you a company can operate with discipline in the narrow domain of security controls and access management. It does not tell you whether what they built is scalable, maintainable, or any good. For that, you need a proper Technical Due Diligence — one that evaluates system design, team capability, delivery track record, and engineering culture. <em>SOC 2 is the starting line, not the finish.</em></p>
</div>
"""

# ============================================================
# RESOURCES + CTA + FOOTER
# ============================================================
body += f"""
<div class="grid md:grid-cols-3 gap-4 my-12">
  <a href="modules/" class="block bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition"><div class="text-2xl mb-2">📊</div><h3 class="text-white font-bold mb-1">Deep Dive Modules</h3><p class="text-slate-400 text-sm">13 detailed analysis modules — security, vendors, BCDR, AI stack, funding signals.</p></a>
  <a href="diagrams/" class="block bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition"><div class="text-2xl mb-2">🏗️</div><h3 class="text-white font-bold mb-1">Architecture Gallery</h3><p class="text-slate-400 text-sm">479 infrastructure diagrams — the one genuine technical signal in SOC 2 reports.</p></a>
  <a href="https://delve-vision-extract.whitecontext.workers.dev/" class="block bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition"><div class="text-2xl mb-2">🔍</div><h3 class="text-white font-bold mb-1">Searchable Database</h3><p class="text-slate-400 text-sm">Search {N} companies by technology, vendor, cloud provider.</p></a>
</div>

<div class="bg-gradient-to-br from-blue-950 to-slate-900 rounded-2xl p-10 my-12 border border-blue-800/50 text-center">
  <h2 class="text-3xl font-black text-white mb-4">SOC 2 is the Starting Line.<br>Real Tech DD is the Race.</h2>
  <p class="text-slate-300 text-lg mb-6 max-w-2xl mx-auto">This analysis shows what compliance reports can tell you about security and operational discipline. For the full picture — system design, team capability, delivery track record, AI practices — you need a proper technical due diligence.</p>
  <div class="flex flex-col sm:flex-row gap-4 justify-center">
    <a href="mailto:hello@altimi.com" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-8 py-3 rounded-lg transition">Talk to Altimi →</a>
    <a href="https://whitecontext.com" class="bg-slate-700 hover:bg-slate-600 text-white font-bold px-8 py-3 rounded-lg transition">Talk to WhiteContext →</a>
  </div>
</div>
"""

# ============================================================
# WRAP IN FULL HTML
# ============================================================
html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>What 500 SOC 2 Reports Reveal About VC-Backed Companies</title>
<meta name="description" content="An analysis of 500 funded startups: what SOC 2 compliance tells investors about security and discipline — and what it doesn't. SOC 2 ≠ Tech DD.">
<meta property="og:title" content="What 500 SOC 2 Reports Reveal About VC-Backed Companies">
<meta property="og:description" content="SOC 2 shows discipline, not maturity. We analyzed 500 reports backed by a16z, Benchmark, Kleiner Perkins, Lightspeed, YC.">
<meta name="author" content="Jacek Podoba, Maksym Huczyński">
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<script>tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ fontFamily: {{ sans: ['Inter', 'system-ui'] }} }} }} }}</script>
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
<article>{body}</article>
<footer class="text-center text-slate-500 text-sm py-8 border-t border-slate-800">
  <p>© 2026 <a href="https://altimi.com" class="text-blue-400">Altimi</a> × <a href="https://whitecontext.com" class="text-blue-400">WhiteContext</a> · {N} SOC 2 reports analyzed · By Jacek Podoba & Maksym Huczyński</p>
</footer>
</div>
</body></html>"""

with open(OUT / "article.html", "w") as f:
    f.write(html)

# Count words
text_parts = re.findall(r'>([^<]+)<', html)
visible = ' '.join(t.strip() for t in text_parts if t.strip() and 'data:image' not in t)
visible = re.sub(r'[A-Za-z0-9+/=]{100,}', '', visible)
words = len([w for w in visible.split() if len(w) > 0])
print(f"Article v2 full: {words} words, {len(html)/1024/1024:.1f} MB, {html.count('<h2')} sections")
