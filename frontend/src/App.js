import React, { useState, useEffect } from 'react';
import './App.css';
import DetectionForm from './components/DetectionForm';

function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting...');
  const [healthData, setHealthData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Test connection to Python FastAPI backend on port 9000
    fetch('http://localhost:9000/health')
      .then(response => response.json())
      .then(data => {
        setBackendStatus('Connected to Python Backend!');
        setHealthData(data);
        setIsConnected(true);
      })
      .catch(error => {
        setBackendStatus('Backend connection failed');
        setIsConnected(false);
        console.error('Connection Error:', error);
      });
  }, []);

  const testAPI = async () => {
    try {
      const response = await fetch('http://localhost:9000/api/test');
      const data = await response.json();
      alert('API Response: ' + data.message);
    } catch (error) {
      alert('API test failed: ' + error.message);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Weapons Trade Detection System</h1>
        <p>Academic Research Platform - Python Backend</p>
        
        <div style={{
          margin: '20px',
          padding: '15px',
          border: '1px solid #ccc',
          borderRadius: '8px',
          backgroundColor: isConnected ? '#d4edda' : '#f8d7da',
          color: '#000'
        }}>
          <strong>Backend Status:</strong> {backendStatus}
          
          {healthData && (
            <div style={{ marginTop: '10px', textAlign: 'left' }}>
              <p>Service: {healthData.service}</p>
              <p>Version: {healthData.version}</p>
              <p>Python: {healthData.python_version}</p>
              <p>Status: {healthData.status}</p>
            </div>
          )}
        </div>

        {isConnected && (
          <button 
            onClick={testAPI}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              margin: '10px'
            }}
          >
            Test API Connection
          </button>
        )}

        {isConnected && <DetectionForm />}
      </header>
    </div>
  );
}

export default App;