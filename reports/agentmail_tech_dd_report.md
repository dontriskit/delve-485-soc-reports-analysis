# Tech Due Diligence Report: AgentMail, Inc.

**Date:** 2026-03-24 | **Source:** SOC 2 Type 2 (August 7, 2025 - November 7, 2025) | **Auditor:** Accorp Partners | **Opinion:** Unqualified

---

## Company Overview

| Field | Detail |
|-------|--------|
| Legal Name | AgentMail, Inc. |
| Product | AgentMail — AgentMail provides an API-first email infrastructure platform designed to give AI agents their own dedicated inboxes at scale. |
| HQ | 2261 Market Street, STE 85434, San Francisco, CA 94114 |
| Website | N/A |
| Leadership | Vikramaditya Singh, Co-Founder & President |
| Cloud | AWS (carve-out method - AWS controls excluded from scope) |

**What they do:** AgentMail provides an API-first email infrastructure platform designed to give AI agents their own dedicated inboxes at scale. The platform enables developers to programmatically create thousands of ephemeral inboxes, send and receive emails, and stream structured JSON events in real time. It solves limitations of traditional email providers by eliminating per-inbox costs, API rate limits, and domain reputation risks.

---

## 1. Technology Stack Assessment

### Infrastructure (Score: 7/10)
- Multi-region deployment across us-west-1 and us-east-1 with multi-AZ configuration
- 100% cloud-hosted on AWS with no physical servers or offices in scope
- AWS Lambda serverless compute alongside virtual servers (hybrid model)
- Infrastructure as code with configuration management tool and rollback capability
- Network segmentation via segmented VPCs with access control lists (ACLs)
- IDS/IPS employed via AWS for threat detection and protection
- **Concern:** No CDN mentioned despite being an API-first platform serving developers
- **Concern:** Single cloud provider (AWS) with carve-out method — AWS infrastructure controls are explicitly excluded from audit scope
- **Concern:** No WAF (Web Application Firewall) disclosed for an API-heavy platform

### Application Architecture (Score: 5/10)
- Hybrid pattern combining AWS Lambda serverless functions with virtual servers
- API-first design with REST endpoints, webhooks, and JSON event streaming
- Branch protection configured with required merge approval for production deployments
- Code review required for all changes; changes logged, time-stamped, and attributed
- Segregated development/test and production environments
- **Concern:** Zero programming languages, frameworks, or specific compute services named anywhere in the report — impossible to assess code quality or maintainability
- **Concern:** No container orchestration mentioned
- **Concern:** Source control platform not named (only described generically)

### Data Layer (Score: 6/10)
- AWS managed database deployed in both regions (specific engine not named)
- Daily backups with multi-AZ configuration and backup failure alerting
- Data classification policy categorizing data by sensitivity and criticality
- Data retention policy with configurable per-customer settings
- Per-tenant data segregation enforced at infrastructure level — critical for multi-tenant email
- **Concern:** No specific database engine, caching layer, file storage service, or data warehouse named
- **Concern:** No caching layer disclosed despite real-time event streaming requirements

### Security Posture (Score: 7/10)
- IDS/IPS via AWS for network monitoring and threat detection
- Firewalls on application gateway and production network, reviewed annually
- Annual external penetration testing by independent third party with remediation tracking
- Monthly automated vulnerability scanning on infrastructure and applications
- MFA enforced for admin access, remote access, source code tools, and employee email
- RBAC with quarterly access reviews and 1-business-day termination revocation SLA
- Encryption at rest via AWS KMS and in transit via TLS
- Anti-virus/malware protection on all production servers and workstations with continuous scanning
- Endpoint protection enabled; server hardening implemented
- Cybersecurity insurance in place
- Network segmentation with VPN access through bastion host
- Content filtering routed through proxy server
- **Concern:** No named WAF despite handling API traffic at scale
- **Concern:** No named SIEM — monitoring tools referenced only generically
- **Concern:** TLS version not specified

