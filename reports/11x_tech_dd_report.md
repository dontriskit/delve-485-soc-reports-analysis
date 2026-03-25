# Tech Due Diligence Report: 11x AI Inc.

**Date:** 2026-03-24 | **Source:** SOC 2 Type 2 (May 1, 2025 - August 1, 2025) | **Auditor:** Accorp Partners | **Opinion:** Unqualified

---

## Company Overview

| Field | Detail |
|-------|--------|
| Legal Name | 11x AI Inc. |
| Product | Digital Workers for GTM teams — 11x AI Inc. is an AI-powered automation company specializing in autonomous 'digital workers' for go-to-market (GTM) teams. |
| HQ | 677 Harrison Street, San Francisco, CA |
| Website | — |
| Leadership | Jeson Patel, Chief Technology Officer |
| Cloud | AWS (carve-out method - AWS controls excluded from scope, AWS SOC 2 reviewed separately) |

**What they do:** 11x AI Inc. is an AI-powered automation company specializing in autonomous 'digital workers' for go-to-market (GTM) teams. Its platform delivers enterprise-ready AI agents that operate 24/7 to research prospects, conduct outreach, qualify leads, and book meetings with minimal human oversight. The platform integrates with major CRMs and communication tools with end-to-end encryption.

---

## 1. Technology Stack Assessment

### Infrastructure (Score: 6/10)
- AWS as primary cloud provider using carve-out method (AWS controls excluded from scope, reviewed separately via AWS SOC 2)
- Multi-AZ deployment for availability; specific AWS regions not disclosed
- Fully cloud-based with no physical servers or offices in scope (HQ is a co-working space)
- Additional cloud providers: Vercel (compute) and Inngest (durable function queues) add diversity but also operational complexity
- Serverless component: Inngest Durable Function Queues
- Infrastructure-as-code with baseline configurations and rollback capability
- **Concern:** Single primary cloud provider (AWS) with no multi-region capability disclosed
- **Concern:** No CDN mentioned despite operating internet-facing AI services
- **Concern:** Specific AWS regions not named, limiting ability to assess geographic risk

### Application Architecture (Score: 5/10)
- Hybrid architecture with separate products: Alice (AI SDR) and Julian (AI Phone Agent)
- Julian architecture includes STYTCH for auth, AWS S3/RDS for storage, Vercel for compute, Inngest for queues, CRM integrations, and telephony (Twilio/WhatsApp)
- Branch protection enforced: repository rules require additional approval for production merges
- Code review required before merging to master branch
- Separate development/test and production environments
- **Concern:** No programming languages, frameworks, or specific compute services named in report text — architecture details only visible in diagrams
- **Concern:** API style not disclosed
- **Concern:** No container orchestration mentioned

### Data Layer (Score: 6/10)
- AWS RDS for relational database storage
- AWS S3 for file/object storage
- Daily backups with multi-AZ configuration and backup failure alerting
- Data classification policy established to categorize data by sensitivity and criticality
- Data retention policy in place
- Per-tenant data segregation confirmed (CC6.1.3)
- **Concern:** No caching layer mentioned — potential performance scalability gap
- **Concern:** No data warehouse or analytics infrastructure mentioned

### Security Posture (Score: 7/10)
- IDS/IPS deployed via AWS for threat detection and protection
- Firewalls configured on application gateway and production network; rules reviewed annually
- MFA enforced comprehensively: production admin access, remote access, source code tools, and email
- Anti-virus/anti-malware on all production servers (continuous scanning, weekly definition updates) and workstations
- Endpoint protection enabled on all devices
- Monthly automated vulnerability scanning with remediation plans for critical/high findings
- Annual external penetration testing by independent third party with remediation tracking
- Server hardening implemented
- Cybersecurity insurance in place
- Content filtering routed through proxy server
- Encryption: TLS in transit, AWS KMS for data at rest, end-to-end encryption claimed
- VPN access through bastion host for remote administration
- **Concern:** No WAF explicitly mentioned despite internet-facing AI services
- **Concern:** Specific TLS version not stated (should be TLS 1.2+ minimum)
- **Concern:** No SIEM tool named; specific monitoring and APM vendors not disclosed

### DevOps Maturity (Score: 6/10)
- Infrastructure-as-code with configuration management tool providing rollback capability
- Source code management with logging (time-stamped, attributed to author), MFA-protected access
- Branch protection requiring approval before production merges
- Separate dev/test and production environments
- Emergency change process documented
- Automatic patch management with monthly reviews by CTO; daily workstation compliance scanning
- Internal tool for tracking changes from initiation through deployment and validation
- **Concern:** Specific CI/CD tool not named — makes independent verification difficult
- **Concern:** Source control platform not named
- **Concern:** No container orchestration mentioned

