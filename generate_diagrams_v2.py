"""Generate infrastructure diagrams using the 'diagrams' library with real cloud icons."""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.network import APIGateway, VPC, ELB, CloudFront
from diagrams.aws.security import WAF, KMS, IAM
from diagrams.aws.management import Cloudwatch
from diagrams.aws.integration import SQS
from diagrams.onprem.client import Users
from diagrams.onprem.network import Internet
from diagrams.onprem.security import Vault
from diagrams.onprem.vcs import Github
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.monitoring import Datadog
from diagrams.saas.chat import Slack
from diagrams.generic.device import Mobile
from diagrams.generic.network import Firewall
from diagrams.programming.framework import React
from diagrams.custom import Custom
import os
import urllib.request

os.makedirs("reports", exist_ok=True)

# Download a few custom icons we need
ICONS = {
    "stytch": "https://cdn.brandfetch.io/id_KsyK7J/w/400/h/400/theme/dark/icon.jpeg?c=1id_KsyK7J&t=1719841064538",
    "vercel": "https://cdn.brandfetch.io/idKdaGM_W2/w/400/h/400/theme/dark/icon.jpeg?c=1dxbfHSJFAPEGdCLU4o5B",
    "twilio": "https://cdn.brandfetch.io/idS5WhqBbM/w/400/h/400/theme/dark/icon.jpeg?c=1a2b3c",
    "elevenlabs": "https://cdn.brandfetch.io/id2S3shSJL/w/400/h/400/theme/dark/icon.jpeg?c=1a2b3c",
    "salesforce": "https://cdn.brandfetch.io/id6a_FMz_b/w/400/h/400/theme/dark/icon.jpeg?c=1a2b3c",
    "hubspot": "https://cdn.brandfetch.io/idGDcB65pY/w/400/h/400/theme/dark/icon.jpeg?c=1a2b3c",
}

icon_dir = "reports/icons"
os.makedirs(icon_dir, exist_ok=True)

for name, url in ICONS.items():
    path = f"{icon_dir}/{name}.jpeg"
    if not os.path.exists(path):
        try:
            urllib.request.urlretrieve(url, path)
            print(f"  Downloaded {name}")
        except Exception as e:
            print(f"  Failed {name}: {e}")

def icon(name):
    path = f"{icon_dir}/{name}.jpeg"
    return path if os.path.exists(path) else None

# ============================================================
# DIAGRAM 1: 11x AI
# ============================================================
graph_attr = {
    "fontsize": "30",
    "bgcolor": "#1a1a2e",
    "fontcolor": "#e0e0e0",
    "pad": "1.5",
    "ranksep": "1.8",
    "nodesep": "1.0",
    "splines": "curved",
    "concentrate": "false",
    "dpi": "200",
}
node_attr = {"fontsize": "12", "fontcolor": "#e0e0e0", "width": "1.8", "height": "1.8"}
edge_attr = {"color": "#555577", "penwidth": "2.0"}

