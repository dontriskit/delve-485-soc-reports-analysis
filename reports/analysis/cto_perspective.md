# CTO Technical Architecture Review — Portfolio Analysis

**Dataset:** 485 SOC 2 compliance reports | **Date:** 2026-03-24

---

## Architecture Landscape

### Cloud Distribution
| Provider | Count | % | Notes |
|----------|-------|---|-------|
| AWS | 287 | 59% | Enterprise default; most feature-rich |
| GCP | 74 | 15% | AI/ML workloads; Vertex AI access |
| Supabase | 39 | 8% | All-in-one for small teams; Postgres-based |
| Azure | 33 | 7% | Enterprise/.NET ecosystem |
| Vercel | 23 | 5% | Next.js ecosystem; edge computing |
| DigitalOcean | 12 | 2% |  |
| Render | 5 | 1% | Simple PaaS; Heroku alternative |
| Fly.io | 5 | 1% |  |
| Other | 2 | 0% |  |
| Railway | 2 | 0% |  |

### Security Feature Adoption

| Feature | Adoption | Assessment |
|---------|----------|------------|
| Bcdr Policy | 100.0% | Standard |
| Mfa | 99.4% | Standard |
| Rbac | 99.0% | Standard |
| Vpc | 96.9% | Standard |
| Multi Az | 88.0% | Standard |
| Firewall | 87.8% | Standard |
| Vuln Scanning | 87.6% | Standard |
| Server Hardening | 87.6% | Standard |
| Ids Ips | 87.4% | Standard |
| Branch Protection | 69.1% | Moderate |
| Pen Testing | 63.3% | Moderate |
| Daily Backups | 54.4% | Moderate |
| Per Tenant Segregation | 53.2% | Moderate |
| Waf | 43.9% | Gap |
| Quarterly Reviews | 43.1% | Gap |
| Multi Region | 28.2% | Gap |
| Cyber Insurance | 22.3% | Gap |

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
3. **No WAF for API-first products** — 56% lack WAF despite being internet-facing SaaS.
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

- **533** unique vendors identified across the portfolio
- Average company uses **4.2** named vendors
- Vendor diversity score has the widest range (3-8) of any dimension — strong differentiator
- Companies with 5+ named vendors consistently score higher overall (correlation with engineering culture transparency)
