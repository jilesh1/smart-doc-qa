import React from 'react';
import { useDropzone } from 'react-dropzone';

function Sidebar({ documents, activeDoc, onUpload, onSelectDoc }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    onDrop: (files) => files[0] && onUpload(files[0]),
  });

  return (
    <aside className="sidebar">
      <h2>Smart Doc Q&A</h2>
      <div className={`dropzone ${isDragActive ? 'active' : ''}`} {...getRootProps()}>
        <input {...getInputProps()} />
        <p>Drag & drop PDF here</p>
        <span>or click to upload</span>
      </div>

      <h3>Documents</h3>
      <div className="doc-list">
        {documents.map((doc) => (
          <button
            key={doc.doc_id}
            className={`doc-item ${activeDoc?.doc_id === doc.doc_id ? 'selected' : ''}`}
            onClick={() => onSelectDoc(doc)}
          >
            <span>{doc.filename}</span>
            <small>{doc.chunks} chunks</small>
          </button>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;
