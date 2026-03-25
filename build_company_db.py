"""
Parse the compliance reports CSV and build a file-based company database.
Maps Google Doc IDs from links to PDF/TXT report files.
"""
import csv
import json
import os
import re
from pathlib import Path

CSV_PATH = "overview_docs/1o_u2S75797hDNOKpJLXYqYU22DjWYsrekPjP6yXPlSg.csv"
PDF_DIR = Path("pdf_reports")
TXT_DIR = Path("txt_reports")
OUTPUT_DIR = Path("company_db")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_doc_id(link: str) -> str | None:
    """Extract Google Doc ID from URL."""
    if not link:
        return None
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
    return m.group(1) if m else None

def resolve_company(row: dict) -> dict:
    """Normalize company info across SOC2 Type1, Type2, and ISO 27001 column layouts."""
    report_type = row.get("Type", "").strip()

    if report_type == "SOC 2 Type 1":
        return {
            "legal_name": row.get("Legal Name", "").strip(),
            "company_name": row.get("Company Name", "").strip(),
            "system_name": row.get("System Name", "").strip(),
            "audit_end_date": row.get("Audit End Date", "").strip(),
            "observation_period": "",
            "infra_provider": row.get("Infra Provider", "").strip(),
            "website": row.get("Company Website", "").strip(),
            "contact_email": row.get("Company Contact Email", "").strip(),
            "address": "",
            "report_type": report_type,
        }
    elif report_type == "SOC 2 Type 2":
        return {
            "legal_name": row.get("Legal Name (type 2)", "").strip(),
            "company_name": row.get("Company Name (type 2)", "").strip(),
            "system_name": row.get("System Name (type 2)", "").strip(),
            "audit_end_date": row.get("Audit End Date", "").strip(),
            "observation_period": row.get("Observation Period (type 2)", "").strip(),
            "infra_provider": row.get("Infra Provider (type 2)", "").strip(),
            "website": row.get("Company Website (type 2)", "").strip(),
            "contact_email": row.get("Company Contact Email (type 2)", "").strip(),
            "address": "",
            "report_type": report_type,
        }
    elif report_type == "ISO 27001":
        return {
            "legal_name": row.get("Legal Name of Company", "").strip(),
            "company_name": row.get("Company Name", "").strip(),  # often empty for ISO
            "system_name": row.get("System Name", "").strip(),
            "audit_end_date": "",
            "observation_period": row.get("Observation Period", "").strip(),
            "infra_provider": row.get("Infra Provider", "").strip(),
            "website": row.get("Company Website", "").strip(),
            "contact_email": "",
            "address": row.get("Company Address", "").strip(),
            "report_type": report_type,
        }
    else:
        return {
            "legal_name": "",
            "company_name": "",
            "system_name": "",
            "audit_end_date": "",
            "observation_period": "",
            "infra_provider": "",
            "website": "",
            "contact_email": "",
            "address": "",
            "report_type": report_type,
        }

