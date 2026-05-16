import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function TypingDots() {
  return <div className="typing"><span></span><span></span><span></span></div>;
}

function ChatArea({ messages, loading, onAsk }) {
  const [input, setInput] = useState('');

  const submit = (e) => {
    e.preventDefault();
    const q = input.trim();
    if (!q) return;
    setInput('');
    onAsk(q);
  };

  return (
    <div className="chat-wrap">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            {msg.role === 'ai' && <div className="avatar">🤖</div>}
            <div className={`bubble ${msg.role}`}>
              <ReactMarkdown>{msg.text}</ReactMarkdown>
              {msg.role === 'ai' && msg.text.includes('[') && (
                <div className="citation-box">Citations included from retrieved document chunks</div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="message-row ai"><div className="avatar">🤖</div><div className="bubble ai"><TypingDots /></div></div>}
      </div>

      <form className="input-bar" onSubmit={submit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the selected PDF..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatArea;