with Diagram(
    "11x AI — Infrastructure Architecture",
    filename="reports/11x_infra_diagram_v2",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    users = Users("Users / Prospects")

    with Cluster("Perimeter Security", graph_attr={"bgcolor": "#2a1a1a", "fontcolor": "#ff6666", "style": "rounded"}):
        fw = Firewall("Firewall\n+ IDS/IPS")
        tls = Vault("TLS\nTermination")

    with Cluster("AWS VPC — Multi-AZ", graph_attr={"bgcolor": "#1a2a1a", "fontcolor": "#ff9900", "style": "rounded"}):

        with Cluster("Identity & Access", graph_attr={"bgcolor": "#2a2a0a", "fontcolor": "#ffaa00"}):
            stytch = Custom("Stytch\nAuth + MFA", icon("stytch")) if icon("stytch") else IAM("Stytch\nAuth + MFA")
            iam = IAM("RBAC\nLeast Privilege")

        with Cluster("Compute Layer", graph_attr={"bgcolor": "#0a1a2a", "fontcolor": "#3b82f6"}):
            vercel = Custom("Vercel\nFrontend/Edge", icon("vercel")) if icon("vercel") else EC2("Vercel\nFrontend/Edge")
            inngest = Lambda("Inngest\nDurable Queues")

        with Cluster("AI / ML Stack", graph_attr={"bgcolor": "#1a0a2a", "fontcolor": "#a855f7"}):
            fixie = Lambda("FIXIE\nLlama Models")
            elevenlabs = Custom("ElevenLabs\nVoice Synth", icon("elevenlabs")) if icon("elevenlabs") else Lambda("ElevenLabs\nVoice Synth")
            voice = SQS("Voice Pipeline\nReal-time")

        with Cluster("Data Layer", graph_attr={"bgcolor": "#1a1a0a", "fontcolor": "#ff9900"}):
            rds = RDS("AWS RDS")
            s3 = S3("AWS S3")
            kms = KMS("AWS KMS\nEncryption")

        with Cluster("CRM Integrations", graph_attr={"bgcolor": "#0a2a1a", "fontcolor": "#10b981"}):
            sf = Custom("Salesforce", icon("salesforce")) if icon("salesforce") else EC2("Salesforce")
            hs = Custom("HubSpot", icon("hubspot")) if icon("hubspot") else EC2("HubSpot")

        with Cluster("Telephony & Media", graph_attr={"bgcolor": "#2a0a0a", "fontcolor": "#ef4444"}):
            twilio = Custom("Twilio\nVoice", icon("twilio")) if icon("twilio") else Mobile("Twilio\nVoice")
            whatsapp = Mobile("WhatsApp\nMedia")

        with Cluster("Operations", graph_attr={"bgcolor": "#0a1a1a", "fontcolor": "#38bdf8"}):
            monitoring = Cloudwatch("Monitoring\nCPU/Disk/Net")
            backups = S3("Daily Backups\nMulti-AZ")

    with Cluster("Products", graph_attr={"bgcolor": "#0a2a1a", "fontcolor": "#22c55e", "style": "rounded"}):
        alice = EC2("ALICE\nAI SDR")
        julian = EC2("JULIAN\nAI Phone Agent")

    # Core request flow (top to bottom)
    users >> Edge(color="#888899") >> fw >> tls
    tls >> Edge(color="#ffaa00") >> stytch
    stytch >> Edge(color="#ffaa00", style="dashed") >> iam

    # Compute flow
    stytch >> Edge(color="#3b82f6") >> vercel
    vercel >> Edge(color="#3b82f6") >> inngest

    # AI flow
    inngest >> Edge(color="#a855f7") >> fixie
    fixie >> Edge(color="#a855f7") >> elevenlabs
    elevenlabs >> Edge(color="#a855f7") >> voice

    # Products
    fixie >> Edge(color="#22c55e", label="  AI SDR") >> alice
    voice >> Edge(color="#22c55e", label="  Voice AI") >> julian

    # Product integrations
    julian >> Edge(color="#ef4444") >> twilio
    julian >> Edge(color="#ef4444") >> whatsapp
    alice >> Edge(color="#10b981") >> sf
    alice >> Edge(color="#10b981") >> hs

    # Data layer
    vercel >> Edge(color="#ff9900", style="dashed") >> rds
    inngest >> Edge(color="#ff9900", style="dashed") >> s3
    rds >> Edge(color="#ff9900", style="dotted") >> kms
    s3 >> Edge(color="#ff9900", style="dotted") >> kms

    # Ops
    monitoring >> Edge(color="#38bdf8", style="dashed") >> backups

print("11x diagram done")

# ============================================================
# DIAGRAM 2: AgentMail
# ============================================================
with Diagram(
    "AgentMail — Infrastructure Architecture",
    filename="reports/agentmail_infra_diagram_v2",
    outformat="png",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    clients = Users("API Clients\n/ AI Agents")

    with Cluster("Edge / Perimeter", graph_attr={"bgcolor": "#2a1a1a", "fontcolor": "#ff6666", "style": "rounded"}):
        apigw = APIGateway("AWS API\nGateway")
        waf = WAF("AWS WAF")
        fw2 = Firewall("IDS/IPS\n+ TLS")

    with Cluster("AWS Multi-Region", graph_attr={"bgcolor": "#1a2a1a", "fontcolor": "#ff9900", "style": "rounded"}):

        with Cluster("us-west-1 (N. California)", graph_attr={"bgcolor": "#0a1a2a", "fontcolor": "#3b82f6"}):
            ec2_w = EC2("EC2/ECS\nCompute")
            lambda_w = Lambda("Lambda\nServerless")
            db_w = RDS("Database\nRegional")
            email_w = SQS("Email Engine\nSPF/DKIM/DMARC")

        with Cluster("us-east-1 (N. Virginia)", graph_attr={"bgcolor": "#0a1a2a", "fontcolor": "#3b82f6"}):
            ec2_e = EC2("EC2/ECS\nCompute")
            lambda_e = Lambda("Lambda\nServerless")
            db_e = RDS("Database\nRegional")
            email_e = SQS("Email Engine\nSPF/DKIM/DMARC")

        with Cluster("Shared Data Layer", graph_attr={"bgcolor": "#1a1a0a", "fontcolor": "#ff9900"}):
            shared_db = Dynamodb("Shared DB\nCross-Region")
            s3_am = S3("AWS S3\nObject Store")
            kms_am = KMS("AWS KMS\nEncryption")

        with Cluster("Access & Security", graph_attr={"bgcolor": "#2a2a0a", "fontcolor": "#ffaa00"}):
            mfa = IAM("MFA / RBAC\nAdmin Access")
            vpn = Vault("Bastion + VPN\nRemote Access")

        with Cluster("Operations", graph_attr={"bgcolor": "#0a1a1a", "fontcolor": "#38bdf8"}):
            mon = Cloudwatch("Monitoring\nCPU/Disk/Net")
            bkp = S3("Daily Backups\nMulti-AZ")

    with Cluster("Product Capabilities", graph_attr={"bgcolor": "#0a2a1a", "fontcolor": "#22c55e", "style": "rounded"}):
        inbox = Lambda("Inbox\nProvisioning")
        events = SQS("JSON Event\nStreaming")
        webhooks = APIGateway("Webhooks\nCallbacks")
        deliver = Cloudwatch("Deliverability\nMonitoring")

    # Data flow
    clients >> Edge(color="#888899") >> apigw
    apigw >> Edge(color="#ff6666") >> waf >> fw2

    fw2 >> Edge(color="#3b82f6") >> ec2_w
    fw2 >> Edge(color="#3b82f6") >> ec2_e

    ec2_w >> Edge(color="#3b82f6") >> lambda_w >> email_w
    ec2_e >> Edge(color="#3b82f6") >> lambda_e >> email_e

    ec2_w >> Edge(color="#ff9900") >> db_w
    ec2_e >> Edge(color="#ff9900") >> db_e

    db_w >> Edge(color="#ff9900", style="bold", label="replication") >> shared_db
    db_e >> Edge(color="#ff9900", style="bold") >> shared_db

    shared_db >> Edge(color="#ff9900") >> s3_am
    s3_am >> Edge(color="#ff9900", style="dashed") >> kms_am

    mfa >> Edge(color="#ffaa00", style="dashed") >> vpn
    mon >> Edge(color="#38bdf8", style="dashed") >> bkp

    email_w >> Edge(color="#22c55e") >> inbox
    email_e >> Edge(color="#22c55e") >> events
    lambda_w >> Edge(color="#22c55e") >> webhooks
    lambda_e >> Edge(color="#22c55e") >> deliver

print("AgentMail diagram done")
print("\nFiles:")
print("  reports/11x_infra_diagram_v2.png")
print("  reports/agentmail_infra_diagram_v2.png")
