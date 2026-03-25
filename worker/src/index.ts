/**
 * Delve Vision Extract — Cloudflare Workflow
 *
 * Processes PDF page images through kimi-k2.5 vision model.
 * Each page is a separate workflow step (up to 5 min each).
 *
 * POST /process      — Start extraction for a company (pages as base64 array)
 * POST /process-urls — Start extraction with R2/URL-based images
 * GET  /status/:id   — Check workflow status
 * GET  /health       — Health check
 * POST /extract-one  — Single page extraction (direct, no workflow)
 */
import { WorkflowEntrypoint, WorkflowStep, WorkflowEvent } from 'cloudflare:workers';

// ============ TYPES ============

interface Env {
	AI: Ai;
	PDF_EXTRACT_WORKFLOW: Workflow;
	REPORT_WORKFLOW: Workflow;
	DB: D1Database;
	PAGES: R2Bucket;
}

interface PageInput {
	page_num: number;
	image_base64: string;
	r2_key?: string;
}

interface WorkflowParams {
	doc_id: string;
	company_name: string;
	report_type: string;
	pages: PageInput[];
	use_r2?: boolean;
	single_call?: boolean;
}

// ============ WORKFLOW ============

export class PDFExtractWorkflow extends WorkflowEntrypoint<Env, WorkflowParams> {
	async run(event: WorkflowEvent<WorkflowParams>, step: WorkflowStep) {
		const { doc_id, company_name, report_type, pages, use_r2 } = event.payload;
		const singleCall = (event.payload as any).single_call;

		// Helper: get image as base64 (from payload or R2)
		const getImageBase64 = async (page: PageInput): Promise<string> => {
			if (page.image_base64) return page.image_base64;
			if (use_r2 && page.r2_key) {
				const obj = await this.env.PAGES.get(page.r2_key);
				if (!obj) throw new Error(`R2 object not found: ${page.r2_key}`);
				const buf = await obj.arrayBuffer();
				// Chunked base64 encoding (btoa fails on large buffers)
				const bytes = new Uint8Array(buf);
				let binary = '';
				const chunkSize = 32768;
				for (let i = 0; i < bytes.length; i += chunkSize) {
					const chunk = bytes.subarray(i, i + chunkSize);
					binary += String.fromCharCode.apply(null, chunk as any);
				}
				return btoa(binary);
			}
			throw new Error(`No image source for page ${page.page_num}`);
		};

		// SINGLE-CALL MODE: send all images in one AI call
		if (singleCall) {
			const allInOneResult = await step.do(
				'extract-all-pages-single',
				{
					retries: { limit: 2, delay: "10 seconds", backoff: "exponential" },
					timeout: "5 minutes",
				},
				async () => {
					const content: any[] = [
						{ type: "text", text: `You are analyzing a complete ${report_type} compliance report for ${company_name} (${pages.length} pages). Extract ALL technology, infrastructure, security, vendor, and compliance data. Return a single comprehensive JSON.` },
					];

					// Load all images from R2
					for (const page of pages) {
						const imgB64 = await getImageBase64(page);
						content.push({
							type: "image_url",
							image_url: { url: `data:image/jpeg;base64,${imgB64}` },
						});
					}

					const singlePrompt = `You are a Tech Due Diligence analyst. Analyze ALL pages of this compliance report and extract a comprehensive JSON.

Return ONLY valid JSON (no markdown) with this structure:
{
  "company": "legal name", "product": "product name", "report_type": "SOC 2 Type 1/2",
  "audit_period": "dates", "auditor": "firm", "opinion": "qualified/unqualified",
  "hq": "address", "signing_authority": "name, title",
  "system_description": {"overview": "what they do", "products": {"name": "desc"}},
  "infrastructure": {"cloud_provider": "", "regions": [], "availability_zones": "", "additional_cloud": [], "serverless": [], "cdn": ""},
  "network_architecture": {"vpc": bool, "firewalls": "", "ids_ips": "", "waf": "", "vpn": "", "tls": "", "multi_region": bool, "topology": "traffic flow description"},
  "application_architecture": {"pattern": "", "languages": [], "frameworks": [], "compute": [], "branch_protection": bool},
  "data_storage": {"databases": [], "caching": [], "file_storage": [], "backup_frequency": "", "multi_az": bool, "per_tenant_segregation": bool},
  "authentication_access_control": {"identity_provider": "", "mfa": "", "rbac": bool, "quarterly_access_reviews": bool, "access_revocation_sla": ""},
  "encryption": {"in_transit": "", "at_rest": "", "key_management": ""},
  "ci_cd_devops": {"source_control": "", "ci_cd_tool": "", "iac": "", "branch_protection": "", "separate_environments": bool},
  "monitoring_logging": {"apm_tool": "", "siem": "", "alerting": "", "metrics": [], "log_protection": bool},
  "third_party_services": [{"vendor": "", "purpose": "", "criticality": "Critical/High/Medium/Low"}],
  "security_tools": {"waf": bool, "ids_ips": bool, "vulnerability_scanning": "", "penetration_testing": "", "server_hardening": bool, "cybersecurity_insurance": bool},
  "bcdr": {"bcdr_policy": bool, "annual_testing": bool, "daily_backups": bool, "multi_az_failover": bool, "rto": "", "rpo": ""},
  "compliance_controls": {"total_controls_tested": 0, "exceptions": 0, "untestable": [], "excluded_criteria": []},
  "red_flags": ["critical concerns"],
  "yellow_flags": ["moderate risks"],
  "green_flags": ["strengths"],
  "key_observations": ["non-obvious insights"],
  "has_diagram": bool,
  "is_template_placeholder": bool,
  "template_artifacts": "any placeholder text found"
}

Focus on UNIQUE content — system description, network diagrams, specific tech named, vendor lists. Flag template placeholders ("Your Name Here", yellow highlights).`;

					const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
						messages: [
							{ role: "system", content: singlePrompt },
							{ role: "user", content },
						],
						max_tokens: 8192,
					} as any);

					return parseAIResponse(response);
				}
			);

