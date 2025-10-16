export interface Protein {
  id: string;
  name: string;
  fullName: string;
  description: string;
  sequence: string;
  intervals: string[];
  function: string;
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
