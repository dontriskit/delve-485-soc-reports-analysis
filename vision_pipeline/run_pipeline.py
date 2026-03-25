"""
Main pipeline orchestrator: PDF -> images -> Cloudflare Workflow -> D1

Usage:
  uv run python -m vision_pipeline.run_pipeline                    # process all remaining
  uv run python -m vision_pipeline.run_pipeline --limit 10         # process 10 companies
  uv run python -m vision_pipeline.run_pipeline --skip-convert     # skip PDF conversion
  uv run python -m vision_pipeline.run_pipeline --status           # check progress only
"""
import asyncio
import argparse
import json
import sys
import time
from pathlib import Path
from tqdm import tqdm

from .config import COMPANY_DB, PAGE_IMAGES_DIR, PDF_DIR
from .convert_pdfs import convert_all_pdfs, convert_single_pdf
from .api_client import WorkflowClient


WORKER_URL = "https://delve-vision-extract.whitecontext.workers.dev"


def load_company_index() -> list[dict]:
    with open(COMPANY_DB / "companies_index.json") as f:
        return json.load(f)["companies"]


def get_todo_list(skip_iso: bool = True) -> list[dict]:
    """Get companies that need processing."""
    companies = load_company_index()
    # Check which already have extracts in local DB
    existing = {
        p.stem.replace("_tech_extract", "")
        for p in COMPANY_DB.glob("*_tech_extract.json")
    }

    todo = []
    for c in companies:
        doc_id = c.get("doc_id")
        if not doc_id or not c.get("pdf_file"):
            continue
        if skip_iso and "ISO" in c.get("report_type", ""):
            continue
        if doc_id in existing:
            continue
        todo.append(c)
    return todo


async def process_batch(
    client: WorkflowClient,
    companies: list[dict],
    concurrent: int = 10,
) -> dict:
    """Process a batch of companies through workflows."""
    semaphore = asyncio.Semaphore(concurrent)
    results = {"completed": 0, "failed": 0, "errors": []}

    async def process_one(company: dict):
        doc_id = company["doc_id"]
        display = company.get("display_name", "Unknown")
        report_type = company.get("report_type", "SOC 2")

        img_dir = PAGE_IMAGES_DIR / doc_id
        pages = sorted(img_dir.glob("page-*.jpg"))

        if not pages:
            results["failed"] += 1
            results["errors"].append((doc_id, display, "No page images"))
            return

        async with semaphore:
            try:
                # Start workflow
                wf_id = await client.start_workflow(doc_id, display, report_type, pages)
                if not wf_id:
                    results["failed"] += 1
                    results["errors"].append((doc_id, display, "Failed to start workflow"))
                    return

                # Poll for completion (max 15 min per company)
                result = await client.wait_for_completion(wf_id, poll_interval=20, max_wait=900)

                if result:
                    # Save locally as well
                    output_path = COMPANY_DB / f"{doc_id}_tech_extract.json"
                    with open(output_path, "w") as f:
                        json.dump(result, f, indent=2)
                    results["completed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append((doc_id, display, "Workflow timeout/error"))

            except Exception as e:
                results["failed"] += 1
                results["errors"].append((doc_id, display, str(e)))

    # Process all companies with concurrency limit
    tasks = [process_one(c) for c in companies]

    # Use tqdm for progress tracking
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing"):
        await coro

    return results


async def check_status():
    """Check current pipeline status from D1."""
    import urllib.request
    try:
        req = urllib.request.Request(
            f"{WORKER_URL}/api/stats",
            headers={"User-Agent": "DelveVisionPipeline/2.0"},
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())

        stats = data.get("stats", {})
        score_dist = data.get("score_distribution", [])
        cloud_dist = data.get("cloud_distribution", [])

        print("=== Pipeline Status ===\n")
        print(f"Companies in DB:    {stats.get('total_companies', 0)}")
        print(f"Extracted:          {stats.get('total_extracted', 0)}")
        print(f"Scored:             {stats.get('scored', 0)}")
        print(f"Avg score:          {stats.get('avg_score', 0)}/10")
        print(f"High scorers (7+):  {stats.get('high_scorers', 0)}")
        print(f"Low scorers (≤3):   {stats.get('low_scorers', 0)}")

        remaining = stats.get("total_companies", 0) - stats.get("total_extracted", 0)
        print(f"Remaining:          {remaining}")

        if score_dist:
            print("\nScore distribution:")
            for s in score_dist:
                bar = "█" * s["count"]
                print(f"  {s['score']:>2}/10: {bar} ({s['count']})")

        if cloud_dist:
            print("\nCloud providers:")
            for c in cloud_dist[:5]:
                print(f"  {c['infra_provider']}: {c['count']}")

    except Exception as e:
        print(f"Error fetching status: {e}")


async def run(args):
    """Main pipeline."""
    if args.status:
        await check_status()
        return

    print("=== Delve Vision Pipeline ===\n")

    # 1. Get companies to process
    todo = get_todo_list(skip_iso=not args.include_iso)
    if args.limit:
        todo = todo[:args.limit]

    print(f"Companies to process: {len(todo)}")
    if not todo:
        print("Nothing to do! All companies are extracted.")
        await check_status()
        return

    # 2. Convert PDFs to images
    if not args.skip_convert:
        print(f"\n--- Phase 1: Converting {len(todo)} PDFs to images ---")
        doc_ids = [c["doc_id"] for c in todo]
        page_counts = convert_all_pdfs(doc_ids)
        print(f"Converted: {len(page_counts)} PDFs, {sum(page_counts.values())} total pages")

        # Filter out companies with no images
        todo = [c for c in todo if c["doc_id"] in page_counts]
    else:
        # Verify images exist
        todo = [
            c for c in todo
            if (PAGE_IMAGES_DIR / c["doc_id"]).exists()
            and list((PAGE_IMAGES_DIR / c["doc_id"]).glob("page-*.jpg"))
        ]
        print(f"Companies with images: {len(todo)}")

    if not todo:
        print("No companies with images to process!")
        return

    # 3. Send to Cloudflare Workflows
    print(f"\n--- Phase 2: Sending to Cloudflare Workflows ---")
    print(f"Concurrent workflows: {args.concurrent}")

    async with WorkflowClient(max_concurrent_workflows=args.concurrent) as client:
        results = await process_batch(client, todo, concurrent=args.concurrent)
        client.print_stats()

    # 4. Report
    print(f"\n=== Pipeline Complete ===")
    print(f"Completed: {results['completed']}")
    print(f"Failed:    {results['failed']}")

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for doc_id, name, err in results["errors"][:20]:
            print(f"  {name}: {err}")

    # 5. Show updated status
    print()
    await check_status()


def main():
    parser = argparse.ArgumentParser(description="Delve Vision Pipeline")
    parser.add_argument("--limit", type=int, help="Max companies to process")
    parser.add_argument("--concurrent", type=int, default=10, help="Concurrent workflows")
    parser.add_argument("--skip-convert", action="store_true", help="Skip PDF conversion")
    parser.add_argument("--include-iso", action="store_true", help="Include ISO 27001 reports")
    parser.add_argument("--status", action="store_true", help="Show status only")
    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
