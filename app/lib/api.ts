import { API_BASE_URL } from './config';

export interface Protein {
  id: string;
  name: string;
  fullName: string;
  description: string;
  sequence: string;
  intervals: string[];
  function: string;
}

// Gene search API types (matching backend Pydantic models)
export interface PaperResult {
  gene_id: number | null;
  gene_symbol: string;
  pmid: string;
  title: string;
  year: string;
  journal: string;
  score: number;
  relevant: boolean;
  reasoning: string;
  modification_effects?: string;
  longevity_association?: string;
  search_date: string;
}

export interface SearchResponse {
  results: PaperResult[];
  count: number;
}

export interface GeneSearchParams {
  gene_symbol: string;
  gene_id?: number;
  max_results?: number;
  top_n?: number;
  include_reprogramming?: boolean;
}

// Async task system types
export interface TaskStartResponse {
  task_id: string;
  status: string;
}

export interface ProgressInfo {
  current_step: string;
  step_number: number;
  total_steps: number;
  papers_screened?: number;
  total_papers?: number;
  message: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'cancelled' | 'failed';
  progress?: ProgressInfo;
  result?: SearchResponse;
  error?: string;
}

const API_URL = 'https://dummyjson.com/c/3418-e7e3-4264-9a03';

/**
 * Fetches all proteins from the REST API
 * @returns Promise<Protein[]> - Array of protein objects
 * @throws Error if the fetch fails or response is invalid
 */
export async function fetchProteins(): Promise<Protein[]> {
  try {
    const response = await fetch(API_URL, {
      // Enable Next.js caching with revalidation
      next: { revalidate: 3600 } // Revalidate every hour
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch proteins: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Validate that we received an array
    if (!Array.isArray(data)) {
      throw new Error('Invalid API response: expected an array of proteins');
    }

    return data as Protein[];
  } catch (error) {
    console.error('Error fetching proteins:', error);
    throw error;
  }
}

/**
 * Fetches a single protein by ID
 * @param id - The protein ID
 * @returns Promise<Protein | undefined> - The protein object or undefined if not found
 */
export async function fetchProteinById(id: string): Promise<Protein | undefined> {
  const proteins = await fetchProteins();
  return proteins.find((p) => p.id === id);
}

/**
 * Searches for gene literature using the backend API (DEPRECATED - use startGeneSearch instead)
 * @param params - Search parameters
 * @returns Promise<SearchResponse> - Search results with papers and metadata
 * @throws Error if the fetch fails or API returns an error
 * @deprecated Use startGeneSearch() for async task-based search with progress tracking
 */
export async function searchGene(params: GeneSearchParams): Promise<SearchResponse> {
  const apiUrl = API_BASE_URL;

  // Build query string from parameters
  const queryParams = new URLSearchParams({
    gene_symbol: params.gene_symbol,
    ...(params.gene_id && { gene_id: params.gene_id.toString() }),
    ...(params.max_results && { max_results: params.max_results.toString() }),
    ...(params.top_n && { top_n: params.top_n.toString() }),
    ...(params.include_reprogramming !== undefined && {
      include_reprogramming: params.include_reprogramming.toString()
    }),
  });

  const url = `${apiUrl}/agent?${queryParams.toString()}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Disable caching for gene searches (data is dynamic)
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `API request failed: ${response.status} ${response.statusText}`);
    }

    const data: SearchResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching gene:', error);
    throw error;
  }
}

/**
 * Start an asynchronous gene literature search task
 * @param params - Search parameters
 * @returns Promise<TaskStartResponse> - Task ID and initial status
 * @throws Error if the request fails
 */
export async function startGeneSearch(params: GeneSearchParams): Promise<TaskStartResponse> {
  const apiUrl = API_BASE_URL;
  const url = `${apiUrl}/agent/start`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        gene_symbol: params.gene_symbol,
        gene_id: params.gene_id,
        max_results: params.max_results || 200,
        top_n: params.top_n || 20,
        include_reprogramming: params.include_reprogramming || false,
      }),
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || errorData.detail || `API request failed: ${response.status}`);
    }

    const data: TaskStartResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error starting gene search:', error);
    throw error;
  }
}

/**
 * Get the status of a gene search task
 * @param taskId - Task ID from startGeneSearch
 * @returns Promise<TaskStatusResponse> - Current task status with progress and results
 * @throws Error if the request fails
 */
export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const apiUrl = API_BASE_URL;
  const url = `${apiUrl}/agent/status/${taskId}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || errorData.detail || `API request failed: ${response.status}`);
    }

    const data: TaskStatusResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting task status:', error);
    throw error;
  }
}

/**
 * Cancel a running gene search task
 * @param taskId - Task ID to cancel
 * @returns Promise<void>
 * @throws Error if the request fails
 */
export async function cancelTask(taskId: string): Promise<void> {
  const apiUrl = API_BASE_URL;
  const url = `${apiUrl}/agent/cancel/${taskId}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || errorData.detail || `API request failed: ${response.status}`);
    }
  } catch (error) {
    console.error('Error cancelling task:', error);
    throw error;
  }
}
