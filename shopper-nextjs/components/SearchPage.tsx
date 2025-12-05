import type { FormEvent } from 'react'
import { SearchMode } from '@/lib/types'

interface SearchPageProps {
  query: string
  location: string
  mode: SearchMode
  disabled: boolean
  onChange: (value: string) => void
  onLocationChange: (value: string) => void
  onModeChange: (value: SearchMode) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}

export function SearchPage({
  query,
  location,
  mode,
  disabled,
  onChange,
  onLocationChange,
  onModeChange,
  onSubmit
}: SearchPageProps) {
  return (
    <section className="search-panel">
      <h1>What do you want to shop today?</h1>
      <form onSubmit={onSubmit} className="search-form">
        <div className="mode-toggle-container">
          <button
            type="button"
            className={`mode-toggle-btn ${mode === 'scraper' ? 'active' : ''}`}
            onClick={() => onModeChange('scraper')}
          >
            Scraper Mode
          </button>
          <button
            type="button"
            className={`mode-toggle-btn ${mode === 'deep-agent' ? 'active' : ''}`}
            onClick={() => onModeChange('deep-agent')}
          >
            Deep Agent Mode
          </button>
        </div>

        <div className="location-selector-container">
          <button
            type="button"
            className={`usa-toggle-btn ${location === 'usa' ? 'active' : ''}`}
            onClick={() => onLocationChange(location === 'usa' ? 'india' : 'usa')}
          >
            {location === 'usa' ? '← Back to India' : 'Shop in USA 🇺🇸'}
          </button>
        </div>

        <div className="search-input-wrapper">
          <input
            type="text"
            placeholder="Describe the product or experience you need..."
            value={query}
            onChange={(event) => onChange(event.target.value)}
            aria-label="Shopping query"
          />
        </div>

        <button type="submit" disabled={disabled}>
          Shop
        </button>
      </form>
    </section>
  )
}
