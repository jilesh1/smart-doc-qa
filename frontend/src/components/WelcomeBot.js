import React from 'react';

function TypingDots() {
  return <div className="typing"><span></span><span></span><span></span></div>;
}

function WelcomeBot({ welcome, loading, onAsk }) {
  return (
    <div className="welcome">
      <div className="avatar big">🤖</div>
      {loading && !welcome ? <TypingDots /> : (
        <>
          <h1>Document ready</h1>
          <p>{welcome?.summary || 'Your PDF has been uploaded. Ask me anything about it.'}</p>
          <div className="chips">
            {(welcome?.questions || []).map((q, i) => (
              <button key={i} onClick={() => onAsk(q)}>{q}</button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default WelcomeBot;
