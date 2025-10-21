import { fetchGenes } from './lib/api';
import { ThemeToggle } from './components/ThemeToggle';
import { ProteinList } from './components/ProteinList';
import { ScrollRestoration } from './components/ScrollRestoration';
import { SearchBar } from './components/SearchBar';

export default async function Home() {
  const proteins = await fetchGenes();
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

          {/* Search Bar */}
          <SearchBar />
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