### DevOps Maturity (Score: 6/10)
- Infrastructure as code with configuration management and rollback capability
- Branch protection with merge approval required for production changes
- Separate development/test and production environments
- Emergency change process documented
- Formal change management lifecycle: changes tested before production deployment
- Automatic patch management with monthly CTO reviews; critical patches applied as available
- Workstations configured for automatic updates and scanned daily for patch compliance
- **Concern:** No specific CI/CD tool or source control platform named
- **Concern:** No container orchestration mentioned
- **Concern:** Tooling details are entirely generic — difficult to assess actual maturity

### BCDR Readiness (Score: 7/10)
- Formal BCDR policy documented and reviewed annually
- Annual DR testing across different loss scenarios
- Multi-AZ and multi-region failover (servers can be spun up across availability zones)
- Daily backups with failure alerting
- **Concern:** No RTO or RPO targets disclosed despite having a formal BCDR program
- **Concern:** Full reliance on AWS for all physical and environmental controls (carve-out)

---

## 2. Vendor Dependency Map

| Vendor | Criticality | Purpose | Risk |
|--------|------------|---------|------|
| Amazon Web Services (AWS) | Critical | Primary cloud infrastructure provider (data center, compute, networking, storage, key management, serverless) | Extreme concentration risk — single point of failure for all infrastructure; carve-out excludes AWS controls from audit scope |
| Third-party certificate authority | High | TLS certificate issuance for web-based systems | Vendor not named; compromise could affect all TLS-secured communications |
| Accorp Partners | Low | Independent SOC 2 audit firm | No operational risk; audit-only relationship |

AgentMail exhibits near-total vendor concentration on AWS. Every layer of the technology stack — compute, storage, networking, key management, IDS/IPS, serverless functions, and database services — runs on a single cloud provider. No additional cloud providers, CDN vendors, or named third-party SaaS tools were disclosed in the report. The carve-out method means AWS's own infrastructure controls are explicitly excluded from the assurance boundary, requiring evaluators to separately examine AWS's SOC 2 report. This concentration represents a material risk: any AWS service disruption, pricing change, or policy shift would directly and comprehensively impact AgentMail's operations.

---

## 3. Risk Assessment

### RED FLAGS
- **Extremely short audit observation period (3 months):** The August 7 - November 7, 2025 window is the minimum typical for a Type 2 report, suggesting controls may have been recently established and lack operational maturity.
- **Four controls untestable due to no events:** CC2.2.3 (change communication), CC3.2.1 (cybersecurity insurance), CC6.5.2 (customer data deletion), and CC7.3.1 (incident response) could not be tested — their operating effectiveness remains unverified.
- **Near-total single-cloud dependency with carve-out:** AWS controls are explicitly excluded from assurance scope, meaning the most critical infrastructure controls (physical security, network backbone, hypervisor security) have no direct audit coverage.
- **No technology stack specifics disclosed:** Zero programming languages, database engines, CI/CD tools, monitoring platforms, or SIEM are named anywhere in the report, making independent technical assessment impossible.

### YELLOW FLAGS
- **No WAF mentioned** despite being an API-first platform handling email traffic at scale.
- **No named SIEM or log aggregation platform** — monitoring tools referenced only generically.
- **No RTO or RPO disclosed** despite having a BCDR policy and annual testing program.
- **Processing Integrity and Privacy trust service categories excluded** as "not relevant" despite handling email content for AI agents.
- **Cybersecurity insurance control (CC3.2.1)** existence confirmed but effectiveness untested.
- **No CDN mentioned** for an API-first platform presumably serving global developer customers.
- **Section 5 (Other Information) is minimal** — only a brief DR description with no additional technical detail.
- **Significant control description repetition** across criteria suggesting heavy use of compliance automation templates.

