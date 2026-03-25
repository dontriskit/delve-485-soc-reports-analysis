# SKILL: Generate Tech Due Diligence Report

## Purpose
Transform a structured tech extraction JSON into a professional, investor-ready Tech DD report in Markdown.

## Inputs
- `DOC_ID`: The Google Doc ID
- `COMPANY_DB`: Path to `company_db/` directory (default: `company_db/`)

## Prerequisites
- `{COMPANY_DB}/{DOC_ID}_tech_extract.json` must exist (output of Skill 01)

## Procedure

### Step 1: Load extracted data
Read `{COMPANY_DB}/{DOC_ID}_tech_extract.json`.

### Step 2: Generate report
Write a Markdown report to `reports/{COMPANY_SLUG}_tech_dd_report.md` where `COMPANY_SLUG` is the lowercased company product name with spaces replaced by underscores.

Follow this exact template:

```markdown
# Tech Due Diligence Report: {Company Name}

**Date:** {TODAY} | **Source:** {report_type} ({audit_period}) | **Auditor:** {auditor} | **Opinion:** {opinion}

---

## Company Overview

| Field | Detail |
|-------|--------|
| Legal Name | {legal_name} |
| Product | {product} — {system_description.overview (first sentence)} |
| HQ | {hq} |
| Website | {website} |
| Leadership | {signing_authority or cto} |
| Cloud | {infrastructure.cloud_provider} |

**What they do:** {system_description.overview}

---

## 1. Technology Stack Assessment

### Infrastructure (Score: {scoring.infrastructure.score}/10)
- Bullet points from infrastructure section
- Concerns noted as "**Concern:**" items

### Application Architecture (Score: {scoring.application_architecture.score}/10)
- Pattern, languages, frameworks, compute
- Notable architectural choices

### Data Layer (Score: {scoring.data_layer.score}/10)
- Databases, caching, storage
- Backup and retention details

### Security Posture (Score: {scoring.security_posture.score}/10)
- Network security, encryption, scanning
- Tools and practices

### DevOps Maturity (Score: {scoring.devops_maturity.score}/10)
- CI/CD, IaC, environments
- Change management

### BCDR Readiness (Score: {scoring.bcdr_readiness.score}/10)
- Backup strategy, failover, DR testing
- RTO/RPO if available

---

## 2. Vendor Dependency Map

| Vendor | Criticality | Purpose | Risk |
|--------|------------|---------|------|
{For each third_party_service, one row}

Analysis paragraph about vendor concentration.

---

## 3. Risk Assessment

### RED FLAGS
{From red_flags list, each as bullet with explanation}

### YELLOW FLAGS
{From yellow_flags list}

### GREEN FLAGS
{From green_flags list}

---

## 4. Compliance Summary

| Control Area | Status | Notes |
|-------------|--------|-------|
| Access Control | Pass/Fail | Key details |
| Encryption | Pass/Fail | Key details |
| Change Management | Pass/Fail | Key details |
| Monitoring | Pass/Fail | Key details |
| Vendor Management | Pass/Fail | Key details |
| BCDR | Pass/Fail | Key details |
| Vulnerability Mgmt | Pass/Fail | Key details |

**Untested controls:** {From compliance_controls.untestable}

---

## 5. Recommendation

**Investment Readiness: {LOW | MODERATE | MODERATE-HIGH | HIGH}**

Based on overall score:
- 1-4: LOW
- 5-6: MODERATE
- 7-8: MODERATE-HIGH
- 9-10: HIGH

{2-3 sentence summary}

Key follow-up items:
1. {Numbered list of 4-6 specific DD questions to ask the company}
```

### Step 3: Validate
- Ensure all score fields are populated
- Ensure at least 1 red flag, 1 yellow flag, 1 green flag
- Ensure vendor table has at least 1 entry
- Ensure recommendation aligns with overall score

## Output
- `reports/{COMPANY_SLUG}_tech_dd_report.md`
