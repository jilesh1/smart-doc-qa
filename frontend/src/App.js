import React, { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import WelcomeBot from './components/WelcomeBot';
import './App.css';

const API = 'http://localhost:8000';

function App() {
  const [documents, setDocuments] = useState([]);
  const [activeDoc, setActiveDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [welcome, setWelcome] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadDocs = async () => {
    const res = await fetch(`${API}/documents`);
    const data = await res.json();
    setDocuments(data.documents || []);
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const uploadPdf = async (file) => {
    const form = new FormData();
    form.append('file', file);
    setLoading(true);

    try {
      const res = await fetch(`${API}/upload`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');

      const doc = { doc_id: data.doc_id, filename: data.filename, chunks: data.chunks };
      setActiveDoc(doc);
      setWelcome(data.welcome);
      setMessages([]);
      await loadDocs();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const switchDoc = async (doc) => {
    setActiveDoc(doc);
    setMessages([]);
    setLoading(true);
    try {
      const res = await fetch(`${API}/welcome`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: doc.doc_id }),
      });
      const data = await res.json();
      setWelcome(data);
    } catch {
      setWelcome(null);
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async (question) => {
    if (!activeDoc || !question.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', text: question }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: activeDoc.doc_id, question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Request failed');
      setMessages((prev) => [...prev, { role: 'ai', text: data.answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'ai', text: err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        documents={documents}
        activeDoc={activeDoc}
        onUpload={uploadPdf}
        onSelectDoc={switchDoc}
      />
      <main className="main">
        {!activeDoc ? (
          <div className="empty-state">
            <div className="robot-large">🤖</div>
            <h1>Upload a PDF to get started</h1>
          </div>
        ) : messages.length === 0 ? (
          <WelcomeBot welcome={welcome} loading={loading} onAsk={askQuestion} />
        ) : (
          <ChatArea messages={messages} loading={loading} onAsk={askQuestion} />
        )}
      </main>
    </div>
  );
}

export default App;
