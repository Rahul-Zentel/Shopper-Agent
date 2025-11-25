type TasksPageProps = {
  queryText: string
  steps: { id: number; label: string; status: 'done' | 'loading' | 'pending' | 'error' }[]
  onBack: () => void
  onShowResults: () => void
  showDetailedLog: boolean
  onToggleDetailedLog: () => void
}

export function TasksPage({
  queryText,
  steps,
  onBack,
  onShowResults,
  showDetailedLog,
  onToggleDetailedLog,
}: TasksPageProps) {
  return (
    <section className="tasks-panel">
      <button type="button" className="back-link" onClick={onBack}>
        &lt;Back
      </button>
      <div className="panel-heading">
        <span className="label">Shopping for :</span>
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
          <p className="log-title">Detailed log</p>
          <div className="log-row">Analyzing preference data for Admin</div>
          <div className="log-row">Comparing shortlisted phones across 25-35k range</div>
          <div className="log-row">Aggregating online reviews and availability</div>
        </div>
      )}
    </section>
  )
}

