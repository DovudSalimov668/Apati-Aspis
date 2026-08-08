export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface HeuristicSignal {
  code: string;
  severity: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  message: string;
  score_impact: number;
}

export interface GeminiExplanation {
  summary: string;
  why_risky: string[];
  recommended_actions: string[];
  education: string[];
}

export interface UrlScanResponse {
  raw_url: string;
  normalized_url: string;
  is_valid: boolean;
  ssrf_blocked: boolean;
  ssrf_blocked_reason?: string;
  domain: string;
  resolved_ips: string[];
  heuristics: HeuristicSignal[];
  evidence: Record<string, any>;
  reasons: string[];
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence: string;
  explanation: GeminiExplanation;
}

export interface MessageScanResponse {
  raw_message: string;
  extracted_urls: string[];
  heuristics: HeuristicSignal[];
  url_scans: UrlScanResponse[];
  evidence: Record<string, any>;
  reasons: string[];
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence: string;
  explanation: GeminiExplanation;
}

export interface QrScanResponse {
  decoded_text?: string;
  payload_type: string;
  image_format: string;
  image_size_bytes: number;
  scan_result?: Record<string, any>;
  evidence: Record<string, any>;
  reasons: string[];
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence: string;
  explanation: GeminiExplanation;
}

export interface CheckupOption {
  id: string;
  text: string;
}

export interface CheckupQuestion {
  id: string;
  category: string;
  category_title: string;
  question: string;
  options: CheckupOption[];
}

export interface CheckupReport {
  overall_score: number;
  security_level: 'LOW' | 'MODERATE' | 'HIGH' | 'EXCELLENT';
  category_scores: Record<string, { title: string; score: number; earned: number; max: number }>;
  weakest_category: string;
  recommendations: string[];
}

export interface ScanRecordHistory {
  id: number;
  scan_type: string;
  indicator: string;
  domain?: string;
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  confidence: string;
  reasons: string[];
  evidence: Record<string, any>;
  created_at: string;
}

export interface PasswordCheckResponse {
  is_pwned: boolean;
  breach_count: number;
  sha1_prefix: string;
  message: string;
  disclaimer: string;
  recommendations: string[];
}


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

export async function scanUrl(url: string): Promise<UrlScanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/scan/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `Scan request failed with status: ${response.status}`);
  }
  return response.json();
}

export async function scanMessage(message: string): Promise<MessageScanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/scan/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `Scan request failed with status: ${response.status}`);
  }
  return response.json();
}

export async function scanQrFile(file: File): Promise<QrScanResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/scan/qr`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `Scan request failed with status: ${response.status}`);
  }
  return response.json();
}

export async function scanImageFile(file: File): Promise<QrScanResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/scan/image`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `Scan request failed with status: ${response.status}`);
  }
  return response.json();
}

export async function fetchCheckupQuestions(): Promise<CheckupQuestion[]> {
  const response = await fetch(`${API_BASE_URL}/api/checkup/questions`);
  if (!response.ok) {
    throw new Error(`Failed to load checkup questions`);
  }
  return response.json();
}

export async function submitCheckup(answers: Record<string, string>): Promise<CheckupReport> {
  const response = await fetch(`${API_BASE_URL}/api/checkup/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  });
  if (!response.ok) {
    throw new Error(`Failed to submit checkup answers`);
  }
  return response.json();
}

export async function fetchScanHistory(limit: number = 20): Promise<ScanRecordHistory[]> {
  const response = await fetch(`${API_BASE_URL}/api/history/scans?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scan history`);
  }
  return response.json();
}

export async function checkPassword(password: string): Promise<PasswordCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/api/password/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `Password check request failed`);
  }
  return response.json();
}
