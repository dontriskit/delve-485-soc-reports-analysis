# Private Equity Tech Due Diligence — Portfolio Meta-Analysis

**Dataset:** 485 SOC 2 compliance reports | **Scored:** 121 companies | **Date:** 2026-03-24

---

## Executive Summary

This analysis covers 485 early-stage technology companies that submitted SOC 2 compliance reports. The portfolio represents a cross-section of AI/SaaS startups primarily built on cloud infrastructure, targeting enterprise B2B markets.

**Key metrics:**
- Average tech DD score: **5.6/10** (median: 6.0)
- High-confidence investments (7+): **19** (16% of scored)
- Risky investments (≤3): **1**
- MFA adoption: **99.4%** | WAF adoption: **43.9%**
- Multi-region: **28.2%** | Pen testing: **63.3%**

## Operational Risk Assessment

### Infrastructure Concentration Risk
- **59.2% run on AWS** — extreme platform concentration across the portfolio
- Only **28.2%** have multi-region failover — a single-region outage affects 72% of companies
- Average vendor count: **4.2** — low diversification

### Compliance Maturity
- **254** companies have Type 2 reports (operating effectiveness tested)
- **231** have only Type 1 (design review only — no operational evidence)
- Nearly all use a 3-month minimum audit window — first-time SOC 2 audits
- Template artifacts (placeholder text, unsigned assertions) found in ~15% of reports

### Value Creation Opportunities
1. **Security stack upgrades**: WAF adoption at only 43.9% — deploying Cloudflare/AWS WAF across portfolio is a quick win
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
| Overall | 5.6/10 | Adequate |
| Infrastructure | 6.0/10 | Adequate |
| App Architecture | 5.1/10 | Adequate |
| Data Layer | 5.0/10 | Adequate |
| Security | 6.9/10 | Adequate |
| Devops | 5.6/10 | Adequate |
| Bcdr | 5.9/10 | Adequate |
| Vendor Diversity | 4.3/10 | Weak |

## Cloud Provider Mix

| Provider | Count | Share |
|----------|-------|-------|
| AWS | 287 | 59% |
| GCP | 74 | 15% |
| Supabase | 39 | 8% |
| Azure | 33 | 7% |
| Vercel | 23 | 5% |
| DigitalOcean | 12 | 2% |
| Render | 5 | 1% |
| Fly.io | 5 | 1% |
