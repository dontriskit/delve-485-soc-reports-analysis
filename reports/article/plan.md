# Article Plan: Tech DD Lead Magnet for VC/PE

## Title Options
- "We Analyzed 485 SOC 2 Reports. Here's What We Found About Startup Tech Maturity."
- "The State of Tech Due Diligence: Insights from 485 AI Startup Compliance Reports"
- "What 485 Compliance Reports Reveal About Startup Infrastructure — A Tech DD Benchmark"

## Audience
PE firms, VCs, Angels evaluating early-stage AI/SaaS companies.
Also: CTOs benchmarking their own compliance.

## CTA
"Get your portfolio analyzed" / "Request a Tech DD assessment"

## Structure (~4500 words)

### 1. Hook / Executive Summary (300 words)
- We read 485 SOC 2 reports so you don't have to
- The portfolio: mostly AI/SaaS startups, all submitted for compliance
- Key stat: only 4% meet full maturity criteria
- Charts: score distribution, investment funnel

### 2. Methodology (200 words)
- How we extracted data (vision AI on PDF pages)
- 7-dimension scoring rubric
- What SOC 2 reports do and don't tell you

### 3. The Score Landscape (500 words)
- Distribution: tight cluster at 5-6/10
- Dimension breakdown: security strongest, vendor diversity weakest
- What drives high scores
- Charts: dimension bars, correlation matrix

### 4. Cloud Infrastructure Landscape (400 words)
- AWS dominance (60%+) — systemic portfolio risk
- PaaS-first pattern (Supabase/Vercel) — speed vs control trade-off
- Cloud provider vs score
- Chart: cloud share donut, cloud vs score

### 5. The Security Maturity Ladder (600 words)
- Three-tier model: table stakes / differentiators / rare
- Feature adoption rates
- Which features predict higher scores
- Chart: security ladder, feature impact bars

### 6. Vendor Transparency = Engineering Culture (400 words)
- The surprising finding: naming more vendors correlates with higher scores
- Why transparency is a maturity proxy
- Top vendors across the portfolio
- Chart: vendor count vs score

### 7. The BCDR Gap (300 words)
- Policy vs practice: 100% have policy, 51% test, 28% multi-region
- The resilience gap waterfall
- Chart: BCDR waterfall

### 8. Red Flags: What to Watch For (400 words)
- Top 10 red flags by frequency
- Which flags matter most (severity analysis)
- Template artifacts — the compliance-as-checkbox signal
- Chart: red flag categories

### 9. The AI Stack Inside the Portfolio (400 words)
- OpenAI dominance, Anthropic rising
- Voice AI stack: Twilio + ElevenLabs
- Self-hosted LLMs as IP moat signal
- Chart: AI vendor landscape

### 10. The Investment Readiness Funnel (400 words)
- 485 → Type 2 → Scored 5+ → 7+ → Multi-region+WAF → Full maturity
- Only 4% make it through
- What the cheapest fixes are
- Chart: funnel

### 11. Top Performers: What They Do Differently (400 words)
- Profile top 5 companies
- Common patterns: multi-region, transparent vendors, named monitoring
- The gold standard checklist
- Chart: top vs bottom comparison

### 12. Implications for Investors (300 words)
- PE: value creation levers (WAF, multi-region, vendor consolidation)
- VC: signal vs noise in SOC 2 reports
- Due diligence checklist (10 questions to ask)

### 13. CTA / About (200 words)
- "This analysis was performed by Delve's automated Tech DD pipeline"
- "Get your portfolio analyzed — contact us"

## Charts to Embed (from existing modules)
1. score_distribution.png (from 01)
2. dimension_averages.png (from 01)
3. cloud_share.png (from 03)
4. security_ladder.png (from 04)
5. feature_impact.png (from 04)
6. vendor_vs_score.png (from 05)
7. resilience_gap.png (from 07)
8. red_flag_categories.png (from 10)
9. ai_share.png (from 09)
10. funnel.png (from 11)
11. top_vs_bottom.png (from 12)
12. cloud_vs_score.png (from 03)

## Design
- Single-page HTML with Tailwind CSS
- Dark theme matching existing report system
- Charts embedded as base64 data URIs (self-contained)
- Responsive layout
- Sticky TOC sidebar on desktop
- Professional typography (Inter font)
