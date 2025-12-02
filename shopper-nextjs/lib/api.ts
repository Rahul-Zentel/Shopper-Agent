import { SearchResponse, SearchMode, LogEntry } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000'

async function getAccessToken(): Promise<string | null> {
  try {
    const response = await fetch('/api/auth/token')
    if (response.ok) {
      const data = await response.json()
      return data.accessToken
    }
  } catch (error) {
    console.error('Failed to get access token:', error)
  }
  return null
}

export async function searchProducts(
  query: string,
  location: string = 'india',
  mode: SearchMode = 'scraper'
): Promise<SearchResponse> {
  const token = await getAccessToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
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
  const token = await getAccessToken()
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}/logs?limit=${limit}`, {
    headers,
  })

  if (!response.ok) {
    throw new Error('Failed to fetch logs')
  }

  const data = await response.json()
  return data.logs
}
