# Analyzing 485 SOC 2 Compliance Reports with AI

**We read 485 SOC 2 reports so you don't have to.**

A quantitative tech due diligence meta-analysis of 485 early-stage AI and SaaS companies, covering $291M+ in tracked venture funding from a16z, Benchmark, Kleiner Perkins, Lightspeed, Union Square Ventures, and Y Combinator.

> **Live report:** [altimi-tech-dd.pages.dev](https://altimi-tech-dd.pages.dev/)
> **Live search:** [delve-vision-extract.whitecontext.workers.dev](https://delve-vision-extract.whitecontext.workers.dev/)

## Why?

I wanted to understand how my friends from San Francisco build their startups. Not the pitch decks or the blog posts — the actual infrastructure. The databases, the cloud providers, the security controls, the vendor dependencies. The stuff that shows up in a SOC 2 report but never in a press release.

So I analyzed all of them. Every page. Every diagram. Every control description. 485 companies. ~38,000 PDF pages. And turned it into a searchable, scored, benchmarked database.

## What I Found

- **Average tech DD score: 5.6/10** — most companies cluster at 5-6, driven by template compliance
- **Only 4% meet full maturity** (multi-region + WAF + pen testing + daily backups + quarterly reviews)
- **Funding ≠ tech maturity** — the highest-funded company ($75M, $350M valuation) scores 6/10; a bootstrapped company scores 8/10
- **AWS dominates at 60%+** — systemic portfolio-level concentration risk
- **MFA is universal (99%)** but WAF adoption is only 44% and multi-region is 28%
- **Vendor transparency predicts quality** — companies naming 5+ vendors score a full point higher
- **Y Combinator is everywhere** — 10 of 27 top companies are YC alumni

## The Pipeline

This wasn't a manual analysis. I built a fully automated pipeline:

```
PDF Reports (576 files)
    ↓ pdftoppm (150 DPI)
~38,000 Page Images
    ↓ Upload to Cloudflare R2
Cloudflare R2 Storage (8.1 GB)
    ↓ Cloudflare Workflows
kimi-k2.5 Vision Model (256K context)
    ↓ Single-call: all pages → one JSON
Structured Extraction (per company)
    ↓ Scoring + Report Generation
Cloudflare D1 Database
    ↓ API + HTML Viewer
Live Dashboard & Search App
```

### Tech Stack

- **Vision AI:** Moonshot kimi-k2.5 via Cloudflare Workers AI — processes all ~80 pages of a PDF in a single inference call (~4 min per company)
- **Orchestration:** Cloudflare Workflows — each company is a workflow with retry, timeout, and D1 persistence
- **Storage:** Cloudflare R2 (page images, 8.1 GB) + D1 (structured data, 17 MB)
- **Worker API:** Handles extraction, report generation, search, and the live dashboard
- **Diagrams:** D2 (ELK layout, dark theme) — template-generated from structured data, 479/485 render successfully
- **Charts:** Seaborn/Matplotlib — 41 charts across 13 analysis modules
- **Article:** 4,400-word Tailwind CSS article with 18 embedded charts
- **Subagents:** Claude Code subagents processed the first 144 companies before we switched to the Cloudflare pipeline

### What Made It Work

1. **Single-call vision processing** — sending all 80 pages to kimi-k2.5 in one call (fits in 256K context) reduced processing time from 60 min/company (page-by-page) to 4 min/company
2. **R2 + Workflows** — uploading images once to R2 and triggering workflows via lightweight JSON payloads meant the pipeline ran autonomously on Cloudflare's edge, independent of local network stability
3. **Template-generated D2 diagrams** — instead of asking AI to write diagram code (30% syntax errors), generating D2 from structured JSON produced 99% valid renders
4. **D1 as single source of truth** — all data in one database, queryable via SQL, served via API

## Repository Structure

```
├── worker/                    # Cloudflare Worker + Workflows
│   ├── src/index.ts          # API, workflows, viewer
│   ├── wrangler.toml         # Bindings: AI, D1, R2, Workflows
│   └── schema.sql            # D1 database schema
├── vision_pipeline/           # Local Python pipeline
│   ├── convert_pdfs.py       # PDF → JPEG page images
│   ├── upload_fast.py        # Async upload to R2
│   ├── api_client.py         # Workflow client
│   └── run_pipeline.py       # Orchestrator
├── reports/
│   ├── modules/              # 13 analysis modules (Python)
│   │   ├── theme.py          # Global dark theme + Tailwind template
│   │   ├── data_loader.py    # Shared data loading
│   │   ├── base_module.py    # Abstract base class
│   │   ├── 01_executive_overview.py
│   │   ├── 02_score_deep_dive.py
│   │   ├── ...
│   │   └── 13_funding_signals.py
│   ├── output/               # Generated HTML + PNG per module
│   ├── article/              # Lead magnet article (HTML)
│   └── analysis/             # Perspective reports + galleries
├── skills/                    # Skill definitions (prompts)
│   ├── 00_pipeline.md        # Pipeline orchestrator
│   ├── 01_extract_tech_data.md
│   ├── 02_generate_tech_dd_report.md
│   ├── 03_generate_infra_diagram.md
│   ├── 04_meta_analysis_charts.md
│   └── 05_html_viewer.md
├── data_export/               # Exported data from D1
│   ├── companies_flat.csv    # 485 companies × 63 columns
│   ├── tech_extracts_full.json
│   ├── funding_research.json # 27 companies with funding data
│   └── company_names.txt
├── company_db/                # Per-company JSON extracts
├── generate_*.py              # Various generation scripts
└── site/                      # Static site (deployed to CF Pages)
```

## Data

The `data_export/` directory contains the full extracted dataset:

- **companies_flat.csv** — 485 rows × 63 columns: scores, booleans, cloud providers, vendor counts, flag counts
- **tech_extracts_full.json** — Rich nested JSON with infrastructure, security, BCDR, vendor, and compliance details per company
- **funding_research.json** — Funding rounds, investors, valuations for 27 top-scoring companies
- **diagrams.json** — Mermaid architecture diagrams (validated)
- **dd_reports.json** — 480 full markdown Tech DD reports

## Running It

```bash
# Install dependencies
uv sync

# Run all analysis modules (generates charts + HTML)
uv run python reports/run_all.py

# Run a single module
uv run python -m reports.modules.04_security_maturity

# Generate the article
uv run python generate_article.py

# Generate D2 diagrams (requires d2 CLI)
uv run python generate_d2_diagrams.py
```

## Shoutouts 🫡

Big respect to the builders. Some companies in this dataset stood out not just for their scores, but for the quality of their engineering and their transparency:

- **[MorphLLM](https://morph.sh)** — 7/10 score, self-hosted Llama models on GPU clusters, backed by Mistral AI. One of the most detailed architecture diagrams in the entire dataset.
- **[FullEnrich](https://fullenrich.com)** — Prometheus + Grafana + LogStash monitoring stack. One of the few companies that actually names their observability tools.
- **[Domu](https://domu.ai)** — AI voice agent for debt collection, WAF + API Gateway + 6 AZ deployment. Punching above their weight on infrastructure for a seed-stage company.
- **[AgentMail](https://agentmail.cc)** — Multi-region AWS (us-west-1 + us-east-1), the only company with explicit dual-region architecture from day one.
- **[Browser Use](https://browser-use.com)** — Making AI agents actually work in the browser. The future of automation.

And to everyone at **[WhiteContext](https://whitecontext.com)** — this whole pipeline was built in a single Claude Code session. From PDF extraction to Cloudflare deployment to this README. That's the power of agentic engineering.

## Authors

- **Jacek Podoba** — CEO, [Altimi.com](https://altimi.com)
- **Maksym Huczyński** — CTO, [WhiteContext.com](https://whitecontext.com)

## License

The analysis methodology, code, and generated reports are open source. The underlying SOC 2 compliance reports are the property of their respective companies and are not included in this repository.

---

*Built with Claude Code, Cloudflare Workers AI, D1, R2, and a lot of curiosity about what's actually running behind the pitch deck.*