### GREEN FLAGS
- **Clean unqualified opinion** with zero exceptions on all 55 testable controls.
- **Multi-region (us-west-1 and us-east-1) multi-AZ architecture** with failover capabilities.
- **Per-tenant data segregation** enforced at infrastructure level — critical for a multi-tenant email platform.
- **Comprehensive access control:** MFA for admin/remote/source code access, RBAC, quarterly access reviews, 1-business-day termination revocation SLA.
- **Infrastructure as code** with configuration management tool and rollback capability.
- **Formal BCDR policy** with annual testing across different loss scenarios.
- **Branch protection** with required merge approval and source code changes logged/timestamped/attributed.
- **Annual external penetration testing** with remediation tracking in risk register.
- **Monthly automated vulnerability scanning** with adjustable frequency.
- **Formal vendor management program** with SOC report reviews and quarterly assessments for vendors without SOC reports.
- **Data classification policy** established and implemented by sensitivity/criticality.
- **Daily backups** with multi-AZ configuration and backup failure alerting.
- **Risk and Governance Executive Committee (RGEC)** with IT Leadership Committee meeting weekly.

---

## 4. Compliance Summary

| Control Area | Status | Notes |
|-------------|--------|-------|
| Access Control | Pass | MFA enforced for admin, remote, and source code access; RBAC with quarterly reviews; 1-business-day termination revocation; unique user IDs; password complexity and lockout policies |
| Encryption | Pass | TLS in transit (version unspecified), AWS KMS at rest; encryption key access restricted to authorized personnel |
| Change Management | Pass | Branch protection with merge approval; separate environments; IaC with rollback; emergency change process; changes logged and attributed |
| Monitoring | Pass | Automated alerting on high/critical events; logging of admin activities, logon attempts, data deletions, config changes; IDS enabled; log protection in place |
| Vendor Management | Pass | Formal program with annual SOC report reviews; quarterly risk assessments for critical vendors without SOC reports |
| BCDR | Pass | Formal policy reviewed annually; annual testing; multi-AZ and multi-region failover; daily backups with failure alerting |
| Vulnerability Mgmt | Pass | Monthly automated scans; annual external pen testing; remediation plans for critical/high findings; server hardening; anti-virus on servers and workstations |

**Untested controls:** CC2.2.3 - Communication of significant changes to people/roles could not be tested (no significant changes during engagement period); CC3.2.1 - Cybersecurity insurance effectiveness could not be tested (no cyber incidents during engagement period); CC6.5.2 - Customer data deletion upon termination could not be tested (no customer terminations during engagement period); CC7.3.1 - Incident response policies effectiveness could not be tested (no security incidents during engagement period)

---

## 5. Recommendation

**Investment Readiness: MODERATE**

AgentMail demonstrates a solid security-conscious posture for an early-stage company, achieving a clean SOC 2 Type 2 report with zero exceptions across all 55 testable controls. Multi-region AWS infrastructure with IaC, comprehensive access controls, per-tenant data segregation, and formal BCDR planning are meaningful strengths. However, the report is notably deficient in technology specifics — no programming languages, database engines, CI/CD tools, or monitoring platforms are named — making independent technical assessment impossible. The extreme AWS concentration, minimal 3-month audit window, four untestable controls, and exclusion of Processing Integrity and Privacy criteria significantly limit the assurance value of this report.

Key follow-up items:
1. Request a detailed technology stack inventory: programming languages, frameworks, database engines, CI/CD platform, monitoring/SIEM tools, and source control system.
2. Ask for AWS's SOC 2 report and confirm AgentMail's specific service usage, given the carve-out method excludes all AWS controls from scope.
3. Request disclosed RTO/RPO targets and evidence of DR test results, including recovery time measurements.
4. Inquire why Processing Integrity and Privacy trust service categories were excluded, given the platform handles email content for AI agents at scale.
5. Request details on email-specific security controls (DKIM key management, SPF/DMARC infrastructure, IP reputation management) that appear in product descriptions but not in audited controls.
6. Ask for a longer-term SOC 2 Type 2 report (12-month observation period) or a commitment to one, to verify sustained control operation and address the four untestable controls.
