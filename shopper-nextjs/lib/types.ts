export interface Product {
  title: string
  price: number
  rating: number
  url: string
  image_url: string | null
  source: string
}

export interface SearchResponse {
  products: Product[]
  analysis: string
  quick_notes?: string
}

export type View = 'search' | 'task' | 'results'
export type TaskStatus = 'done' | 'loading' | 'pending' | 'error'
export type SearchMode = 'scraper' | 'deep-agent'

export interface TaskStep {
  id: number
  label: string
  status: TaskStatus
}
