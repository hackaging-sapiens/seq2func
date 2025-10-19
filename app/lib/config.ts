/**
 * Frontend configuration
 * Centralizes all environment variable access and defaults
 */

/**
 * Backend API base URL
 *
 * Defaults to production Cloud Run deployment.
 * Override by setting NEXT_PUBLIC_API_URL in .env.local for local development.
 *
 * @example
 * // Production (default)
 * API_BASE_URL = 'https://seq2func-108061143941.us-west1.run.app'
 *
 * // Local development (set in .env.local)
 * NEXT_PUBLIC_API_URL=http://localhost:8000
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'https://seq2func-108061143941.us-west1.run.app';
