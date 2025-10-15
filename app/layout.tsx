import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'seq2func - Sequence to Function Longevity Gene Knowledge Base',
  description: 'A comprehensive knowledge base for protein modifications linked to longevity. Explore sequence-to-function relationships in aging research.',
  keywords: ['longevity', 'aging', 'proteins', 'genes', 'bioinformatics', 'sequence analysis'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50">
        {children}
      </body>
    </html>
  );
}