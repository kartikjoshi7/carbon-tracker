import React, { useState, useRef } from 'react';

interface Props {
  onParsed: (category: string, value: number) => void;
}

const ReceiptUploader: React.FC<Props> = ({ onParsed }) => {
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/footprint/upload-receipt', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      onParsed(data.category, data.value);
      alert(`Success! Found ${data.value} for ${data.category}. Form auto-filled.`);
    } catch (err) {
      console.error(err);
      alert("Error parsing receipt.");
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="glass-panel" style={{ marginBottom: '2rem', textAlign: 'center', padding: '1.5rem' }}>
      <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem' }}>📄 AI Receipt Parsing</h2>
      <p className="insight-muted" style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
        Upload a utility bill or transit receipt. Our AI Vision will extract the exact usage and auto-fill your forms!
      </p>
      
      <input 
        type="file" 
        accept="image/*" 
        style={{ display: 'none' }} 
        ref={fileInputRef}
        onChange={handleUpload}
      />
      
      <button 
        onClick={() => fileInputRef.current?.click()} 
        disabled={loading}
        style={{ width: 'auto', padding: '0.75rem 2rem' }}
      >
        {loading ? 'Processing Image...' : 'Upload Image'}
      </button>
    </div>
  );
};

export default ReceiptUploader;
