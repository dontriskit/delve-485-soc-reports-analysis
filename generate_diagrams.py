"""Generate network/infrastructure diagrams for 11x AI and AgentMail."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

os.makedirs("reports", exist_ok=True)

# Color palette
C = {
    "bg": "#0F1419",
    "card": "#1A2332",
    "card_border": "#2A3A4E",
    "aws": "#FF9900",
    "aws_bg": "#2A1F0A",
    "compute": "#3B82F6",
    "compute_bg": "#0F1A2E",
    "ai": "#A855F7",
    "ai_bg": "#1A0F2E",
    "crm": "#10B981",
    "crm_bg": "#0A2E1F",
    "telephony": "#EF4444",
    "telephony_bg": "#2E0F0F",
    "auth": "#F59E0B",
    "auth_bg": "#2E1F0A",
    "text": "#E2E8F0",
    "subtext": "#94A3B8",
    "accent": "#38BDF8",
    "arrow": "#475569",
    "green": "#22C55E",
    "red": "#EF4444",
    "yellow": "#EAB308",
}

def box(ax, x, y, w, h, label, color, bg, fontsize=8, sublabel=None, bold=False):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                          facecolor=bg, edgecolor=color, linewidth=1.5)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2 + (0.015 if sublabel else 0), label,
            ha='center', va='center', fontsize=fontsize, color=color,
            fontweight=weight, fontfamily='monospace')
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.02, sublabel,
                ha='center', va='center', fontsize=6, color=C["subtext"],
                fontfamily='monospace')

def arrow(ax, x1, y1, x2, y2, color=None, style='->', bidir=False):
    c = color or C["arrow"]
    s = '<->' if bidir else style
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=s, color=c, lw=1.2,
                               connectionstyle="arc3,rad=0"))

def section_label(ax, x, y, label, color):
    ax.text(x, y, label, ha='left', va='center', fontsize=7,
            color=color, fontweight='bold', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=C["bg"],
                     edgecolor=color, alpha=0.8))

# ============================================================
# DIAGRAM 1: 11x AI
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 11))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
ax.text(0.5, 0.97, "11x AI Inc. — Network & Infrastructure Architecture",
        ha='center', va='top', fontsize=14, color=C["text"],
        fontweight='bold', fontfamily='monospace')
ax.text(0.5, 0.945, "SOC 2 Type II  |  AWS Cloud-Native  |  Multi-AZ  |  Microservices",
        ha='center', va='top', fontsize=8, color=C["subtext"], fontfamily='monospace')

# === INTERNET / USERS ===
box(ax, 0.38, 0.87, 0.24, 0.04, "INTERNET / USERS", C["text"], C["card"], fontsize=9, bold=True)

# === PERIMETER ===
section_label(ax, 0.02, 0.83, "PERIMETER", C["red"])
# Firewall + IDS/IPS + TLS
box(ax, 0.12, 0.80, 0.18, 0.04, "Firewall", C["red"], C["telephony_bg"], sublabel="App Gateway Rules")
box(ax, 0.41, 0.80, 0.18, 0.04, "IDS / IPS", C["red"], C["telephony_bg"], sublabel="AWS Managed")
box(ax, 0.70, 0.80, 0.18, 0.04, "TLS Termination", C["red"], C["telephony_bg"], sublabel="Third-party CA")

arrow(ax, 0.50, 0.87, 0.21, 0.84, C["arrow"])
arrow(ax, 0.50, 0.87, 0.50, 0.84, C["arrow"])
arrow(ax, 0.50, 0.87, 0.79, 0.84, C["arrow"])

# === AWS VPC ===
vpc_rect = FancyBboxPatch((0.03, 0.10), 0.94, 0.67, boxstyle="round,pad=0.02",
                           facecolor=C["aws_bg"], edgecolor=C["aws"], linewidth=2, alpha=0.3)
ax.add_patch(vpc_rect)
ax.text(0.06, 0.755, "AWS VPC  —  Multi-AZ  —  Segmented Subnets + ACLs",
        fontsize=8, color=C["aws"], fontweight='bold', fontfamily='monospace')

# === IDENTITY & ACCESS ===
section_label(ax, 0.05, 0.72, "IDENTITY & ACCESS", C["auth"])
box(ax, 0.05, 0.66, 0.20, 0.05, "STYTCH", C["auth"], C["auth_bg"], fontsize=9, sublabel="Auth & Authorization", bold=True)
box(ax, 0.05, 0.59, 0.20, 0.05, "MFA / RBAC", C["auth"], C["auth_bg"], sublabel="AWS Password Policy")
box(ax, 0.05, 0.52, 0.20, 0.05, "Bastion + VPN", C["auth"], C["auth_bg"], sublabel="Remote Access")

# === COMPUTE ===
section_label(ax, 0.30, 0.72, "COMPUTE & EDGE", C["compute"])
box(ax, 0.30, 0.66, 0.20, 0.05, "Vercel", C["compute"], C["compute_bg"], fontsize=9, sublabel="Frontend / Edge", bold=True)
box(ax, 0.30, 0.59, 0.20, 0.05, "Inngest", C["compute"], C["compute_bg"], sublabel="Durable Function Queues")

# === AI / ML ===
section_label(ax, 0.55, 0.72, "AI / ML STACK", C["ai"])
box(ax, 0.55, 0.66, 0.20, 0.05, "FIXIE", C["ai"], C["ai_bg"], fontsize=9, sublabel="Proprietary Llama Models", bold=True)
box(ax, 0.55, 0.59, 0.20, 0.05, "ElevenLabs", C["ai"], C["ai_bg"], sublabel="Voice Synthesis")
box(ax, 0.55, 0.52, 0.20, 0.05, "Voice Pipeline", C["ai"], C["ai_bg"], sublabel="Real-time Voice AI")

# === DATA LAYER ===
section_label(ax, 0.05, 0.46, "DATA LAYER", C["aws"])
box(ax, 0.05, 0.40, 0.20, 0.05, "AWS RDS", C["aws"], C["aws_bg"], fontsize=9, sublabel="Relational Database", bold=True)
box(ax, 0.30, 0.40, 0.20, 0.05, "AWS S3", C["aws"], C["aws_bg"], fontsize=9, sublabel="File Storage", bold=True)
box(ax, 0.55, 0.40, 0.20, 0.05, "AWS KMS", C["aws"], C["aws_bg"], fontsize=9, sublabel="Encryption Keys", bold=True)

# === INTEGRATIONS ===
section_label(ax, 0.05, 0.34, "CRM INTEGRATIONS", C["crm"])
box(ax, 0.05, 0.28, 0.14, 0.05, "Salesforce", C["crm"], C["crm_bg"], sublabel="CRM")
box(ax, 0.21, 0.28, 0.14, 0.05, "HubSpot", C["crm"], C["crm_bg"], sublabel="CRM")
box(ax, 0.37, 0.28, 0.14, 0.05, "ZOHO", C["crm"], C["crm_bg"], sublabel="CRM")

section_label(ax, 0.55, 0.34, "TELEPHONY & MEDIA", C["telephony"])
box(ax, 0.55, 0.28, 0.18, 0.05, "Twilio", C["telephony"], C["telephony_bg"], sublabel="Voice / Phone")
box(ax, 0.76, 0.28, 0.18, 0.05, "WhatsApp", C["telephony"], C["telephony_bg"], sublabel="Media / Messaging")

# === OPS ===
section_label(ax, 0.05, 0.22, "OPERATIONS", C["accent"])
box(ax, 0.05, 0.16, 0.20, 0.05, "IaC + Rollback", C["accent"], C["card"], sublabel="Config Management")
box(ax, 0.28, 0.16, 0.20, 0.05, "Monitoring", C["accent"], C["card"], sublabel="CPU/Disk/Net/Alerts")
box(ax, 0.51, 0.16, 0.20, 0.05, "Vuln Scanning", C["accent"], C["card"], sublabel="Monthly + Annual Pentest")
box(ax, 0.74, 0.16, 0.20, 0.05, "Daily Backups", C["accent"], C["card"], sublabel="Multi-AZ + Alerting")

# === PRODUCTS ===
box(ax, 0.80, 0.66, 0.15, 0.05, "ALICE", C["green"], "#0A2E1A", fontsize=9, sublabel="AI SDR Agent", bold=True)
box(ax, 0.80, 0.59, 0.15, 0.05, "JULIAN", C["green"], "#0A2E1A", fontsize=9, sublabel="AI Phone Agent", bold=True)

# Key arrows showing data flow
arrow(ax, 0.25, 0.685, 0.30, 0.685, C["auth"])       # STYTCH -> Vercel
arrow(ax, 0.50, 0.685, 0.55, 0.685, C["compute"])     # Vercel -> FIXIE
arrow(ax, 0.75, 0.685, 0.80, 0.685, C["ai"])          # AI -> Products
arrow(ax, 0.50, 0.615, 0.55, 0.615, C["compute"])     # Inngest -> ElevenLabs
arrow(ax, 0.40, 0.59, 0.40, 0.45, C["aws"])           # Compute -> S3
arrow(ax, 0.15, 0.59, 0.15, 0.45, C["aws"])           # Auth -> RDS
arrow(ax, 0.87, 0.59, 0.87, 0.33, C["telephony"], bidir=True)  # Julian -> Telephony
arrow(ax, 0.87, 0.66, 0.44, 0.33, C["crm"], bidir=True)        # Alice -> CRM

# Legend
ax.text(0.05, 0.06, "RISK SUMMARY", fontsize=8, color=C["text"],
        fontweight='bold', fontfamily='monospace')
ax.text(0.05, 0.03, "Single cloud (AWS) | No SIEM named | No RTO/RPO | 3-mo audit | Proprietary AI = strong moat",
        fontsize=7, color=C["subtext"], fontfamily='monospace')

plt.tight_layout()
plt.savefig("reports/11x_infra_diagram.png", dpi=200, facecolor=C["bg"],
            bbox_inches='tight', pad_inches=0.3)
plt.close()

# ============================================================
# DIAGRAM 2: AgentMail
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(16, 11))
fig.patch.set_facecolor(C["bg"])
ax.set_facecolor(C["bg"])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title
ax.text(0.5, 0.97, "AgentMail, Inc. — Network & Infrastructure Architecture",
        ha='center', va='top', fontsize=14, color=C["text"],
        fontweight='bold', fontfamily='monospace')
ax.text(0.5, 0.945, "SOC 2 Type II  |  AWS Multi-Region  |  Serverless-Heavy  |  API-First",
        ha='center', va='top', fontsize=8, color=C["subtext"], fontfamily='monospace')

# === INTERNET ===
box(ax, 0.35, 0.87, 0.30, 0.04, "INTERNET / API CLIENTS / AI AGENTS",
    C["text"], C["card"], fontsize=9, bold=True)

# === EDGE / PERIMETER ===
section_label(ax, 0.02, 0.83, "EDGE / PERIMETER", C["red"])
box(ax, 0.10, 0.78, 0.22, 0.04, "AWS API Gateway", C["aws"], C["aws_bg"], fontsize=9, sublabel="API Front Door", bold=True)
box(ax, 0.39, 0.78, 0.22, 0.04, "AWS WAF", C["red"], C["telephony_bg"], fontsize=9, sublabel="Web Application Firewall", bold=True)
box(ax, 0.68, 0.78, 0.22, 0.04, "IDS / IPS + TLS", C["red"], C["telephony_bg"], sublabel="AWS Managed + CA Certs")

arrow(ax, 0.50, 0.87, 0.21, 0.82, C["arrow"])
arrow(ax, 0.50, 0.87, 0.50, 0.82, C["arrow"])
arrow(ax, 0.50, 0.87, 0.79, 0.82, C["arrow"])

# === AWS MULTI-REGION ===
# Region 1: us-west-1
r1 = FancyBboxPatch((0.03, 0.38), 0.44, 0.36, boxstyle="round,pad=0.02",
                     facecolor=C["aws_bg"], edgecolor=C["aws"], linewidth=2, alpha=0.3)
ax.add_patch(r1)
ax.text(0.06, 0.72, "AWS  us-west-1  (N. California)",
        fontsize=8, color=C["aws"], fontweight='bold', fontfamily='monospace')

box(ax, 0.06, 0.62, 0.18, 0.06, "EC2 / ECS", C["compute"], C["compute_bg"],
    fontsize=9, sublabel="Compute Instances", bold=True)
box(ax, 0.27, 0.62, 0.18, 0.06, "AWS Lambda", C["compute"], C["compute_bg"],
    fontsize=9, sublabel="Serverless Functions", bold=True)
box(ax, 0.06, 0.52, 0.18, 0.06, "Database", C["aws"], C["aws_bg"],
    fontsize=9, sublabel="Regional Replica", bold=True)
box(ax, 0.27, 0.52, 0.18, 0.06, "Email Engine", C["green"], "#0A2E1A",
    fontsize=9, sublabel="SPF/DKIM/DMARC", bold=True)

# Arrows within region 1
arrow(ax, 0.15, 0.62, 0.15, 0.58, C["aws"])
arrow(ax, 0.36, 0.62, 0.36, 0.58, C["compute"])

# Region 2: us-east-1
r2 = FancyBboxPatch((0.53, 0.38), 0.44, 0.36, boxstyle="round,pad=0.02",
                     facecolor=C["aws_bg"], edgecolor=C["aws"], linewidth=2, alpha=0.3)
ax.add_patch(r2)
ax.text(0.56, 0.72, "AWS  us-east-1  (N. Virginia)",
        fontsize=8, color=C["aws"], fontweight='bold', fontfamily='monospace')

box(ax, 0.56, 0.62, 0.18, 0.06, "EC2 / ECS", C["compute"], C["compute_bg"],
    fontsize=9, sublabel="Compute Instances", bold=True)
box(ax, 0.77, 0.62, 0.18, 0.06, "AWS Lambda", C["compute"], C["compute_bg"],
    fontsize=9, sublabel="Serverless Functions", bold=True)
box(ax, 0.56, 0.52, 0.18, 0.06, "Database", C["aws"], C["aws_bg"],
    fontsize=9, sublabel="Regional Replica", bold=True)
box(ax, 0.77, 0.52, 0.18, 0.06, "Email Engine", C["green"], "#0A2E1A",
    fontsize=9, sublabel="SPF/DKIM/DMARC", bold=True)

arrow(ax, 0.65, 0.62, 0.65, 0.58, C["aws"])
arrow(ax, 0.86, 0.62, 0.86, 0.58, C["compute"])

# Cross-region arrow
arrow(ax, 0.47, 0.55, 0.53, 0.55, C["aws"], bidir=True)
ax.text(0.50, 0.565, "REPL", ha='center', fontsize=6, color=C["aws"], fontfamily='monospace')

# From edge to regions
arrow(ax, 0.21, 0.78, 0.25, 0.74, C["aws"])
arrow(ax, 0.50, 0.78, 0.75, 0.74, C["aws"])

# === SHARED DATA LAYER ===
section_label(ax, 0.02, 0.35, "SHARED DATA LAYER", C["aws"])
shared = FancyBboxPatch((0.10, 0.22), 0.80, 0.10, boxstyle="round,pad=0.02",
                         facecolor=C["aws_bg"], edgecolor=C["aws"], linewidth=1.5, alpha=0.4)
ax.add_patch(shared)
box(ax, 0.12, 0.235, 0.18, 0.06, "Shared DB", C["aws"], C["aws_bg"],
    fontsize=9, sublabel="Cross-Region Store", bold=True)
box(ax, 0.34, 0.235, 0.18, 0.06, "AWS S3", C["aws"], C["aws_bg"],
    fontsize=9, sublabel="Object Storage", bold=True)
box(ax, 0.56, 0.235, 0.18, 0.06, "AWS KMS", C["aws"], C["aws_bg"],
    fontsize=9, sublabel="Encryption Keys", bold=True)
box(ax, 0.78, 0.235, 0.10, 0.06, "Audit\nLogs", C["aws"], C["aws_bg"], fontsize=8)

arrow(ax, 0.15, 0.52, 0.21, 0.32, C["aws"])
arrow(ax, 0.65, 0.52, 0.43, 0.32, C["aws"])

# === ACCESS CONTROL ===
section_label(ax, 0.02, 0.19, "ACCESS & SECURITY", C["auth"])
box(ax, 0.03, 0.12, 0.18, 0.05, "MFA / RBAC", C["auth"], C["auth_bg"], sublabel="All Admin Access")
box(ax, 0.24, 0.12, 0.18, 0.05, "Bastion + VPN", C["auth"], C["auth_bg"], sublabel="Remote Access")
box(ax, 0.45, 0.12, 0.18, 0.05, "Vuln Scanning", C["accent"], C["card"], sublabel="Monthly + Pentest")
box(ax, 0.66, 0.12, 0.18, 0.05, "Daily Backups", C["accent"], C["card"], sublabel="Multi-AZ + Alerts")

# === PRODUCT FEATURES (right side) ===
section_label(ax, 0.02, 0.46, "PRODUCT CAPABILITIES", C["green"])
box(ax, 0.06, 0.40, 0.18, 0.05, "Inbox Provisioning", C["green"], "#0A2E1A", sublabel="Ephemeral @ Scale")
box(ax, 0.27, 0.40, 0.18, 0.05, "JSON Events", C["green"], "#0A2E1A", sublabel="Real-time Streaming")
box(ax, 0.56, 0.40, 0.18, 0.05, "Webhooks", C["green"], "#0A2E1A", sublabel="API Callbacks")
box(ax, 0.77, 0.40, 0.18, 0.05, "Deliverability", C["green"], "#0A2E1A", sublabel="Warm-up + Monitoring")

# OPS
section_label(ax, 0.45, 0.19, "OPERATIONS", C["accent"])

# Legend
ax.text(0.05, 0.06, "RISK SUMMARY", fontsize=8, color=C["text"],
        fontweight='bold', fontfamily='monospace')
ax.text(0.05, 0.03, "AWS-only (no other vendors named) | Multi-region = strong | No RTO/RPO | No CDN | Privacy excluded despite email content",
        fontsize=7, color=C["subtext"], fontfamily='monospace')

plt.tight_layout()
plt.savefig("reports/agentmail_infra_diagram.png", dpi=200, facecolor=C["bg"],
            bbox_inches='tight', pad_inches=0.3)
plt.close()

print("Diagrams saved:")
print("  reports/11x_infra_diagram.png")
print("  reports/agentmail_infra_diagram.png")
