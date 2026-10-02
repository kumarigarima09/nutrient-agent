import { useState, useEffect, useRef, useCallback } from 'react';
import { chatApi } from '../api/client';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  tools_used?: string[];
}

function renderContent(content: string) {
  const lines = content.split('\n');
  return lines.map((line, i) => {
    if (line.startsWith('### ')) {
      return (
        <h3 key={i} style={{ fontFamily: 'var(--font-serif)', fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', margin: '14px 0 6px' }}>
          {line.slice(4)}
        </h3>
      );
    }
    if (line.startsWith('## ')) {
      return (
        <h3 key={i} style={{ fontFamily: 'var(--font-serif)', fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: '16px 0 6px' }}>
          {line.slice(3)}
        </h3>
      );
    }
    if (line.startsWith('**') && line.endsWith('**')) {
      return (
        <p key={i} style={{ color: 'var(--accent-terracotta)', fontWeight: 700, margin: '6px 0' }}>
          {line.slice(2, -2)}
        </p>
      );
    }
    if (line.startsWith('- ')) {
      return (
        <li key={i} style={{ color: 'var(--text-secondary)', margin: '3px 0', listStyle: 'disc', marginLeft: 18, fontSize: 14 }}>
          {line.slice(2)}
        </li>
      );
    }
    if (line.trim() === '') return <br key={i} />;
    return (
      <p key={i} style={{ color: 'var(--text-secondary)', margin: '4px 0', lineHeight: 1.65, fontSize: 14 }}>
        {line}
      </p>
    );
  });
}

const STARTER_PROMPTS = [
  'Help me build a lunch from what I have',
  'What makes a snack feel satisfying?',
  'Ideas for easier weekday breakfasts',
  'Am I hitting my protein targets today?',
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadHistory = useCallback(async () => {
    try {
      const hist = await chatApi.history(sessionId);
      setMessages(hist || []);
    } catch {
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function send(text?: string) {
    const msg = text || input;
    if (!msg.trim() || loading) return;
    setInput('');
    const userMsg: Message = { id: Date.now(), role: 'user', content: msg, created_at: new Date().toISOString() };
    setMessages(m => [...m, userMsg]);
    setLoading(true);
    try {
      const resp = await chatApi.send(msg, sessionId);
      if (resp.session_id) setSessionId(resp.session_id);
      const assistantMsg: Message = {
        id: resp.message_id || Date.now() + 1,
        role: 'assistant',
        content: resp.response || resp.message || '',
        created_at: new Date().toISOString(),
        tools_used: resp.tools_used,
      };
      setMessages(m => [...m, assistantMsg]);
    } catch (e: any) {
      setMessages(m => [
        ...m,
        { id: Date.now(), role: 'assistant', content: `Sorry, an error occurred: ${e.message}`, created_at: new Date().toISOString() }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--bg-base)' }}>
      {/* Header if in active chat session */}
      {messages.length > 0 && (
        <div style={{
          padding: '14px 28px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          background: 'var(--bg-card)'
        }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: '50%',
            background: 'var(--accent-sage-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-sage-dark)'
          }}>
            🌱
          </div>
          <div>
            <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-serif)' }}>
              Nutrient AI Coach
            </div>
            <div style={{ fontSize: 11, color: 'var(--accent-sage-dark)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-sage)' }} />
              Deterministic calculations · Grounded nutritional facts
            </div>
          </div>
          <button
            id="chat-new-session"
            className="btn-secondary"
            style={{ marginLeft: 'auto', fontSize: 12, padding: '6px 14px' }}
            onClick={() => { setMessages([]); setSessionId(undefined); }}
          >
            + New Chat
          </button>
        </div>
      )}

      {/* Messages area or Blank Hero State */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            maxWidth: 720,
            margin: '0 auto',
            padding: '40px 16px'
          }}>
            {/* Concentric Circle Sprout Icon */}
            <div style={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              background: 'var(--accent-sage-light)',
              border: '1px solid rgba(126, 146, 120, 0.4)',
              boxShadow: '0 0 0 6px rgba(126, 146, 120, 0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 20
            }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--accent-sage-dark)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22v-7"/>
                <path d="M12 15c-3.5 0-6-2.5-6-6 4 0 6 2 6 6Z"/>
                <path d="M12 15c3.5 0 6-2.5 6-6-4 0-6 2-6 6Z"/>
              </svg>
            </div>

            {/* Sub-label */}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              letterSpacing: '0.14em',
              color: 'var(--accent-terracotta)',
              fontWeight: 600,
              textTransform: 'uppercase',
              marginBottom: 10
            }}>
              A softer start to food guidance
            </div>

            {/* Editorial Heading */}
            <h1 style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 44,
              fontWeight: 600,
              color: 'var(--text-primary)',
              lineHeight: 1.15,
              marginBottom: 14
            }}>
              What would make eating feel <em style={{ fontStyle: 'italic', color: 'var(--accent-terracotta)' }}>easier?</em>
            </h1>

            {/* Lead description */}
            <p style={{
              fontSize: 15.5,
              color: 'var(--text-secondary)',
              maxWidth: 540,
              lineHeight: 1.6,
              marginBottom: 28
            }}>
              Bring a real-life question. We'll find a simple, flexible idea that meets you where you are.
            </p>

            {/* Starter Suggestion Pills */}
            <div style={{ width: '100%', marginBottom: 32 }}>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 10.5,
                letterSpacing: '0.1em',
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                marginBottom: 12
              }}>
                Not sure where to begin?
              </div>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 10,
                justifyContent: 'center',
                maxWidth: 620,
                margin: '0 auto'
              }}>
                {STARTER_PROMPTS.map(p => (
                  <button
                    key={p}
                    onClick={() => send(p)}
                    style={{
                      background: '#ffffff',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius-full)',
                      padding: '8px 18px',
                      fontFamily: 'var(--font-sans)',
                      fontSize: 13,
                      color: 'var(--text-primary)',
                      cursor: 'pointer',
                      transition: 'all 0.18s ease',
                      boxShadow: '0 1px 3px rgba(31, 41, 34, 0.03)'
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.borderColor = 'var(--accent-terracotta)';
                      e.currentTarget.style.color = 'var(--accent-terracotta)';
                      e.currentTarget.style.background = 'var(--accent-terracotta-light)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.borderColor = 'var(--border)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                      e.currentTarget.style.background = '#ffffff';
                    }}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Card Input in Hero */}
            <div style={{
              width: '100%',
              maxWidth: 680,
              background: '#ffffff',
              border: '1px solid var(--border)',
              borderRadius: 22,
              padding: '16px 20px',
              boxShadow: '0 4px 20px rgba(31, 41, 34, 0.05)',
              textAlign: 'left'
            }}>
              <textarea
                rows={2}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
                placeholder="Ask about a meal, snack, or food routine..."
                style={{
                  width: '100%',
                  border: 'none',
                  outline: 'none',
                  fontSize: 15,
                  fontFamily: 'var(--font-sans)',
                  color: 'var(--text-primary)',
                  resize: 'none',
                  background: 'transparent',
                  lineHeight: 1.5
                }}
              />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 10 }}>
                <span style={{ fontSize: 11.5, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  Enter to send · Shift + Enter for a new line
                </span>
                <button
                  onClick={() => send()}
                  disabled={loading || !input.trim()}
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    background: input.trim() ? 'var(--accent-terracotta)' : 'var(--bg-subtle)',
                    color: input.trim() ? '#ffffff' : 'var(--text-muted)',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 16,
                    cursor: input.trim() ? 'pointer' : 'default',
                    transition: 'all 0.2s',
                    boxShadow: input.trim() ? '0 2px 8px rgba(209, 100, 77, 0.3)' : 'none'
                  }}
                >
                  ↑
                </button>
              </div>
            </div>

            {/* Legal Disclaimers */}
            <div style={{ marginTop: 24, fontSize: 11, color: 'var(--text-muted)', maxWidth: 560, lineHeight: 1.5 }}>
              <div>General guidance only. Not medical advice, diagnosis, or treatment. For personal health concerns, talk with a qualified clinician.</div>
              <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                <span>🔒 Science-grounded AI agent · Deterministic nutrition targets</span>
              </div>
            </div>
          </div>
        ) : (
          messages.map(msg => (
            <div key={msg.id} className="fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {msg.role === 'user' ? (
                <div className="chat-bubble-user">
                  <p style={{ fontSize: 14, margin: 0, color: '#ffffff' }}>{msg.content}</p>
                </div>
              ) : (
                <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', maxWidth: '85%' }}>
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    flexShrink: 0,
                    background: 'var(--accent-sage-light)',
                    border: '1px solid rgba(126, 146, 120, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 14,
                    marginTop: 2
                  }}>
                    🌱
                  </div>
                  <div>
                    <div className="chat-bubble-assistant">
                      <div className="chat-content">
                        {renderContent(msg.content)}
                      </div>
                      {msg.tools_used && msg.tools_used.length > 0 && (
                        <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                          {msg.tools_used.map(t => (
                            <span key={t} className="badge badge-teal" style={{ fontSize: 10 }}>
                              ✓ {t.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div style={{ fontSize: 10.5, color: 'var(--text-muted)', marginTop: 4, marginLeft: 6, fontFamily: 'var(--font-mono)' }}>
                      {new Date(msg.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="fade-in" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: 'var(--accent-sage-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 14
            }}>
              🌱
            </div>
            <div style={{
              display: 'flex',
              gap: 5,
              padding: '12px 18px',
              background: '#ffffff',
              border: '1px solid var(--border)',
              borderRadius: '20px 20px 20px 4px',
              boxShadow: 'var(--shadow-card)'
            }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: 'var(--accent-terracotta)',
                  animation: 'bounce 1.2s ease-in-out infinite',
                  animationDelay: `${i * 0.15}s`,
                }} />
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Persistent Bottom Input when chat is active */}
      {messages.length > 0 && (
        <div style={{
          padding: '16px 28px',
          borderTop: '1px solid var(--border)',
          background: 'var(--bg-card)',
          display: 'flex',
          gap: 12,
          alignItems: 'center'
        }}>
          <textarea
            id="chat-input"
            rows={1}
            value={input}
            onChange={e => {
              setInput(e.target.value);
              (e.target as HTMLTextAreaElement).style.height = 'auto';
              (e.target as HTMLTextAreaElement).style.height = Math.min((e.target as HTMLTextAreaElement).scrollHeight, 120) + 'px';
            }}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Ask about a meal, snack, or food routine..."
            className="input-field"
            style={{ flex: 1, resize: 'none', lineHeight: 1.5, minHeight: 44, maxHeight: 120, overflow: 'auto', borderRadius: 'var(--radius-full)' }}
          />
          <button
            id="chat-send"
            onClick={() => send()}
            disabled={loading || !input.trim()}
            style={{
              width: 44,
              height: 44,
              borderRadius: '50%',
              background: input.trim() ? 'var(--accent-terracotta)' : 'var(--bg-subtle)',
              color: input.trim() ? '#ffffff' : 'var(--text-muted)',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 18,
              cursor: input.trim() ? 'pointer' : 'default',
              transition: 'all 0.2s',
              boxShadow: input.trim() ? '0 2px 10px rgba(209, 100, 77, 0.3)' : 'none',
              flexShrink: 0
            }}
          >
            {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : '↑'}
          </button>
        </div>
      )}

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
          40% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
