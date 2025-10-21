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
