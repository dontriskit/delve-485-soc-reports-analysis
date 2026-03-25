# SKILL: Generate Infrastructure Diagram

## Purpose
Create a network/infrastructure architecture diagram as PNG from extracted tech data, using D2 diagramming language with ELK layout.

## Inputs
- `DOC_ID`: The Google Doc ID
- `COMPANY_DB`: Path to `company_db/` directory (default: `company_db/`)

## Prerequisites
- `{COMPANY_DB}/{DOC_ID}_tech_extract.json` must exist (output of Skill 01)
- `d2` CLI must be installed (`~/.local/bin/d2`)

## Procedure

### Step 1: Load extracted data
Read `{COMPANY_DB}/{DOC_ID}_tech_extract.json`. Identify:
- Company name (for title)
- Report type (for subtitle)
- Cloud provider(s) and regions
- Network architecture components
- Application architecture components
- Data layer components
- Third-party services
- Security tools
- Key risk summary

### Step 2: Generate D2 source file
Write a D2 file to `reports/{COMPANY_SLUG}_infra.d2`.

Follow this structure and dark theme styling:

```d2
direction: down

title: |md
  # {Company} — Network & Infrastructure Architecture
  {report_type} · {cloud_provider} · {key architecture trait}
| {
  near: top-center
  style.font-size: 28
}

# --- USER/CLIENT ENTRY POINT ---
users: {appropriate label} {
  shape: image
  icon: https://icons.terrastruct.com/essentials%2F359-users.svg
  style.font-size: 16
}

# --- PERIMETER LAYER ---
# Include: API Gateway, WAF, Firewall, IDS/IPS, TLS
# Use hexagon shapes, red theme (#ef4444 stroke, #2a1a1a fill)

# --- MAIN CLOUD CONTAINER ---
# If multi-region: separate clusters per region
# If single region: one cluster with internal groupings
# Use #ff9900 stroke for AWS, #4285F4 for GCP, #0078D4 for Azure

# --- INTERNAL CLUSTERS ---
# Group by function:
#   - Identity & Access (yellow theme: #f59e0b)
#   - Compute (blue theme: #3b82f6)
#   - AI/ML if applicable (purple theme: #a855f7)
#   - Data Layer (orange theme: #ff9900, cylinder shapes for DBs)
#   - Integrations (green theme: #10b981)
#   - Telephony/External APIs (red theme: #ef4444)
#   - Operations (cyan theme: #38bdf8)

# --- PRODUCT LAYER ---
# Show the actual products/features
# Green theme: #22c55e

# --- CONNECTIONS ---
# Use labeled edges showing data flow direction
# Solid lines for primary data flow
# Dashed lines for secondary/internal flows
# Dotted lines for encryption/key management

# --- RISK SUMMARY ---
risk: |md
  **Risk Summary**
  {One line with key risks separated by " · "}
| {
  near: bottom-center
  style.font-size: 13
  style.font-color: "#94a3b8"
  style.fill: "#1a1a2e"
  style.stroke: "#334155"
  style.border-radius: 8
}
```

### D2 Style Guide

**Color Themes by Component:**
| Component | Stroke | Fill | Font Color |
|-----------|--------|------|------------|
| Perimeter/Security | #ef4444 | #2a1a1a | #fca5a5 |
| Identity/Auth | #f59e0b | #2a2a0a | #fde68a |
| Compute | #3b82f6 | #0f1a2e | #93c5fd |
| AI/ML | #a855f7 | #1a0f2e | #d8b4fe |
| Data/Storage | #ff9900 | #2a1f0a | #fcd34d |
| Integrations | #10b981 | #0a2a1a | #6ee7b7 |
| External APIs | #ef4444 | #2e0f0f | #fca5a5 |
| Operations | #38bdf8 | #0f1a2a | #7dd3fc |
| Products | #22c55e | #0a2a1a | #86efac |

**Shape Rules:**
- Databases → `shape: cylinder`
- Encryption/KMS → `shape: diamond`
- Firewalls/WAF → `shape: hexagon`
- Everything else → `shape: rectangle` (default)

**Edge Rules:**
- Primary data flow → solid, `style.stroke-width: 2`
- Internal flow → `style.stroke-dash: 5`
- Encryption → `style.stroke-dash: 3`
- Cross-region → `style.stroke-width: 3` + dashed

### Step 3: Render to PNG
```bash
~/.local/bin/d2 --theme 200 --pad 40 --layout elk \
  reports/{COMPANY_SLUG}_infra.d2 \
  reports/{COMPANY_SLUG}_infra_diagram.png
```

Theme 200 = dark theme. ELK = best layout engine for complex diagrams.

### Step 4: Validate
- Verify the PNG was created and is non-empty
- Read the PNG to visually confirm the diagram renders correctly

## Output
- `reports/{COMPANY_SLUG}_infra.d2` — editable D2 source
- `reports/{COMPANY_SLUG}_infra_diagram.png` — rendered diagram

## Fallback
If D2 is not installed, fall back to the `diagrams` Python library:
```bash
uv run python -c "from diagrams import Diagram; print('ok')"
```
Use `diagrams` with `direction="TB"`, `graph_attr={"bgcolor": "#1a1a2e", ...}`.
This produces lower quality but is a viable fallback.
