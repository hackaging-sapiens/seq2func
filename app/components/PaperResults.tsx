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

          {/* AI-Extracted Insights */}
          {(paper.modification_effects && paper.modification_effects !== "Not specified") ||
           (paper.longevity_association && paper.longevity_association !== "Not specified") ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Modification Effects */}
              {paper.modification_effects && paper.modification_effects !== "Not specified" && (
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/50 dark:to-indigo-950/50 rounded-xl p-5 border-2 border-blue-200 dark:border-blue-800 hover:border-blue-300 dark:hover:border-blue-700 transition-all hover:shadow-md">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-blue-900 dark:text-blue-200 mb-2 flex items-center gap-2">
                        Modification Effects
                        <span className="inline-block w-2 h-2 bg-blue-500 rounded-full"></span>
                      </h4>
                      <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                        {paper.modification_effects}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Longevity Association */}
              {paper.longevity_association && paper.longevity_association !== "Not specified" && (
                <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/50 dark:to-teal-950/50 rounded-xl p-5 border-2 border-emerald-200 dark:border-emerald-800 hover:border-emerald-300 dark:hover:border-emerald-700 transition-all hover:shadow-md">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-emerald-100 dark:bg-emerald-900 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-emerald-900 dark:text-emerald-200 mb-2 flex items-center gap-2">
                        Longevity Association
                        <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full"></span>
                      </h4>
                      <p className="text-sm text-emerald-800 dark:text-emerald-200 leading-relaxed">
                        {paper.longevity_association}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </article>
      ))}
    </div>
  );
}
