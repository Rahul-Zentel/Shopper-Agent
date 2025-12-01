'use client'

import { useCallback, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { SearchPage } from '@/components/SearchPage'
import { TasksPage } from '@/components/TasksPage'
import { ResultsPage } from '@/components/ResultsPage'
import { searchProducts } from '@/lib/api'
import type { Product, View, TaskStep, SearchMode } from '@/lib/types'

const DEFAULT_QUERY = 'A smart phone with modern features'

const rawTaskSteps = [
  { id: 1, label: 'Analyzing your request', completed: true },
  { id: 2, label: 'Searching online for products', completed: true },
  { id: 3, label: 'Ranking and selecting the best options', completed: false },
  { id: 4, label: 'Finalizing results', completed: false },
]

const getInitialTaskSteps = (): TaskStep[] =>
  rawTaskSteps.map((task, index) => ({
    id: task.id,
    label: task.label,
    status: index === 0 ? 'loading' : 'pending',
  }))

export default function Home() {
  const [view, setView] = useState<View>('search')
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('india')
  const [mode, setMode] = useState<SearchMode>('scraper')
  const [submittedQuery, setSubmittedQuery] = useState(DEFAULT_QUERY)
  const [taskSteps, setTaskSteps] = useState<TaskStep[]>(() => getInitialTaskSteps())
  const [showDetailedLog, setShowDetailedLog] = useState(false)
  const [products, setProducts] = useState<Product[]>([])
  const [analysis, setAnalysis] = useState<string>('')
  const [quickNotes, setQuickNotes] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  const disableShop = useMemo(() => query.trim().length === 0, [query])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (disableShop) {
      return
    }

    const trimmed = query.trim()
    setSubmittedQuery(trimmed || DEFAULT_QUERY)
    setTaskSteps(getInitialTaskSteps())
    setShowDetailedLog(false)
    setProducts([])
    setError(null)
    setView('task')

    try {
      setTaskSteps(prev => prev.map(s => s.id === 1 ? { ...s, status: 'loading' } : s))

      const data = await searchProducts(trimmed || DEFAULT_QUERY, location, mode)

      setTaskSteps(prev => prev.map(s => {
        if (s.id === 1) return { ...s, status: 'done' }
        if (s.id === 2) return { ...s, status: 'loading' }
        return s
      }))

      await new Promise(resolve => setTimeout(resolve, 800))
      setTaskSteps(prev => prev.map(s => {
        if (s.id === 2) return { ...s, status: 'done' }
        if (s.id === 3) return { ...s, status: 'loading' }
        return s
      }))

      await new Promise(resolve => setTimeout(resolve, 800))
      setTaskSteps(prev => prev.map(s => {
        if (s.id === 3) return { ...s, status: 'done' }
        if (s.id === 4) return { ...s, status: 'loading' }
        return s
      }))

      setProducts(data.products)
      setAnalysis(data.analysis)
      setQuickNotes(data.quick_notes || '')

      await new Promise(resolve => setTimeout(resolve, 500))
      setTaskSteps(prev => prev.map(s => s.id === 4 ? { ...s, status: 'done' } : s))

      setTimeout(() => {
        setView('results')
      }, 500)

    } catch (err) {
      console.error(err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
      setTaskSteps(prev => prev.map(s => s.status === 'loading' ? { ...s, status: 'error' } : s))
    }
  }

  const handleBackToSearch = useCallback(() => {
    setTaskSteps(getInitialTaskSteps())
    setShowDetailedLog(false)
    setView('search')
  }, [])

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">Shopper</div>
        <nav className="header-nav" aria-label="Primary navigation">
          <a href="#" onClick={(event) => event.preventDefault()}>
            My Shopping Tasks
          </a>
          <a href="#" onClick={(event) => event.preventDefault()}>
            Preferences
          </a>
        </nav>
        <div className="user-info">
          <span>Welcome Admin</span>
          <span className="user-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" focusable="false">
              <path fill="none" d="M0 0h24v24H0z" />
              <path d="M12 14v8H4a8 8 0 0 1 8-8zm0-1c-3.315 0-6-2.685-6-6s2.685-6 6-6 6 2.685 6 6-2.685 6-6 6zm9 4h1v5h-8v-5h1v-1a3 3 0 0 1 6 0v1zm-2 0v-1a1 1 0 0 0-2 0v1h2z" />
            </svg>
          </span>
        </div>
      </header>

      <main className="app-main">
        {view === 'search' && (
          <SearchPage
            query={query}
            location={location}
            mode={mode}
            disabled={disableShop}
            onChange={(value) => setQuery(value)}
            onLocationChange={(value) => setLocation(value)}
            onModeChange={(value) => setMode(value)}
            onSubmit={(event) => {
              handleSubmit(event)
            }}
          />
        )}

        {view === 'task' && (
          <>
            {error && (
              <div className="error-banner" style={{ color: 'red', padding: '1rem', textAlign: 'center' }}>
                Error: {error}
              </div>
            )}
            <TasksPage
              queryText={submittedQuery}
              steps={taskSteps}
              onBack={handleBackToSearch}
              onShowResults={() => setView('results')}
              showDetailedLog={showDetailedLog}
              onToggleDetailedLog={() => setShowDetailedLog((prev) => !prev)}
            />
          </>
        )}

        {view === 'results' && (
          <ResultsPage
            query={submittedQuery}
            products={products}
            analysis={analysis}
            quickNotes={quickNotes}
            onBack={() => {
              setShowDetailedLog(false)
              setView('task')
            }}
          />
        )}
      </main>
    </div>
  )
}
