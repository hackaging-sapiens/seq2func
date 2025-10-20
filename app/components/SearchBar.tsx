'use client';

import { useState, FormEvent, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

const STORAGE_KEY = 'seq2func_advanced_options';

interface SavedOptions {
  maxResults: number;
  topN: number;
  includeReprogramming: boolean;
}

export function SearchBar() {
  const [geneSymbol, setGeneSymbol] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Advanced options with defaults
  const [maxResults, setMaxResults] = useState(200);
  const [topN, setTopN] = useState(20);
  const [includeReprogramming, setIncludeReprogramming] = useState(false);

  const router = useRouter();
  const isFirstRender = useRef(true);

  // Load saved options from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const options: SavedOptions = JSON.parse(saved);
        setMaxResults(options.maxResults);
        setTopN(options.topN);
        setIncludeReprogramming(options.includeReprogramming);
      }
    } catch (error) {
      console.error('Failed to load saved options:', error);
    }
  }, []);

  // Save options to localStorage whenever they change (skip first render)
  useEffect(() => {
    // Skip saving on first render to avoid overwriting loaded values
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    try {
      const options: SavedOptions = {
        maxResults,
        topN,
        includeReprogramming,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(options));
    } catch (error) {
      console.error('Failed to save options:', error);
    }
  }, [maxResults, topN, includeReprogramming]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const trimmed = geneSymbol.trim();
    if (trimmed) {
      // Build URL with query parameters
      const params = new URLSearchParams({
        gene: trimmed.toUpperCase(),
        ...(maxResults !== 200 && { max_results: maxResults.toString() }),
        ...(topN !== 20 && { top_n: topN.toString() }),
        ...(includeReprogramming && { include_reprogramming: 'true' }),
      });

      router.push(`/agent?${params.toString()}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-4">
      {/* Main Search Input */}
      <div className="relative">
        <input
          type="text"
          value={geneSymbol}
          onChange={(e) => setGeneSymbol(e.target.value)}
          placeholder="Search genes and proteins (e.g., NRF2, SOX2, SIRT1)..."
          className="w-full px-6 py-4 rounded-lg bg-white text-gray-900 dark:text-gray-100 dark:bg-gray-800 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-300 dark:focus:ring-blue-600"
          aria-label="Search for genes and proteins"
        />
        <button
          type="submit"
          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          aria-label="Search"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </button>
      </div>

      {/* Advanced Options Toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-blue-100 dark:text-blue-200 hover:text-white transition-colors flex items-center gap-2"
      >
        <svg
          className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        Advanced Options
      </button>

      {/* Advanced Options Panel */}
      {showAdvanced && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 space-y-6 shadow-lg border border-blue-200 dark:border-blue-700">
          {/* Max Results Slider */}
          <div>
            <label className="flex justify-between items-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <span>Maximum Papers to Retrieve</span>
              <span className="text-blue-600 dark:text-blue-400">{maxResults}</span>
            </label>
            <input
              type="range"
              min="1"
              max="500"
              step="1"
              value={maxResults}
              onChange={(e) => setMaxResults(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600 dark:accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>1</span>
              <span>500</span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
              More papers = more comprehensive but slower search
            </p>
          </div>

          {/* Top N Slider */}
          <div>
            <label className="flex justify-between items-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <span>Top Papers to Return</span>
              <span className="text-blue-600 dark:text-blue-400">{topN}</span>
            </label>
            <input
              type="range"
              min="1"
              max="100"
              step="1"
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600 dark:accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>1</span>
              <span>100</span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
              Only the top N most relevant papers will be returned
            </p>
          </div>

          {/* Include Reprogramming Checkbox */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="include-reprogramming"
              checked={includeReprogramming}
              onChange={(e) => setIncludeReprogramming(e.target.checked)}
              className="mt-1 w-4 h-4 text-blue-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:focus:ring-blue-600 focus:ring-2"
            />
            <div className="flex-1">
              <label
                htmlFor="include-reprogramming"
                className="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer"
              >
                Include Reprogramming Terms
              </label>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Add cellular reprogramming and stem cell related terms to the search query
              </p>
            </div>
          </div>

          {/* Reset Button */}
          <button
            type="button"
            onClick={() => {
              setMaxResults(200);
              setTopN(20);
              setIncludeReprogramming(false);
            }}
            className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
          >
            Reset to Defaults
          </button>
        </div>
      )}
    </form>
  );
}
