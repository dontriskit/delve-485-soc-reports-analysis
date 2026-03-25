# SKILL: Tech DD Pipeline Orchestrator

## Purpose
End-to-end pipeline that runs all Tech DD skills for one or many companies.

## Usage

### Single company
```
Run pipeline for DOC_ID=1iLWI1vyf09MepflEFzeuRBioyuKaxWblWloQiEaUnUA
```

### Batch (all companies)
```
Run pipeline for ALL companies in company_db/companies_index.json
```

### Meta-analysis only (after batch extraction)
```
Run Skill 04 + Skill 05 only
```

## Pipeline Steps

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 0: Validate prerequisites                             │
│  - company_db/companies_index.json exists                   │
│  - pdf_reports/ directory exists with PDFs                  │
│  - d2 is installed (~/.local/bin/d2)                        │
│  - Python deps available (seaborn, pandas, matplotlib)      │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Extract (Skill 01) — PARALLELIZABLE                │
│  For each company:                                          │
│    - Launch subagent with skills/01_extract_tech_data.md     │
│    - Input: DOC_ID                                          │
│    - Output: company_db/{DOC_ID}_tech_extract.json          │
│                                                              │
│  ⚡ Run up to 5 subagents in parallel                       │
│  ⚡ Skip companies that already have _tech_extract.json      │
│     (unless --force flag)                                    │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Report (Skill 02) — PARALLELIZABLE                 │
│  For each company with _tech_extract.json:                  │
│    - Launch subagent with skills/02_generate_tech_dd.md      │
│    - Input: DOC_ID                                          │
│    - Output: reports/{slug}_tech_dd_report.md                │
│                                                              │
│  ⚡ Run up to 5 subagents in parallel                       │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Diagram (Skill 03) — PARALLELIZABLE                │
│  For each company with _tech_extract.json:                  │
│    - Launch subagent with skills/03_generate_infra_diagram.md│
│    - Input: DOC_ID                                          │
│    - Output: reports/{slug}_infra.d2 + .png                 │
│                                                              │
│  ⚡ Run up to 3 subagents in parallel (D2 is CPU-heavy)     │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Meta-Analysis (Skill 04)                            │
│  - Run once after all extractions complete                   │
│  - Input: all company_db/*_tech_extract.json                │
│  - Output: reports/charts/*.png + meta_summary.json          │
│                                                              │
│  ⚠ Requires minimum 5 companies for meaningful analysis     │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: HTML Viewer (Skill 05)                              │
│  - Run once after all previous steps complete                │
│  - Input: all outputs from Steps 1-4                        │
│  - Output: reports/tech_dd_viewer.html                       │
│                                                              │
│  Final deliverable — open in browser                        │
└─────────────────────────────────────────────────────────────┘
```

## Batch Execution Strategy

For 576 companies, running all steps sequentially would take too long. Use this strategy:

### Phase 1: Mass Extraction (Skill 01)
- Process companies in batches of 5 parallel subagents
- Each subagent reads 1 PDF (4 read calls of 20 pages each)
- Estimated: ~2 min per company, ~5 companies per batch
- Total: ~116 batches × 2 min = ~4 hours
- Save progress: skip DOC_IDs that already have `_tech_extract.json`

### Phase 2: Mass Reports + Diagrams (Skills 02 & 03)
- Can run in parallel since they only read JSON (no PDFs)
- Reports: 5 parallel, ~30s each → ~1 hour
- Diagrams: 3 parallel (CPU-bound D2), ~15s each → ~1.5 hours

### Phase 3: Analysis + Viewer (Skills 04 & 05)
- Single run each, ~5 min total

### Resume/Recovery
- Each step checks for existing output before processing
- If a subagent fails, log the DOC_ID and continue
- After batch completes, report: {completed}/{total}, list failures
- Failures can be retried individually

## Progress Tracking
After each batch, update `company_db/pipeline_status.json`:
```json
{
  "last_run": "2026-03-24T...",
  "step1_extract": {"completed": 576, "failed": 3, "skipped": 0},
  "step2_report": {"completed": 573, "failed": 0, "skipped": 3},
  "step3_diagram": {"completed": 573, "failed": 5, "skipped": 3},
  "step4_charts": {"status": "completed"},
  "step5_viewer": {"status": "completed"},
  "failures": [
    {"doc_id": "xxx", "step": 1, "error": "PDF unreadable"}
  ]
}
```

## Quick Test
To verify the pipeline works end-to-end before running the full batch:
```
Run pipeline for these 2 test companies:
- 1iLWI1vyf09MepflEFzeuRBioyuKaxWblWloQiEaUnUA (11x AI)
- 1EMKlQpbmyu0V9UaaNPBU2ri6PRtTgEKxnmSzlyNgLkI (AgentMail)
```
This tests all 5 skills on known-good data with known expected output.
