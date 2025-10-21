import Link from 'next/link';
import { notFound } from 'next/navigation';
import { fetchGenes, fetchGeneBySymbol } from '@/app/lib/api';
import { ThemeToggle } from '@/app/components/ThemeToggle';

interface GenePageProps {
  params: Promise<{ symbol: string }>;
}

export async function generateStaticParams() {
  const genes = await fetchGenes();
  return genes.map((gene) => ({
    symbol: gene.gene_symbol,
  }));
}

export default async function GenePage({ params }: GenePageProps) {
  const { symbol } = await params;
  let gene;

  try {
    gene = await fetchGeneBySymbol(symbol);
  } catch (error) {
    console.error(`Error fetching gene ${symbol}:`, error);
    notFound();
  }

  if (!gene) {
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
          <h1 className="text-4xl font-bold">{gene.gene_symbol}</h1>
          <p className="text-xl text-blue-100 dark:text-blue-200 mt-2">{gene.gene_name}</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Gene Information Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Gene Information</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Gene Symbol</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.gene_symbol}</dd>
            </div>
            {gene.gene_symbol_aliases && (
              <div>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Aliases</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.gene_symbol_aliases}</dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">HGNC ID</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.hgnc_gene_id}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">NCBI Gene ID</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.ncbi_gene_id}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Ensembl Gene ID</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.ensembl_geneid}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Gene Type</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.gene_type.replace(/_/g, ' ')}</dd>
            </div>
          </div>
        </section>

        {/* Genomic Location Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Genomic Location</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Chromosome</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.chromosome}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Assembly</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.assembly}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Start Position</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.gene_start_position.toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">End Position</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.gene_end_position.toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Number of Exons</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.number_of_exons}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Gene Length</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">
                {(gene.gene_end_position - gene.gene_start_position + 1).toLocaleString()} bp
              </dd>
            </div>
          </div>
        </section>

        {/* Description Section */}
        <section className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4 flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">Overview</span>
          </h2>
          <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {gene.description}
          </div>
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
