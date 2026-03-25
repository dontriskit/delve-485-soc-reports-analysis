# SKILL: Extract Tech Data from Compliance Report PDF

## Purpose
Read a single company's SOC 2 or ISO 27001 compliance report PDF and extract all technology/infrastructure data into a structured JSON file for Tech Due Diligence.

## Inputs
- `DOC_ID`: The Google Doc ID (matches PDF filename without extension)
- `COMPANY_DB`: Path to `company_db/` directory (default: `company_db/`)
- `PDF_DIR`: Path to `pdf_reports/` directory (default: `pdf_reports/`)

## Procedure

### Step 1: Load company metadata
Read `{COMPANY_DB}/{DOC_ID}.json` to get:
- `display_name`, `legal_name`, `company_name`
- `report_type` (SOC 2 Type 1, SOC 2 Type 2, ISO 27001)
- `infra_provider`, `website`, `system_description`
- `pdf_file` (confirm it exists)

### Step 2: Read the PDF
Read `{PDF_DIR}/{DOC_ID}.pdf` in chunks of 20 pages (the Read tool max).
- First get page count via: `pdfinfo {PDF_DIR}/{DOC_ID}.pdf | grep Pages`
- Read pages: 1-20, 21-40, 41-60, ... until end
- Focus especially on:
  - **System Description section** (usually pages 10-25)
  - **Control descriptions** (usually pages 25-60)
  - **Network/architecture diagrams** (look for diagram descriptions)
  - **Trust criteria testing results** (usually pages 40-end)

### Step 3: Extract structured data
From the full report text, extract ALL of the following dimensions. For each dimension, capture every specific technology, vendor, tool, or practice mentioned. Quote relevant passages where useful.

