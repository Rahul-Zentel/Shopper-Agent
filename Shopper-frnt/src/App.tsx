import { useState } from 'react'
import { searchProducts, type Product, type ConversationMessage } from './services/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

interface LocalMessage extends ConversationMessage {
  id: string
  products?: Product[]
  quick_notes?: string
  clarifying_questions?: string[]
  isTyping?: boolean
}



function App() {
  const [messages, setMessages] = useState<LocalMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return

    const userMsg: LocalMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    }

    setMessages(prev => [...prev, userMsg])
    setInputValue('')
    setIsLoading(true)

    const typingMsgId = 'typing-' + Date.now()
    setMessages(prev => [...prev, {
      id: typingMsgId,
      role: 'assistant',
      content: 'Thinking...',
      isTyping: true
    }])

    try {
      const history = messages
        .filter(m => !m.isTyping)
        .map(m => ({ role: m.role, content: m.content }))

      const response = await searchProducts(text, history)

      setMessages(prev => prev.filter(m => m.id !== typingMsgId))

      const agentMsg: LocalMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.reply_message || response.analysis,
        products: response.products,
        quick_notes: response.quick_notes,
        clarifying_questions: response.clarifying_questions,
      }

      setMessages(prev => [...prev, agentMsg])

    } catch (error) {
      console.error(error)
      setMessages(prev => prev.filter(m => m.id !== typingMsgId))
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(inputValue)
    }
  }

  return (
    <div className="app-wrapper">

      {/* Admin Icon - Top Right */}
      <div className="admin-section">
        <div className="admin-avatar">A</div>
        <span className="admin-name">Admin</span>
      </div>

      {/* Main Content */}
      <div className="main-wrapper">
        {messages.length === 0 ? (
          // Initial State - Large Heading and Search Bar
          <div className="initial-state">
            <h1 className="app-title">Shopper</h1>
            <p className="app-subtitle">Your AI Shopping Assistant</p>

            <div className="search-container">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="What are you looking for today?"
                disabled={isLoading}
                className="search-input"
              />
              <button
                onClick={() => handleSendMessage(inputValue)}
                disabled={isLoading || !inputValue.trim()}
                className="search-button"
              >
                <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" height="20" width="20">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
        ) : (
          // Chat State
          <div className="chat-state">
            <div className="messages-area">
              {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  {msg.isTyping ? (
                    <span className="typing">Thinking...</span>
                  ) : (
                    <>
                      <div className="message-text markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>

                      {msg.clarifying_questions && msg.clarifying_questions.length > 0 && (
                        <div className="questions">
                          {msg.clarifying_questions.map((q, idx) => (
                            <button
                              key={idx}
                              className="question-chip"
                              onClick={() => handleSendMessage(q)}
                              disabled={isLoading}
                            >
                              {q}
                            </button>
                          ))}
                        </div>
                      )}

                      {msg.products && msg.products.length > 0 && (
                        <div className="products-grid">
                          {msg.products.map((product, idx) => (
                            <a
                              key={idx}
                              href={product.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="product-card"
                            >
                              <div className="product-image">
                                {product.image_url ? (
                                  <img src={product.image_url} alt={product.title} />
                                ) : (
                                  <div className="no-image">No Image</div>
                                )}
                              </div>
                              <div className="product-info">
                                <div className="product-title">{product.title}</div>
                                <div className="product-price">
                                  {product.currency === 'INR' ? '₹' : (product.currency === 'USD' ? '$' : (product.currency || '$'))} {product.price?.toLocaleString()}
                                </div>
                                <div className="product-source">{product.source}</div>
                              </div>
                            </a>
                          ))}
                        </div>
                      )}

                      {msg.quick_notes && (
                        <div className="quick-notes">
                          <div className="quick-notes-header">
                            <span>📝</span> Quick Notes
                          </div>
                          <ul className="quick-notes-list">
                            {msg.quick_notes.split('\n').filter(line => line.trim()).map((line, idx) => {
                              const cleanLine = line.replace(/^[-*•]\s*/, '');
                              const parts = cleanLine.split(/(\*\*.*?\*\*)/g);
                              return (
                                <li key={idx} className="quick-notes-item">
                                  {parts.map((part, i) => {
                                    if (part.startsWith('**') && part.endsWith('**')) {
                                      return <strong key={i}>{part.slice(2, -2)}</strong>;
                                    }
                                    return <span key={i}>{part}</span>;
                                  })}
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>

            <div className="input-area">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Send a message..."
                disabled={isLoading}
              />
              <button
                onClick={() => handleSendMessage(inputValue)}
                disabled={isLoading || !inputValue.trim()}
              >
                <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" height="16" width="16">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
