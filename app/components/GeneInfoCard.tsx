import { GeneInfo } from '@/app/lib/api';

interface GeneInfoCardProps {
  gene: GeneInfo;
}

export function GeneInfoCard({ gene }: GeneInfoCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 mb-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            {gene.gene_symbol}
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 mt-1">
            {gene.gene_name}
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
            Chr {gene.chromosome}
          </span>
          {gene.papers_count > 0 && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200">
              {gene.papers_count} paper{gene.papers_count !== 1 ? 's' : ''} in database
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wider">
          Overview
        </h3>
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
          {gene.description}
        </p>
      </div>

      {/* Metadata Grid */}
      <div className="border-t border-gray-200 dark:border-gray-700 mt-4 pt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <dt className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Gene Type</dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.gene_type.replace(/_/g, ' ')}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Exons</dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.number_of_exons}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">NCBI ID</dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100 font-mono">{gene.ncbi_gene_id}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Assembly</dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-gray-100">{gene.assembly}</dd>
        </div>
      </div>
    </div>
  );
}