```json
{
  "company": "Legal entity name",
  "product": "Product/brand name",
  "report_type": "SOC 2 Type 1 | SOC 2 Type 2 | ISO 27001",
  "audit_period": "Start - End date",
  "auditor": "Audit firm name",
  "opinion": "Qualified | Unqualified | With exceptions",
  "trust_criteria": ["Security", "Availability", ...],
  "hq": "Address",
  "signing_authority": "Name, Title",

  "system_description": {
    "overview": "What the product does in 2-3 sentences",
    "products": {"product_name": "description", ...}
  },

  "infrastructure": {
    "cloud_provider": "Primary cloud + method (carve-out/inclusive)",
    "regions": ["us-east-1", ...],
    "physical_presence": "None / Office address",
    "availability_zones": "Single-AZ | Multi-AZ",
    "additional_cloud": ["Vercel", "Render", ...],
    "serverless": ["Lambda", "Cloud Functions", ...],
    "cdn": "CloudFront / Cloudflare / None mentioned"
  },

  "network_architecture": {
    "vpc": true/false,
    "network_segmentation": "Description of segmentation approach",
    "api_gateway": "Service name or null",
    "waf": "Service name or null",
    "firewalls": "Description",
    "ids_ips": "Description",
    "vpn": "Description",
    "tls": "Description",
    "content_filtering": "Description or null",
    "multi_region": true/false,
    "topology": "Brief text description of traffic flow"
  },

  "application_architecture": {
    "pattern": "Monolith | Microservices | Serverless-heavy | Hybrid",
    "languages": ["Python", "TypeScript", ...],
    "frameworks": ["Next.js", "Django", ...],
    "compute": ["EC2", "Lambda", "ECS", ...],
    "api_style": "REST | GraphQL | gRPC",
    "environments": "How many, how separated",
    "branch_protection": true/false,
    "code_review_required": true/false
  },

  "data_storage": {
    "databases": ["RDS", "DynamoDB", ...],
    "caching": ["Redis", "ElastiCache", ...],
    "file_storage": ["S3", ...],
    "data_warehouse": "BigQuery / Redshift / None",
    "backup_frequency": "Daily / Hourly / etc",
    "multi_az": true/false,
    "data_classification_policy": true/false,
    "data_retention_policy": true/false,
    "per_tenant_segregation": true/false
  },

  "authentication_access_control": {
    "identity_provider": "STYTCH / Auth0 / Okta / AWS IAM / etc",
    "mfa": "Description of where MFA is enforced",
    "rbac": true/false,
    "sso": true/false,
    "unique_user_ids": true/false,
    "quarterly_access_reviews": true/false,
    "access_revocation_sla": "Within X hours/days",
    "password_policy": "Description"
  },

  "encryption": {
    "in_transit": "TLS version if specified",
    "at_rest": "KMS / AES-256 / etc",
    "key_management": "AWS KMS / Vault / etc",
    "end_to_end": true/false
  },

  "ci_cd_devops": {
    "source_control": "GitHub / GitLab / Bitbucket",
    "ci_cd_tool": "GitHub Actions / CircleCI / Jenkins / etc",
    "branch_protection": "Description of merge rules",
    "iac": "Terraform / CloudFormation / Pulumi / etc",
    "container_orchestration": "ECS / EKS / K8s / None",
    "patch_management": "Description",
    "separate_environments": true/false,
    "emergency_change_process": true/false
  },

  "monitoring_logging": {
    "apm_tool": "Datadog / New Relic / etc",
    "siem": "Splunk / Sentinel / etc",
    "log_aggregation": "CloudWatch / ELK / etc",
    "alerting": "PagerDuty / OpsGenie / etc",
    "metrics": ["CPU", "disk", "network", ...],
    "log_protection": true/false,
    "ids": true/false
  },

  "third_party_services": [
    {"vendor": "Name", "purpose": "What it does", "criticality": "Critical|High|Medium|Low"}
  ],

  "security_tools": {
    "waf": true/false,
    "ids_ips": true/false,
    "antivirus": "Description",
    "endpoint_protection": true/false,
    "vulnerability_scanning": "Frequency + tool if named",
    "penetration_testing": "Frequency + internal/external",
    "server_hardening": true/false,
    "cybersecurity_insurance": true/false
  },

  "bcdr": {
    "bcdr_policy": true/false,
    "annual_review": true/false,
    "annual_testing": true/false,
    "multi_az_failover": true/false,
    "multi_region_failover": true/false,
    "daily_backups": true/false,
    "rto": "X hours or 'Not disclosed'",
    "rpo": "X hours or 'Not disclosed'"
  },

  "compliance_controls": {
    "total_controls_tested": 0,
    "exceptions": 0,
    "untestable": ["CC2.2.3 reason", ...],
    "excluded_criteria": ["CC6.4 reason", ...],
    "notable_controls": ["Description of interesting controls"]
  },

  "scoring": {
    "infrastructure": {"score": 0, "max": 10, "rationale": ""},
    "application_architecture": {"score": 0, "max": 10, "rationale": ""},
    "data_layer": {"score": 0, "max": 10, "rationale": ""},
    "security_posture": {"score": 0, "max": 10, "rationale": ""},
    "devops_maturity": {"score": 0, "max": 10, "rationale": ""},
    "bcdr_readiness": {"score": 0, "max": 10, "rationale": ""},
    "vendor_diversity": {"score": 0, "max": 10, "rationale": ""},
    "overall": {"score": 0, "max": 10, "rationale": ""}
  },

  "red_flags": ["List of concerns"],
  "yellow_flags": ["List of moderate risks"],
  "green_flags": ["List of strengths"],
  "key_observations": ["Non-obvious insights"]
}
```

### Step 4: Score each dimension
Apply these scoring guidelines:

| Dimension | 8-10 | 5-7 | 1-4 |
|-----------|------|-----|-----|
| Infrastructure | Multi-region, multi-AZ, IaC, CDN | Single region multi-AZ, basic IaC | Single AZ, manual |
| App Architecture | Microservices, typed, tested | Modular monolith, some tests | Monolith, no tests mentioned |
| Data Layer | Multi-DB types, caching, warehouse, backups | Single DB + backups | No specifics disclosed |
| Security | WAF + IDS + pen test + vuln scan + SIEM | Firewall + pen test + basic scanning | Minimal disclosure |
| DevOps | Named CI/CD + IaC + containers + branch protection | IaC + branch protection, tools unnamed | Manual deployment |
| BCDR | Tested DR, stated RTO/RPO, multi-region | Annual DR test, daily backups, no RTO/RPO | Policy exists but untested |
| Vendor Diversity | 5+ vendors, no single critical dependency | 2-4 vendors, manageable concentration | Single vendor or undisclosed |

### Step 5: Save output
Write the complete JSON to: `{COMPANY_DB}/{DOC_ID}_tech_extract.json`

## Output
- `{COMPANY_DB}/{DOC_ID}_tech_extract.json` — structured extraction with scores

## Error Handling
- If PDF has fewer than 10 pages, flag as potentially incomplete report
- If report type is ISO 27001, many tech fields will be empty — this is expected (ISO reports are less detailed than SOC 2)
- If no network diagram description found, note "No diagram described in report"
- Always produce output even if partial — set missing fields to null with a note
