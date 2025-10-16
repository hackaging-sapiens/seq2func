'use client';

import Link from 'next/link';
import { useCallback, ReactNode } from 'react';

interface ProteinLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
}

/**
 * Custom Link component that saves scroll position before navigating
 */
export function ProteinLink({ href, children, className }: ProteinLinkProps) {
  const handleClick = useCallback(() => {
    // Save current scroll position before navigating
    const position = window.scrollY;
    sessionStorage.setItem('home-scroll-position', position.toString());
  }, []);

  return (
    <Link href={href} className={className} onClick={handleClick}>
      {children}
    </Link>
  );
}
