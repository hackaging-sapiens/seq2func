'use client';

import { useState } from 'react';

export default function TestApiPage() {
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const testEndpoint = async (endpoint: string, label: string) => {
    setLoading(prev => ({ ...prev, [label]: true }));
    const url = `${apiUrl}${endpoint}`;

    try {
      console.log(`Testing ${label}:`, url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      setResults(prev => ({
        ...prev,
        [label]: {
          success: true,
          status: response.status,
          statusText: response.statusText,
          data: data,
        }
      }));

      console.log(`${label} SUCCESS:`, data);
    } catch (error: any) {
      setResults(prev => ({
        ...prev,
        [label]: {
          success: false,
          error: error.message,
          errorType: error.name,
        }
      }));

      console.error(`${label} ERROR:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [label]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Backend API Connection Test
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Configuration
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex gap-2">
              <span className="font-semibold text-gray-700 dark:text-gray-300">API URL:</span>
              <code className="bg-gray-100 dark:bg-gray-900 px-2 py-1 rounded text-blue-600 dark:text-blue-400">
                {apiUrl}
              </code>
            </div>
            <div className="flex gap-2">
              <span className="font-semibold text-gray-700 dark:text-gray-300">NEXT_PUBLIC_API_URL:</span>
              <code className="bg-gray-100 dark:bg-gray-900 px-2 py-1 rounded text-blue-600 dark:text-blue-400">
                {process.env.NEXT_PUBLIC_API_URL || '(not set, using default)'}
              </code>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
            Test Endpoints
          </h2>

          <div className="space-y-3">
            <button
              onClick={() => testEndpoint('/', 'Root')}
              disabled={loading['Root']}
              className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors text-left flex items-center justify-between"
            >
              <span>Test GET {apiUrl}/</span>
              {loading['Root'] && <span className="text-sm">Testing...</span>}
            </button>

            <button
              onClick={() => testEndpoint('/openapi.json', 'OpenAPI')}
              disabled={loading['OpenAPI']}
              className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors text-left flex items-center justify-between"
            >
              <span>Test GET {apiUrl}/openapi.json</span>
              {loading['OpenAPI'] && <span className="text-sm">Testing...</span>}
            </button>

            <button
              onClick={() => testEndpoint('/agent?gene_symbol=NRF2', 'Agent')}
              disabled={loading['Agent']}
              className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors text-left flex items-center justify-between"
            >
              <span>Test GET {apiUrl}/agent?gene_symbol=NRF2</span>
              {loading['Agent'] && <span className="text-sm">Testing...</span>}
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Results
          </h2>

          {Object.keys(results).length === 0 && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 text-center text-gray-500 dark:text-gray-400">
              Click a button above to test an endpoint
            </div>
          )}

          {Object.entries(results).map(([label, result]) => (
            <div
              key={label}
              className={`rounded-lg p-6 ${
                result.success
                  ? 'bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800'
                  : 'bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800'
              }`}
            >
              <div className="flex items-center gap-2 mb-3">
                {result.success ? (
                  <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                <h3 className={`text-lg font-semibold ${
                  result.success ? 'text-green-900 dark:text-green-200' : 'text-red-900 dark:text-red-200'
                }`}>
                  {label} - {result.success ? 'SUCCESS' : 'FAILED'}
                </h3>
              </div>

              {result.success && (
                <div className="space-y-2 text-sm">
                  <div className="flex gap-2">
                    <span className="font-semibold text-green-800 dark:text-green-300">Status:</span>
                    <span className="text-green-700 dark:text-green-400">{result.status} {result.statusText}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-green-800 dark:text-green-300">Response:</span>
                    <pre className="mt-2 bg-green-100 dark:bg-green-900 p-3 rounded overflow-x-auto text-xs text-green-900 dark:text-green-100">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {!result.success && (
                <div className="space-y-2 text-sm">
                  <div className="flex gap-2">
                    <span className="font-semibold text-red-800 dark:text-red-300">Error Type:</span>
                    <span className="text-red-700 dark:text-red-400">{result.errorType}</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="font-semibold text-red-800 dark:text-red-300">Error Message:</span>
                    <span className="text-red-700 dark:text-red-400">{result.error}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-8 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
            Debug Instructions
          </h3>
          <div className="text-sm text-yellow-800 dark:text-yellow-300 space-y-2">
            <p>1. Open browser DevTools (F12) → Console tab to see detailed logs</p>
            <p>2. Check Network tab to see actual HTTP requests</p>
            <p>3. Verify backend is running: <code className="bg-yellow-100 dark:bg-yellow-900 px-2 py-1 rounded">uv run uvicorn server:app --reload --port 8000</code></p>
            <p>4. Check backend terminal for request logs</p>
          </div>
        </div>
      </div>
    </div>
  );
}
