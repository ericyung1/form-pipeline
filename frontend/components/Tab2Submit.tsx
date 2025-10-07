'use client';

import { useState, useEffect, useRef } from 'react';
import { loadFromStorage } from '@/lib/storage';
import {
  startSubmission,
  getSubmissionStatus,
  pauseSubmission,
  resumeSubmission,
  killSubmission,
  SubmissionStatus,
  CleanedRow,
} from '@/lib/api';

export default function Tab2Submit() {
  const [targetUrl, setTargetUrl] = useState('');
  const [students, setStudents] = useState<CleanedRow[]>([]);
  const [validStudents, setValidStudents] = useState<CleanedRow[]>([]);
  const [skippedCount, setSkippedCount] = useState(0);
  const [status, setStatus] = useState<SubmissionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localElapsedSeconds, setLocalElapsedSeconds] = useState(0);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Load data from localStorage on mount
  useEffect(() => {
    const stored = loadFromStorage();
    if (stored.targetUrl) setTargetUrl(stored.targetUrl);
    if (stored.results.length > 0) {
      setStudents(stored.results);
      const valid = stored.results.filter((r: CleanedRow) => r.status === 'ok' || r.status === 'fixed');
      const skipped = stored.results.filter((r: CleanedRow) => r.status === 'skipped');
      setValidStudents(valid);
      setSkippedCount(skipped.length);
    }
  }, []);

  // Local timer - runs independently in browser for smooth counting
  useEffect(() => {
    if (status?.status !== 'running') return;

    const interval = setInterval(() => {
      setLocalElapsedSeconds(prev => prev + 1);
    }, 1000); // Increment every second locally

    return () => clearInterval(interval);
  }, [status?.status]);

  // Reset local timer when starting fresh
  useEffect(() => {
    if (status?.status === 'running' && localElapsedSeconds === 0) {
      setLocalElapsedSeconds(1);
    }
    if (status?.status === 'idle' || status?.status === 'completed' || status?.status === 'killed') {
      if (status?.status === 'idle') setLocalElapsedSeconds(0);
    }
  }, [status?.status]);

  // Poll status when submitting
  useEffect(() => {
    if (!isSubmitting) return;

    const interval = setInterval(async () => {
      try {
        const currentStatus = await getSubmissionStatus();
        setStatus(currentStatus);

        // Stop polling if completed or killed
        if (currentStatus.status === 'completed' || currentStatus.status === 'killed') {
          setIsSubmitting(false);
        }
      } catch (err: any) {
        console.error('Failed to fetch status:', err);
      }
    }, 1000); // Poll every 1 second for backend updates

    return () => clearInterval(interval);
  }, [isSubmitting]);

  // Auto-scroll log to bottom
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [status?.log]);

  const handleStart = async () => {
    if (validStudents.length === 0) {
      setError('No valid students to submit');
      return;
    }

    setError(null);
    setLocalElapsedSeconds(0); // Reset local timer
    setIsSubmitting(true);

    try {
      await startSubmission({
        url: targetUrl,
        students: validStudents.map(s => ({
          row_number: s.row_number,
          data: s.data,
        })),
      });
    } catch (err: any) {
      setError(err.message || 'Failed to start submission');
      setIsSubmitting(false);
    }
  };

  const handlePause = async () => {
    try {
      await pauseSubmission();
      const currentStatus = await getSubmissionStatus();
      setStatus(currentStatus);
    } catch (err: any) {
      setError(err.message || 'Failed to pause submission');
    }
  };

  const handleResume = async () => {
    try {
      await resumeSubmission();
      setIsSubmitting(true);
    } catch (err: any) {
      setError(err.message || 'Failed to resume submission');
    }
  };

  const handleKill = async () => {
    try {
      await killSubmission();
      setIsSubmitting(false);
      const currentStatus = await getSubmissionStatus();
      setStatus(currentStatus);
    } catch (err: any) {
      setError(err.message || 'Failed to kill submission');
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const progressPercentage = status ? Math.round((status.completed / status.total) * 100) : 0;
  const failedRows = status?.log.filter(l => l.status === 'failed') || [];

  return (
    <div className="space-y-6">
      {/* Summary Info */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Submission Summary</h3>
        <div className="space-y-2 text-gray-700">
          <p><span className="font-medium">Target URL:</span> {targetUrl || 'Not set'}</p>
          <p><span className="font-medium">Valid Students:</span> {validStudents.length}</p>
          {skippedCount > 0 && (
            <p className="text-yellow-600">
              <span className="font-medium">Skipped Rows:</span> {skippedCount} (will be ignored during submission)
            </p>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex gap-3">
        {!status || status.status === 'idle' ? (
          <button
            onClick={handleStart}
            disabled={validStudents.length === 0 || !targetUrl}
            className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Start Submission
          </button>
        ) : status.status === 'running' ? (
          <button
            onClick={handlePause}
            className="flex-1 bg-yellow-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-yellow-700 transition-colors"
          >
            Pause
          </button>
        ) : status.status === 'paused' ? (
          <button
            onClick={handleResume}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Continue
          </button>
        ) : null}

        {status && status.status !== 'idle' && status.status !== 'completed' && status.status !== 'killed' && (
          <button
            onClick={handleKill}
            className="px-6 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            Kill Switch
          </button>
        )}
      </div>

      {/* Progress Display */}
      {status && status.total > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{progressPercentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-800">{status.completed}/{status.total}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{status.failed}</div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{formatTime(localElapsedSeconds)}</div>
              <div className="text-sm text-gray-600">Elapsed</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${
                status.status === 'running' ? 'text-green-600' :
                status.status === 'paused' ? 'text-yellow-600' :
                status.status === 'completed' ? 'text-blue-600' :
                'text-gray-600'
              }`}>
                {status.status.toUpperCase()}
              </div>
              <div className="text-sm text-gray-600">Status</div>
            </div>
          </div>
        </div>
      )}

      {/* Live Log */}
      {status && status.log.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Live Log</h3>
          <div
            ref={logContainerRef}
            className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto space-y-1 font-mono text-sm"
          >
            {status.log.map((entry, index) => (
              <div
                key={index}
                className={entry.status === 'success' ? 'text-green-600' : 'text-red-600'}
              >
                {entry.status === 'success' ? '✓' : '✗'} Row {entry.row}: {entry.student} - {entry.status}
                {entry.error && ` (${entry.error})`}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Final Summary - Failed Rows */}
      {status?.status === 'completed' && failedRows.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-600 mb-4">
            Failed Submissions ({failedRows.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Row</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {failedRows.map((entry, index) => (
                  <tr key={index}>
                    <td className="px-4 py-3 text-sm text-gray-900">{entry.row}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{entry.student}</td>
                    <td className="px-4 py-3 text-sm text-red-600">{entry.error || 'Unknown error'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Success Message */}
      {status?.status === 'completed' && status.failed === 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <div className="text-green-600 text-xl font-semibold mb-2">
            ✓ All submissions completed successfully!
          </div>
          <p className="text-gray-600">
            {status.completed} student{status.completed > 1 ? 's' : ''} submitted in {formatTime(localElapsedSeconds)}
          </p>
        </div>
      )}
    </div>
  );
}
