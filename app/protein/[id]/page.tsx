import Link from 'next/link';
import { notFound } from 'next/navigation';
import { proteins } from '@/app/data/proteins';

interface ProteinPageProps {
  params: Promise<{ id: string }>;
}

export async function generateStaticParams() {
  return proteins.map((protein) => ({
    id: protein.id,
  }));
}

export default async function ProteinPage({ params }: ProteinPageProps) {
  const { id } = await params;
  const protein = proteins.find((p) => p.id === id);

  if (!protein) {
    notFound();
  }

  return (
    <main className="min-h-screen">
      {/* Header with Breadcrumb */}
      <div className="bg-gradient-to-r from-blue-600 via-teal-600 to-emerald-600 text-white py-8 px-6">
        <div className="max-w-5xl mx-auto">
          <nav className="mb-4 text-sm">
            <Link
              href="/"
              className="text-blue-100 hover:text-white flex items-center gap-2"
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
          <h1 className="text-4xl font-bold">{protein.name}</h1>
          <p className="text-xl text-blue-100 mt-2">{protein.fullName}</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Description Section */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-blue-600">Overview</span>
          </h2>
          <p className="text-gray-700 leading-relaxed">{protein.description}</p>
        </section>

        {/* Sequence Section */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-blue-600">Protein Sequence</span>
            <span className="text-xs font-mono bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {protein.sequence.length} aa
            </span>
          </h2>
          <div className="bg-gray-50 rounded p-4 overflow-x-auto border border-gray-300">
            <pre className="font-mono text-sm text-gray-800 whitespace-pre-wrap break-all leading-relaxed">
              {protein.sequence}
            </pre>
          </div>
        </section>

        {/* Intervals/Domains Section */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-blue-600">Key Intervals & Domains</span>
          </h2>
          <ul className="space-y-2">
            {protein.intervals.map((interval, index) => (
              <li
                key={index}
                className="flex items-start gap-3 text-gray-700"
              >
                <span className="text-teal-600 mt-1">▸</span>
                <span className="font-mono text-sm bg-gray-50 px-3 py-1 rounded border border-gray-300">
                  {interval}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Function Section */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-blue-600">Biological Function</span>
          </h2>
          <p className="text-gray-700 leading-relaxed">{protein.function}</p>
        </section>

        {/* Back Button */}
        <div className="flex justify-center mt-12">
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg transition-colors"
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
