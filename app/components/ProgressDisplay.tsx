import type { ProgressInfo } from '../lib/api';

interface ProgressDisplayProps {
  progress: ProgressInfo;
  geneName: string;
}

export function ProgressDisplay({ progress, geneName }: ProgressDisplayProps) {
  // Calculate paper screening progress if available
  const paperProgress = progress.papers_screened && progress.total_papers
    ? (progress.papers_screened / progress.total_papers) * 100
    : 0;

  const isScreening = progress.papers_screened !== undefined && progress.total_papers;

  return (
    <div className="space-y-6">
      {/* Spinner */}
      <div className="flex justify-center">
        <div className="relative w-20 h-20">
          <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-200 dark:border-blue-900 rounded-full"></div>
          <div className="absolute top-0 left-0 w-full h-full border-4 border-transparent border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
        </div>
      </div>

      {/* Title */}
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          {isScreening ? 'Screening Papers...' : 'Preparing Search...'}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Searching for sequence-to-function data for <strong>{geneName}</strong>
        </p>
      </div>

      {/* Current Action Message */}
      {progress.message && (
        <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-sm text-blue-900 dark:text-blue-200 font-medium text-center">
            {progress.message}
          </p>
        </div>
      )}

      {/* Paper Screening Progress */}
      {isScreening ? (
        <div className="space-y-3">
          <div className="flex justify-between text-lg font-semibold text-gray-700 dark:text-gray-300">
            <span>Screening Progress</span>
            <span className="text-blue-600 dark:text-blue-400">
              {progress.papers_screened} / {progress.total_papers}
            </span>
          </div>
          <div className="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
            <div
              className="h-full bg-gradient-to-r from-blue-500 via-teal-500 to-emerald-500 transition-all duration-300 ease-out relative overflow-hidden"
              style={{ width: `${paperProgress}%` }}
            >
              {/* Animated shine effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
            </div>
          </div>
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {paperProgress.toFixed(1)}% complete
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Using AI to analyze papers for sequence→function→aging links
            </p>
          </div>
        </div>
      ) : (
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-full">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Building query and searching PubMed...
            </p>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
        <p className="text-sm text-gray-700 dark:text-gray-300 text-center">
          <strong>Note:</strong> This process may take 1-3 minutes depending on the number of papers.
          You can cancel at any time using the button below.
        </p>
      </div>
    </div>
  );
}
