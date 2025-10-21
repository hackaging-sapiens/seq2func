'use client';

import { Protein, GeneInfo } from '@/app/lib/api';
import { ProteinLink } from './ProteinLink';

interface ProteinTableProps {
  proteins: (Protein | GeneInfo)[];
}

// Type guard to check if item is GeneInfo
function isGeneInfo(item: Protein | GeneInfo): item is GeneInfo {
  return 'gene_symbol' in item;
}

export function ProteinTable({ proteins }: ProteinTableProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Gene
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Full Name
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Chromosome
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Description
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {proteins.map((protein) => {
              const isGene = isGeneInfo(protein);
              const id = isGene ? protein.gene_symbol : protein.id;
              const name = isGene ? protein.gene_symbol : protein.name;
              const fullName = isGene ? protein.gene_name : protein.fullName;
              const description = isGene ? protein.description : protein.description;

              return (
                <tr
                  key={id}
                  className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <ProteinLink
                      href={`/gene/${id}`}
                      className="group flex flex-col"
                    >
                      <span className="text-sm font-bold text-blue-700 dark:text-blue-400 group-hover:text-blue-900 dark:group-hover:text-blue-300">
                        {name}
                      </span>
                      {isGene && protein.gene_symbol_aliases && (
                        <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                          {protein.gene_symbol_aliases}
                        </span>
                      )}
                    </ProteinLink>
                  </td>
                  <td className="px-6 py-4">
                    <ProteinLink
                      href={`/gene/${id}`}
                      className="text-sm text-gray-900 dark:text-gray-100 hover:text-blue-700 dark:hover:text-blue-400"
                    >
                      {fullName}
                    </ProteinLink>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <ProteinLink
                      href={`/gene/${id}`}
                      className="text-sm text-gray-700 dark:text-gray-300 hover:text-blue-700 dark:hover:text-blue-400"
                    >
                      {isGene ? `Chr ${protein.chromosome}` : 'N/A'}
                    </ProteinLink>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <ProteinLink
                      href={`/gene/${id}`}
                      className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-700 dark:hover:text-blue-400"
                    >
                      {isGene ? (
                        <span className="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                          {protein.gene_start_position.toLocaleString()}-{protein.gene_end_position.toLocaleString()}
                        </span>
                      ) : (
                        'N/A'
                      )}
                    </ProteinLink>
                  </td>
                  <td className="px-6 py-4 max-w-md">
                    <ProteinLink
                      href={`/gene/${id}`}
                      className="text-sm text-gray-700 dark:text-gray-300 hover:text-blue-700 dark:hover:text-blue-400 line-clamp-2"
                    >
                      {description}
                    </ProteinLink>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View (stacked list) */}
      <div className="md:hidden divide-y divide-gray-200 dark:divide-gray-700">
        {proteins.map((protein) => {
          const isGene = isGeneInfo(protein);
          const id = isGene ? protein.gene_symbol : protein.id;
          const name = isGene ? protein.gene_symbol : protein.name;
          const fullName = isGene ? protein.gene_name : protein.fullName;
          const description = isGene ? protein.description : protein.description;

          return (
            <ProteinLink
              key={id}
              href={`/gene/${id}`}
              className="block p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-lg font-bold text-blue-700 dark:text-blue-400">
                    {name}
                  </h3>
                  {isGene && protein.gene_symbol_aliases && (
                    <p className="text-xs font-mono text-gray-500 dark:text-gray-400">
                      {protein.gene_symbol_aliases}
                    </p>
                  )}
                </div>
                {isGene && (
                  <span className="text-xs font-mono bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                    Chr {protein.chromosome}
                  </span>
                )}
              </div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                {fullName}
              </h4>
              <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                {description}
              </p>
            </ProteinLink>
          );
        })}
      </div>
    </div>
  );
}
