'use client';

import { Protein, GeneInfo } from '@/app/lib/api';
import { ProteinLink } from './ProteinLink';

interface ProteinGridProps {
  proteins: (Protein | GeneInfo)[];
}

// Type guard to check if item is GeneInfo
function isGeneInfo(item: Protein | GeneInfo): item is GeneInfo {
  return 'gene_symbol' in item;
}

export function ProteinGrid({ proteins }: ProteinGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {proteins.map((protein) => {
        const isGene = isGeneInfo(protein);
        const id = isGene ? protein.gene_symbol : protein.id;
        const name = isGene ? protein.gene_symbol : protein.name;
        const fullName = isGene ? protein.gene_name : protein.fullName;
        const description = isGene ? protein.description : protein.description;
        const badge = isGene ? `Chr ${protein.chromosome}` : protein.id;

        return (
          <ProteinLink
            key={id}
            href={`/gene/${id}`}
            className="group block"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 h-full">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-2xl font-bold text-blue-700 dark:text-blue-400 group-hover:text-blue-900 dark:group-hover:text-blue-300">
                  {name}
                </h3>
                <span className="text-xs font-mono bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 px-2 py-1 rounded">
                  {badge}
                </span>
              </div>

              <h4 className="text-sm text-gray-600 dark:text-gray-400 mb-3 font-medium">
                {fullName}
              </h4>

              <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed mb-4 line-clamp-4">
                {description}
              </p>

              {isGene && protein.papers_count > 0 && (
                <div className="mb-3">
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    {protein.papers_count} paper{protein.papers_count !== 1 ? 's' : ''}
                  </span>
                </div>
              )}

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
          </ProteinLink>
        );
      })}
    </div>
  );
}
