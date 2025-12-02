import { TaskStep, LogEntry } from '@/lib/types'
import { useEffect, useRef } from 'react'

interface TasksPageProps {
  queryText: string
  steps: TaskStep[]
  onBack: () => void
  onShowResults: () => void
  showDetailedLog: boolean
  onToggleDetailedLog: () => void
  logs: LogEntry[]
  logsLoading: boolean
}

export function TasksPage({
  queryText,
  steps,
  onBack,
  onShowResults,
  showDetailedLog,
  onToggleDetailedLog,
  logs,
  logsLoading,
}: TasksPageProps) {
  const logContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])
  return (
    <section className="tasks-panel">
      <button type="button" className="back-link" onClick={onBack}>
        ← Back
      </button>
      <div className="panel-heading">
        <span className="label">Shopping for:</span>
        <span className="value">{queryText}</span>
      </div>
      <ul className="task-list">
        {steps.map((task) => (
          <li key={task.id} className={task.status}>
            <span className="checkbox" aria-hidden="true">
              {task.status === 'done' && '✓'}
              {task.status === 'loading' && <span className="spinner" />}
              {task.status === 'error' && '✕'}
            </span>
            <span>{task.label}</span>
          </li>
        ))}
      </ul>
      <div className="task-actions">
        <button type="button" className="detail-link" onClick={onToggleDetailedLog}>
          {showDetailedLog ? 'Close detailed log' : 'Show detailed log'}
        </button>
        <button type="button" className="result-button" onClick={onShowResults}>
          View results
        </button>
      </div>
      {showDetailedLog && (
        <div className="detailed-log" role="region" aria-live="polite">
          <p className="log-title">Detailed log {logsLoading && '(updating...)'}</p>
          <div ref={logContainerRef} style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {logs.length === 0 ? (
              <div className="log-row">No logs available yet...</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="log-row">
                  <span style={{ color: '#888', marginRight: '8px' }}>{log.timestamp}</span>
                  <span>{log.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </section>
  )
}
