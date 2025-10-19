import type { PaperResult } from '../lib/api';

interface PaperResultsProps {
  results: PaperResult[];
}

export function PaperResults({ results }: PaperResultsProps) {
  return (
    <div className="space-y-6">
      {results.map((paper, index) => (
        <article
          key={paper.pmid}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-200 dark:border-gray-700"
        >
          {/* Rank and Score Badge */}
          <div className="flex items-start justify-between mb-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
              #{index + 1}
            </span>
            <div className="flex items-center gap-2">
              {/* Relevance Score */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Score:</span>
                <div className="flex items-center gap-1">
                  <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        paper.score >= 0.8
                          ? 'bg-green-500'
                          : paper.score >= 0.6
                          ? 'bg-yellow-500'
                          : 'bg-orange-500'
                      }`}
                      style={{ width: `${paper.score * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    {(paper.score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Title */}
          <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3 leading-tight">
            {paper.title}
          </h3>

          {/* Metadata */}
          <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span className="font-medium">{paper.journal}</span>
            </div>
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{paper.year}</span>
            </div>
            <a
              href={`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              PMID: {paper.pmid}
            </a>
          </div>

          {/* AI Reasoning */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  AI Analysis
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {paper.reasoning}
                </p>
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