			// Score it
			const scored = await step.do(
				'score-company',
				{ retries: { limit: 2, delay: "5 seconds" }, timeout: "3 minutes" },
				async () => {
					const prompt = SCORING_PROMPT + `\n\nRespond with ONLY valid JSON matching:\n${JSON.stringify(SCORING_SCHEMA, null, 0)}`;
					const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
						messages: [
							{ role: "system", content: prompt },
							{ role: "user", content: `Score this company:\n${JSON.stringify(allInOneResult)}` },
						],
						max_tokens: 2048,
					} as any);
					return parseAIResponse(response);
				}
			);

			const final = {
				...allInOneResult,
				_page_count: pages.length,
				_extraction_mode: "single_call",
				scoring: scored?.scoring || {},
				red_flags: [...(allInOneResult?.red_flags || []), ...(scored?.red_flags || [])],
				yellow_flags: [...(allInOneResult?.yellow_flags || []), ...(scored?.yellow_flags || [])],
				green_flags: [...(allInOneResult?.green_flags || []), ...(scored?.green_flags || [])],
				key_observations: [...(allInOneResult?.key_observations || []), ...(scored?.key_observations || [])],
			};

			// Save to D1
			await step.do('save-to-d1', async () => {
				const s = final.scoring || {};
				await this.env.DB.prepare(`INSERT OR REPLACE INTO tech_extracts (
					doc_id, company, product, report_type, audit_period, auditor, opinion, hq, signing_authority,
					score_infrastructure, score_app_architecture, score_data_layer, score_security,
					score_devops, score_bcdr, score_vendor_diversity, score_overall,
					scoring_detail, system_description, infrastructure, network_architecture,
					application_architecture, data_storage, authentication, encryption,
					ci_cd_devops, monitoring_logging, security_tools, bcdr, compliance_controls,
					third_party_services, red_flags, yellow_flags, green_flags, key_observations,
					page_count, extraction_method
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).bind(
					doc_id, final.company, final.product, final.report_type, final.audit_period,
					final.auditor, final.opinion, final.hq, final.signing_authority,
					s.infrastructure?.score ?? null, s.application_architecture?.score ?? null,
					s.data_layer?.score ?? null, s.security_posture?.score ?? null,
					s.devops_maturity?.score ?? null, s.bcdr_readiness?.score ?? null,
					s.vendor_diversity?.score ?? null, s.overall?.score ?? null,
					JSON.stringify(final.scoring), JSON.stringify(final.system_description),
					JSON.stringify(final.infrastructure), JSON.stringify(final.network_architecture),
					JSON.stringify(final.application_architecture), JSON.stringify(final.data_storage),
					JSON.stringify(final.authentication_access_control), JSON.stringify(final.encryption),
					JSON.stringify(final.ci_cd_devops), JSON.stringify(final.monitoring_logging),
					JSON.stringify(final.security_tools), JSON.stringify(final.bcdr),
					JSON.stringify(final.compliance_controls), JSON.stringify(final.third_party_services),
					JSON.stringify(final.red_flags), JSON.stringify(final.yellow_flags),
					JSON.stringify(final.green_flags), JSON.stringify(final.key_observations),
					pages.length, 'vision-single'
				).run();

				await this.env.DB.prepare(
					`INSERT OR REPLACE INTO pipeline_status (doc_id, status, pages_total, pages_extracted, completed_at) VALUES (?, 'complete', ?, ?, datetime('now'))`
				).bind(doc_id, pages.length, pages.length).run();
			});

			return final;
		}

		// PER-PAGE MODE: Extract each page separately (one step per page for resilience)
		const pageResults: any[] = [];
		const diagramPages: number[] = [];

		for (const page of pages) {
			const result = await step.do(
				`extract-page-${page.page_num}`,
				{
					retries: { limit: 3, delay: "5 seconds", backoff: "exponential" },
					timeout: "4 minutes",
				},
				async () => {
					const imageB64 = await getImageBase64(page);
					const prompt = SYSTEM_PROMPT_PAGE + `\n\nRespond with ONLY a valid JSON object matching this schema (no markdown, no code fences):\n${JSON.stringify(PAGE_SCHEMA, null, 0)}`;

					const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
						messages: [
							{ role: "system", content: prompt },
							{
								role: "user",
								content: [
									{ type: "text", text: `Extract data from page ${page.page_num} of a ${report_type} report for ${company_name}.` },
									{ type: "image_url", image_url: { url: `data:image/jpeg;base64,${imageB64}` } },
								],
							},
						],
						max_tokens: 4096,
					} as any);

					return parseAIResponse(response);
				}
			);

			pageResults.push({ page_num: page.page_num, ...result });

			if (result?.has_diagram && !result?.is_sample_placeholder) {
				diagramPages.push(page.page_num);
			}
		}

		// Step 2: Diagram detail pass (if diagram pages found)
		let diagramDetail = null;
		if (diagramPages.length > 0) {
			diagramDetail = await step.do(
				'extract-diagram-detail',
				{
					retries: { limit: 2, delay: "10 seconds", backoff: "exponential" },
					timeout: "4 minutes",
				},
				async () => {
					const diagramImages = diagramPages
						.slice(0, 4)
						.map(pn => pages.find(p => p.page_num === pn)!)
						.filter(Boolean);

					const content: any[] = [
						{ type: "text", text: `Analyze architecture diagram(s) for ${company_name}.` },
					];
					for (const di of diagramImages) {
						const imgB64 = await getImageBase64(di);
						content.push({
							type: "image_url",
							image_url: { url: `data:image/jpeg;base64,${imgB64}` },
						});
					}

					const prompt = SYSTEM_PROMPT_DIAGRAM + `\n\nRespond with ONLY valid JSON matching:\n${JSON.stringify(DIAGRAM_SCHEMA, null, 0)}`;

					const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
						messages: [
							{ role: "system", content: prompt },
							{ role: "user", content },
						],
						max_tokens: 4096,
					} as any);

					return parseAIResponse(response);
				}
			);
		}

		// Step 3: Merge all page results
		const merged = await step.do('merge-results', async () => {
			return mergePageResults(doc_id, company_name, report_type, pageResults, diagramDetail);
		});

		// Step 4: Score the merged data
		const scored = await step.do(
			'score-company',
			{
				retries: { limit: 2, delay: "5 seconds" },
				timeout: "3 minutes",
			},
			async () => {
				const prompt = SCORING_PROMPT + `\n\nRespond with ONLY valid JSON matching:\n${JSON.stringify(SCORING_SCHEMA, null, 0)}`;

				const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
					messages: [
						{ role: "system", content: prompt },
						{ role: "user", content: `Score this company:\n${JSON.stringify(merged)}` },
					],
					max_tokens: 2048,
				} as any);

				return parseAIResponse(response);
			}
		);

		// Step 5: Combine and return final result
		const final = {
			...merged,
			scoring: scored?.scoring || {},
			red_flags: scored?.red_flags || [],
			yellow_flags: scored?.yellow_flags || [],
			green_flags: scored?.green_flags || [],
			key_observations: [
				...(merged.key_observations || []),
				...(scored?.key_observations || []),
			],
		};

		// Step 6: Save to D1
		await step.do('save-to-d1', async () => {
			const s = final.scoring || {};
			await this.env.DB.prepare(`INSERT OR REPLACE INTO tech_extracts (
				doc_id, company, product, report_type, audit_period, auditor, opinion, hq, signing_authority,
				score_infrastructure, score_app_architecture, score_data_layer, score_security,
				score_devops, score_bcdr, score_vendor_diversity, score_overall,
				scoring_detail, system_description, infrastructure, network_architecture,
				application_architecture, data_storage, authentication, encryption,
				ci_cd_devops, monitoring_logging, security_tools, bcdr, compliance_controls,
				third_party_services, red_flags, yellow_flags, green_flags, key_observations,
				diagram_detail, diagram_pages, template_pages, page_count, extraction_method
			) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).bind(
				doc_id,
				final.company, final.product, final.report_type, final.audit_period,
				final.auditor, final.opinion, final.hq, final.signing_authority,
				s.infrastructure?.score ?? null, s.application_architecture?.score ?? null,
				s.data_layer?.score ?? null, s.security_posture?.score ?? null,
				s.devops_maturity?.score ?? null, s.bcdr_readiness?.score ?? null,
				s.vendor_diversity?.score ?? null, s.overall?.score ?? null,
				JSON.stringify(final.scoring), JSON.stringify(final.system_description),
				JSON.stringify(final.infrastructure), JSON.stringify(final.network_architecture),
				JSON.stringify(final.application_architecture), JSON.stringify(final.data_storage),
				JSON.stringify(final.authentication_access_control), JSON.stringify(final.encryption),
				JSON.stringify(final.ci_cd_devops), JSON.stringify(final.monitoring_logging),
				JSON.stringify(final.security_tools), JSON.stringify(final.bcdr),
				JSON.stringify(final.compliance_controls), JSON.stringify(final.third_party_services),
				JSON.stringify(final.red_flags), JSON.stringify(final.yellow_flags),
				JSON.stringify(final.green_flags), JSON.stringify(final.key_observations),
				JSON.stringify(final.network_architecture?.diagram_detail),
				JSON.stringify(final._diagram_pages), JSON.stringify(final._template_pages),
				final._page_count, 'vision'
			).run();

			// Save page-level extractions
			for (const page of pageResults) {
				if (!page) continue;
				await this.env.DB.prepare(
					`INSERT OR REPLACE INTO page_extractions (doc_id, page_num, page_type, has_diagram, is_template_placeholder, raw_extraction) VALUES (?, ?, ?, ?, ?, ?)`
				).bind(doc_id, page.page_num, page.page_type || 'other', page.has_diagram ? 1 : 0, page.is_template_placeholder ? 1 : 0, JSON.stringify(page)).run();
			}

			// Save vendors
			for (const v of final.third_party_services || []) {
				await this.env.DB.prepare(
					`INSERT OR IGNORE INTO vendors (doc_id, vendor_name, purpose, criticality) VALUES (?, ?, ?, ?)`
				).bind(doc_id, v.vendor, v.purpose, v.criticality).run();
			}

			// Update pipeline status
			await this.env.DB.prepare(
				`INSERT OR REPLACE INTO pipeline_status (doc_id, status, pages_total, pages_extracted, completed_at) VALUES (?, 'complete', ?, ?, datetime('now'))`
			).bind(doc_id, pages.length, pageResults.filter(Boolean).length).run();
		});

		return final;
	}
}

// ============ HTTP HANDLER ============

