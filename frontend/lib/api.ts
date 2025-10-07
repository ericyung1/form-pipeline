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

