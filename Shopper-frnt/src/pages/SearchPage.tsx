import type { FormEvent } from 'react'

type SearchPageProps = {
  query: string
  location: string
  disabled: boolean
  onChange: (value: string) => void
  onLocationChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}

export function SearchPage({ query, location, disabled, onChange, onLocationChange, onSubmit }: SearchPageProps) {
  return (
    <section className="search-panel">
      <h1>What do you want to shop today?</h1>
      <form onSubmit={onSubmit} className="search-form">
        {/* Location Toggle */}
        <div className="location-toggle-container">
          <button
            type="button"
            className={`location-toggle-btn ${location === 'india' ? 'active' : ''}`}
            onClick={() => onLocationChange('india')}
          >
            🇮🇳 India
          </button>
          <button
            type="button"
            className={`location-toggle-btn ${location === 'usa' ? 'active' : ''}`}
            onClick={() => onLocationChange('usa')}
          >
            🇺🇸 USA
          </button>
        </div>

        {/* Search Input */}
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

