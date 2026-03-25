"""
Generate D2 infrastructure diagrams for all 485 companies from structured data.
Deterministic template — no AI needed, zero syntax errors.
Renders via ~/.local/bin/d2 with ELK layout + dark theme.
"""
import json
import os
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

OUTPUT = Path("reports/d2_diagrams")
OUTPUT.mkdir(parents=True, exist_ok=True)

with open("data_export/tech_extracts_full.json") as f:
    extracts = json.load(f)


def p(field):
    if not field: return {}
    if isinstance(field, (dict, list)): return field
    try: return json.loads(field)
    except: return {}


def safe_id(name):
    """Make a valid D2 node ID."""
    return name.replace(" ", "_").replace(".", "").replace("/", "_").replace("(", "").replace(")", "").replace(",", "").replace("-", "_").replace("&", "and").replace("'", "").replace('"', '').replace("+", "plus")[:40]


def generate_d2(extract):
    """Generate D2 source from a tech extract."""
    company = extract.get('company') or extract.get('product') or 'Unknown'
    rtype = extract.get('report_type', '')
    infra = p(extract.get('infrastructure'))
    net = p(extract.get('network_architecture'))
    app = p(extract.get('application_architecture'))
    storage = p(extract.get('data_storage'))
    auth = p(extract.get('authentication'))
    sec = p(extract.get('security_tools'))
    bcdr = p(extract.get('bcdr'))
    vendors = p(extract.get('third_party_services'))
    if not isinstance(vendors, list): vendors = []

    cloud = infra.get('cloud_provider', 'Cloud')
    if isinstance(cloud, str):
        cloud_short = 'AWS' if 'aws' in cloud.lower() else 'GCP' if 'gcp' in cloud.lower() or 'google' in cloud.lower() else 'Azure' if 'azure' in cloud.lower() else 'Supabase' if 'supabase' in cloud.lower() else 'Vercel' if 'vercel' in cloud.lower() else 'Render' if 'render' in cloud.lower() else 'DigitalOcean' if 'digital' in cloud.lower() else cloud[:20]
    else:
        cloud_short = 'Cloud'

    regions = infra.get('regions', [])
    if isinstance(regions, list) and regions:
        region_text = ", ".join(str(r) for r in regions[:3])
    else:
        region_text = "Single Region"

    has_multi_az = bool(infra.get('availability_zones') and 'multi' in str(infra.get('availability_zones', '')).lower())
    has_multi_region = bool(net.get('multi_region'))

    d2 = f"""direction: down

title: |md
  # {company}
  {rtype} · {cloud_short} · {region_text}
| {{
  near: top-center
  style.font-size: 24
}}

users: Users / Clients {{
  shape: image
  icon: https://icons.terrastruct.com/essentials%2F359-users.svg
}}

"""

    # Perimeter
    perimeter_items = []
    if net.get('firewalls'): perimeter_items.append(('fw', 'Firewall', 'hexagon'))
    if net.get('ids_ips'): perimeter_items.append(('ids', 'IDS / IPS', 'hexagon'))
    if net.get('tls'): perimeter_items.append(('tls', 'TLS', 'hexagon'))
    if net.get('waf'): perimeter_items.append(('waf', 'WAF', 'hexagon'))
    if net.get('vpn'): perimeter_items.append(('vpn', 'VPN / Bastion', 'hexagon'))

    if perimeter_items:
        d2 += """perimeter: Perimeter {
  style.fill: "#2a1a1a"
  style.stroke: "#ef4444"
  style.font-color: "#fca5a5"
  style.border-radius: 8
"""
        for pid, label, shape in perimeter_items:
            d2 += f"""  {pid}: {label} {{
    shape: {shape}
    style.fill: "#3a1a1a"
    style.stroke: "#ef4444"
    style.font-color: "#fca5a5"
  }}
"""
        d2 += "}\n\n"

    # Main cloud container
    az_label = "Multi-AZ" if has_multi_az else ""
    mr_label = "Multi-Region" if has_multi_region else ""
    cloud_label = f"{cloud_short} {az_label} {mr_label}".strip()

    d2 += f"""cloud: {cloud_label} {{
  style.fill: "#0f1a0a"
  style.stroke: "#ff9900"
  style.font-color: "#ff9900"
  style.font-size: 16
  style.border-radius: 10
"""

    # Auth inside cloud
    auth_provider = ''
    if isinstance(auth, dict):
        auth_provider = auth.get('identity_provider', '')
    if auth_provider:
        auth_label = str(auth_provider)[:30]
        d2 += f"""  auth: Auth ({auth_label}) {{
    style.fill: "#2a2a0a"
    style.stroke: "#f59e0b"
    style.font-color: "#fde68a"
  }}
"""

    # Compute
    compute_items = app.get('compute', [])
    if isinstance(compute_items, list) and compute_items:
        d2 += """  compute: Compute {
    style.fill: "#0a0f1a"
    style.stroke: "#3b82f6"
    style.font-color: "#93c5fd"
    style.border-radius: 8
"""
        for i, c in enumerate(compute_items[:5]):
            cid = safe_id(str(c))
            d2 += f"""    c{i}: {str(c)[:35]} {{
      style.fill: "#0f1a2e"
      style.stroke: "#3b82f6"
      style.font-color: "#93c5fd"
    }}
"""
        d2 += "  }\n"

    # Databases
    dbs = storage.get('databases', [])
    cache = storage.get('caching', [])
    if isinstance(dbs, list) and dbs:
        d2 += """  data: Data {
    style.fill: "#1a1a0a"
    style.stroke: "#ff9900"
    style.font-color: "#fcd34d"
    style.border-radius: 8
"""
        for i, db in enumerate(dbs[:4]):
            d2 += f"""    db{i}: {str(db)[:30]} {{
      shape: cylinder
      style.fill: "#2a1f0a"
      style.stroke: "#ff9900"
      style.font-color: "#fcd34d"
    }}
"""
        if isinstance(cache, list):
            for i, c in enumerate(cache[:2]):
                if c and str(c).lower() not in ('not mentioned', 'none', ''):
                    d2 += f"""    cache{i}: {str(c)[:25]} {{
      style.fill: "#2a1f0a"
      style.stroke: "#f97316"
      style.font-color: "#fdba74"
    }}
"""
        d2 += "  }\n"

    # Security
    sec_items = []
    if sec.get('vulnerability_scanning'): sec_items.append('Vuln Scan')
    if sec.get('penetration_testing'): sec_items.append('Pen Test')
    if sec.get('server_hardening'): sec_items.append('Hardening')
    if sec.get('cybersecurity_insurance'): sec_items.append('Cyber Insurance')

    if sec_items:
        d2 += """  security: Security {
    style.fill: "#0a1a1a"
    style.stroke: "#38bdf8"
    style.font-color: "#7dd3fc"
    style.border-radius: 8
"""
        for i, s in enumerate(sec_items[:4]):
            d2 += f"""    s{i}: {s} {{
      style.fill: "#0f1a2a"
      style.stroke: "#38bdf8"
      style.font-color: "#7dd3fc"
    }}
"""
        d2 += "  }\n"

    d2 += "}\n\n"

    # Vendor integrations
    vendor_nodes = []
    for v in vendors[:8]:
        if isinstance(v, dict):
            name = v.get('vendor', '')
            if name and len(name) > 2 and name.lower() not in ('accorp partners', 'accorp', 'not disclosed'):
                vid = safe_id(name)
                criticality = v.get('criticality', 'Medium')
                color = '#ef4444' if criticality == 'Critical' else '#f59e0b' if criticality == 'High' else '#22c55e'
                vendor_nodes.append((vid, name[:25], color))

    if vendor_nodes:
        d2 += """vendors: Integrations {
  style.fill: "#0a1a0f"
  style.stroke: "#10b981"
  style.font-color: "#6ee7b7"
  style.border-radius: 8
"""
        for vid, label, color in vendor_nodes:
            d2 += f"""  {vid}: {label} {{
    style.fill: "#0a2a1a"
    style.stroke: "{color}"
    style.font-color: "#e2e8f0"
  }}
"""
        d2 += "}\n\n"

    # Connections
    if perimeter_items:
        d2 += 'users -> perimeter: HTTPS {style.stroke: "#888"}\n'
        d2 += 'perimeter -> cloud: filtered {style.stroke: "#ef4444"}\n'
    else:
        d2 += 'users -> cloud: HTTPS {style.stroke: "#888"}\n'

    if auth_provider and compute_items:
        d2 += 'cloud.auth -> cloud.compute: authorize {style.stroke: "#f59e0b"; style.stroke-dash: 5}\n'
    if compute_items and dbs:
        d2 += 'cloud.compute -> cloud.data: read/write {style.stroke: "#ff9900"}\n'
    if vendor_nodes:
        d2 += 'cloud -> vendors: integrate {style.stroke: "#10b981"; style.stroke-dash: 5}\n'

    return d2