export default {
	async fetch(request: Request, env: Env): Promise<Response> {
		const url = new URL(request.url);

		// Serve app
		if (url.pathname === "/" || url.pathname === "/app") {
			return new Response(APP_HTML, { headers: { "Content-Type": "text/html; charset=utf-8" } });
		}

		if (url.pathname === "/health") {
			return Response.json({ status: "ok", model: "@cf/moonshotai/kimi-k2.5", workflow: "delve-pdf-extract" });
		}

		// Start a workflow (with base64 pages in body)
		if (request.method === "POST" && url.pathname === "/process") {
			const body = await request.json() as WorkflowParams;

			if (!body.doc_id || !body.pages?.length) {
				return Response.json({ error: "doc_id and pages[] required" }, { status: 400 });
			}

			const instance = await env.PDF_EXTRACT_WORKFLOW.create({
				id: `extract-${body.doc_id}`,
				params: body,
			});

			return Response.json({
				workflow_id: instance.id,
				status: "started",
				pages: body.pages.length,
			});
		}

		// Start a workflow reading from R2 (lightweight — no image upload needed)
		if (request.method === "POST" && url.pathname === "/process-r2") {
			const body = await request.json() as {
				doc_id: string;
				company_name: string;
				report_type: string;
				page_count: number;
			};

			if (!body.doc_id || !body.page_count) {
				return Response.json({ error: "doc_id and page_count required" }, { status: 400 });
			}

			// Build page list from R2 keys (convention: {doc_id}/page-{NN}.jpg)
			const pages: PageInput[] = [];
			for (let i = 1; i <= body.page_count; i++) {
				const pageNum = String(i).padStart(2, '0');
				pages.push({ page_num: i, image_base64: "", r2_key: `${body.doc_id}/page-${pageNum}.jpg` });
			}

			const instance = await env.PDF_EXTRACT_WORKFLOW.create({
				id: `extract-${body.doc_id}`,
				params: {
					doc_id: body.doc_id,
					company_name: body.company_name,
					report_type: body.report_type,
					pages,
					use_r2: true,
				},
			});

			return Response.json({
				workflow_id: instance.id,
				status: "started",
				pages: body.page_count,
				source: "r2",
			});
		}

		// ALL-IN-ONE: send all pages in a single kimi call (256K context fits ~80 images)
		if (request.method === "POST" && url.pathname === "/process-r2-single") {
			const body = await request.json() as {
				doc_id: string;
				company_name: string;
				report_type: string;
				page_count: number;
			};

			if (!body.doc_id || !body.page_count) {
				return Response.json({ error: "doc_id and page_count required" }, { status: 400 });
			}

			const pages: PageInput[] = [];
			for (let i = 1; i <= body.page_count; i++) {
				pages.push({
					page_num: i,
					image_base64: "",
					r2_key: `${body.doc_id}/page-${String(i).padStart(2, '0')}.jpg`,
				});
			}

			const instance = await env.PDF_EXTRACT_WORKFLOW.create({
				id: `single-${body.doc_id}`,
				params: {
					doc_id: body.doc_id,
					company_name: body.company_name,
					report_type: body.report_type,
					pages,
					use_r2: true,
					single_call: true,  // flag for workflow to use one AI call
				},
			});

			return Response.json({
				workflow_id: instance.id,
				status: "started",
				pages: body.page_count,
				mode: "single-call",
			});
		}

		// Fast R2 processing — only key pages (1-25 + sample of controls)
		if (request.method === "POST" && url.pathname === "/process-r2-fast") {
			const body = await request.json() as {
				doc_id: string;
				company_name: string;
				report_type: string;
				page_count: number;
			};

			if (!body.doc_id || !body.page_count) {
				return Response.json({ error: "doc_id and page_count required" }, { status: 400 });
			}

			// Smart page selection: first 25 (metadata, system desc, diagrams) + sample of controls
			const selectedPages: number[] = [];
			// Always include pages 1-25 (cover, opinion, system description, diagrams, key controls)
			for (let i = 1; i <= Math.min(25, body.page_count); i++) {
				selectedPages.push(i);
			}
			// Sample every 10th page from 26 onwards (capture control variety)
			for (let i = 30; i <= body.page_count; i += 10) {
				selectedPages.push(i);
			}
			// Always include last 2 pages (often have BCDR/appendix)
			if (body.page_count > 25) {
				selectedPages.push(body.page_count - 1);
				selectedPages.push(body.page_count);
			}
			const unique = [...new Set(selectedPages)].sort((a, b) => a - b);

			const pages: PageInput[] = unique.map(i => ({
				page_num: i,
				image_base64: "",
				r2_key: `${body.doc_id}/page-${String(i).padStart(2, '0')}.jpg`,
			}));

			const instance = await env.PDF_EXTRACT_WORKFLOW.create({
				id: `fast-${body.doc_id}`,
				params: {
					doc_id: body.doc_id,
					company_name: body.company_name,
					report_type: body.report_type,
					pages,
					use_r2: true,
				},
			});

			return Response.json({
				workflow_id: instance.id,
				status: "started",
				total_pages: body.page_count,
				selected_pages: unique.length,
				source: "r2-fast",
			});
		}

		// Bulk start: process all unextracted companies from D1, reading from R2
		// Uses fast mode by default (25 key pages + sampling)
		if (request.method === "POST" && url.pathname === "/process-all") {
			const body = await request.json() as { limit?: number; skip_iso?: boolean; full?: boolean };
			const limit = body.limit || 50;
			const useFast = !body.full; // default to fast mode

			// Get unprocessed companies from D1
			const { results } = await env.DB.prepare(`
				SELECT c.doc_id, c.display_name, c.report_type
				FROM companies c
				LEFT JOIN tech_extracts t ON c.doc_id = t.doc_id
				WHERE t.doc_id IS NULL
				${body.skip_iso ? "AND c.report_type NOT LIKE '%ISO%'" : ""}
				LIMIT ?
			`).bind(limit).all();

			const started: string[] = [];
			const errors: string[] = [];

			for (const company of results as any[]) {
				try {
					// Get page count from R2 by listing prefix
					const listed = await env.PAGES.list({ prefix: `${company.doc_id}/`, limit: 200 });
					const pageCount = listed.objects.length;

					if (pageCount < 10) {
						errors.push(`${company.display_name}: only ${pageCount} pages in R2`);
						continue;
					}

					let pages: PageInput[];
					if (useFast) {
						// Smart selection: first 25 + every 10th + last 2
						const selected: number[] = [];
						for (let i = 1; i <= Math.min(25, pageCount); i++) selected.push(i);
						for (let i = 30; i <= pageCount; i += 10) selected.push(i);
						if (pageCount > 25) { selected.push(pageCount - 1); selected.push(pageCount); }
						const unique = [...new Set(selected)].sort((a, b) => a - b);
						pages = unique.map(i => ({
							page_num: i,
							image_base64: "",
							r2_key: listed.objects[i - 1]?.key || `${company.doc_id}/page-${String(i).padStart(2, '0')}.jpg`,
						}));
					} else {
						pages = listed.objects.map((obj: any, i: number) => ({
							page_num: i + 1,
							image_base64: "",
							r2_key: obj.key,
						}));
					}

					const instance = await env.PDF_EXTRACT_WORKFLOW.create({
						id: `v2-${company.doc_id}`,
						params: {
							doc_id: company.doc_id,
							company_name: company.display_name,
							report_type: company.report_type,
							pages,
							use_r2: true,
							single_call: true,
						},
					});

					started.push(instance.id);

					// Update pipeline status
					await env.DB.prepare(
						`INSERT OR REPLACE INTO pipeline_status (doc_id, status, workflow_id, pages_total, started_at) VALUES (?, 'extracting', ?, ?, datetime('now'))`
					).bind(company.doc_id, instance.id, pageCount).run();

				} catch (e: any) {
					errors.push(`${company.display_name}: ${e.message}`);
				}
			}

			return Response.json({
				started: started.length,
				errors: errors.length,
				workflow_ids: started,
				error_details: errors,
			});
		}

		// Check workflow status
		if (request.method === "GET" && url.pathname.startsWith("/status/")) {
			const id = url.pathname.replace("/status/", "");
			try {
				const instance = await env.PDF_EXTRACT_WORKFLOW.get(id);
				return Response.json({
					id: instance.id,
					status: await instance.status(),
				});
			} catch (e: any) {
				return Response.json({ error: "Workflow not found" }, { status: 404 });
			}
		}

		// Single page extraction (direct, for testing)
		if (request.method === "POST" && url.pathname === "/extract-one") {
			try {
				const body = await request.json() as any;
				const { image_base64, company_name, report_type } = body;

				const prompt = SYSTEM_PROMPT_PAGE + `\n\nRespond with ONLY a valid JSON object (no markdown, no code fences):\n${JSON.stringify(PAGE_SCHEMA, null, 0)}`;

				const response = await env.AI.run("@cf/moonshotai/kimi-k2.5", {
					messages: [
						{ role: "system", content: prompt },
						{
							role: "user",
							content: [
								{ type: "text", text: `Extract data from this ${report_type || "compliance"} report page for ${company_name || "Unknown"}.` },
								{ type: "image_url", image_url: { url: `data:image/jpeg;base64,${image_base64}` } },
							],
						},
					],
					max_tokens: 4096,
				} as any);

				return Response.json({ result: parseAIResponse(response) });
			} catch (e: any) {
				return Response.json({ error: e.message }, { status: 500 });
			}
		}

		// Upload page image to R2 (binary body, key in URL)
		if (request.method === "PUT" && url.pathname.startsWith("/r2/")) {
			const key = url.pathname.replace("/r2/", "");
			const body = await request.arrayBuffer();
			await env.PAGES.put(key, body, { httpMetadata: { contentType: "image/jpeg" } });
			return Response.json({ key, size: body.byteLength });
		}

		// Check which companies have ALL pages in R2
		if (request.method === "GET" && url.pathname === "/r2/ready") {
			const body = url.searchParams.get("doc_ids")?.split(",") || [];
			const results: Record<string, number> = {};
			for (const docId of body.slice(0, 50)) {
				const listed = await env.PAGES.list({ prefix: `${docId}/`, limit: 200 });
				results[docId] = listed.objects.length;
			}
			return Response.json({ counts: results }, { headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// List all doc_ids that have pages in R2 with counts
		if (request.method === "GET" && url.pathname === "/r2/inventory") {
			// List all objects, group by doc_id prefix
			const counts: Record<string, number> = {};
			let cursor: string | undefined;
			let totalObjects = 0;
			do {
				const listed = await env.PAGES.list({ limit: 1000, cursor });
				for (const obj of listed.objects) {
					const docId = obj.key.split("/")[0];
					counts[docId] = (counts[docId] || 0) + 1;
					totalObjects++;
				}
				cursor = listed.truncated ? listed.cursor : undefined;
			} while (cursor && totalObjects < 50000);

			const readyCompanies = Object.entries(counts).filter(([_, c]) => c >= 50); // likely complete
			return Response.json({
				total_objects: totalObjects,
				total_doc_ids: Object.keys(counts).length,
				ready_companies: readyCompanies.length,
				companies: counts,
			}, { headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// === REPORT GENERATION ===

		// Generate reports + diagrams for all extracted companies without reports
		if (request.method === "POST" && url.pathname === "/generate-all") {
			const body = await request.json() as { limit?: number };
			const limit = body.limit || 100;

			const { results } = await env.DB.prepare(`
				SELECT doc_id, company, product FROM tech_extracts
				WHERE dd_report IS NULL
				LIMIT ?
			`).bind(limit).all();

			const started: string[] = [];
			const errors: string[] = [];

			for (const row of results as any[]) {
				try {
					const instance = await env.REPORT_WORKFLOW.create({
						id: `rpt-${row.doc_id}`,
						params: { doc_id: row.doc_id, company_name: row.company || row.product || 'Unknown' },
					});
					started.push(instance.id);
				} catch (e: any) {
					errors.push(`${row.company}: ${e.message}`);
				}
			}

			return Response.json({ started: started.length, errors: errors.length, error_details: errors.slice(0, 20) });
		}

		// Get report for a company
		if (request.method === "GET" && url.pathname.startsWith("/api/report/")) {
			const docId = url.pathname.replace("/api/report/", "");
			const row = await env.DB.prepare("SELECT dd_report, diagram_mermaid, diagram_d2 FROM tech_extracts WHERE doc_id = ?").bind(docId).first();
			if (!row) return Response.json({ error: "Not found" }, { status: 404 });
			return Response.json({ report: row.dd_report, diagram_mermaid: row.diagram_mermaid, diagram_d2: row.diagram_d2 },
				{ headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// === D1 QUERY ENDPOINTS ===

		// Full-text search across companies
		if (request.method === "GET" && url.pathname === "/api/search") {
			const q = url.searchParams.get("q") || "";
			const cloud = url.searchParams.get("cloud") || "";
			const minScore = parseInt(url.searchParams.get("min_score") || "0");
			const maxScore = parseInt(url.searchParams.get("max_score") || "10");
			const reportType = url.searchParams.get("type") || "";
			const hasFeature = url.searchParams.get("feature") || "";
			const sort = url.searchParams.get("sort") || "score";
			const limit = Math.min(parseInt(url.searchParams.get("limit") || "50"), 200);

			let where = ["t.is_valid = 1"];
			let params: any[] = [];

			if (q) {
				where.push("(t.company LIKE ? OR t.product LIKE ? OR t.system_description LIKE ? OR t.infrastructure LIKE ? OR t.third_party_services LIKE ? OR t.network_architecture LIKE ? OR t.application_architecture LIKE ?)");
				const pattern = `%${q}%`;
				params.push(pattern, pattern, pattern, pattern, pattern, pattern, pattern);
			}
			if (cloud) {
				where.push("t.infrastructure LIKE ?");
				params.push(`%${cloud}%`);
			}
			if (minScore > 0) {
				where.push("t.score_overall >= ?");
				params.push(minScore);
			}
			if (maxScore < 10) {
				where.push("t.score_overall <= ?");
				params.push(maxScore);
			}
			if (reportType) {
				where.push("t.report_type LIKE ?");
				params.push(`%${reportType}%`);
			}
			if (hasFeature) {
				// Search across security/infra features
				const featureMap: Record<string, string> = {
					'waf': "t.security_tools LIKE '%\"waf\": true%'",
					'multi_region': "t.network_architecture LIKE '%\"multi_region\": true%'",
					'kubernetes': "(t.application_architecture LIKE '%EKS%' OR t.application_architecture LIKE '%ECS%' OR t.application_architecture LIKE '%Kubernetes%')",
					'serverless': "(t.infrastructure LIKE '%Lambda%' OR t.infrastructure LIKE '%serverless%' OR t.infrastructure LIKE '%Cloud Functions%')",
					'redis': "t.data_storage LIKE '%Redis%'",
					'postgres': "t.data_storage LIKE '%Postgres%'",
					'mongodb': "t.data_storage LIKE '%Mongo%'",
					'openai': "t.third_party_services LIKE '%OpenAI%'",
					'anthropic': "t.third_party_services LIKE '%Anthropic%'",
				};
				if (featureMap[hasFeature]) where.push(featureMap[hasFeature]);
			}

			const orderMap: Record<string, string> = {
				'score': 't.score_overall DESC NULLS LAST',
				'name': 't.company ASC',
				'vendors': 'vendor_count DESC',
				'infra': 't.score_infrastructure DESC NULLS LAST',
				'security': 't.score_security DESC NULLS LAST',
			};
			const orderBy = orderMap[sort] || orderMap['score'];

			params.push(limit);

			const sql = `
				SELECT t.doc_id, t.company, t.product, t.report_type, t.audit_period, t.auditor,
					t.score_overall, t.score_infrastructure, t.score_app_architecture,
					t.score_data_layer, t.score_security, t.score_devops, t.score_bcdr,
					t.score_vendor_diversity, t.extraction_method,
					t.infrastructure, t.system_description, t.third_party_services,
					t.red_flags, t.green_flags, t.dd_report, t.diagram_mermaid,
					LENGTH(t.third_party_services) as vendor_count,
					c.infra_provider, c.website
				FROM tech_extracts t
				LEFT JOIN companies c ON t.doc_id = c.doc_id
				WHERE ${where.join(" AND ")}
				ORDER BY ${orderBy}
				LIMIT ?
			`;

			const stmt = env.DB.prepare(sql);
			const { results } = await stmt.bind(...params).all();

			return Response.json({
				results,
				total: results.length,
				query: { q, cloud, minScore, maxScore, reportType, hasFeature, sort },
			}, { headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// List all companies with scores
		if (request.method === "GET" && url.pathname === "/api/companies") {
			const { results } = await env.DB.prepare(`
				SELECT c.doc_id, c.display_name, c.report_type, c.infra_provider, c.website,
					t.score_overall, t.score_infrastructure, t.score_app_architecture,
					t.score_data_layer, t.score_security, t.score_devops, t.score_bcdr,
					t.score_vendor_diversity, t.company, t.audit_period, t.auditor,
					t.extraction_method, t.is_valid, t.dd_report, t.diagram_mermaid
				FROM companies c
				INNER JOIN tech_extracts t ON c.doc_id = t.doc_id
				WHERE t.is_valid = 1
				ORDER BY t.score_overall DESC NULLS LAST
			`).all();
			return Response.json({ companies: results, total: results.length },
				{ headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// Get single company detail
		if (request.method === "GET" && url.pathname.startsWith("/api/company/")) {
			const docId = url.pathname.replace("/api/company/", "");
			const company = await env.DB.prepare("SELECT * FROM tech_extracts WHERE doc_id = ?").bind(docId).first();
			if (!company) return Response.json({ error: "Not found" }, { status: 404 });

			const vendors = await env.DB.prepare("SELECT * FROM vendors WHERE doc_id = ?").bind(docId).all();
			const pages = await env.DB.prepare("SELECT page_num, page_type, has_diagram, is_template_placeholder FROM page_extractions WHERE doc_id = ? ORDER BY page_num").bind(docId).all();

			return Response.json({ company, vendors: vendors.results, pages: pages.results },
				{ headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// Stats overview
		if (request.method === "GET" && url.pathname === "/api/stats") {
			const stats = await env.DB.prepare(`
				SELECT
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1) as total_companies,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1) as total_extracted,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1 AND dd_report IS NOT NULL) as with_reports,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1 AND diagram_mermaid IS NOT NULL) as with_diagrams,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1 AND score_overall > 0) as scored,
					(SELECT ROUND(AVG(score_overall), 1) FROM tech_extracts WHERE is_valid = 1 AND score_overall > 0) as avg_score,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1 AND score_overall >= 7) as high_scorers,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 1 AND score_overall <= 3) as low_scorers,
					(SELECT COUNT(*) FROM pipeline_status WHERE status = 'complete') as pipeline_complete,
					(SELECT COUNT(*) FROM pipeline_status WHERE status = 'failed') as pipeline_failed,
					(SELECT COUNT(*) FROM vendors) as total_vendor_entries,
					(SELECT COUNT(DISTINCT vendor_name) FROM vendors) as unique_vendors,
					(SELECT COUNT(*) FROM tech_extracts WHERE is_valid = 0) as filtered_out
			`).first();

			const cloudDist = await env.DB.prepare(`
				SELECT infra_provider, COUNT(*) as count
				FROM companies WHERE infra_provider != ''
				GROUP BY infra_provider ORDER BY count DESC
			`).all();

			const scoreDist = await env.DB.prepare(`
				SELECT score_overall as score, COUNT(*) as count
				FROM tech_extracts WHERE score_overall > 0
				GROUP BY score_overall ORDER BY score_overall
			`).all();

			return Response.json({ stats, cloud_distribution: cloudDist.results, score_distribution: scoreDist.results },
				{ headers: { "Access-Control-Allow-Origin": "*" } });
		}

		// Top vendors across all companies
		if (request.method === "GET" && url.pathname === "/api/vendors") {
			const { results } = await env.DB.prepare(`
				SELECT vendor_name, COUNT(*) as company_count,
					GROUP_CONCAT(DISTINCT doc_id) as doc_ids
				FROM vendors
				GROUP BY vendor_name
				ORDER BY company_count DESC
				LIMIT 50
			`).all();
			return Response.json({ vendors: results },
				{ headers: { "Access-Control-Allow-Origin": "*" } });
		}

		return Response.json({
			error: "Not found",
			endpoints: ["/health", "/process", "/status/:id", "/extract-one",
				"/api/companies", "/api/company/:doc_id", "/api/stats", "/api/vendors"]
		}, { status: 404 });
	},
};

// ============ HELPERS ============

function parseAIResponse(response: any): any {
	let text = "";
	if (typeof response === "string") text = response;
	else if (response?.response) text = response.response;
	else if (response?.choices?.[0]?.message?.content) text = response.choices[0].message.content;
	else return null;

	if (!text) return null;

	try { return JSON.parse(text); } catch {}
	const cleaned = text.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim();
	try { return JSON.parse(cleaned); } catch {}
	const start = cleaned.indexOf("{");
	const end = cleaned.lastIndexOf("}");
	if (start >= 0 && end > start) {
		try { return JSON.parse(cleaned.substring(start, end + 1)); } catch {}
	}
	return null;
}

function mergePageResults(docId: string, companyName: string, reportType: string, pages: any[], diagramDetail: any): any {
	const merged: any = {
		company: null, product: companyName, report_type: reportType,
		audit_period: null, auditor: null, opinion: null, hq: null, signing_authority: null,
		system_description: { overview: "", products: {} },
		infrastructure: { cloud_provider: null, regions: [], availability_zones: null, additional_cloud: [], serverless: [], cdn: null },
		network_architecture: { vpc: false, firewalls: null, ids_ips: null, vpn: null, tls: null, waf: null, multi_region: false, topology: null, diagram_detail: diagramDetail },
		application_architecture: { pattern: null, languages: [], frameworks: [], compute: [], branch_protection: false, code_review_required: false },
		data_storage: { databases: [], caching: [], file_storage: [], backup_frequency: null, multi_az: false, per_tenant_segregation: false },
		authentication_access_control: { mfa: null, rbac: false, quarterly_access_reviews: false },
		encryption: { in_transit: null, at_rest: null, key_management: null },
		ci_cd_devops: { source_control: null, iac: null, branch_protection: null, separate_environments: false },
		monitoring_logging: { alerting: null, metrics: [], log_protection: false, ids: false },
		third_party_services: [],
		security_tools: { waf: false, ids_ips: false, vulnerability_scanning: null, penetration_testing: null, server_hardening: false },
		bcdr: { bcdr_policy: false, annual_testing: false, daily_backups: false, rto: "Not disclosed", rpo: "Not disclosed" },
		compliance_controls: { total_controls_tested: 0, exceptions: 0, untestable: [], excluded_criteria: [] },
		key_observations: [],
		_page_count: pages.length,
		_diagram_pages: [] as number[],
		_template_pages: [] as number[],
	};

	const vendors = new Set<string>();
	const databases = new Set<string>();
	const controlIds = new Set<string>();
	const sysDescParts: string[] = [];

	for (const page of pages) {
		if (!page) continue;
		if (page.company_name && !merged.company) merged.company = page.company_name;
		if (page.signing_authority && !merged.signing_authority) merged.signing_authority = page.signing_authority;
		if (page.audit_period && !merged.audit_period) merged.audit_period = page.audit_period;
		if (page.auditor && !merged.auditor) merged.auditor = page.auditor;
		if (page.opinion && !merged.opinion) merged.opinion = page.opinion;
		if (page.hq_address && !merged.hq) merged.hq = page.hq_address;
		if (page.has_diagram) merged._diagram_pages.push(page.page_num);
		if (page.is_template_placeholder) merged._template_pages.push(page.page_num);
		if (page.system_description_text) sysDescParts.push(page.system_description_text);
		if (page.cloud_provider) {
			if (!merged.infrastructure.cloud_provider) merged.infrastructure.cloud_provider = page.cloud_provider;
		}
		if (page.infrastructure_details) {
			const t = page.infrastructure_details.toLowerCase();
			if (t.includes("multi-az") || t.includes("multi az")) { merged.infrastructure.availability_zones = "Multi-AZ"; merged.data_storage.multi_az = true; }
			if (t.includes("vpc")) merged.network_architecture.vpc = true;
		}
		if (page.network_architecture_details) {
			const t = page.network_architecture_details;
			if (!merged.network_architecture.topology || t.length > (merged.network_architecture.topology?.length || 0))
				merged.network_architecture.topology = t;
		}
		if (page.auth_details?.toLowerCase().includes("mfa")) merged.authentication_access_control.mfa = page.auth_details;
		if (page.auth_details?.toLowerCase().includes("rbac")) merged.authentication_access_control.rbac = true;
		if (page.bcdr_details) {
			if (page.bcdr_details.toLowerCase().includes("daily")) merged.bcdr.daily_backups = true;
			if (page.bcdr_details.toLowerCase().includes("annual")) merged.bcdr.annual_testing = true;
			merged.bcdr.bcdr_policy = true;
		}
		for (const v of page.vendors_mentioned || []) vendors.add(v);
		for (const d of page.databases_mentioned || []) databases.add(d);
		for (const c of page.control_ids_tested || []) controlIds.add(c);
	}

	if (sysDescParts.length) merged.system_description.overview = sysDescParts.join(" ");
	merged.data_storage.databases = [...databases];
	merged.third_party_services = [...vendors].map(v => ({ vendor: v, purpose: "Identified in report", criticality: "Unknown" }));
	merged.compliance_controls.total_controls_tested = controlIds.size;
	if (!merged.company) merged.company = companyName;

	return merged;
}

// ============ SCHEMAS & PROMPTS ============

const PAGE_SCHEMA = {
	type: "object",
	properties: {
		page_type: { type: "string", enum: ["cover", "toc", "opinion_letter", "system_description", "network_diagram", "org_chart", "controls_testing", "control_description", "appendix", "other"] },
		has_diagram: { type: "boolean" },
		company_name: { type: ["string", "null"] },
		signing_authority: { type: ["string", "null"] },
		report_type: { type: ["string", "null"] },
		audit_period: { type: ["string", "null"] },
		auditor: { type: ["string", "null"] },
		opinion: { type: ["string", "null"] },
		hq_address: { type: ["string", "null"] },
		system_description_text: { type: ["string", "null"] },
		cloud_provider: { type: ["string", "null"] },
		infrastructure_details: { type: ["string", "null"] },
		network_architecture_details: { type: ["string", "null"] },
		application_details: { type: ["string", "null"] },
		databases_mentioned: { type: "array", items: { type: "string" } },
		vendors_mentioned: { type: "array", items: { type: "string" } },
		security_tools_mentioned: { type: "array", items: { type: "string" } },
		auth_details: { type: ["string", "null"] },
		encryption_details: { type: ["string", "null"] },
		cicd_details: { type: ["string", "null"] },
		monitoring_details: { type: ["string", "null"] },
		bcdr_details: { type: ["string", "null"] },
		control_ids_tested: { type: "array", items: { type: "string" } },
		exceptions_noted: { type: "array", items: { type: "string" } },
		is_template_placeholder: { type: "boolean" },
		template_artifacts: { type: ["string", "null"] },
	},
	required: ["page_type", "has_diagram", "is_template_placeholder"],
};

const DIAGRAM_SCHEMA = {
	type: "object",
	properties: {
		diagram_type: { type: "string" },
		components: { type: "array", items: { type: "object", properties: { name: { type: "string" }, type: { type: "string" }, details: { type: "string" } } } },
		connections: { type: "array", items: { type: "object", properties: { from: { type: "string" }, to: { type: "string" }, label: { type: "string" } } } },
		zones: { type: "array", items: { type: "object", properties: { name: { type: "string" }, components: { type: "array", items: { type: "string" } } } } },
		traffic_flow_description: { type: "string" },
		cloud_providers_visible: { type: "array", items: { type: "string" } },
		is_sample_placeholder: { type: "boolean" },
	},
	required: ["diagram_type", "components", "traffic_flow_description", "is_sample_placeholder"],
};

const SCORING_SCHEMA = {
	type: "object",
	properties: {
		scoring: { type: "object" },
		red_flags: { type: "array", items: { type: "string" } },
		yellow_flags: { type: "array", items: { type: "string" } },
		green_flags: { type: "array", items: { type: "string" } },
		key_observations: { type: "array", items: { type: "string" } },
	},
	required: ["scoring", "red_flags", "yellow_flags", "green_flags"],
};

const SYSTEM_PROMPT_PAGE = `You are analyzing a SINGLE PAGE from a SOC 2 / ISO 27001 compliance report.
Extract ALL technology, infrastructure, and security data visible on THIS page only.
Be precise — only report what you can actually see.

Look for: company name, auditor, report type, audit dates, cloud providers, specific technologies (databases, languages, frameworks, CI/CD, monitoring), network architecture (VPC, firewalls, IDS/IPS, WAF), third-party vendors, security controls (MFA, RBAC, encryption, pen testing), BCDR details.
If this is a DIAGRAM page, describe every component and connection.
If you see template placeholders ("Your Name Here", yellow highlights), set is_template_placeholder=true.
Focus on UNIQUE content — most use Accorp Partners templates.`;

const SYSTEM_PROMPT_DIAGRAM = `Analyze this infrastructure/network architecture diagram from a compliance report.
Extract EVERY component, connection, and zone. Name every service, database, API, cloud provider.
Describe complete traffic flow from users through all layers to storage.
If SAMPLE/PLACEHOLDER diagram, set is_sample_placeholder=true.`;

const SCORING_PROMPT = `Score this company's tech due diligence 1-10 per dimension:
Infrastructure (multi-region/IaC/CDN), App Architecture (microservices/typed/tested), Data (multi-DB/caching/backups), Security (WAF/IDS/pentest/SIEM), DevOps (CI-CD/IaC/containers), BCDR (DR testing/RTO-RPO), Vendor Diversity (5+ vendors vs single). Identify red/yellow/green flags and observations.`;


// ============ REPORT GENERATION WORKFLOW ============

interface ReportParams {
	doc_id: string;
	company_name: string;
}

export class ReportGenWorkflow extends WorkflowEntrypoint<Env, ReportParams> {
	async run(event: WorkflowEvent<ReportParams>, step: WorkflowStep) {
		const { doc_id, company_name } = event.payload;

		// Step 1: Read tech extract from D1
		const extract = await step.do('read-extract', async () => {
			const row = await this.env.DB.prepare("SELECT * FROM tech_extracts WHERE doc_id = ?").bind(doc_id).first();
			if (!row) throw new Error("No tech extract found for " + doc_id);
			return row;
		});

		// Step 2: Generate Mermaid diagram
		const diagram = await step.do('generate-diagram', {
			retries: { limit: 2, delay: "5 seconds" },
			timeout: "3 minutes",
		}, async () => {
			const infra = extract.infrastructure ? JSON.parse(extract.infrastructure as string) : {};
			const net = extract.network_architecture ? JSON.parse(extract.network_architecture as string) : {};
			const app = extract.application_architecture ? JSON.parse(extract.application_architecture as string) : {};
			const vendors = extract.third_party_services ? JSON.parse(extract.third_party_services as string) : [];
			const sec = extract.security_tools ? JSON.parse(extract.security_tools as string) : {};
			const storage = extract.data_storage ? JSON.parse(extract.data_storage as string) : {};

			const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
				messages: [
					{ role: "system", content: DIAGRAM_GEN_PROMPT },
					{ role: "user", content: `Generate a Mermaid.js infrastructure diagram for ${company_name}.

Cloud: ${infra.cloud_provider || 'Unknown'}
Regions: ${JSON.stringify(infra.regions || [])}
Architecture: ${app.pattern || 'Unknown'}
Compute: ${JSON.stringify(app.compute || [])}
Databases: ${JSON.stringify(storage.databases || [])}
Caching: ${JSON.stringify(storage.caching || [])}
Network: VPC=${net.vpc}, WAF=${net.waf || 'none'}, IDS=${net.ids_ips || 'none'}, Firewall=${net.firewalls || 'none'}
Topology: ${net.topology || 'Unknown'}
Vendors: ${vendors.map((v: any) => v.vendor + ' (' + v.purpose + ')').join(', ')}
Security: WAF=${sec.waf}, IDS=${sec.ids_ips}, Pentest=${sec.penetration_testing || 'none'}
Auth: ${extract.authentication ? JSON.parse(extract.authentication as string).identity_provider || '' : ''}
Encryption: ${extract.encryption ? JSON.parse(extract.encryption as string).in_transit || '' : ''} / ${extract.encryption ? JSON.parse(extract.encryption as string).at_rest || '' : ''}` },
				],
				max_tokens: 4096,
			} as any);

			const text = (response as any)?.response || (response as any)?.choices?.[0]?.message?.content || '';
			// Extract mermaid code block
			const match = text.match(/\`\`\`mermaid\n([\s\S]*?)\`\`\`/);
			return match ? match[1].trim() : text.trim();
		});

		// Step 3: Generate DD Report
		const report = await step.do('generate-report', {
			retries: { limit: 2, delay: "5 seconds" },
			timeout: "3 minutes",
		}, async () => {
			const sys = extract.system_description ? JSON.parse(extract.system_description as string) : {};
			const scoring = extract.scoring_detail ? JSON.parse(extract.scoring_detail as string) : {};
			const vendors = extract.third_party_services ? JSON.parse(extract.third_party_services as string) : [];
			const reds = extract.red_flags ? JSON.parse(extract.red_flags as string) : [];
			const yellows = extract.yellow_flags ? JSON.parse(extract.yellow_flags as string) : [];
			const greens = extract.green_flags ? JSON.parse(extract.green_flags as string) : [];
			const observations = extract.key_observations ? JSON.parse(extract.key_observations as string) : [];

			const response = await this.env.AI.run("@cf/moonshotai/kimi-k2.5", {
				messages: [
					{ role: "system", content: REPORT_GEN_PROMPT },
					{ role: "user", content: `Generate a Tech Due Diligence Report for:

Company: ${extract.company}
Product: ${extract.product}
Report Type: ${extract.report_type}
Audit Period: ${extract.audit_period}
Auditor: ${extract.auditor}
Opinion: ${extract.opinion}
HQ: ${extract.hq}
Signing Authority: ${extract.signing_authority}

System Description: ${sys.overview || ''}

Scores:
- Infrastructure: ${scoring.infrastructure?.score || '?'}/10 — ${scoring.infrastructure?.rationale || ''}
- App Architecture: ${scoring.application_architecture?.score || '?'}/10 — ${scoring.application_architecture?.rationale || ''}
- Data Layer: ${scoring.data_layer?.score || '?'}/10 — ${scoring.data_layer?.rationale || ''}
- Security: ${scoring.security_posture?.score || '?'}/10 — ${scoring.security_posture?.rationale || ''}
- DevOps: ${scoring.devops_maturity?.score || '?'}/10 — ${scoring.devops_maturity?.rationale || ''}
- BCDR: ${scoring.bcdr_readiness?.score || '?'}/10 — ${scoring.bcdr_readiness?.rationale || ''}
- Vendor Diversity: ${scoring.vendor_diversity?.score || '?'}/10 — ${scoring.vendor_diversity?.rationale || ''}
- Overall: ${scoring.overall?.score || extract.score_overall || '?'}/10

Vendors: ${vendors.map((v: any) => v.vendor + ' (' + (v.criticality || '') + ': ' + (v.purpose || '') + ')').join('\n')}

Red Flags: ${reds.join('\n- ')}
Yellow Flags: ${yellows.join('\n- ')}
Green Flags: ${greens.join('\n- ')}
Key Observations: ${observations.join('\n- ')}` },
				],
				max_tokens: 4096,
			} as any);

			return (response as any)?.response || (response as any)?.choices?.[0]?.message?.content || '';
		});

		// Step 4: Save to D1
		await step.do('save-reports', async () => {
			await this.env.DB.prepare(
				`UPDATE tech_extracts SET dd_report = ?, diagram_mermaid = ?, report_generated_at = datetime('now') WHERE doc_id = ?`
			).bind(report, diagram, doc_id).run();
		});

		return { doc_id, report_length: report.length, diagram_length: diagram.length };
	}
}

const DIAGRAM_GEN_PROMPT = `Generate a Mermaid.js flowchart (graph TD) showing the infrastructure architecture.
Use these conventions:
- subgraph for each layer: Perimeter, Compute, Data, Integrations, Products
- Color classes: classDef aws fill:#ff9900,color:#000; classDef security fill:#ef4444,color:#fff; classDef data fill:#3b82f6,color:#fff; classDef product fill:#22c55e,color:#000;
- Show data flow with labeled arrows
- Include ALL named vendors and services
- Keep it readable — max 30 nodes

Return ONLY the mermaid code inside a \`\`\`mermaid code fence. No other text.`;

const REPORT_GEN_PROMPT = `Generate a concise Tech Due Diligence report in Markdown.

Format:
# Tech Due Diligence Report: {Company}
**Date:** {today} | **Source:** {report_type} ({audit_period}) | **Auditor:** {auditor} | **Opinion:** {opinion}
## Company Overview (table: Legal Name, Product, HQ, Cloud)
## Technology Stack Assessment (subsection per dimension with score/10 and bullet points)
## Vendor Dependency Map (table: Vendor, Criticality, Purpose, Risk)
## Risk Assessment (### RED FLAGS, ### YELLOW FLAGS, ### GREEN FLAGS)
## Recommendation (**Investment Readiness: LOW/MODERATE/MODERATE-HIGH/HIGH** based on overall score)

Keep it concise but complete. Use the exact scores provided.`;

const APP_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Delve — Tech Due Diligence Database</title>
<style>
:root{--bg:#0f172a;--bg2:#1e293b;--card:#1a2332;--border:#334155;--text:#e2e8f0;--muted:#94a3b8;--blue:#3b82f6;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--purple:#a855f7}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,sans-serif;font-size:14px}
a{color:var(--blue);text-decoration:none}

/* Layout */
.app{display:flex;height:100vh}
.sidebar{width:320px;background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0}
.main{flex:1;overflow-y:auto;padding:0}

/* Sidebar */
.sidebar h1{padding:16px 16px 4px;font-size:18px}
.sidebar .sub{padding:0 16px 12px;color:var(--muted);font-size:11px}
.search-box{padding:0 12px 8px}
.search-box input{width:100%;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:13px}
.filters{padding:0 12px 12px;display:flex;flex-direction:column;gap:6px}
.filters select,.filters input{padding:7px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:12px}
.filter-row{display:flex;gap:6px}
.filter-row>*{flex:1}
.pill-group{display:flex;flex-wrap:wrap;gap:4px;padding:0 12px 8px}
.pill{padding:3px 8px;border-radius:12px;font-size:11px;cursor:pointer;border:1px solid var(--border);background:var(--bg)}
.pill.active{background:var(--blue);border-color:var(--blue);color:white}
.results-list{flex:1;overflow-y:auto}
.result-item{padding:10px 16px;border-bottom:1px solid #1a2332;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.result-item:hover{background:var(--card)}
.result-item.active{background:#1e3a5f;border-left:3px solid var(--blue)}
.result-item .name{font-weight:600;font-size:13px}
.result-item .meta{color:var(--muted);font-size:11px}
.badge{padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700}
.b-g{background:#14532d;color:#86efac}.b-y{background:#78350f;color:#fde68a}.b-r{background:#7f1d1d;color:#fca5a5}.b-b{background:#1e3a5f;color:#93c5fd}

/* Main content */
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;color:var(--muted)}
.welcome h2{font-size:24px;color:var(--text);margin-bottom:8px}
.company-view{padding:24px;max-width:1200px;margin:0 auto}
.section{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}
.section h2{font-size:18px;margin-bottom:12px}
.section h3{font-size:15px;margin-bottom:8px;color:var(--blue)}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.stat{background:var(--bg);border-radius:8px;padding:14px}
.stat .val{font-size:28px;font-weight:700}
.stat .lbl{color:var(--muted);font-size:11px;margin-top:2px}
.score-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.score-card{background:var(--bg);padding:10px;border-radius:8px;text-align:center}
.score-card .num{font-size:22px;font-weight:700}
.score-card .dim{color:var(--muted);font-size:11px}
.flag{padding:8px 12px;border-radius:6px;margin-bottom:4px;font-size:13px}
.f-r{background:#7f1d1d20;border-left:3px solid var(--red)}
.f-y{background:#78350f20;border-left:3px solid var(--yellow)}
.f-g{background:#14532d20;border-left:3px solid var(--green)}
.vendor-table{width:100%;font-size:13px;border-collapse:collapse}
.vendor-table th{text-align:left;padding:6px 10px;color:var(--muted);font-size:11px;border-bottom:1px solid var(--border)}
.vendor-table td{padding:6px 10px;border-bottom:1px solid #1a2332}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;background:var(--bg);border:1px solid var(--border);margin:2px}
.diagram-container{background:var(--bg);border-radius:8px;padding:16px;text-align:center;overflow:auto;max-height:600px}
.diagram-container img{max-width:100%;cursor:zoom-in}
.diagram-container img.zoomed{max-width:none;width:150%;cursor:zoom-out}
.report-content{white-space:pre-wrap;font-size:13px;line-height:1.6;max-height:500px;overflow-y:auto;background:var(--bg);padding:16px;border-radius:8px}
.count{color:var(--muted);font-size:12px;padding:8px 16px}
.tabs{display:flex;gap:2px;margin-bottom:16px}
.tab{padding:8px 16px;background:var(--bg);border:1px solid var(--border);border-radius:8px 8px 0 0;cursor:pointer;font-size:13px}
.tab.active{background:var(--card);border-bottom-color:var(--card)}
</style>
</head>
<body>
<div class="app">
<aside class="sidebar">
  <h1>Delve Tech DD</h1>
  <div class="sub">485 companies · searchable database</div>
  <div class="search-box"><input type="text" id="q" placeholder="Search: company, technology, vendor..." autofocus></div>
  <div class="filters">
    <div class="filter-row">
      <select id="cloud"><option value="">All Clouds</option><option>AWS</option><option>GCP</option><option>Azure</option><option>Supabase</option><option>Vercel</option><option>Render</option><option>DigitalOcean</option></select>
      <select id="type"><option value="">All Types</option><option value="Type 1">Type 1</option><option value="Type 2">Type 2</option></select>
    </div>
    <div class="filter-row">
      <select id="sort"><option value="score">Sort: Score</option><option value="name">Sort: Name</option><option value="vendors">Sort: Vendors</option><option value="infra">Sort: Infrastructure</option><option value="security">Sort: Security</option></select>
      <select id="score"><option value="0-10">All Scores</option><option value="7-10">7+ High</option><option value="5-6">5-6 Moderate</option><option value="1-4">1-4 Low</option></select>
    </div>
  </div>
  <div class="pill-group" id="features">
    <span class="pill" data-f="serverless">Serverless</span>
    <span class="pill" data-f="kubernetes">K8s/ECS</span>
    <span class="pill" data-f="multi_region">Multi-Region</span>
    <span class="pill" data-f="waf">WAF</span>
    <span class="pill" data-f="redis">Redis</span>
    <span class="pill" data-f="postgres">Postgres</span>
    <span class="pill" data-f="openai">OpenAI</span>
    <span class="pill" data-f="anthropic">Anthropic</span>
  </div>
  <div class="count" id="count">Loading...</div>
  <div class="results-list" id="results"></div>
</aside>
<main class="main" id="main">
  <div class="welcome"><h2>Search the database</h2><p>Type a technology, vendor, or company name</p></div>
</main>
</div>

<script>
const API = window.location.origin;
let activeFeature = '';
let currentDocId = null;

// Debounced search
let timer;
function search() {
  clearTimeout(timer);
  timer = setTimeout(doSearch, 300);
}

async function doSearch() {
  const q = document.getElementById('q').value;
  const cloud = document.getElementById('cloud').value;
  const type = document.getElementById('type').value;
  const sort = document.getElementById('sort').value;
  const [min, max] = document.getElementById('score').value.split('-').map(Number);

  const params = new URLSearchParams({q, cloud, sort, min_score: min, max_score: max, limit: '100'});
  if (type) params.set('type', type);
  if (activeFeature) params.set('feature', activeFeature);

  try {
    const r = await fetch(\`\${API}/api/search?\${params}\`);
    const d = await r.json();
    renderResults(d.results);
    document.getElementById('count').textContent = \`\${d.total} results\`;
  } catch(e) {
    document.getElementById('count').textContent = 'Error loading';
  }
}

function renderResults(items) {
  const list = document.getElementById('results');
  list.innerHTML = items.map(c => {
    const score = c.score_overall;
    const cls = score >= 7 ? 'b-g' : score >= 4 ? 'b-y' : score ? 'b-r' : 'b-b';
    const badge = score ? \`<span class="badge \${cls}">\${score}</span>\` : '';
    const cloud = extractCloud(c.infrastructure);
    const active = c.doc_id === currentDocId ? 'active' : '';
    return \`<div class="result-item \${active}" onclick="showCompany('\${c.doc_id}')">
      <div><div class="name">\${c.company || c.product || 'Unknown'}</div><div class="meta">\${(c.report_type||'').replace('SOC 2 ','')} · \${cloud}</div></div>
      \${badge}
    </div>\`;
  }).join('');
}

function extractCloud(infra) {
  if (!infra) return '';
  const s = typeof infra === 'string' ? infra : JSON.stringify(infra);
  for (const c of ['AWS','GCP','Azure','Supabase','Vercel','Render','DigitalOcean']) {
    if (s.toLowerCase().includes(c.toLowerCase())) return c;
  }
  return '';
}

function parse(field) {
  if (!field) return null;
  if (typeof field === 'object') return field;
  try { return JSON.parse(field); } catch { return field; }
}

async function showCompany(docId) {
  currentDocId = docId;
  // Highlight in sidebar
  document.querySelectorAll('.result-item').forEach(el => el.classList.remove('active'));
  const item = document.querySelector(\`.result-item[onclick*="\${docId}"]\`);
  if (item) item.classList.add('active');

  const r = await fetch(\`\${API}/api/company/\${docId}\`);
  const d = await r.json();
  const c = d.company;
  if (!c) { document.getElementById('main').innerHTML = '<div class="welcome"><h2>Not found</h2></div>'; return; }

  const sys = parse(c.system_description) || {};
  const infra = parse(c.infrastructure) || {};
  const net = parse(c.network_architecture) || {};
  const app = parse(c.application_architecture) || {};
  const storage = parse(c.data_storage) || {};
  const auth = parse(c.authentication) || {};
  const enc = parse(c.encryption) || {};
  const sec = parse(c.security_tools) || {};
  const bcdr = parse(c.bcdr) || {};
  const vendors = parse(c.third_party_services) || [];
  const scoring = parse(c.scoring_detail) || {};
  const reds = parse(c.red_flags) || [];
  const yellows = parse(c.yellow_flags) || [];
  const greens = parse(c.green_flags) || [];
  const observations = parse(c.key_observations) || [];
  const report = c.dd_report || '';
  const diagram = c.diagram_mermaid || '';
  const cloud = extractCloud(c.infrastructure);

  const scoreDims = ['infrastructure','application_architecture','data_layer','security_posture','devops_maturity','bcdr_readiness','vendor_diversity','overall'];

  document.getElementById('main').innerHTML = \`
  <div class="company-view">
    <div class="section">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <h2>\${c.company || 'Unknown'}</h2>
          <div style="color:var(--muted);margin-bottom:8px">\${c.report_type || ''} · \${c.auditor || ''} · \${c.audit_period || ''}</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            \${cloud ? \`<span class="tag">\${cloud}</span>\` : ''}
            \${c.report_type ? \`<span class="tag">\${c.report_type.replace('SOC 2 ','')}</span>\` : ''}
            \${net.multi_region ? '<span class="tag" style="border-color:var(--green)">Multi-Region</span>' : ''}
            \${net.vpc ? '<span class="tag">VPC</span>' : ''}
            \${sec.waf ? '<span class="tag" style="border-color:var(--green)">WAF</span>' : ''}
          </div>
        </div>
        <div style="text-align:right">
          <div style="font-size:48px;font-weight:800;line-height:1">\${scoring.overall?.score || c.score_overall || '—'}</div>
          <div style="color:var(--muted);font-size:12px">/10 overall</div>
        </div>
      </div>
      <p style="margin-top:12px">\${sys.overview || c.product || ''}</p>
    </div>

    <div class="tabs">
      <div class="tab active" onclick="showTab('scores',this)">Scores</div>
      <div class="tab" onclick="showTab('arch',this)">Architecture</div>
      <div class="tab" onclick="showTab('risks',this)">Risks</div>
      <div class="tab" onclick="showTab('vendors',this)">Vendors</div>
      <div class="tab" onclick="showTab('report',this)">Full Report</div>
    </div>

    <div id="tab-scores">
      <div class="section">
        <h3>Dimension Scores</h3>
        <div class="score-grid">
          \${scoreDims.map(dim => {
            const s = scoring[dim] || {};
            const label = dim.replace(/_/g,' ');
            const val = s.score || '—';
            const color = val >= 7 ? 'var(--green)' : val >= 4 ? 'var(--yellow)' : val ? 'var(--red)' : 'var(--muted)';
            return \`<div class="score-card"><div class="num" style="color:\${color}">\${val}</div><div class="dim">\${label}</div></div>\`;
          }).join('')}
        </div>
      </div>
    </div>

    <div id="tab-arch" style="display:none">
      <div class="section">
        <h3>Infrastructure</h3>
        <div class="grid-3">
          <div class="stat"><div class="val" style="font-size:16px">\${infra.cloud_provider || '—'}</div><div class="lbl">Cloud Provider</div></div>
          <div class="stat"><div class="val" style="font-size:16px">\${infra.availability_zones || '—'}</div><div class="lbl">Availability</div></div>
          <div class="stat"><div class="val" style="font-size:16px">\${(infra.regions||[]).join(', ') || '—'}</div><div class="lbl">Regions</div></div>
        </div>
      </div>
      <div class="section">
        <h3>Application</h3>
        <p><strong>Pattern:</strong> \${app.pattern || '—'}</p>
        <p><strong>Compute:</strong> \${(app.compute||[]).join(', ') || '—'}</p>
        <p><strong>Languages:</strong> \${(app.languages||[]).join(', ') || '—'}</p>
        <p><strong>Databases:</strong> \${(storage.databases||[]).join(', ') || '—'}</p>
      </div>
      \${diagram ? \`<div class="section"><h3>Architecture Diagram (Mermaid)</h3><pre style="background:var(--bg);padding:12px;border-radius:8px;overflow-x:auto;font-size:11px">\${diagram}</pre></div>\` : ''}
    </div>

    <div id="tab-risks" style="display:none">
      \${reds.length ? \`<div class="section"><h3 style="color:var(--red)">Red Flags (\${reds.length})</h3>\${reds.map(f=>\`<div class="flag f-r">\${f}</div>\`).join('')}</div>\` : ''}
      \${yellows.length ? \`<div class="section"><h3 style="color:var(--yellow)">Yellow Flags (\${yellows.length})</h3>\${yellows.map(f=>\`<div class="flag f-y">\${f}</div>\`).join('')}</div>\` : ''}
      \${greens.length ? \`<div class="section"><h3 style="color:var(--green)">Green Flags (\${greens.length})</h3>\${greens.map(f=>\`<div class="flag f-g">\${f}</div>\`).join('')}</div>\` : ''}
      \${observations.length ? \`<div class="section"><h3>Key Observations</h3>\${observations.map(o=>\`<p style="margin-bottom:6px;padding-left:10px;border-left:2px solid var(--border)">• \${o}</p>\`).join('')}</div>\` : ''}
    </div>

    <div id="tab-vendors" style="display:none">
      <div class="section">
        <h3>Vendor Dependencies (\${Array.isArray(vendors) ? vendors.length : 0})</h3>
        <table class="vendor-table">
          <tr><th>Vendor</th><th>Purpose</th><th>Criticality</th></tr>
          \${(Array.isArray(vendors) ? vendors : []).map(v => \`<tr><td><strong>\${v.vendor||''}</strong></td><td>\${v.purpose||'—'}</td><td>\${v.criticality||'—'}</td></tr>\`).join('')}
        </table>
      </div>
    </div>

    <div id="tab-report" style="display:none">
      <div class="section">
        <h3>Full DD Report</h3>
        <div class="report-content">\${report || 'No report generated'}</div>
      </div>
    </div>
  </div>\`;
}

function showTab(id, el) {
  document.querySelectorAll('[id^="tab-"]').forEach(t => t.style.display = 'none');
  document.getElementById('tab-' + id).style.display = '';
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
}

// Event listeners
document.getElementById('q').addEventListener('input', search);
['cloud','type','sort','score'].forEach(id => document.getElementById(id).addEventListener('change', search));

// Feature pills
document.querySelectorAll('.pill').forEach(pill => {
  pill.addEventListener('click', () => {
    const f = pill.dataset.f;
    if (activeFeature === f) {
      activeFeature = '';
      pill.classList.remove('active');
    } else {
      document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      activeFeature = f;
      pill.classList.add('active');
    }
    doSearch();
  });
});

// Initial load
doSearch();
</script>
</body>
</html>
`;
