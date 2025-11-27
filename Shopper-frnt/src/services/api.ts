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

const API_BASE_URL = 'http://127.0.0.1:8000';

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
