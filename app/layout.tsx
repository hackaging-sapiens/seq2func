import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from './components/ThemeProvider';

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
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 transition-colors">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}