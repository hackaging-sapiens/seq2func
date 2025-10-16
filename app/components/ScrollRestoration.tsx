'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';

/**
 * Component that handles scroll position restoration when navigating back
 */
export function ScrollRestoration() {
  const pathname = usePathname();
  const isRestoringRef = useRef(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Only restore on home page
    if (pathname === '/') {
      const savedPosition = sessionStorage.getItem('home-scroll-position');

      if (savedPosition && !isRestoringRef.current) {
        isRestoringRef.current = true;
        const position = parseInt(savedPosition, 10);

        // Immediately scroll before React paints
        window.scrollTo({ top: position, behavior: 'instant' });

        // Use requestAnimationFrame to ensure it happens before paint
        requestAnimationFrame(() => {
          window.scrollTo({ top: position, behavior: 'instant' });

          // Additional frame for safety
          requestAnimationFrame(() => {
            window.scrollTo({ top: position, behavior: 'instant' });
          });
        });

        // Reset flag after a short delay
        setTimeout(() => {
          isRestoringRef.current = false;
        }, 100);
      }
    }

    // Save scroll position as user scrolls on home page
    const handleScroll = () => {
      if (pathname === '/' && !isRestoringRef.current) {
        // Debounce the save operation
        if (scrollTimeoutRef.current !== null) {
          clearTimeout(scrollTimeoutRef.current);
        }

        scrollTimeoutRef.current = setTimeout(() => {
          const position = window.scrollY;
          sessionStorage.setItem('home-scroll-position', position.toString());
        }, 100);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current !== null) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [pathname]);

  return null;
}
