export interface Product {
  title: string;
  price: number;
  rating: number;
  url: string;
  image_url: string | null;
  source: string;
}

export interface SearchResponse {
  products: Product[];
  analysis: string;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL as string | undefined;

if (!API_BASE_URL) {
  throw new Error('VITE_BACKEND_URL is not defined in the environment');
}

export async function searchProducts(query: string, location: string = 'india'): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, marketplace: location }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch products');
  }

  return response.json();
}
