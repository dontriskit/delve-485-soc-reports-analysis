"""
Shared data loader for all report modules.
Loads once, cached on import.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
from functools import lru_cache

BASE = Path(__file__).resolve().parent.parent.parent  # delve/
DATA = BASE / "data_export"


def _norm_cloud(cp):
    if pd.isna(cp) or cp == '': return 'Unknown'
    cp = str(cp).lower()
    for name, key in [('aws','AWS'),('amazon','AWS'),('gcp','GCP'),('google','GCP'),
                       ('azure','Azure'),('supabase','Supabase'),('vercel','Vercel'),
                       ('render','Render'),('digitalocean','DigitalOcean'),('fly','Fly.io'),
                       ('railway','Railway'),('oracle','Oracle'),('heroku','Heroku')]:
        if name in cp: return key
    return 'Other'


def _parse_json_field(val):
    if not val or pd.isna(val): return []
    if isinstance(val, list): return val
    try: return json.loads(val)
    except: return []


@lru_cache(maxsize=1)
def load_all():
    """Load and prepare all data. Returns a namespace dict."""

    # Main CSV
    df = pd.read_csv(DATA / "companies_clean.csv")
    if 'cloud' not in df.columns:
        df['cloud'] = df.cloud_provider.apply(_norm_cloud)
    df['type'] = df.report_type.replace({
        'SOC 2 Type II': 'Type 2', 'SOC 2 Type I': 'Type 1',
        'SOC 2 Type 2': 'Type 2', 'SOC 2 Type 1': 'Type 1',
    })

    # Scored subset
    scored = df[df.score_overall.notna()].copy()

    # Full JSON extracts
    with open(DATA / "tech_extracts_full.json") as f:
        extracts = json.load(f)
    extract_map = {e['doc_id']: e for e in extracts}

    # Parse vendors
    all_vendors = Counter()
    vendor_rows = []
    for e in extracts:
        v = e.get('third_party_services')
        if isinstance(v, str):
            try: v = json.loads(v)
            except: v = []
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and item.get('vendor'):
                    vname = item['vendor']
                    all_vendors[vname] += 1
                    vendor_rows.append({
                        'doc_id': e['doc_id'],
                        'company': e.get('company', ''),
                        'vendor': vname,
                        'purpose': item.get('purpose', ''),
                        'criticality': item.get('criticality', ''),
                    })
    vendors_df = pd.DataFrame(vendor_rows) if vendor_rows else pd.DataFrame()

    # Parse flags
    all_red_flags = []
    all_yellow_flags = []
    all_green_flags = []
    all_observations = []
    for e in extracts:
        for color, target in [('red_flags', all_red_flags), ('yellow_flags', all_yellow_flags),
                               ('green_flags', all_green_flags), ('key_observations', all_observations)]:
            flags = e.get(color)
            if isinstance(flags, str):
                try: flags = json.loads(flags)
                except: flags = []
            if isinstance(flags, list):
                target.extend([f for f in flags if isinstance(f, str) and len(f) > 5])

    N = len(df)
    NS = len(scored)

    SCORE_COLS = ['score_overall', 'score_infrastructure', 'score_app_architecture',
                  'score_data_layer', 'score_security', 'score_devops',
                  'score_bcdr', 'score_vendor_diversity']
    DIM_LABELS = ['Overall', 'Infrastructure', 'App Arch', 'Data Layer',
                  'Security', 'DevOps', 'BCDR', 'Vendor Div']

    BOOL_FEATURES = [
        'has_vpc', 'has_waf', 'has_firewall', 'has_ids_ips', 'has_vpn', 'has_tls',
        'has_mfa', 'has_rbac', 'has_vuln_scanning', 'has_pen_testing',
        'has_server_hardening', 'has_cyber_insurance', 'has_bcdr_policy',
        'annual_dr_testing', 'daily_backups', 'multi_az', 'multi_region',
        'branch_protection', 'quarterly_reviews', 'per_tenant_segregation',
    ]

    return {
        'df': df, 'scored': scored, 'extracts': extracts, 'extract_map': extract_map,
        'vendors_df': vendors_df, 'all_vendors': all_vendors,
        'all_red_flags': all_red_flags, 'all_yellow_flags': all_yellow_flags,
        'all_green_flags': all_green_flags, 'all_observations': all_observations,
        'N': N, 'NS': NS,
        'SCORE_COLS': SCORE_COLS, 'DIM_LABELS': DIM_LABELS,
        'BOOL_FEATURES': BOOL_FEATURES,
        'parse_json': _parse_json_field,
    }


# Convenience: module-level access
def get():
    return load_all()
