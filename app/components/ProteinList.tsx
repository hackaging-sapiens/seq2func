'use client';

import { useState, useCallback, useEffect } from 'react';
import { Protein } from '@/app/lib/api';
import { ViewMode, ViewToggle } from './ViewToggle';
import { ProteinGrid } from './ProteinGrid';
import { ProteinTable } from './ProteinTable';

interface ProteinListProps {
  proteins: Protein[];
}

export function ProteinList({ proteins }: ProteinListProps) {
  // Initialize with saved preference or default to 'grid'
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    if (typeof window === 'undefined') return 'grid';
    const saved = localStorage.getItem('protein-view') as ViewMode;
    return (saved === 'grid' || saved === 'table') ? saved : 'grid';
  });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Set mounted immediately without delay
    setMounted(true);
  }, []);

  const handleViewChange = useCallback((view: ViewMode) => {
    setViewMode(view);
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
          Longevity-Associated Proteins
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {proteins.length} proteins
          </span>
          {mounted ? (
            <ViewToggle onViewChange={handleViewChange} />
          ) : (
            <div className="p-2 w-9 h-9 rounded-lg bg-gray-200 dark:bg-gray-700" aria-hidden="true" />
          )}
        </div>
      </div>

      {viewMode === 'grid' ? (
        <ProteinGrid proteins={proteins} />
      ) : (
        <ProteinTable proteins={proteins} />
      )}
    </div>
  );
}
