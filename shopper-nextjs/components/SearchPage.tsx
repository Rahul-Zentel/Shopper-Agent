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
  disabled,
  onChange,
  onLocationChange,
  onSubmit
}: SearchPageProps) {
  return (
    <section className="search-panel">
      <div className="location-selector-corner">
        <select
          value={location}
          onChange={(e) => onLocationChange(e.target.value)}
          className="location-select"
        >
          <option value="usa">USA</option>
          <option value="india">India</option>
        </select>
      </div>
      <h1>What do you want to shop today?</h1>
      <form onSubmit={onSubmit} className="search-form">
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
