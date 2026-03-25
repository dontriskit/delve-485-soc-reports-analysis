"""JSON schemas for per-page extraction and diagram detail extraction."""

PAGE_EXTRACTION_SCHEMA = {
    "name": "page_extraction",
    "schema": {
        "type": "object",
        "properties": {
            "page_type": {
                "type": "string",
                "enum": [
                    "cover", "toc", "opinion_letter", "system_description",
                    "network_diagram", "org_chart", "controls_testing",
                    "control_description", "appendix", "other"
                ]
            },
            "has_diagram": {"type": "boolean"},
            "company_name": {"type": ["string", "null"]},
            "signing_authority": {"type": ["string", "null"]},
            "report_type": {"type": ["string", "null"]},
            "audit_period": {"type": ["string", "null"]},
            "auditor": {"type": ["string", "null"]},
            "opinion": {"type": ["string", "null"]},
            "hq_address": {"type": ["string", "null"]},
            "system_description_text": {"type": ["string", "null"]},
            "cloud_provider": {"type": ["string", "null"]},
            "infrastructure_details": {"type": ["string", "null"]},
            "network_architecture_details": {"type": ["string", "null"]},
            "application_details": {"type": ["string", "null"]},
            "databases_mentioned": {"type": "array", "items": {"type": "string"}},
            "vendors_mentioned": {"type": "array", "items": {"type": "string"}},
            "security_tools_mentioned": {"type": "array", "items": {"type": "string"}},
            "auth_details": {"type": ["string", "null"]},
            "encryption_details": {"type": ["string", "null"]},
            "cicd_details": {"type": ["string", "null"]},
            "monitoring_details": {"type": ["string", "null"]},
            "bcdr_details": {"type": ["string", "null"]},
            "control_ids_tested": {"type": "array", "items": {"type": "string"}},
            "exceptions_noted": {"type": "array", "items": {"type": "string"}},
            "is_template_placeholder": {"type": "boolean"},
            "template_artifacts": {"type": ["string", "null"]},
        },
        "required": ["page_type", "has_diagram", "is_template_placeholder"]
    }
}

DIAGRAM_DETAIL_SCHEMA = {
    "name": "diagram_detail",
    "schema": {
        "type": "object",
        "properties": {
            "diagram_type": {
                "type": "string",
                "enum": ["network_architecture", "application_architecture",
                         "data_flow", "org_chart", "deployment", "other"]
            },
            "components": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "details": {"type": ["string", "null"]},
                        "zone": {"type": ["string", "null"]}
                    },
                    "required": ["name", "type"]
                }
            },
            "connections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "from_component": {"type": "string"},
                        "to_component": {"type": "string"},
                        "label": {"type": ["string", "null"]},
                        "protocol": {"type": ["string", "null"]},
                        "bidirectional": {"type": "boolean"}
                    },
                    "required": ["from_component", "to_component"]
                }
            },
            "zones": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": ["string", "null"]},
                        "components": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name"]
                }
            },
            "traffic_flow_description": {"type": "string"},
            "cloud_providers_visible": {"type": "array", "items": {"type": "string"}},
            "is_sample_placeholder": {"type": "boolean"}
        },
        "required": ["diagram_type", "components", "connections", "traffic_flow_description", "is_sample_placeholder"]
    }
}

SYSTEM_PROMPT_PAGE = """You are analyzing a SINGLE PAGE from a SOC 2 / ISO 27001 compliance report.
Extract ALL technology, infrastructure, and security data visible on THIS page only.
Be precise — only report what you can actually see on this page.

Key things to look for:
- Company name, auditor, report type, audit dates, signing authority
- Cloud providers (AWS, GCP, Azure, Supabase, Vercel, Render, etc.)
- Specific technologies: databases, languages, frameworks, CI/CD tools, monitoring tools
- Network architecture: VPC, firewalls, IDS/IPS, WAF, load balancers, CDN
- Third-party vendors and integrations
- Security controls: MFA, RBAC, encryption, pen testing frequency
- BCDR: backup frequency, RTO/RPO, failover strategy
- If this is a DIAGRAM page, describe every component and connection visible
- If you see yellow-highlighted template instructions or "Your Name Here" placeholders, flag is_template_placeholder=true

Many reports use Accorp Partners templates — focus on UNIQUE content that differs from boilerplate."""

SYSTEM_PROMPT_DIAGRAM = """You are analyzing an infrastructure/network architecture diagram from a compliance report.
Extract EVERY component, connection, and zone visible in this diagram with maximum detail.
Name every service, database, API, cloud provider, and external integration you can see.
Describe the complete traffic flow from users/internet through all layers to data storage.
If this is a SAMPLE/PLACEHOLDER diagram (e.g., has instructions to replace), set is_sample_placeholder=true."""
