-- Delve Tech DD Database Schema

-- Companies: core metadata from CSV registry
CREATE TABLE IF NOT EXISTS companies (
  doc_id TEXT PRIMARY KEY,
  legal_name TEXT,
  company_name TEXT,
  display_name TEXT,
  report_type TEXT,
  system_description TEXT,
  infra_provider TEXT,
  website TEXT,
  contact_email TEXT,
  audit_end_date TEXT,
  observation_period TEXT,
  address TEXT,
  pdf_file TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Tech extractions: full structured data per company
CREATE TABLE IF NOT EXISTS tech_extracts (
  doc_id TEXT PRIMARY KEY REFERENCES companies(doc_id),
  company TEXT,
  product TEXT,
  report_type TEXT,
  audit_period TEXT,
  auditor TEXT,
  opinion TEXT,
  hq TEXT,
  signing_authority TEXT,

  -- Scores (1-10)
  score_infrastructure INTEGER,
  score_app_architecture INTEGER,
  score_data_layer INTEGER,
  score_security INTEGER,
  score_devops INTEGER,
  score_bcdr INTEGER,
  score_vendor_diversity INTEGER,
  score_overall INTEGER,

  -- Scoring rationales (JSON)
  scoring_detail TEXT,  -- full scoring object as JSON

  -- Structured sections as JSON
  system_description TEXT,
  infrastructure TEXT,
  network_architecture TEXT,
  application_architecture TEXT,
  data_storage TEXT,
  authentication TEXT,
  encryption TEXT,
  ci_cd_devops TEXT,
  monitoring_logging TEXT,
  security_tools TEXT,
  bcdr TEXT,
  compliance_controls TEXT,

  -- Lists as JSON arrays
  third_party_services TEXT,
  red_flags TEXT,
  yellow_flags TEXT,
  green_flags TEXT,
  key_observations TEXT,
  trust_criteria TEXT,

  -- Diagram data
  diagram_detail TEXT,
  diagram_pages TEXT,  -- JSON array of page numbers
  template_pages TEXT, -- JSON array of page numbers with template artifacts

  -- Meta
  page_count INTEGER,
  extraction_method TEXT DEFAULT 'vision',  -- 'vision' or 'subagent'
  extracted_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Page-level extractions (raw per-page data)
CREATE TABLE IF NOT EXISTS page_extractions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT REFERENCES companies(doc_id),
  page_num INTEGER,
  page_type TEXT,
  has_diagram INTEGER DEFAULT 0,
  is_template_placeholder INTEGER DEFAULT 0,
  raw_extraction TEXT,  -- full JSON from vision model
  extracted_at TEXT DEFAULT (datetime('now')),
  UNIQUE(doc_id, page_num)
);

-- Vendors: normalized vendor data across all companies
CREATE TABLE IF NOT EXISTS vendors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT REFERENCES companies(doc_id),
  vendor_name TEXT,
  purpose TEXT,
  criticality TEXT,
  UNIQUE(doc_id, vendor_name)
);

-- Processing status
CREATE TABLE IF NOT EXISTS pipeline_status (
  doc_id TEXT PRIMARY KEY REFERENCES companies(doc_id),
  status TEXT DEFAULT 'pending',  -- pending, converting, extracting, merging, scoring, complete, failed
  workflow_id TEXT,
  pages_total INTEGER,
  pages_extracted INTEGER DEFAULT 0,
  error TEXT,
  started_at TEXT,
  completed_at TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tech_extracts_score ON tech_extracts(score_overall DESC);
CREATE INDEX IF NOT EXISTS idx_tech_extracts_report_type ON tech_extracts(report_type);
CREATE INDEX IF NOT EXISTS idx_vendors_name ON vendors(vendor_name);
CREATE INDEX IF NOT EXISTS idx_pipeline_status ON pipeline_status(status);
CREATE INDEX IF NOT EXISTS idx_page_extractions_doc ON page_extractions(doc_id);
