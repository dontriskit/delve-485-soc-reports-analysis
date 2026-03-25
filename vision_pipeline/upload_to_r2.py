"""
Convert all PDFs to page images and upload to R2 via wrangler.

Usage:
  uv run python -m vision_pipeline.upload_to_r2              # all PDFs
  uv run python -m vision_pipeline.upload_to_r2 --limit 10   # first 10
  uv run python -m vision_pipeline.upload_to_r2 --skip-iso   # skip ISO 27001
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

from .config import COMPANY_DB, PAGE_IMAGES_DIR, PDF_DIR, PDF_CONVERT_WORKERS
from .convert_pdfs import convert_single_pdf


def upload_file_to_r2(local_path: Path, r2_key: str) -> tuple[str, bool, str]:
    """Upload a single file to R2 via wrangler."""
    try:
        result = subprocess.run(
            ["wrangler", "r2", "object", "put", f"delve-pages/{r2_key}",
             "--file", str(local_path), "--content-type", "image/jpeg"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return r2_key, True, ""
        return r2_key, False, result.stderr[:200]
    except Exception as e:
        return r2_key, False, str(e)


def upload_company_pages(doc_id: str) -> tuple[str, int, int]:
    """Upload all page images for a company. Returns (doc_id, uploaded, failed)."""
    img_dir = PAGE_IMAGES_DIR / doc_id
    if not img_dir.exists():
        return doc_id, 0, 0

    pages = sorted(img_dir.glob("page-*.jpg"))
    uploaded = 0
    failed = 0

    for page_path in pages:
        r2_key = f"{doc_id}/{page_path.name}"
        _, success, _ = upload_file_to_r2(page_path, r2_key)
        if success:
            uploaded += 1
        else:
            failed += 1

    return doc_id, uploaded, failed


def main():
    parser = argparse.ArgumentParser(description="Upload page images to R2")
    parser.add_argument("--limit", type=int, help="Max companies")
    parser.add_argument("--skip-iso", action="store_true", help="Skip ISO 27001")
    parser.add_argument("--skip-convert", action="store_true", help="Skip PDF conversion")
    parser.add_argument("--upload-workers", type=int, default=4, help="Parallel upload threads")
    args = parser.parse_args()

    # 1. Get company list
    with open(COMPANY_DB / "companies_index.json") as f:
        companies = json.load(f)["companies"]

    todo = [c for c in companies if c.get("doc_id") and c.get("pdf_file")]
    if args.skip_iso:
        todo = [c for c in todo if "ISO" not in c.get("report_type", "")]
    if args.limit:
        todo = todo[:args.limit]

    print(f"Companies: {len(todo)}")

    # 2. Convert PDFs to images
    if not args.skip_convert:
        print(f"\n--- Converting PDFs to images ---")
        PAGE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        to_convert = []
        for c in todo:
            img_dir = PAGE_IMAGES_DIR / c["doc_id"]
            if img_dir.exists() and list(img_dir.glob("page-*.jpg")):
                continue
            to_convert.append(c["doc_id"])

        if to_convert:
            print(f"  Need to convert: {len(to_convert)} PDFs")
            with ProcessPoolExecutor(max_workers=PDF_CONVERT_WORKERS) as pool:
                futures = {pool.submit(convert_single_pdf, did): did for did in to_convert}
                converted = 0
                for future in tqdm(as_completed(futures), total=len(to_convert), desc="Converting"):
                    doc_id, count, error = future.result()
                    if not error:
                        converted += 1
                print(f"  Converted: {converted}/{len(to_convert)}")
        else:
            print("  All PDFs already converted")

    # 3. Upload to R2
    print(f"\n--- Uploading to R2 ---")
    total_uploaded = 0
    total_failed = 0

    # Check which are already uploaded by listing R2 (expensive for large buckets)
    # Instead just upload everything — R2 overwrites are fine

    with ThreadPoolExecutor(max_workers=args.upload_workers) as pool:
        futures = {}
        for c in todo:
            doc_id = c["doc_id"]
            img_dir = PAGE_IMAGES_DIR / doc_id
            if not img_dir.exists():
                continue

            pages = sorted(img_dir.glob("page-*.jpg"))
            for page_path in pages:
                r2_key = f"{doc_id}/{page_path.name}"
                futures[pool.submit(upload_file_to_r2, page_path, r2_key)] = r2_key

        print(f"  Uploading {len(futures)} page images...")
        for future in tqdm(as_completed(futures), total=len(futures), desc="Uploading"):
            r2_key, success, error = future.result()
            if success:
                total_uploaded += 1
            else:
                total_failed += 1

    print(f"\n=== Upload Complete ===")
    print(f"Uploaded: {total_uploaded}")
    print(f"Failed:   {total_failed}")

    # 4. Save manifest
    manifest = {}
    for c in todo:
        doc_id = c["doc_id"]
        img_dir = PAGE_IMAGES_DIR / doc_id
        if img_dir.exists():
            pages = sorted(img_dir.glob("page-*.jpg"))
            manifest[doc_id] = {
                "company": c.get("display_name", "Unknown"),
                "report_type": c.get("report_type", ""),
                "pages": len(pages),
                "r2_keys": [f"{doc_id}/{p.name}" for p in pages],
            }

    manifest_path = COMPANY_DB / "r2_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest saved: {manifest_path} ({len(manifest)} companies)")


if __name__ == "__main__":
    main()
