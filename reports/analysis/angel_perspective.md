# Angel Investor Tech Assessment — Quick Portfolio Screen

**Dataset:** 485 compliance reports analyzed | **Date:** 2026-03-24

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

### Green Zone (19 companies — 7+/10)
These companies demonstrate genuine technical maturity:
- Named tech stacks beyond cloud provider defaults
- Real architecture diagrams (not templates)
- Multiple vendor integrations showing market traction
- Clean audits with meaningful control descriptions

### Yellow Zone (101 companies — 4-6/10)
Adequate foundations but hard to differentiate:
- Standard cloud infrastructure (AWS/GCP)
- Template-driven compliance reports
- Generic control descriptions
- May have strong products hidden behind boilerplate compliance

### Red Zone (1 companies — ≤3/10)
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
