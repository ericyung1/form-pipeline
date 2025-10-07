/**
 * LocalStorage utilities for data persistence
 */

import { CleanedRow } from './api';

const STORAGE_KEYS = {
  TARGET_URL: 'form_pipeline_target_url',
  CLEANED_DATA: 'form_pipeline_cleaned_data',
  SUMMARY: 'form_pipeline_summary',
  CLEANED_FILE: 'form_pipeline_cleaned_file',
  FILENAME: 'form_pipeline_filename',
};

export interface StoredData {
  targetUrl: string;
  results: CleanedRow[];
  summary: {
    ok: number;
    fixed: number;
    skipped: number;
    total: number;
  } | null;
  cleanedFile: string | null;
  filename: string | null;
}

export function saveToStorage(data: Partial<StoredData>): void {
  if (typeof window === 'undefined') return;

  if (data.targetUrl !== undefined) {
    localStorage.setItem(STORAGE_KEYS.TARGET_URL, data.targetUrl);
  }
  if (data.results !== undefined) {
    localStorage.setItem(STORAGE_KEYS.CLEANED_DATA, JSON.stringify(data.results));
  }
  if (data.summary !== undefined) {
    localStorage.setItem(STORAGE_KEYS.SUMMARY, JSON.stringify(data.summary));
  }
  if (data.cleanedFile !== undefined) {
    if (data.cleanedFile === null) {
      localStorage.removeItem(STORAGE_KEYS.CLEANED_FILE);
    } else {
      localStorage.setItem(STORAGE_KEYS.CLEANED_FILE, data.cleanedFile);
    }
  }
  if (data.filename !== undefined) {
    if (data.filename === null) {
      localStorage.removeItem(STORAGE_KEYS.FILENAME);
    } else {
      localStorage.setItem(STORAGE_KEYS.FILENAME, data.filename);
    }
  }
}

export function loadFromStorage(): StoredData {
  if (typeof window === 'undefined') {
    return {
      targetUrl: '',
      results: [],
      summary: null,
      cleanedFile: null,
      filename: null,
    };
  }

  const targetUrl = localStorage.getItem(STORAGE_KEYS.TARGET_URL) || '';
  const resultsStr = localStorage.getItem(STORAGE_KEYS.CLEANED_DATA);
  const summaryStr = localStorage.getItem(STORAGE_KEYS.SUMMARY);
  const cleanedFile = localStorage.getItem(STORAGE_KEYS.CLEANED_FILE);
  const filename = localStorage.getItem(STORAGE_KEYS.FILENAME);

  return {
    targetUrl,
    results: resultsStr ? JSON.parse(resultsStr) : [],
    summary: summaryStr ? JSON.parse(summaryStr) : null,
    cleanedFile,
    filename,
  };
}

export function clearStorage(): void {
  if (typeof window === 'undefined') return;

  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key);
  });
}