### BCDR Readiness (Score: 6/10)
- BCDR policy documented, reviewed annually
- DR plans tested annually with multiple loss scenarios; plans updated based on test results
- Multi-AZ failover configured
- Daily backups with backup failure alerting
- **Concern:** No RTO/RPO targets disclosed despite having BCDR policy and testing
- **Concern:** No multi-region failover — single region dependency for a 24/7 AI service

---

## 2. Vendor Dependency Map

| Vendor | Criticality | Purpose | Risk |
|--------|------------|---------|------|
| AWS | Critical | Primary cloud infrastructure and data center services (subservice organization) | Single cloud provider dependency; carve-out method means AWS controls excluded from audit scope |
| STYTCH | Critical | Authentication and authorization for application users | Single point of failure for user authentication |
| Twilio | Critical | Telephony and voice for Julian AI Phone Agent | Core dependency for voice product; outage disables Julian |
| FIXIE (Proprietary Llama Models) | Critical | AI/LLM responses for Julian voice AI stack | Proprietary model dependency; operational complexity of self-hosted LLMs |
| Vercel | High | Cloud compute provider for Julian | Secondary compute dependency outside primary AWS footprint |
| Inngest | High | Durable function queues for async processing | Relatively niche vendor for critical async workloads |
| Salesforce | High | CRM integration | Customer-facing integration; degradation impacts pipeline automation |
| HubSpot | High | CRM integration | Customer-facing integration; degradation impacts pipeline automation |
| ElevenLabs | High | Voice synthesis for Julian real-time voice AI stack | Third-party AI dependency for core voice product capability |
| WhatsApp | High | Messaging channel for Julian | Platform policy changes could disrupt messaging capability |
| Zoho | Medium | CRM integration | Lower-tier CRM integration; limited blast radius |

**Vendor Analysis:** 11x relies on 11+ distinct third-party vendors across infrastructure, authentication, CRM, telephony, and AI/voice domains. Four vendors are rated Critical (AWS, STYTCH, Twilio, FIXIE), meaning outages at any of these could materially impact service availability. The vendor portfolio shows reasonable diversity with no extreme single-vendor lock-in, though AWS remains the dominant infrastructure dependency. Notably, 11x runs proprietary LLM models (FIXIE/Llama) rather than relying on mainstream LLM API providers — this carries both IP value and operational complexity. The formal vendor management program with SOC report reviews and quarterly risk assessments for non-SOC vendors is a positive governance signal.

---

## 3. Risk Assessment

### RED FLAGS
- **Very short audit period (3 months):** The May-August 2025 window is the minimum viable period for a Type 2 report, strongly suggesting this is 11x's first SOC 2 audit. A 3-month window provides limited assurance that controls operate consistently over time.
- **No RTO/RPO targets disclosed:** Despite having a documented BCDR policy and annual testing, the absence of stated recovery objectives means there is no measurable commitment to service restoration timelines.
- **Processing Integrity and Privacy criteria excluded:** For an AI company that autonomously handles customer prospect data, conducts outbound outreach, and makes decisions about lead qualification, excluding these trust criteria is a notable gap that warrants scrutiny.
- **Cybersecurity insurance control untestable:** Control CC3.2.1 could not be operationally tested due to no incidents during the audit period. While understandable, insurance coverage itself should be independently verifiable through policy documentation.
- **Julian product newly added to SOC 2 scope:** Adding a new product to scope during the audit period indicates a rapidly expanding system boundary that may outpace security controls maturation. Julian introduces telephony, voice AI, and messaging channels — a significant surface area expansion.

### YELLOW FLAGS
- **Security and DevOps tooling not named:** No specific CI/CD, SIEM, monitoring, or APM tools identified throughout the report, making independent verification and benchmarking difficult.
- **No WAF explicitly mentioned:** Internet-facing AI services handling customer data should have web application firewall protection.
- **No multi-region failover:** Single-region dependency for a platform marketed as operating 24/7 is a material availability risk.
- **TLS version not specified:** The report confirms TLS encryption but does not state the version; TLS 1.2+ should be the minimum.
- **Content filtering description is vague:** "Routed through proxy server" does not name the technology or approach.
- **4 controls untestable:** Due to no qualifying events during the short audit period (no role changes, no cyber incidents, no customer terminations, no security incidents).
- **Physical access exclusion (CC6.4):** Reasonable for cloud-only, but the HQ address is listed suggesting some physical presence exists.

