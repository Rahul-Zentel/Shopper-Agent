'use client'

import { useCallback, useMemo, useState, useEffect } from 'react'
import type { FormEvent } from 'react'
import { SearchPage } from '@/components/SearchPage'
import { TasksPage } from '@/components/TasksPage'
import { ResultsPage } from '@/components/ResultsPage'
import { searchProducts, fetchLogs } from '@/lib/api'
import type { Product, View, TaskStep, SearchMode, LogEntry } from '@/lib/types'

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
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [logsLoading, setLogsLoading] = useState(false)

  const disableShop = useMemo(() => query.trim().length === 0, [query])

  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null

    const loadLogs = async () => {
      if (showDetailedLog) {
        setLogsLoading(true)
        try {
          const fetchedLogs = await fetchLogs(100)
          setLogs(fetchedLogs)
        } catch (err) {
          console.error('Failed to fetch logs:', err)
        } finally {
          setLogsLoading(false)
        }
      }
    }

    if (showDetailedLog) {
      loadLogs()
      intervalId = setInterval(loadLogs, 2000)
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [showDetailedLog])

  const handleBackToSearch = useCallback(() => {
    setTaskSteps(getInitialTaskSteps())
    setShowDetailedLog(false)
    setView('search')
  }, [])

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
          <span>Welcome to Shopper</span>
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
              logs={logs}
              logsLoading={logsLoading}
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
