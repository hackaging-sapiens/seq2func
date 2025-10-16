'use client';

import { useState, useEffect } from 'react';

export type ViewMode = 'grid' | 'table';

interface ViewToggleProps {
  onViewChange: (view: ViewMode) => void;
}

export function ViewToggle({ onViewChange }: ViewToggleProps) {
  const [view, setView] = useState<ViewMode>('grid');
  const [mounted, setMounted] = useState(false);

  // Load view preference from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const savedView = localStorage.getItem('protein-view') as ViewMode;
    if (savedView === 'grid' || savedView === 'table') {
      setView(savedView);
      onViewChange(savedView);
    }
  }, [onViewChange]);

  const toggleView = () => {
    const newView: ViewMode = view === 'grid' ? 'table' : 'grid';
    setView(newView);
    localStorage.setItem('protein-view', newView);
    onViewChange(newView);
  };

  // Show placeholder during SSR and initial hydration to prevent mismatch
  if (!mounted) {
    return (
      <div className="p-2 w-9 h-9 rounded-lg bg-white/10 dark:bg-gray-800/50" aria-hidden="true" />
    );
  }

  return (
    <button
      onClick={toggleView}
      className="p-2 rounded-lg bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 transition-colors border border-gray-300 dark:border-gray-600"
      aria-label={`Switch to ${view === 'grid' ? 'table' : 'grid'} view`}
      title={`Switch to ${view === 'grid' ? 'table' : 'grid'} view`}
    >
      {view === 'grid' ? (
        // Table/List icon - show when in grid mode (to switch to table)
        <svg
          className="w-5 h-5 text-gray-700 dark:text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 10h16M4 14h16M4 18h16"
          />
        </svg>
      ) : (
        // Grid icon - show when in table mode (to switch to grid)
        <svg
          className="w-5 h-5 text-gray-700 dark:text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
          />
        </svg>
      )}
    </button>
  );
}
