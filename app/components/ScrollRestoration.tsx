'use client';

import { useEffect, useRef } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

/**
 * Component that handles scroll position restoration when navigating back
 */
export function ScrollRestoration() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isRestoringRef = useRef(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Only restore on home page
    if (pathname === '/') {
      const savedPosition = sessionStorage.getItem('home-scroll-position');

      if (savedPosition && !isRestoringRef.current) {
        isRestoringRef.current = true;
        const position = parseInt(savedPosition, 10);

        // Multiple delayed attempts to ensure DOM and images are loaded
        const restore = () => {
          window.scrollTo({ top: position, behavior: 'instant' });
        };

        // Immediate restore
        restore();

        // Additional attempts with increasing delays
        const delays = [10, 50, 100, 200, 300, 500];
        delays.forEach(delay => {
          setTimeout(restore, delay);
        });

        // Reset flag
        setTimeout(() => {
          isRestoringRef.current = false;
        }, 600);
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
  }, [pathname, searchParams]);

  return null;
}