def render_d2(doc_id, d2_code):
    """Write D2 file and render to PNG."""
    d2_path = OUTPUT / f"{doc_id}.d2"
    png_path = OUTPUT / f"{doc_id}.png"

    with open(d2_path, 'w') as f:
        f.write(d2_code)

    try:
        result = subprocess.run(
            [os.path.expanduser("~/.local/bin/d2"),
             "--theme", "200", "--pad", "30", "--layout", "elk",
             str(d2_path), str(png_path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return doc_id, True, None
        return doc_id, False, result.stderr[:100]
    except Exception as e:
        return doc_id, False, str(e)[:100]


def render_one(args):
    doc_id, d2_code = args
    return render_d2(doc_id, d2_code)


def main():
    print(f"Generating D2 diagrams for {len(extracts)} companies...")

    # Generate D2 source for all
    d2_sources = []
    for e in extracts:
        doc_id = e['doc_id']
        d2_code = generate_d2(e)
        d2_sources.append((doc_id, d2_code))

    print(f"Generated {len(d2_sources)} D2 source files")
    print(f"Rendering with d2 (ELK layout, dark theme)...")

    ok = 0
    fail = 0
    with ProcessPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(render_one, args): args[0] for args in d2_sources}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Rendering"):
            doc_id, success, error = future.result()
            if success:
                ok += 1
            else:
                fail += 1
                if fail <= 5:
                    print(f"\n  FAIL {doc_id[:30]}: {error}")

    print(f"\n=== Done: {ok} rendered, {fail} failed ===")
    print(f"PNGs at: {OUTPUT}/")


if __name__ == "__main__":
    main()
