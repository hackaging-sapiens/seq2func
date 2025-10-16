import Link from 'next/link';
import { notFound } from 'next/navigation';
import { fetchProteins, fetchProteinById } from '@/app/lib/api';
import { ThemeToggle } from '@/app/components/ThemeToggle';

interface ProteinPageProps {
  params: Promise<{ id: string }>;
}

export async function generateStaticParams() {
  const proteins = await fetchProteins();
  return proteins.map((protein) => ({
    id: protein.id,
  }));
}

export default async function ProteinPage({ params }: ProteinPageProps) {
  const { id } = await params;
  const protein = await fetchProteinById(id);

  if (!protein) {
    notFound();
  }

  return (
    <main className="min-h-screen">
      {/* Header with Breadcrumb */}
      <div className="bg-gradient-to-r from-blue-600 via-teal-600 to-emerald-600 dark:from-blue-900 dark:via-teal-900 dark:to-emerald-900 text-white py-8 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-start mb-4">
            <nav className="text-sm">
              <Link
                href="/"
                className="text-blue-100 dark:text-blue-200 hover:text-white flex items-center gap-2"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                Back to Knowledge Base
              </Link>
            </nav>
            <ThemeToggle />
          </div>
          <h1 className="text-4xl font-bold">{protein.name}</h1>
          <p className="text-xl text-blue-100 dark:text-blue-200 mt-2">{protein.fullName}</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Description Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Overview</span>
          </h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{protein.description}</p>
        </section>

        {/* Sequence Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Protein Sequence</span>
            <span className="text-xs font-mono bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 px-2 py-1 rounded">
              {protein.sequence.length} aa
            </span>
          </h2>
          <div className="bg-gray-50 dark:bg-gray-900 rounded p-4 overflow-x-auto border border-gray-300 dark:border-gray-600">
            <pre className="font-mono text-sm text-gray-800 dark:text-gray-300 whitespace-pre-wrap break-all leading-relaxed">
              {protein.sequence}
            </pre>
          </div>
        </section>

        {/* Intervals/Domains Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Key Intervals & Domains</span>
          </h2>
          <ul className="space-y-2">
            {protein.intervals.map((interval, index) => (
              <li
                key={index}
                className="flex items-start gap-3 text-gray-700 dark:text-gray-300"
              >
                <span className="text-teal-600 dark:text-teal-400 mt-1">▸</span>
                <span className="font-mono text-sm bg-gray-50 dark:bg-gray-900 px-3 py-1 rounded border border-gray-300 dark:border-gray-600">
                  {interval}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Function Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Biological Function</span>
          </h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{protein.function}</p>
        </section>

        {/* Back Button */}
        <div className="flex justify-center mt-12">
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white font-medium px-6 py-3 rounded-lg transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Return to Knowledge Base
          </Link>
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
