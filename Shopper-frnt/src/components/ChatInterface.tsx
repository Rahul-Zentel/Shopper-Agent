import { useState, useRef, useEffect } from 'react'
import { searchProducts, type Product, type ConversationMessage } from '../services/api'
import '../App.css' // Reusing existing styles where possible

interface LocalMessage extends ConversationMessage {
    id: string
    products?: Product[]
    quick_notes?: string
    clarifying_questions?: string[]
    isTyping?: boolean
}

export function ChatInterface() {
    const [messages, setMessages] = useState<LocalMessage[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: 'Hello! I am your personal shopping assistant. What are you looking for today?',
        }
    ])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
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

        // Add a temporary typing indicator
        const typingMsgId = 'typing-' + Date.now()
        setMessages(prev => [...prev, {
            id: typingMsgId,
            role: 'assistant',
            content: 'Thinking...',
            isTyping: true
        }])

        try {
            // Prepare history for API (exclude local fields and typing indicators)
            const history = messages
                .filter(m => !m.isTyping)
                .map(m => ({ role: m.role, content: m.content }))

            const response = await searchProducts(text, history)

            // Remove typing indicator
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
                content: 'Sorry, I encountered an error while processing your request. Please try again.',
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

    // Helper function to convert currency code to symbol
    const getCurrencySymbol = (currency: string) => {
        if (currency === 'INR') return '₹'
        if (currency === 'USD') return '$'
        return currency
    }

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.map((msg) => (
                    <div key={msg.id} className={`message-wrapper ${msg.role}`}>
                        <div className="message-bubble">
                            {msg.isTyping ? (
                                <span className="typing-dots">Thinking...</span>
                            ) : (
                                <div className="message-content">
                                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>

                                    {/* Clarifying Questions */}
                                    {msg.clarifying_questions && msg.clarifying_questions.length > 0 && (
                                        <div className="clarifying-questions">
                                            {msg.clarifying_questions.map((q, idx) => (
                                                <button
                                                    key={idx}
                                                    className="suggestion-chip"
                                                    // onClick={() => handleSuggestionClick(q)} // Disabled as requested
                                                    disabled={true} // Visually disabled
                                                    style={{ cursor: 'default', opacity: 0.8 }}
                                                >
                                                    {q}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                    {/* Product Grid */}
                                    {msg.products && msg.products.length > 0 && (
                                        <div className="chat-product-grid">
                                            {msg.products.map((product, idx) => (
                                                <a
                                                    key={idx}
                                                    href={product.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="mini-product-card"
                                                >
                                                    <div className="mini-card-image">
                                                        {product.image_url ? (
                                                            <img src={product.image_url} alt={product.title} />
                                                        ) : (
                                                            <div className="placeholder-img" />
                                                        )}
                                                    </div>
                                                    <div className="mini-card-info">
                                                        <div className="mini-card-title" title={product.title}>{product.title}</div>
                                                        <div className="mini-card-price">
                                                            {getCurrencySymbol(product.currency)} {product.price?.toLocaleString()}
                                                        </div>
                                                        <div className="mini-card-source">{product.source}</div>
                                                    </div>
                                                </a>
                                            ))}
                                        </div>
                                    )}

                                    {/* Quick Notes - Removed as per Zentel specifications */}
                                    {/* {msg.quick_notes && (
                                        <div className="quick-notes-box">
                                            <strong>📝 Quick Notes:</strong>
                                            <div style={{ marginTop: '5px', fontSize: '0.9em' }}>{msg.quick_notes}</div>
                                        </div>
                                    )} */}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <div style={{ position: 'relative', width: '100%', maxWidth: '768px', display: 'flex', alignItems: 'center' }}>
                    <input
                        ref={inputRef}
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Send a message..."
                        disabled={isLoading}
                        style={{ width: '100%', paddingRight: '50px' }}
                    />
                    <button
                        onClick={() => handleSendMessage(inputValue)}
                        disabled={isLoading || !inputValue.trim()}
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', padding: '5px', borderRadius: '4px', border: 'none', background: 'transparent', cursor: 'pointer', color: inputValue.trim() ? 'white' : 'gray' }}
                    >
                        <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" height="16" width="16" xmlns="http://www.w3.org/2000/svg"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    </button>
                </div>
            </div>
        </div>
    )
}
