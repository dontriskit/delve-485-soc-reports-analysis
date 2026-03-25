"""Convert PDFs to JPEG page images using pdftoppm."""
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
from .config import PDF_DIR, PAGE_IMAGES_DIR, DPI, PDF_CONVERT_WORKERS


def get_page_count(pdf_path: Path) -> int:
    r = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    return 0


def convert_single_pdf(doc_id: str) -> tuple[str, int, str | None]:
    """Convert one PDF to JPEGs. Returns (doc_id, page_count, error)."""
    pdf_path = PDF_DIR / f"{doc_id}.pdf"
    if not pdf_path.exists():
        return doc_id, 0, "PDF not found"

    out_dir = PAGE_IMAGES_DIR / doc_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check if already converted
    existing = sorted(out_dir.glob("page-*.jpg"))
    expected = get_page_count(pdf_path)
    if len(existing) == expected and expected > 0:
        return doc_id, expected, None

    try:
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", str(DPI), str(pdf_path), str(out_dir / "page")],
            capture_output=True, check=True, timeout=120,
        )
        pages = sorted(out_dir.glob("page-*.jpg"))
        return doc_id, len(pages), None
    except subprocess.CalledProcessError as e:
        return doc_id, 0, f"pdftoppm error: {e.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return doc_id, 0, "Timeout (>120s)"


def convert_all_pdfs(doc_ids: list[str]) -> dict[str, int]:
    """Convert all PDFs in parallel. Returns {doc_id: page_count}."""
    PAGE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    errors = []

    with ProcessPoolExecutor(max_workers=PDF_CONVERT_WORKERS) as pool:
        futures = {pool.submit(convert_single_pdf, did): did for did in doc_ids}
        for future in tqdm(as_completed(futures), total=len(doc_ids), desc="Converting PDFs"):
            doc_id, count, error = future.result()
            if error:
                errors.append((doc_id, error))
            else:
                results[doc_id] = count

    if errors:
        print(f"\n{len(errors)} conversion errors:")
        for did, err in errors[:10]:
            print(f"  {did[:30]}... : {err}")

    return results
