/**
 * API client for backend communication
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CleanedRow {
  row_number: number;
  status: 'ok' | 'fixed' | 'skipped';
  note: string;
  data: {
    'Email Address': string;
    'First Name': string;
    'Last Name': string;
    'Phone': string;
    'Date of Birth': string;
    'Zip Code': string;
  };
}

export interface CleanResponse {
  success: boolean;
  results: CleanedRow[];
  summary: {
    ok: number;
    fixed: number;
    skipped: number;
    total: number;
  };
  cleaned_file: string; // base64 encoded
  filename: string;
}

export async function cleanSpreadsheet(file: File): Promise<CleanResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/clean`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to clean spreadsheet');
  }

  return response.json();
}

export function downloadCleanedFile(base64Data: string, filename: string) {
  const blob = base64ToBlob(base64Data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

function base64ToBlob(base64: string, contentType: string): Blob {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: contentType });
}

// Submission API Types
export interface LogEntry {
  row: number;
  status: 'success' | 'failed';
  student: string;
  error?: string;
  timestamp: string;
}

export interface SubmissionStatus {
  completed: number;
  total: number;
  elapsed_seconds: number;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'killed';
  current_position: number;
  failed: number;
  log: LogEntry[];
  errors: string[];
}

export interface SubmitRequest {
  url: string;
  students: {
    row_number: number;
    data: CleanedRow['data'];
  }[];
}

// Submission API Functions
export async function startSubmission(request: SubmitRequest): Promise<{ status: string; total: number }> {
  const response = await fetch(`${API_URL}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start submission');
  }

  return response.json();
}

export async function getSubmissionStatus(): Promise<SubmissionStatus> {
  const response = await fetch(`${API_URL}/status`);
  
  if (!response.ok) {
    throw new Error('Failed to get submission status');
  }

  return response.json();
}

export async function pauseSubmission(): Promise<{ status: string; position: number }> {
  const response = await fetch(`${API_URL}/pause`, { method: 'POST' });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to pause submission');
  }

  return response.json();
}

export async function resumeSubmission(): Promise<{ status: string; resumed_from: number }> {
  const response = await fetch(`${API_URL}/resume`, { method: 'POST' });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to resume submission');
  }

  return response.json();
}

export async function killSubmission(): Promise<{ status: string; final_position: number }> {
  const response = await fetch(`${API_URL}/kill`, { method: 'POST' });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to kill submission');
  }

  return response.json();
}