### GREEN FLAGS
- **Clean unqualified opinion with zero exceptions** across all 55 tested controls — a strong result for a growth-stage company.
- **Comprehensive MFA enforcement:** Production access, remote access, source code tools, and email all require multi-factor authentication.
- **Infrastructure-as-code** with configuration management and rollback capability.
- **Branch protection** requiring approval before production merges — developers cannot push directly to production.
- **Annual external penetration testing** with remediation tracking for high/critical findings.
- **Monthly automated vulnerability scanning** with remediation plans for critical and high findings.
- **BCDR plans tested annually** with multiple loss scenarios and plan updates based on test results.
- **Daily backups** with multi-AZ deployment and backup failure alerting.
- **Formal vendor management program** with SOC report reviews and quarterly risk assessments for non-SOC vendors.
- **Data classification policy** implemented to categorize data by sensitivity.
- **Structured security governance:** RGEC meets semiannually; IT Leadership Committee meets weekly.
- **Access revocation within one business day** of employment termination.
- **Quarterly access reviews** for all user accounts including administrative privileges.

---

## 4. Compliance Summary

| Control Area | Status | Notes |
|-------------|--------|-------|
| Access Control | Pass | MFA enforced across production, remote, source code, and email. RBAC implemented. Quarterly access reviews. Access revoked within 1 business day of termination. Unique user IDs enforced. |
| Encryption | Pass | TLS in transit (version unspecified), AWS KMS at rest. End-to-end encryption claimed. Key access restricted to authorized individuals. |
| Change Management | Pass | Branch protection with approval required for production merges. Source code changes logged with timestamps and attribution. Separate dev/test and production environments. Emergency change process documented. |
| Monitoring | Pass | Automated alerts for high/critical events. Logging enabled for admin activities, logon attempts, data deletions, configuration changes, and permission changes. IDS deployed. Log protection enabled. |
| Vendor Management | Pass | Formal vendor management program. SOC report reviews for critical vendors. Quarterly risk assessments for vendors without SOC reports. 11+ vendors tracked. |
| BCDR | Pass | BCDR policy documented and reviewed annually. Annual DR testing with multiple loss scenarios. Multi-AZ failover. Daily backups with failure alerting. No RTO/RPO disclosed. |
| Vulnerability Mgmt | Pass | Monthly automated vulnerability scanning. Annual external penetration testing. Remediation plans for critical/high findings. Automatic patch management with monthly reviews. |

**Untested controls:** CC2.2.3 (no significant changes to people/roles during engagement period), CC3.2.1 (cybersecurity insurance — no cyber incidents to trigger testing), CC6.5.2 (customer data deletion upon termination — no customer terminations occurred), CC7.3.1 (incident response — no security incidents reported during engagement period).

---

## 5. Recommendation

**Investment Readiness: MODERATE**

11x AI Inc. demonstrates solid foundational security and compliance for a growth-stage AI company, achieving a clean SOC 2 Type 2 opinion with zero exceptions across 55 controls. The platform shows reasonable architectural maturity with multi-AZ deployment, IaC, comprehensive MFA, and structured security governance. However, the very short 3-month audit window, exclusion of Processing Integrity and Privacy criteria (notable for an autonomous AI outreach platform), undisclosed RTO/RPO targets, and lack of specificity around key tooling limit confidence. The overall score of 6/10 reflects a company that has established the right frameworks but needs more operational history and transparency to inspire high confidence.

Key follow-up items:
1. Request the full 12-month SOC 2 Type 2 report when available — the 3-month window is insufficient to assess sustained operational effectiveness of controls.
2. Ask 11x to disclose specific RTO/RPO targets and provide evidence of DR test results demonstrating recovery within those targets.
3. Inquire why Processing Integrity and Privacy trust criteria were excluded, and request a timeline for their inclusion given the AI platform autonomously handles prospect data and conducts outreach.
4. Request details on the specific CI/CD pipeline, SIEM, monitoring/APM tools, and source control platform in use — the absence of named tooling is unusual and impedes technical benchmarking.
5. Ask for clarification on the "end-to-end encryption" claim: what exactly is encrypted E2E given the platform sends outbound emails, LinkedIn messages, and phone calls?
6. Request a technical deep-dive on the FIXIE/Llama proprietary model infrastructure — hosting costs, model update cadence, performance benchmarks, and fallback strategy if proprietary models underperform.
