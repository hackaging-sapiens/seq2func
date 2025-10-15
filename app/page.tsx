import Link from 'next/link';
import { proteins } from './data/proteins';

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-teal-600 to-emerald-600 text-white py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-5xl font-bold mb-4">seq2func</h1>
          <p className="text-xl text-blue-100 mb-8">
            Sequence-to-Function Longevity Gene Knowledge Base
          </p>

          {/* Search Bar - Placeholder */}
          <div className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                placeholder="Search proteins and genes... (coming soon)"
                className="w-full px-6 py-4 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-300"
                disabled
              />
              <svg
                className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400"
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
      <div className="absolute top-0 left-0 w-full h-64 overflow-hidden opacity-10 pointer-events-none">
        <svg className="w-full h-full" viewBox="0 0 1200 200">
          <path
            d="M0,100 Q150,50 300,100 T600,100 T900,100 T1200,100"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            className="text-blue-600"
          />
          <path
            d="M0,100 Q150,150 300,100 T600,100 T900,100 T1200,100"
            stroke="currentColor"
            strokeWidth="2"
            fill="none"
            className="text-teal-600"
          />
        </svg>
      </div>

      {/* Protein Cards Grid */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <h2 className="text-3xl font-bold text-gray-800 mb-8">
          Longevity-Associated Proteins
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {proteins.map((protein) => (
            <Link
              key={protein.id}
              href={`/protein/${protein.id}`}
              className="group block"
            >
              <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-gray-200 hover:border-blue-400 h-full">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-2xl font-bold text-blue-700 group-hover:text-blue-900">
                    {protein.name}
                  </h3>
                  <span className="text-xs font-mono bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {protein.id}
                  </span>
                </div>

                <h4 className="text-sm text-gray-600 mb-3 font-medium">
                  {protein.fullName}
                </h4>

                <p className="text-gray-700 text-sm leading-relaxed mb-4">
                  {protein.description}
                </p>

                <div className="flex items-center text-blue-600 text-sm font-medium group-hover:text-blue-800">
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
      <footer className="bg-gray-800 text-gray-300 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm">
            seq2func - A knowledge base for protein modifications linked to longevity
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Exploring sequence-to-function relationships in aging research
          </p>
        </div>
      </footer>
    </main>
  );
}