# Parse CSV
companies = []
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    # The CSV header has duplicate column names (Audit End Date appears twice).
    # csv.DictReader picks the last one by default, so we need to handle this.
    reader = csv.reader(f)
    raw_headers = next(reader)

    # Deduplicate headers by appending suffix
    seen = {}
    headers = []
    for h in raw_headers:
        h = h.strip()
        if h in seen:
            seen[h] += 1
        else:
            seen[h] = 0
        headers.append(h)

    # Map to expected column indices
    # SOC 2 Type 1 columns: Link(0), Timestamp(1), Type(2), Legal Name(3), Company Name(4),
    #   Audit End Date(5), Observation Period (type 2)(6), System Name(7), Infra Provider(8),
    #   Company Website(9), Company Contact Email(10)
    # SOC 2 Type 2 columns: Legal Name (type 2)(11), Company Name (type 2)(12),
    #   System Name (type 2)(13), Audit End Date(14), Infra Provider (type 2)(15),
    #   Company Website (type 2)(16), Company Contact Email (type 2)(17)
    # ISO 27001 columns: Legal Name of Company(18), Company Name(19), System Name(20),
    #   Observation Period(21), Infra Provider(22), Company Website(23), Company Address(24)

    for row_vals in reader:
        if len(row_vals) < 11:
            continue
        # Pad row if needed
        while len(row_vals) < 25:
            row_vals.append("")

        link = row_vals[0].strip()
        timestamp = row_vals[1].strip()
        report_type = row_vals[2].strip()
        doc_id = extract_doc_id(link)

        if report_type == "SOC 2 Type 1":
            info = {
                "legal_name": row_vals[3].strip(),
                "company_name": row_vals[4].strip(),
                "system_description": row_vals[7].strip(),
                "audit_end_date": row_vals[5].strip(),
                "observation_period": "",
                "infra_provider": row_vals[8].strip(),
                "website": row_vals[9].strip(),
                "contact_email": row_vals[10].strip(),
                "address": "",
                "report_type": report_type,
            }
        elif report_type == "SOC 2 Type 2":
            info = {
                "legal_name": row_vals[11].strip(),
                "company_name": row_vals[12].strip(),
                "system_description": row_vals[13].strip(),
                "audit_end_date": row_vals[14].strip() if len(row_vals) > 14 else "",
                "observation_period": row_vals[6].strip(),
                "infra_provider": row_vals[15].strip(),
                "website": row_vals[16].strip(),
                "contact_email": row_vals[17].strip(),
                "address": "",
                "report_type": report_type,
            }
        elif report_type == "ISO 27001":
            info = {
                "legal_name": row_vals[18].strip(),
                "company_name": "",
                "system_description": "",
                "audit_end_date": "",
                "observation_period": "",
                "infra_provider": "",
                "website": "",
                "contact_email": "",
                "address": row_vals[24].strip() if len(row_vals) > 24 else "",
                "report_type": report_type,
            }
        else:
            continue

        # Check if PDF and TXT exist
        has_pdf = doc_id and (PDF_DIR / f"{doc_id}.pdf").exists()
        has_txt = doc_id and (TXT_DIR / f"{doc_id}.txt").exists()

        # Build display name
        display_name = info["company_name"] or info["legal_name"] or "Unknown"

        company = {
            "doc_id": doc_id,
            "link": link,
            "timestamp": timestamp,
            "display_name": display_name,
            **info,
            "pdf_file": f"{doc_id}.pdf" if has_pdf else None,
            "txt_file": f"{doc_id}.txt" if has_txt else None,
            "has_report": has_pdf or has_txt,
        }
        companies.append(company)

# Deduplicate by doc_id (keep first occurrence which is most recent by timestamp)
seen_ids = set()
unique_companies = []
no_link = []
for c in companies:
    if c["doc_id"] is None:
        no_link.append(c)
        continue
    if c["doc_id"] not in seen_ids:
        seen_ids.add(c["doc_id"])
        unique_companies.append(c)

# Stats
total = len(unique_companies)
with_pdf = sum(1 for c in unique_companies if c["pdf_file"])
with_txt = sum(1 for c in unique_companies if c["txt_file"])
by_type = {}
by_infra = {}
for c in unique_companies:
    rt = c["report_type"]
    by_type[rt] = by_type.get(rt, 0) + 1
    ip = c["infra_provider"] or "Unknown/Not Listed"
    by_infra[ip] = by_infra.get(ip, 0) + 1

print(f"=== Company Database Stats ===")
print(f"Total unique companies (with doc ID): {total}")
print(f"Rows without link: {len(no_link)}")
print(f"With PDF report: {with_pdf}")
print(f"With TXT report: {with_txt}")
print(f"\nBy report type:")
for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print(f"\nBy infra provider:")
for k, v in sorted(by_infra.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Save master index
with open(OUTPUT_DIR / "companies_index.json", "w") as f:
    json.dump({
        "total_companies": total,
        "rows_without_link": len(no_link),
        "with_pdf": with_pdf,
        "with_txt": with_txt,
        "by_report_type": by_type,
        "by_infra_provider": by_infra,
        "companies": unique_companies,
    }, f, indent=2)

# Save individual company files for easy lookup
for c in unique_companies:
    doc_id = c["doc_id"]
    with open(OUTPUT_DIR / f"{doc_id}.json", "w") as f:
        json.dump(c, f, indent=2)

# Save companies without links separately
if no_link:
    with open(OUTPUT_DIR / "no_link_entries.json", "w") as f:
        json.dump(no_link, f, indent=2)

# Check for PDFs that don't match any CSV entry
all_pdf_ids = {p.stem for p in PDF_DIR.glob("*.pdf")}
csv_ids = {c["doc_id"] for c in unique_companies}
orphan_pdfs = all_pdf_ids - csv_ids
if orphan_pdfs:
    print(f"\nOrphan PDFs (no CSV match): {len(orphan_pdfs)}")
    with open(OUTPUT_DIR / "orphan_pdfs.json", "w") as f:
        json.dump(sorted(orphan_pdfs), f, indent=2)

unmatched_csv = csv_ids - all_pdf_ids
if unmatched_csv:
    print(f"CSV entries without PDF: {len(unmatched_csv)}")

print(f"\nDatabase written to {OUTPUT_DIR}/")
print(f"  - companies_index.json (master index)")
print(f"  - {total} individual company JSON files")
