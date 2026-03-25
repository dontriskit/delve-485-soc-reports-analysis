"""
Fast upload of page images to R2 via Worker's /r2/ endpoint.
Uses aiohttp for parallel uploads (50+ concurrent).

Usage:
  uv run python -m vision_pipeline.upload_fast              # all
  uv run python -m vision_pipeline.upload_fast --limit 10   # 10 companies
"""
import asyncio
import argparse
import json
import os
from pathlib import Path
from tqdm import tqdm
import aiohttp

from .config import COMPANY_DB, PAGE_IMAGES_DIR

WORKER_URL = "https://delve-vision-extract.whitecontext.workers.dev"
MAX_CONCURRENT = 50


async def upload_file(session: aiohttp.ClientSession, sem: asyncio.Semaphore, local_path: Path, r2_key: str) -> bool:
    async with sem:
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            async with session.put(
                f"{WORKER_URL}/r2/{r2_key}",
                data=data,
                headers={"Content-Type": "image/jpeg"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                return resp.status == 200
        except Exception:
            return False


async def upload_all(companies: list[dict]):
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    headers = {"User-Agent": "DelveUploader/1.0"}

    # Collect all files to upload
    tasks_data = []
    for c in companies:
        doc_id = c["doc_id"]
        img_dir = PAGE_IMAGES_DIR / doc_id
        if not img_dir.exists():
            continue
        for page_path in sorted(img_dir.glob("page-*.jpg")):
            r2_key = f"{doc_id}/{page_path.name}"
            tasks_data.append((page_path, r2_key))

    print(f"Total files to upload: {len(tasks_data)}")

    uploaded = 0
    failed = 0

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [upload_file(session, sem, lp, rk) for lp, rk in tasks_data]

        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Uploading"):
            success = await coro
            if success:
                uploaded += 1
            else:
                failed += 1

    print(f"\nUploaded: {uploaded}, Failed: {failed}")
    return uploaded, failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--skip-iso", action="store_true", default=True)
    args = parser.parse_args()

    with open(COMPANY_DB / "companies_index.json") as f:
        companies = json.load(f)["companies"]

    todo = [c for c in companies if c.get("doc_id") and c.get("pdf_file")]
    if args.skip_iso:
        todo = [c for c in todo if "ISO" not in c.get("report_type", "")]
    if args.limit:
        todo = todo[:args.limit]

    print(f"Companies: {len(todo)}")
    asyncio.run(upload_all(todo))


if __name__ == "__main__":
    main()
