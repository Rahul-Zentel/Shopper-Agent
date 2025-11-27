import type { Product } from '../services/api'

type ResultsPageProps = {
  query: string
  products: Product[]
  analysis: string
  quick_notes?: string
  onBack: () => void
}

export function ResultsPage({ query, products, analysis, quick_notes, onBack }: ResultsPageProps) {
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
            {/* Product Image */}
            <div className="product-image-container">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.title}
                  className="product-image"
                  onError={(e) => {
                    // Fallback to placeholder if image fails to load
                    e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23333" width="200" height="200"/%3E%3Ctext fill="%23666" font-family="sans-serif" font-size="14" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E'
                  }}
                />
              ) : (
                <div className="product-image-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                </div>
              )}
            </div>

            {/* Source Badge */}
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '12px' }}>
              {product.source || 'Product'}
            </div>

            {/* Product Title */}
            <h3>{product.title}</h3>

            {/* Price and Rating */}
            <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="price">
                {product.source && (product.source.includes('India') || product.source === 'Flipkart' || product.source === 'Amazon.in')
                  ? `₹${product.price?.toLocaleString() || 'N/A'}`
                  : `$${product.price?.toLocaleString() || 'N/A'}`
                }
              </div>
              <div className="rating">⭐ {product.rating || 'N/A'}</div>
            </div>
          </a>
        ))}
      </div>

      {quick_notes && (
        <div style={{
          marginTop: '40px',
          padding: '24px',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '16px',
          border: '1px solid rgba(255,255,255,0.1)',
        }}>
          <h2 style={{
            fontSize: '20px',
            marginBottom: '16px',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span>📝</span> Quick Notes
          </h2>
          <div style={{
            color: 'rgba(255,255,255,0.8)',
            fontSize: '15px',
            lineHeight: '1.8',
            whiteSpace: 'pre-line'
          }}>
            {quick_notes}
          </div>
        </div>
      )}
    </section>
  )
}
