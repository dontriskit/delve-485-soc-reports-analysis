"""Merge per-page extraction fragments into a single company tech extract."""
import json


def merge_page_fragments(doc_id: str, page_results: list[dict | None], company_meta: dict) -> dict:
    """Merge page-level extractions into the full schema."""
    merged = {
        "company": None,
        "product": company_meta.get("display_name", "Unknown"),
        "report_type": company_meta.get("report_type", "Unknown"),
        "audit_period": None,
        "auditor": None,
        "opinion": None,
        "trust_criteria": [],
        "hq": None,
        "signing_authority": None,
        "system_description": {"overview": "", "products": {}},
        "infrastructure": {
            "cloud_provider": company_meta.get("infra_provider", None),
            "regions": [], "physical_presence": None,
            "availability_zones": None, "additional_cloud": [],
            "serverless": [], "cdn": None,
        },
        "network_architecture": {
            "vpc": False, "network_segmentation": None, "api_gateway": None,
            "waf": None, "firewalls": None, "ids_ips": None, "vpn": None,
            "tls": None, "content_filtering": None, "multi_region": False,
            "topology": None, "diagram_detail": None,
        },
        "application_architecture": {
            "pattern": None, "languages": [], "frameworks": [],
            "compute": [], "api_style": None, "environments": None,
            "branch_protection": False, "code_review_required": False,
        },
        "data_storage": {
            "databases": [], "caching": [], "file_storage": [],
            "data_warehouse": None, "backup_frequency": None,
            "multi_az": False, "data_classification_policy": False,
            "data_retention_policy": False, "per_tenant_segregation": False,
        },
        "authentication_access_control": {
            "identity_provider": None, "mfa": None, "rbac": False,
            "sso": False, "unique_user_ids": False,
            "quarterly_access_reviews": False, "access_revocation_sla": None,
            "password_policy": None,
        },
        "encryption": {
            "in_transit": None, "at_rest": None,
            "key_management": None, "end_to_end": False,
        },
        "ci_cd_devops": {
            "source_control": None, "ci_cd_tool": None,
            "branch_protection": None, "iac": None,
            "container_orchestration": None, "patch_management": None,
            "separate_environments": False, "emergency_change_process": False,
        },
        "monitoring_logging": {
            "apm_tool": None, "siem": None, "log_aggregation": None,
            "alerting": None, "metrics": [], "log_protection": False, "ids": False,
        },
        "third_party_services": [],
        "security_tools": {
            "waf": False, "ids_ips": False, "antivirus": None,
            "endpoint_protection": False, "vulnerability_scanning": None,
            "penetration_testing": None, "server_hardening": False,
            "cybersecurity_insurance": False,
        },
        "bcdr": {
            "bcdr_policy": False, "annual_review": False, "annual_testing": False,
            "multi_az_failover": False, "multi_region_failover": False,
            "daily_backups": False, "rto": "Not disclosed", "rpo": "Not disclosed",
        },
        "compliance_controls": {
            "total_controls_tested": 0, "exceptions": 0,
            "untestable": [], "excluded_criteria": [], "notable_controls": [],
        },
        "scoring": {},
        "red_flags": [],
        "yellow_flags": [],
        "green_flags": [],
        "key_observations": [],
        "_page_count": 0,
        "_diagram_pages": [],
        "_template_pages": [],
    }

    all_vendors = set()
    all_databases = set()
    all_security_tools = set()
    all_control_ids = set()
    all_exceptions = []
    sys_desc_parts = []

    for i, page in enumerate(page_results):
        if page is None:
            continue
        merged["_page_count"] += 1

        # Metadata (first non-null wins)
        if page.get("company_name") and not merged["company"]:
            merged["company"] = page["company_name"]
        if page.get("signing_authority") and not merged["signing_authority"]:
            merged["signing_authority"] = page["signing_authority"]
        if page.get("audit_period") and not merged["audit_period"]:
            merged["audit_period"] = page["audit_period"]
        if page.get("auditor") and not merged["auditor"]:
            merged["auditor"] = page["auditor"]
        if page.get("opinion") and not merged["opinion"]:
            merged["opinion"] = page["opinion"]
        if page.get("hq_address") and not merged["hq"]:
            merged["hq"] = page["hq_address"]
        if page.get("report_type") and merged["report_type"] == "Unknown":
            merged["report_type"] = page["report_type"]

        # Diagrams
        if page.get("has_diagram"):
            merged["_diagram_pages"].append(i + 1)

        # Template artifacts
        if page.get("is_template_placeholder"):
            merged["_template_pages"].append(i + 1)
            if page.get("template_artifacts"):
                merged["key_observations"].append(
                    f"Page {i+1}: Template artifact — {page['template_artifacts']}"
                )

        # System description
        if page.get("system_description_text"):
            sys_desc_parts.append(page["system_description_text"])

        # Cloud provider
        if page.get("cloud_provider"):
            cp = page["cloud_provider"]
            if not merged["infrastructure"]["cloud_provider"]:
                merged["infrastructure"]["cloud_provider"] = cp
            elif cp not in merged["infrastructure"]["cloud_provider"]:
                merged["infrastructure"]["additional_cloud"].append(cp)

        # Infrastructure
        if page.get("infrastructure_details"):
            txt = page["infrastructure_details"]
            if "multi-az" in txt.lower() or "multi az" in txt.lower():
                merged["infrastructure"]["availability_zones"] = "Multi-AZ"
                merged["data_storage"]["multi_az"] = True
            if "multi-region" in txt.lower() or "multi region" in txt.lower():
                merged["network_architecture"]["multi_region"] = True
            if "vpc" in txt.lower():
                merged["network_architecture"]["vpc"] = True

        # Network architecture
        if page.get("network_architecture_details"):
            txt = page["network_architecture_details"]
            if not merged["network_architecture"]["topology"]:
                merged["network_architecture"]["topology"] = txt
            elif len(txt) > len(merged["network_architecture"]["topology"] or ""):
                merged["network_architecture"]["topology"] = txt
            # Detect features
            lower = txt.lower()
            if "firewall" in lower and not merged["network_architecture"]["firewalls"]:
                merged["network_architecture"]["firewalls"] = txt
            if "ids" in lower or "ips" in lower:
                merged["network_architecture"]["ids_ips"] = txt
                merged["security_tools"]["ids_ips"] = True
            if "waf" in lower:
                merged["network_architecture"]["waf"] = txt
                merged["security_tools"]["waf"] = True
            if "vpn" in lower or "bastion" in lower:
                merged["network_architecture"]["vpn"] = txt
            if "tls" in lower:
                merged["network_architecture"]["tls"] = txt

        # Auth
        if page.get("auth_details"):
            txt = page["auth_details"]
            if "mfa" in txt.lower():
                merged["authentication_access_control"]["mfa"] = txt
            if "rbac" in txt.lower() or "role-based" in txt.lower():
                merged["authentication_access_control"]["rbac"] = True
            if "quarterly" in txt.lower() and "review" in txt.lower():
                merged["authentication_access_control"]["quarterly_access_reviews"] = True

        # Encryption
        if page.get("encryption_details"):
            txt = page["encryption_details"]
            if "transit" in txt.lower() and not merged["encryption"]["in_transit"]:
                merged["encryption"]["in_transit"] = txt
            if "rest" in txt.lower() and not merged["encryption"]["at_rest"]:
                merged["encryption"]["at_rest"] = txt
            if "kms" in txt.lower():
                merged["encryption"]["key_management"] = txt

        # CI/CD
        if page.get("cicd_details"):
            txt = page["cicd_details"]
            if "branch" in txt.lower() and "protection" in txt.lower():
                merged["application_architecture"]["branch_protection"] = True
                merged["ci_cd_devops"]["branch_protection"] = txt
            if "infrastructure as code" in txt.lower() or "iac" in txt.lower():
                merged["ci_cd_devops"]["iac"] = txt

        # Monitoring
        if page.get("monitoring_details"):
            if not merged["monitoring_logging"]["alerting"]:
                merged["monitoring_logging"]["alerting"] = page["monitoring_details"]

        # BCDR
        if page.get("bcdr_details"):
            txt = page["bcdr_details"]
            if "daily" in txt.lower() and "backup" in txt.lower():
                merged["bcdr"]["daily_backups"] = True
                merged["data_storage"]["backup_frequency"] = "Daily"
            if "annual" in txt.lower() and "test" in txt.lower():
                merged["bcdr"]["annual_testing"] = True
            merged["bcdr"]["bcdr_policy"] = True

        # Vendors
        for v in page.get("vendors_mentioned", []):
            all_vendors.add(v)

        # Databases
        for d in page.get("databases_mentioned", []):
            all_databases.add(d)

        # Security tools
        for s in page.get("security_tools_mentioned", []):
            all_security_tools.add(s)

        # Controls
        for c in page.get("control_ids_tested", []):
            all_control_ids.add(c)
        for e in page.get("exceptions_noted", []):
            all_exceptions.append(e)

    # Finalize
    if sys_desc_parts:
        merged["system_description"]["overview"] = " ".join(sys_desc_parts)

    merged["data_storage"]["databases"] = sorted(all_databases)
    merged["third_party_services"] = [
        {"vendor": v, "purpose": "Identified in report", "criticality": "Unknown"}
        for v in sorted(all_vendors)
    ]
    merged["compliance_controls"]["total_controls_tested"] = len(all_control_ids)
    merged["compliance_controls"]["exceptions"] = len(all_exceptions)

    # Use company_meta fallback
    if not merged["company"]:
        merged["company"] = company_meta.get("legal_name") or company_meta.get("display_name", "Unknown")

    return merged
