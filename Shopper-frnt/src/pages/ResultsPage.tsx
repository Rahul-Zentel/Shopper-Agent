import type { Product } from '../services/api'

type ResultsPageProps = {
  query: string
  products: Product[]
  analysis: string
  onBack: () => void
}

export function ResultsPage({ query, products, analysis, onBack }: ResultsPageProps) {
  return (
    <section className="results-panel">
      <button onClick={onBack} className="back-link">
        ← Back to Search
      </button>
      <div className="panel-heading">
        <span className="label">Results for:</span>
        <span>{query}</span>
      </div>

      <div style={{
        marginBottom: '24px',
        padding: '20px',
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '12px',
        border: '1px solid rgba(255,255,255,0.1)',
        color: 'rgba(255,255,255,0.9)',
        fontSize: '15px',
        lineHeight: '1.6'
      }}>
        <strong style={{ color: '#ffffff' }}>🤖 Agent Analysis:</strong> {analysis}
      </div>

      <div className="card-grid">
        {products.map((product, index) => (
          <a
            key={index}
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className="product-card"
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {product.source || 'Product'}
            </div>
            <h3>{product.title}</h3>
            <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="price">₹{product.price?.toLocaleString() || 'N/A'}</div>
              <div className="rating">⭐ {product.rating || 'N/A'}</div>
            </div>
          </a>
        ))}
      </div>
    </section>
  )
}
