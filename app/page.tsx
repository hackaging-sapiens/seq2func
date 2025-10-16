import { fetchProteins } from './lib/api';
import { ThemeToggle } from './components/ThemeToggle';
import { ProteinList } from './components/ProteinList';
import { ScrollRestoration } from './components/ScrollRestoration';

export default async function Home() {
  const proteins = await fetchProteins();
  return (
    <main className="min-h-screen">
      <ScrollRestoration />
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-teal-600 to-emerald-600 dark:from-blue-900 dark:via-teal-900 dark:to-emerald-900 text-white py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-5xl font-bold mb-4">seq2func</h1>
              <p className="text-xl text-blue-100 dark:text-blue-200 mb-8">
                Sequence-to-Function Longevity Gene Knowledge Base
              </p>
            </div>
            <ThemeToggle />
          </div>

          {/* Search Bar - Placeholder */}
          <div className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                placeholder="Search proteins and genes... (coming soon)"
                className="w-full px-6 py-4 rounded-lg text-gray-900 dark:text-gray-100 dark:bg-gray-800 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-300 dark:focus:ring-blue-600"
                disabled
              />
              <svg
                className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400 dark:text-gray-500"
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
            </div>
          </div>
        </div>
      </div>

      {/* DNA Pattern Background Decoration */}
      <div className="absolute top-0 left-0 w-full h-64 overflow-hidden opacity-10 dark:opacity-5 pointer-events-none">
        <svg className="w-full h-full" viewBox="0 0 1200 200">
          <path
            d="M0,100 Q150,50 300,100 T600,100 T900,100 T1200,100"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            className="text-blue-600 dark:text-blue-400"
          />
          <path
            d="M0,100 Q150,150 300,100 T600,100 T900,100 T1200,100"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            className="text-teal-600 dark:text-teal-400"
          />
        </svg>
      </div>

      {/* Protein List with View Toggle */}
      <ProteinList proteins={proteins} />

      {/* Footer */}
      <footer className="bg-gray-800 dark:bg-gray-950 text-gray-300 dark:text-gray-400 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm">
            seq2func - A knowledge base for protein modifications linked to longevity
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
            Exploring sequence-to-function relationships in aging research
          </p>
        </div>
      </footer>
    </main>
  );
}
