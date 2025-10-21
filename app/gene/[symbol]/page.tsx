import Link from 'next/link';
import { notFound } from 'next/navigation';
import { fetchGenes, fetchGeneBySymbol } from '@/app/lib/api';
import { ThemeToggle } from '@/app/components/ThemeToggle';
import { PaperResults } from '@/app/components/PaperResults';

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

        {/* Research Papers Section */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Research Papers
            </h2>
            <div className="flex items-center gap-4">
              {gene.papers_count > 0 && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {gene.papers_count} paper{gene.papers_count !== 1 ? 's' : ''} in database
                </span>
              )}
              <Link
                href={`/agent?gene=${gene.gene_symbol}`}
                className="inline-flex items-center gap-2 bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Search for More Papers
              </Link>
            </div>
          </div>

          {gene.papers_count > 0 ? (
            <PaperResults results={gene.papers} />
          ) : (
            <div className="bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg p-8 text-center">
              <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-yellow-900 dark:text-yellow-200 mb-2">
                No Papers in Database Yet
              </h3>
              <p className="text-yellow-700 dark:text-yellow-400 mb-6">
                Click "Search for More Papers" above to find relevant research papers for {gene.gene_symbol}.
              </p>
            </div>
          )}
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
