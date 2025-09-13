import React, { useState } from 'react';

function DetectionForm() {
  const [content, setContent] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeContent = async () => {
    if (!content.trim()) {
      alert('Please enter some content to analyze');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:9000/api/detection/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
      });

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed: ' + error.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ margin: '20px', maxWidth: '800px' }}>
      <h2>Content Analysis</h2>
      
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Enter text content to analyze for weapons trade indicators..."
        rows={6}
        style={{
          width: '100%',
          padding: '10px',
          borderRadius: '5px',
          border: '1px solid #ccc'
        }}
      />
      
      <button
        onClick={analyzeContent}
        disabled={loading}
        style={{
          padding: '10px 20px',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer',
          margin: '10px 0'
        }}
      >
        {loading ? 'Analyzing...' : 'Analyze Content'}
      </button>

      {results && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          border: '1px solid #ccc',
          borderRadius: '5px',
          backgroundColor: results.risk_level === 'HIGH' ? '#f8d7da' : 
                          results.risk_level === 'MEDIUM' ? '#fff3cd' : '#d4edda'
        }}>
          <h3>Analysis Results</h3>
          <p><strong>Risk Level:</strong> {results.risk_level}</p>
          <p><strong>Risk Score:</strong> {(results.risk_score * 100).toFixed(1)}%</p>
          <p><strong>Confidence:</strong> {(results.confidence * 100).toFixed(1)}%</p>
          
          {results.flags && results.flags.length > 0 && (
            <div>
              <strong>Detected Issues:</strong>
              <ul>
                {results.flags.map((flag, index) => (
                  <li key={index}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
          
          <p><strong>Summary:</strong> {results.summary}</p>
        </div>
      )}
    </div>
  );
}

export default DetectionForm;