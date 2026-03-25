"""Client for the Cloudflare Workflow-based vision extraction."""
import asyncio
import base64
import json
import time
from pathlib import Path
import aiohttp

WORKER_URL = "https://delve-vision-extract.whitecontext.workers.dev"


class WorkflowClient:
    """Client that sends pages to the CF Workflow and polls for results."""

    def __init__(self, max_concurrent_workflows: int = 20):
        self.worker_url = WORKER_URL
        self.max_concurrent = max_concurrent_workflows
        self.semaphore = asyncio.Semaphore(max_concurrent_workflows)
        self.session: aiohttp.ClientSession | None = None
        self.total_started = 0
        self.total_completed = 0
        self.total_failed = 0

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Content-Type": "application/json", "User-Agent": "DelveVisionPipeline/2.0"},
            timeout=aiohttp.ClientTimeout(total=600),
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def start_workflow(self, doc_id: str, company_name: str, report_type: str, page_images: list[Path]) -> str | None:
        """Start a workflow for a company. Chunks pages into batches of 10 to avoid payload limits."""
        # Build all page data
        all_pages = []
        for i, img_path in enumerate(page_images):
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            all_pages.append({"page_num": i + 1, "image_base64": b64})

        # Send in chunks of 10 pages
        CHUNK_SIZE = 10
        chunks = [all_pages[i:i+CHUNK_SIZE] for i in range(0, len(all_pages), CHUNK_SIZE)]

        workflow_ids = []
        for ci, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}__chunk{ci}"
            payload = {
                "doc_id": chunk_id,
                "company_name": company_name,
                "report_type": report_type,
                "pages": chunk,
            }

            async with self.semaphore:
                try:
                    async with self.session.post(f"{self.worker_url}/process", json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            workflow_ids.append(data.get("workflow_id"))
                            self.total_started += 1
                        else:
                            text = await resp.text()
                            print(f"  Chunk {ci} start failed ({resp.status}): {text[:200]}")
                            workflow_ids.append(None)
                except Exception as e:
                    print(f"  Chunk {ci} start error: {e}")
                    workflow_ids.append(None)

            # Small delay between chunks to avoid rate limits
            await asyncio.sleep(1)

        return json.dumps({"chunks": workflow_ids, "total_chunks": len(chunks)}) if any(workflow_ids) else None

    async def check_status(self, workflow_id: str) -> dict:
        """Check workflow status. Returns {status, output}."""
        try:
            async with self.session.get(f"{self.worker_url}/status/{workflow_id}") as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"status": "unknown", "error": resp.status}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def wait_for_completion(self, workflow_info: str, poll_interval: int = 20, max_wait: int = 900) -> dict | None:
        """Poll until all workflow chunks complete. Merges chunk results."""
        info = json.loads(workflow_info)
        chunk_ids = info["chunks"]
        total = info["total_chunks"]

        start = time.monotonic()
        chunk_results = [None] * total

        while time.monotonic() - start < max_wait:
            all_done = True
            for i, wf_id in enumerate(chunk_ids):
                if chunk_results[i] is not None or wf_id is None:
                    continue

                status = await self.check_status(wf_id)
                s = status.get("status", {})
                state = s.get("status") if isinstance(s, dict) else s

                if state == "complete":
                    chunk_results[i] = s.get("output") if isinstance(s, dict) else status.get("output")
                elif state in ("errored", "terminated"):
                    chunk_results[i] = {"_error": True}
                else:
                    all_done = False

            if all_done:
                # Merge all chunk results
                valid = [r for r in chunk_results if r and not r.get("_error")]
                if not valid:
                    self.total_failed += 1
                    return None

                # Use first chunk as base, merge the rest
                merged = valid[0]
                for chunk in valid[1:]:
                    # Merge page extractions and vendors
                    if chunk.get("third_party_services"):
                        existing = {v["vendor"] for v in (merged.get("third_party_services") or [])}
                        for v in chunk["third_party_services"]:
                            if v["vendor"] not in existing:
                                merged.setdefault("third_party_services", []).append(v)
                    # Merge key observations
                    if chunk.get("key_observations"):
                        merged.setdefault("key_observations", []).extend(chunk["key_observations"])
                    # Merge system description
                    if chunk.get("system_description", {}).get("overview"):
                        if merged.get("system_description", {}).get("overview"):
                            merged["system_description"]["overview"] += " " + chunk["system_description"]["overview"]
                        else:
                            merged.setdefault("system_description", {})["overview"] = chunk["system_description"]["overview"]
                    # Keep highest scores
                    for key in ("scoring",):
                        if chunk.get(key) and isinstance(chunk[key], dict):
                            if not merged.get(key):
                                merged[key] = chunk[key]

                self.total_completed += 1
                return merged

            await asyncio.sleep(poll_interval)

        self.total_failed += 1
        return None

    async def extract_single_page(self, image_path: Path, company_name: str, report_type: str) -> dict | None:
        """Direct single-page extraction (no workflow, for quick tests)."""
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        payload = {
            "image_base64": b64,
            "company_name": company_name,
            "report_type": report_type,
        }

        try:
            async with self.session.post(f"{self.worker_url}/extract-one", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result")
                return None
        except Exception as e:
            return None

    async def process_company(self, doc_id: str, company_name: str, report_type: str, page_images: list[Path]) -> dict | None:
        """Full pipeline: start workflow, wait for result."""
        wf_id = await self.start_workflow(doc_id, company_name, report_type, page_images)
        if not wf_id:
            return None

        result = await self.wait_for_completion(wf_id, poll_interval=15, max_wait=900)
        if result:
            self.total_completed += 1
        return result

    def print_stats(self):
        print(f"\n=== Workflow Stats ===")
        print(f"Started:   {self.total_started}")
        print(f"Completed: {self.total_completed}")
        print(f"Failed:    {self.total_failed}")
