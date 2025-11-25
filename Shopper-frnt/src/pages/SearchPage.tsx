import type { FormEvent } from 'react'
// Marketplace selector component

type SearchPageProps = {
  query: string
  marketplace: string
  disabled: boolean
  onChange: (value: string) => void
  onMarketplaceChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}

export function SearchPage({ query, marketplace, disabled, onChange, onMarketplaceChange, onSubmit }: SearchPageProps) {
  return (
    <section className="search-panel">
      <h1>What do you want to shop today?</h1>
      <form onSubmit={onSubmit} className="search-form">
        <div style={{ display: 'flex', gap: '0.5rem', width: '100%' }}>
          <select
            value={marketplace}
            onChange={(event) => onMarketplaceChange(event.target.value)}
            aria-label="Select marketplace"
          >
            <option value="flipkart">Flipkart</option>
            <option value="amazon">Amazon</option>
          </select>
          <input
            type="text"
            placeholder="Describe the product or experience you need..."
            value={query}
            onChange={(event) => onChange(event.target.value)}
            aria-label="Shopping query"
            style={{ flex: 1 }}
          />
        </div>
        <button type="submit" disabled={disabled}>
          Shop
        </button>
      </form>
    </section>
  )
}

