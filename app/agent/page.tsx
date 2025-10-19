'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { startGeneSearch, getTaskStatus, cancelTask, type TaskStatusResponse, type ProgressInfo } from '../lib/api';
import { PaperResults } from '../components/PaperResults';
import { ProgressDisplay } from '../components/ProgressDisplay';

function AgentPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  // Get search parameters from URL
  const gene = searchParams.get('gene');
  const maxResults = searchParams.get('max_results');
  const topN = searchParams.get('top_n');
  const includeReprogramming = searchParams.get('include_reprogramming');

  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  // Prevent duplicate task creation (React Strict Mode runs effects twice)
  const hasStartedTask = useRef(false);

  // Start the search task
  useEffect(() => {
    if (!gene) {
      router.push('/');
      return;
    }

    // Prevent duplicate task creation
    if (hasStartedTask.current) return;
    hasStartedTask.current = true;

    // Start the task
    startGeneSearch({
      gene_symbol: gene,
      max_results: maxResults ? parseInt(maxResults) : undefined,
      top_n: topN ? parseInt(topN) : undefined,
      include_reprogramming: includeReprogramming === 'true',
    })
      .then((response) => {
        setTaskId(response.task_id);
      })
      .catch((err) => {
        setError(err.message || 'Failed to start gene search');
      });
  }, [gene, maxResults, topN, includeReprogramming, router]);

  // Poll for task status
  useEffect(() => {
    if (!taskId) return;

    // Poll every 2 seconds
    const intervalId = setInterval(() => {
      getTaskStatus(taskId)
        .then((status) => {
          setTaskStatus(status);

          // Stop polling if task is complete, cancelled, or failed
          if (['completed', 'cancelled', 'failed'].includes(status.status)) {
            clearInterval(intervalId);
          }
        })
        .catch((err) => {
          console.error('Error polling task status:', err);
          setError(err.message || 'Failed to get task status');
          clearInterval(intervalId);
        });
    }, 2000);

    // Initial poll
    getTaskStatus(taskId)
      .then((status) => {
        setTaskStatus(status);
      })
      .catch((err) => {
        setError(err.message || 'Failed to get task status');
      });

    return () => clearInterval(intervalId);
  }, [taskId]);

  // Handle cancel
  const handleCancel = async () => {
    if (!taskId) return;

    setIsCancelling(true);
    try {
      await cancelTask(taskId);
      // The polling will pick up the cancelled status
    } catch (err: any) {
      setError(err.message || 'Failed to cancel task');
    }
    // Note: Don't set isCancelling back to false - keep button disabled
  };

  if (!gene) {
    return null; // Redirecting...
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-teal-600 to-emerald-600 dark:from-blue-900 dark:via-teal-900 dark:to-emerald-900 text-white py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => router.push('/')}
            className="mb-4 text-blue-100 hover:text-white transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Home
          </button>
          <h1 className="text-4xl font-bold mb-2">Gene Literature Search</h1>
          <p className="text-xl text-blue-100">
            Searching for sequence→function→aging links for <span className="font-semibold">{gene}</span>
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-8 text-center">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-red-900 dark:text-red-200 mb-2">
              Search Failed
            </h2>
            <p className="text-red-700 dark:text-red-400 mb-6">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600 text-white rounded-lg transition-colors"
            >
              Return to Home
            </button>
          </div>
        )}

        {/* Loading/Progress State */}
        {!error && taskStatus && ['pending', 'running'].includes(taskStatus.status) && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            {taskStatus.progress ? (
              <ProgressDisplay progress={taskStatus.progress} geneName={gene} />
            ) : (
              <div className="text-center py-12">
                <div className="relative w-16 h-16 mx-auto mb-6">
                  <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-200 dark:border-blue-900 rounded-full"></div>
                  <div className="absolute top-0 left-0 w-full h-full border-4 border-transparent border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
                </div>
                <p className="text-gray-600 dark:text-gray-400">Starting search...</p>
              </div>
            )}

            {/* Cancel Button */}
            <div className="mt-8 text-center">
              <button
                onClick={handleCancel}
                disabled={isCancelling || taskStatus?.status === 'cancelled'}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium"
              >
                {isCancelling || taskStatus?.status === 'cancelled' ? 'Cancelled' : 'Cancel Search'}
              </button>
            </div>
          </div>
        )}

        {/* Cancelled State */}
        {taskStatus?.status === 'cancelled' && (
          <div className="bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg p-8 text-center">
            <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
              Search Cancelled
            </h2>
            <p className="text-yellow-700 dark:text-yellow-400 mb-6">
              The search for {gene} was cancelled.
            </p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-700 dark:hover:bg-yellow-600 text-white rounded-lg transition-colors"
            >
              Return to Home
            </button>
          </div>
        )}

        {/* Failed State */}
        {taskStatus?.status === 'failed' && (
          <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-8 text-center">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-red-900 dark:text-red-200 mb-2">
              Search Failed
            </h2>
            <p className="text-red-700 dark:text-red-400 mb-6">{taskStatus.error || 'An unexpected error occurred'}</p>
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-600 text-white rounded-lg transition-colors"
            >
              Return to Home
            </button>
          </div>
        )}

        {/* Success State */}
        {taskStatus?.status === 'completed' && taskStatus.result && (
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
                Search Results
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Found <strong>{taskStatus.result.count}</strong> relevant paper{taskStatus.result.count !== 1 ? 's' : ''} for <strong>{gene}</strong>
              </p>
            </div>

            {taskStatus.result.count > 0 ? (
              <PaperResults results={taskStatus.result.results} />
            ) : (
              <div className="bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg p-8 text-center">
                <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
                  No Relevant Papers Found
                </h3>
                <p className="text-yellow-700 dark:text-yellow-400 mb-6">
                  No papers met the relevance criteria for sequence→function→aging links for {gene}.
                </p>
                <button
                  onClick={() => router.push('/')}
                  className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-700 dark:hover:bg-yellow-600 text-white rounded-lg transition-colors"
                >
                  Try Another Gene
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}

export default function AgentPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-6">
            <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-200 dark:border-blue-900 rounded-full"></div>
            <div className="absolute top-0 left-0 w-full h-full border-4 border-transparent border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    }>
      <AgentPageContent />
    </Suspense>
  );
}
