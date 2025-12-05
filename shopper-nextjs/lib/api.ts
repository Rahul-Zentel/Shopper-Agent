import { SearchResponse, SearchMode, LogEntry } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000'

export async function searchProducts(
  query: string,
  location: string = 'india',
  mode: SearchMode = 'scraper'
): Promise<SearchResponse> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ query, marketplace: location, mode }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to fetch products')
  }

  return response.json()
}

export async function fetchLogs(limit: number = 100): Promise<LogEntry[]> {
  const headers: Record<string, string> = {}

  const response = await fetch(`${API_BASE_URL}/logs?limit=${limit}`, {
    headers,
  })

  if (!response.ok) {
    throw new Error('Failed to fetch logs')
  }

  const data = await response.json()
  return data.logs
}
