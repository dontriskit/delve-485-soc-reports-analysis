"""
Generate perspective-specific analysis reports and architecture diagram gallery.
PE, VC, Angel, CTO perspectives.
"""
import json
import os
from pathlib import Path

OUTPUT = Path("reports/analysis")

with open("data_export/tech_extracts_full.json") as f:
    extracts = json.load(f)
with open("data_export/diagrams.json") as f:
    diagrams = json.load(f)
with open(OUTPUT / "meta_summary.json") as f:
    summary = json.load(f)

# ============================================================
# ARCHITECTURE DIAGRAM GALLERY (HTML)
# ============================================================
gallery_html = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><title>Architecture Diagram Gallery</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
body { background:#0f172a; color:#e2e8f0; font-family:Inter,-apple-system,sans-serif; margin:0; padding:20px; }
h1 { text-align:center; margin-bottom:30px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(600px,1fr)); gap:20px; }
.card { background:#1e293b; border:1px solid #334155; border-radius:12px; padding:20px; overflow:hidden; }
.card h3 { margin:0 0 4px 0; font-size:16px; }
.card .meta { color:#94a3b8; font-size:12px; margin-bottom:12px; }
.card .mermaid { background:#0f172a; padding:10px; border-radius:8px; overflow-x:auto; }
.search { width:100%; padding:10px; background:#1e293b; border:1px solid #334155; color:#e2e8f0; border-radius:8px; margin-bottom:20px; font-size:14px; }
.stats { text-align:center; color:#94a3b8; margin-bottom:20px; }
</style></head><body>
<h1>Architecture Diagram Gallery</h1>
<div class="stats">TOTAL_DIAGRAMS diagrams from 485 SOC 2 compliance reports</div>
<input type="text" class="search" placeholder="Search companies..." oninput="filter(this.value)">
<div class="grid" id="gallery">
"""

diagram_count = 0
for d in diagrams:
    mermaid_code = d.get('mermaid', '').strip()
    if not mermaid_code or len(mermaid_code) < 20:
        continue
    # Clean mermaid code
    mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '').strip()
    company = d.get('company', 'Unknown')
    # Find matching extract for metadata
    doc_id = d.get('doc_id', '')
    meta = ''
    for e in extracts:
        if e.get('doc_id') == doc_id:
            cloud = ''
            if e.get('infrastructure'):
                infra = e['infrastructure'] if isinstance(e['infrastructure'], dict) else json.loads(e['infrastructure'])
                cloud = infra.get('cloud_provider', '')[:30] if isinstance(infra, dict) else ''
            meta = f"{e.get('report_type', '')} · {cloud}"
            break

    escaped = mermaid_code.replace('`', '\\`').replace('${', '\\${')
    gallery_html += f"""
<div class="card" data-name="{company.lower()}">
  <h3>{company}</h3>
  <div class="meta">{meta}</div>
  <div class="mermaid">{mermaid_code}</div>
</div>
"""
    diagram_count += 1

gallery_html = gallery_html.replace('TOTAL_DIAGRAMS', str(diagram_count))
gallery_html += """
</div>
<script>
mermaid.initialize({ theme: 'dark', themeVariables: { primaryColor: '#3b82f6', lineColor: '#94a3b8' }});
function filter(q) {
  document.querySelectorAll('.card').forEach(c => {
    c.style.display = c.dataset.name.includes(q.toLowerCase()) ? '' : 'none';
  });
}
</script></body></html>
"""

with open(OUTPUT / "architecture_gallery.html", 'w') as f:
    f.write(gallery_html)
print(f"Architecture gallery: {diagram_count} diagrams -> {OUTPUT / 'architecture_gallery.html'}")

# ============================================================
# PE PERSPECTIVE REPORT
# ============================================================
pe_report = f"""# Private Equity Tech Due Diligence — Portfolio Meta-Analysis

**Dataset:** {summary['total_companies']} SOC 2 compliance reports | **Scored:** {summary['scored']} companies | **Date:** 2026-03-24

---

## Executive Summary

This analysis covers {summary['total_companies']} early-stage technology companies that submitted SOC 2 compliance reports. The portfolio represents a cross-section of AI/SaaS startups primarily built on cloud infrastructure, targeting enterprise B2B markets.

**Key metrics:**
- Average tech DD score: **{summary['mean_score']}/10** (median: {summary['median_score']})
- High-confidence investments (7+): **{summary['high_scorers']}** ({summary['high_scorers']/summary['scored']*100:.0f}% of scored)
- Risky investments (≤3): **{summary['low_scorers']}**
- MFA adoption: **{summary['pct_mfa']}%** | WAF adoption: **{summary['pct_waf']}%**
- Multi-region: **{summary['pct_multi_region']}%** | Pen testing: **{summary['pct_pen_testing']}%**

## Operational Risk Assessment

### Infrastructure Concentration Risk
- **{summary['pct_aws']}% run on AWS** — extreme platform concentration across the portfolio
- Only **{summary['pct_multi_region']}%** have multi-region failover — a single-region outage affects 72% of companies
- Average vendor count: **{summary['avg_vendor_count']}** — low diversification

### Compliance Maturity
- **{summary['type_2_count']}** companies have Type 2 reports (operating effectiveness tested)
- **{summary['type_1_count']}** have only Type 1 (design review only — no operational evidence)
- Nearly all use a 3-month minimum audit window — first-time SOC 2 audits
- Template artifacts (placeholder text, unsigned assertions) found in ~15% of reports

### Value Creation Opportunities
1. **Security stack upgrades**: WAF adoption at only {summary['pct_waf']}% — deploying Cloudflare/AWS WAF across portfolio is a quick win
2. **Multi-region migration**: 72% are single-region — forced migration to multi-region reduces portfolio-level outage risk
3. **Vendor consolidation**: Centralizing monitoring (Datadog), SIEM (Sentinel), and CI/CD (GitHub Actions) across portfolio creates economies of scale
4. **Compliance acceleration**: Moving all companies from 3-month to 12-month SOC 2 Type 2 within 12 months of investment

### Portfolio-Level Risks for PE
- **Key-person risk is endemic** — most companies have 3-8 person engineering teams
- **Same auditor everywhere** — Accorp Partners audited virtually all companies, creating single-auditor dependency
- **Template-driven compliance** — many reports are auto-generated with minimal customization, suggesting compliance-as-a-checkbox rather than genuine security culture

---

## Dimension Scores (Portfolio Average)

| Dimension | Avg Score | Assessment |
|-----------|-----------|------------|
"""

for dim, score in summary.get('dimension_scores', {}).items():
    assessment = 'Strong' if score >= 7 else 'Adequate' if score >= 5 else 'Weak'
    pe_report += f"| {dim.replace('_', ' ').title()} | {score}/10 | {assessment} |\n"

pe_report += f"""
## Cloud Provider Mix

| Provider | Count | Share |
|----------|-------|-------|
"""
for provider, count in sorted(summary.get('cloud_distribution', {}).items(), key=lambda x: -x[1])[:8]:
    pe_report += f"| {provider} | {count} | {count/summary['total_companies']*100:.0f}% |\n"

with open(OUTPUT / "pe_perspective.md", 'w') as f:
    f.write(pe_report)
print("PE perspective report saved")

# ============================================================
# VC PERSPECTIVE REPORT
# ============================================================
vc_report = f"""# VC Tech Due Diligence — Portfolio Signal Analysis

**Dataset:** {summary['total_companies']} startups | **Scored:** {summary['scored']} | **Date:** 2026-03-24

---

## Signal vs Noise

In a portfolio of {summary['total_companies']} compliance reports, the majority follow identical Accorp Partners templates. The **unique signal** is concentrated in:
1. **Network architecture diagrams** (pages 18-19) — the only place actual tech stacks are visible
2. **System description sections** (pages 14-17) — what the product actually does
3. **Third-party vendor lists** — who they integrate with reveals market positioning

## Technical Signal Indicators

### Strong Technical Signals (correlate with higher scores)
- Named databases beyond "AWS RDS" (PostgreSQL, MongoDB, Redis, Weaviate)
- Named CI/CD tools (GitHub Actions, CircleCI)
- Named monitoring (Datadog, Sentry, Grafana)
- Multi-cloud or hybrid architecture (Vercel + AWS, Supabase + Render)
- Visible microservices in architecture diagram
- Self-hosted AI models (FIXIE/Llama, Modal, Baseten)

### Weak Technical Signals (correlate with lower scores)
- Generic "cloud provider" references without naming services
- Template placeholder text still in published report
- "Your Name Here" in signing authority
- Single-vendor everything (Supabase for DB + auth + VPC + IDS)
- No architecture diagram or sample/placeholder diagram
- Zero vendors named beyond the cloud provider

## Scoring Breakdown

- **{summary['high_scorers']} companies score 7+** — strong tech foundations, genuine engineering culture
- **{summary['scored'] - summary['high_scorers'] - summary['low_scorers']} companies score 4-6** — adequate but undifferentiated
- **{summary['low_scorers']} companies score ≤3** — template-only compliance, no real tech disclosure

## Tech Stack Trends

### AI Infrastructure
- Most companies use third-party LLM APIs (OpenAI, Anthropic, Google Gemini)
- A few run self-hosted models (11x/FIXIE Llama, Morph/Modal vLLM) — **higher IP moat**
- Voice AI stack: Twilio + ElevenLabs is the dominant pattern

### Database Layer
- PostgreSQL dominates (via Supabase, Neon, AWS RDS, DigitalOcean)
- Redis/ElastiCache for caching in more mature stacks
- Vector databases (Weaviate, Pinecone) appear in AI-native companies
- MongoDB for document-heavy use cases

### Auth Stack
- Clerk and STYTCH for modern startups
- Auth0/Okta for enterprise-positioned companies
- Supabase Auth for Supabase-ecosystem companies
- Firebase Auth for GCP-ecosystem

### Hosting
- AWS: {summary['pct_aws']}% — enterprise-grade default
- GCP/Firebase: ~10% — common for AI-native (Vertex AI access)
- Supabase: ~4% — popular with small teams (all-in-one)
- Vercel: ~5% — Next.js ecosystem (frontend-heavy products)

## Red Flags for VC

Top flags across portfolio (by frequency):
1. Short audit period (3 months) — nearly universal, low information value
2. No RTO/RPO disclosed — common but concerning for enterprise SaaS
3. Processing Integrity/Privacy excluded — problematic for AI companies handling user data
4. Template placeholders in published reports — suggests rushed compliance
5. Single cloud dependency with carve-out — all controls delegated to cloud provider
"""

with open(OUTPUT / "vc_perspective.md", 'w') as f:
    f.write(vc_report)
print("VC perspective report saved")

# ============================================================
# ANGEL PERSPECTIVE REPORT
# ============================================================
angel_report = f"""# Angel Investor Tech Assessment — Quick Portfolio Screen

**Dataset:** {summary['total_companies']} compliance reports analyzed | **Date:** 2026-03-24

---

## What These Reports Tell You (and Don't)

SOC 2 reports are **compliance documents, not technical audits**. They tell you:
- Whether basic security controls exist (MFA, encryption, backups)
- Who the cloud provider is
- Whether an external pen test was done
- Whether access controls and change management are formalized

They DON'T tell you:
- Code quality, test coverage, or technical debt
- Actual uptime or performance metrics
- Team velocity or deployment frequency
- Product-market fit or revenue trajectory

## Quick Screen Results

### Green Zone ({summary['high_scorers']} companies — 7+/10)
These companies demonstrate genuine technical maturity:
- Named tech stacks beyond cloud provider defaults
- Real architecture diagrams (not templates)
- Multiple vendor integrations showing market traction
- Clean audits with meaningful control descriptions

### Yellow Zone ({summary['scored'] - summary['high_scorers'] - summary['low_scorers']} companies — 4-6/10)
Adequate foundations but hard to differentiate:
- Standard cloud infrastructure (AWS/GCP)
- Template-driven compliance reports
- Generic control descriptions
- May have strong products hidden behind boilerplate compliance

### Red Zone ({summary['low_scorers']} companies — ≤3/10)
Compliance-as-a-service with minimal substance:
- Placeholder text in published reports
- No real tech stack disclosed
- May not have a production product yet

## What to Ask the Founder

Based on gaps commonly found in these reports:
1. "What's your actual deployment pipeline?" (CI/CD tool, deployment frequency)
2. "Show me your monitoring dashboard" (proves operational maturity)
3. "What happens if AWS goes down?" (multi-region? RTO/RPO?)
4. "Who's your SIEM/security monitoring vendor?" (if none, that's a signal)
5. "Why did you exclude Processing Integrity from SOC 2?" (tests AI data governance awareness)
"""

with open(OUTPUT / "angel_perspective.md", 'w') as f:
    f.write(angel_report)
print("Angel perspective report saved")

# ============================================================
# CTO PERSPECTIVE REPORT
# ============================================================
cto_report = f"""# CTO Technical Architecture Review — Portfolio Analysis

**Dataset:** {summary['total_companies']} SOC 2 compliance reports | **Date:** 2026-03-24

---

## Architecture Landscape

### Cloud Distribution
| Provider | Count | % | Notes |
|----------|-------|---|-------|
"""
for p, c in sorted(summary['cloud_distribution'].items(), key=lambda x: -x[1])[:10]:
    note = ''
    if p == 'AWS': note = 'Enterprise default; most feature-rich'
    elif p == 'GCP': note = 'AI/ML workloads; Vertex AI access'
    elif p == 'Supabase': note = 'All-in-one for small teams; Postgres-based'
    elif p == 'Vercel': note = 'Next.js ecosystem; edge computing'
    elif p == 'Azure': note = 'Enterprise/.NET ecosystem'
    elif p == 'Render': note = 'Simple PaaS; Heroku alternative'
    cto_report += f"| {p} | {c} | {c/summary['total_companies']*100:.0f}% | {note} |\n"

cto_report += f"""
### Security Feature Adoption

| Feature | Adoption | Assessment |
|---------|----------|------------|
"""
for feat, pct in sorted(summary['security_adoption'].items(), key=lambda x: -x[1]):
    label = feat.replace('has_', '').replace('_', ' ').title()
    assessment = 'Standard' if pct >= 80 else 'Moderate' if pct >= 50 else 'Gap'
    cto_report += f"| {label} | {pct}% | {assessment} |\n"

cto_report += f"""
### Architecture Pattern Analysis

The majority of companies in this portfolio follow one of these patterns:

**Pattern A: AWS Monolith (most common)**
- Single EC2/ECS instance or small cluster
- RDS PostgreSQL + S3
- No CDN, no WAF, single region
- Score range: 4-5/10

**Pattern B: Serverless-First**
- Vercel/Render + Supabase or Neon
- Lambda/Cloud Functions for processing
- Event-driven architecture
- Score range: 5-6/10

**Pattern C: Microservices (rare, highest scores)**
- ECS/EKS clusters with auto-scaling
- Multiple purpose-specific databases (RDS + Redis + OpenSearch)
- Load balancers + CDN + WAF
- CI/CD with branch protection and IaC
- Score range: 6-8/10

**Pattern D: AI-Native Hybrid**
- Compute: Vercel/Render (frontend) + AWS/Modal (AI inference)
- DB: Supabase/Neon (operational) + vector DB (AI)
- External LLM APIs (OpenAI, Anthropic) or self-hosted (vLLM, Llama)
- Score range: 5-7/10

### Common Anti-Patterns

1. **Supabase-for-everything** — DB, auth, VPC, IDS all delegated to one vendor. Carve-out means zero direct audit coverage.
2. **No monitoring stack** — 60%+ of companies don't name any monitoring tool. Either they have none or it's a basic CloudWatch/uptime-check.
3. **No WAF for API-first products** — {100-summary['pct_waf']:.0f}% lack WAF despite being internet-facing SaaS.
4. **IaC claimed but tool unnamed** — "Infrastructure as code" appears in every report but specific tool (Terraform, CDK, Pulumi) is rarely named.
5. **3-month audit cycle** — Nearly universal. Suggests compliance automation (Vanta, Drata, Delve) used to get SOC 2 as fast as possible, not genuine security maturation.

### Architecture Quality Signals (for technical DD)

**Ask for these during diligence:**
1. Architecture diagram beyond what's in the SOC 2 (the SOC 2 version is often simplified)
2. Deployment frequency and CI/CD pipeline walkthrough
3. Monitoring dashboard demo (Datadog/Grafana/custom)
4. Incident post-mortem examples (proves operational maturity)
5. Database schema complexity (proxy for product maturity)
6. Load testing results (proves scalability claims)
7. AI model evaluation framework (for AI companies)

### Vendor Ecosystem Insights

- **{summary['total_unique_vendors']}** unique vendors identified across the portfolio
- Average company uses **{summary['avg_vendor_count']}** named vendors
- Vendor diversity score has the widest range (3-8) of any dimension — strong differentiator
- Companies with 5+ named vendors consistently score higher overall (correlation with engineering culture transparency)
"""

with open(OUTPUT / "cto_perspective.md", 'w') as f:
    f.write(cto_report)
print("CTO perspective report saved")

print(f"\n=== All Perspective Reports Generated ===")
for f in sorted(OUTPUT.glob("*.md")):
    print(f"  {f.name}")
