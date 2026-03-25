"""Pipeline configuration — reads from environment variables."""
import os
from pathlib import Path

BASE_DIR = Path("/home/mhm/Documents/delve")
PDF_DIR = BASE_DIR / "pdf_reports"
COMPANY_DB = BASE_DIR / "company_db"
PAGE_IMAGES_DIR = BASE_DIR / "page_images"
REPORTS_DIR = BASE_DIR / "reports"

# Cloudflare Workers AI
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_MODEL = "@cf/moonshotai/kimi-k2.5"
CF_API_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"

# Processing
DPI = 150
MAX_CONCURRENT = 50
RATE_LIMIT_PER_MIN = 280
MAX_RETRIES = 3
PDF_CONVERT_WORKERS = 8

# Progress tracking
PROGRESS_FILE = COMPANY_DB / "vision_pipeline_status.json"
