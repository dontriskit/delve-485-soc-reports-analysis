# VC Tech Due Diligence — Portfolio Signal Analysis

**Dataset:** 485 startups | **Scored:** 121 | **Date:** 2026-03-24

---

## Signal vs Noise

In a portfolio of 485 compliance reports, the majority follow identical Accorp Partners templates. The **unique signal** is concentrated in:
1. **Network architecture diagrams** (pages 18-19) — the only place actual tech stacks are visible
2. **System description sections** (pages 14-17) — what the product actually does
3. **Third-party vendor lists** — who they integrate with reveals market positioning

## Technical Signal Indicators

### Strong Technical Signals (correlate with higher scores)
- Named databases beyond "AWS RDS" (PostgreSQL, MongoDB, Redis, Weaviate)
- Named CI/CD tools (GitHub Actions, CircleCI)
- Named monitoring (Datadog, Sentry, Grafana)
- Multi-cloud or hybrid architecture (Vercel + AWS, Supabase + Render)
- Visible microservices in architecture diagram
- Self-hosted AI models (FIXIE/Llama, Modal, Baseten)

### Weak Technical Signals (correlate with lower scores)
- Generic "cloud provider" references without naming services
- Template placeholder text still in published report
- "Your Name Here" in signing authority
- Single-vendor everything (Supabase for DB + auth + VPC + IDS)
- No architecture diagram or sample/placeholder diagram
- Zero vendors named beyond the cloud provider

## Scoring Breakdown

- **19 companies score 7+** — strong tech foundations, genuine engineering culture
- **101 companies score 4-6** — adequate but undifferentiated
- **1 companies score ≤3** — template-only compliance, no real tech disclosure

## Tech Stack Trends

### AI Infrastructure
- Most companies use third-party LLM APIs (OpenAI, Anthropic, Google Gemini)
- A few run self-hosted models (11x/FIXIE Llama, Morph/Modal vLLM) — **higher IP moat**
- Voice AI stack: Twilio + ElevenLabs is the dominant pattern

### Database Layer
- PostgreSQL dominates (via Supabase, Neon, AWS RDS, DigitalOcean)
- Redis/ElastiCache for caching in more mature stacks
- Vector databases (Weaviate, Pinecone) appear in AI-native companies
- MongoDB for document-heavy use cases

### Auth Stack
- Clerk and STYTCH for modern startups
- Auth0/Okta for enterprise-positioned companies
- Supabase Auth for Supabase-ecosystem companies
- Firebase Auth for GCP-ecosystem

### Hosting
- AWS: 59.2% — enterprise-grade default
- GCP/Firebase: ~10% — common for AI-native (Vertex AI access)
- Supabase: ~4% — popular with small teams (all-in-one)
- Vercel: ~5% — Next.js ecosystem (frontend-heavy products)

## Red Flags for VC

Top flags across portfolio (by frequency):
1. Short audit period (3 months) — nearly universal, low information value
2. No RTO/RPO disclosed — common but concerning for enterprise SaaS
3. Processing Integrity/Privacy excluded — problematic for AI companies handling user data
4. Template placeholders in published reports — suggests rushed compliance
5. Single cloud dependency with carve-out — all controls delegated to cloud provider
