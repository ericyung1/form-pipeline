'use client';

import { useState, useRef, useEffect } from 'react';
import { cleanSpreadsheet, downloadCleanedFile, CleanedRow } from '@/lib/api';
import { saveToStorage, loadFromStorage, clearStorage } from '@/lib/storage';

export default function Tab1Clean() {
  const [targetUrl, setTargetUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<CleanedRow[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [cleanedFile, setCleanedFile] = useState<string | null>(null);
  const [cleanedFilename, setCleanedFilename] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load data from localStorage on mount
  useEffect(() => {
    const stored = loadFromStorage();
    if (stored.targetUrl) setTargetUrl(stored.targetUrl);
    if (stored.results.length > 0) setResults(stored.results);
    if (stored.summary) setSummary(stored.summary);
    if (stored.cleanedFile) setCleanedFile(stored.cleanedFile);
    if (stored.filename) setCleanedFilename(stored.filename);
  }, []);

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith('.xlsx') && !selectedFile.name.endsWith('.xls')) {
      setError('Please upload an Excel file (.xlsx or .xls)');
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileChange(droppedFile);
    }
  };

  const handleClean = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!targetUrl.trim()) {
      setError('Please enter a target form URL');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await cleanSpreadsheet(file);
      
      setResults(response.results);
      setSummary(response.summary);
      setCleanedFile(response.cleaned_file);
      setCleanedFilename(response.filename);

      // Save to localStorage
      saveToStorage({
        targetUrl,
        results: response.results,
        summary: response.summary,
        cleanedFile: response.cleaned_file,
        filename: response.filename,
      });
    } catch (err: any) {
      setError(err.message || 'Failed to clean spreadsheet');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setTargetUrl('');
    setFile(null);
    setResults([]);
    setSummary(null);
    setCleanedFile(null);
    setCleanedFilename(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    clearStorage();
  };

  const handleDownload = () => {
    if (cleanedFile && cleanedFilename) {
      downloadCleanedFile(cleanedFile, cleanedFilename);
    }
  };

  const skippedRows = results.filter(r => r.status === 'skipped');

  return (
    <div className="space-y-6">
      {/* Target URL Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Target Form URL
        </label>
        <input
          type="url"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          placeholder="https://www.goarmy.com/info?iom=..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Student Spreadsheet
        </label>
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer text-blue-600 hover:text-blue-700"
          >
            {file ? (
              <div>
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-gray-500 mt-1">Click to change file</p>
              </div>
            ) : (
              <div>
                <p className="font-medium">Click to upload or drag and drop</p>
                <p className="text-sm text-gray-500 mt-1">Excel files (.xlsx, .xls)</p>
              </div>
            )}
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleClean}
          disabled={loading || !file || !targetUrl.trim()}
          className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Cleaning...' : 'Clean Spreadsheet'}
        </button>
        <button
          onClick={handleClear}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          Clear
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-lg mb-3">Summary</h3>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{summary.ok}</div>
              <div className="text-sm text-gray-600">OK</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{summary.fixed}</div>
              <div className="text-sm text-gray-600">Fixed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{summary.skipped}</div>
              <div className="text-sm text-gray-600">Skipped</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-800">{summary.total}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>
        </div>
      )}

      {/* Download Button - Floating Icon on Bottom Right */}
      {cleanedFile && (
        <button
          onClick={handleDownload}
          className="fixed bottom-8 right-8 bg-green-600 text-white p-4 rounded-full shadow-lg hover:bg-green-700 transition-all hover:scale-110 z-50"
          title="Download Cleaned Spreadsheet"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
            />
          </svg>
        </button>
      )}

      {/* Unfixable Rows Warning */}
      {skippedRows.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">
            ⚠️ {skippedRows.length} Unfixable Row{skippedRows.length > 1 ? 's' : ''}
          </h3>
          <p className="text-sm text-yellow-700 mb-3">
            The following rows have errors that need manual correction. Please fix these in your Excel file and re-upload.
          </p>
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Row</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">First Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">DOB</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ZIP</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Note</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((row) => (
                  <tr
                    key={row.row_number}
                    className={
                      row.status === 'skipped'
                        ? 'bg-red-50'
                        : row.status === 'fixed'
                        ? 'bg-blue-50'
                        : ''
                    }
                  >
                    <td className="px-4 py-3 text-sm text-gray-900">{row.row_number}</td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          row.status === 'ok'
                            ? 'bg-green-100 text-green-800'
                            : row.status === 'fixed'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {row.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.data['Email Address']}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.data['First Name']}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.data['Last Name']}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.data['Phone']}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.data['Date of Birth']}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{row.data['Zip Code']}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

