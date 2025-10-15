'use client';

import Link from 'next/link';
import { proteins } from './data/proteins';
import { ThemeToggle } from './components/ThemeToggle';

export default function Home() {
  return (
    <main className="min-h-screen">
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

      {/* Protein Cards Grid */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-8">
          Longevity-Associated Proteins
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {proteins.map((protein) => (
            <Link
              key={protein.id}
              href={`/protein/${protein.id}`}
              className="group block"
            >
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 h-full">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-2xl font-bold text-blue-700 dark:text-blue-400 group-hover:text-blue-900 dark:group-hover:text-blue-300">
                    {protein.name}
                  </h3>
                  <span className="text-xs font-mono bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 px-2 py-1 rounded">
                    {protein.id}
                  </span>
                </div>

                <h4 className="text-sm text-gray-600 dark:text-gray-400 mb-3 font-medium">
                  {protein.fullName}
                </h4>

                <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed mb-4">
                  {protein.description}
                </p>

                <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm font-medium group-hover:text-blue-800 dark:group-hover:text-blue-300">
                  View Details
                  <svg
                    className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

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
