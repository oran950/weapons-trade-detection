import React, { useState, useEffect } from 'react';
import './App.css';
import DetectionForm from './components/DetectionForm';
import ContentPlayground from './components/ContentPlayground';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import { Datasets, Reports, Settings } from './components/PlaceholderComponents';
import RedditCollector from './components/RedditCollector';
import TelegramCollector from './components/TelegramCollector';

function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting...');
  const [healthData, setHealthData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

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

  const renderContent = () => {
    if (!isConnected) {
      return (
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '100vh',
          padding: '20px'
        }}>
          <h1 style={{ color: '#1f2937', marginBottom: '20px' }}>
            Weapons Trade Detection System
          </h1>
          <p style={{ color: '#6b7280', marginBottom: '30px' }}>
            Academic Research Platform - Python Backend
          </p>
          
          <div style={{
            padding: '20px',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            backgroundColor: '#fef2f2',
            color: '#1f2937',
            maxWidth: '500px',
            textAlign: 'center'
          }}>
            <strong>Backend Status:</strong> {backendStatus}
            <br />
            <p style={{ marginTop: '10px', fontSize: '14px', color: '#6b7280' }}>
              Please ensure your Python backend is running on port 9000
            </p>
          </div>
        </div>
      );
    }

    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'analysis':
        return (
          <div style={{ padding: '30px' }}>
            <h2 style={{ color: '#1f2937', marginBottom: '30px' }}>
              Content Analysis
            </h2>
            <DetectionForm />
          </div>
        );
      case 'playground':
        return <ContentPlayground />;
      case 'reddit':
        return <RedditCollector />;
      case 'telegram':
        return <TelegramCollector />;
      case 'datasets':
        return <Datasets />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App" style={{ display: 'flex', minHeight: '100vh' }}>
      {isConnected && (
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      )}
      
      <main style={{ 
        marginLeft: isConnected ? '250px' : '0',
        flex: 1,
        backgroundColor: '#f9fafb',
        minHeight: '100vh'
      }}>
        {renderContent()}
      </main>

      {/* Floating API Test Button (when connected) */}
      {isConnected && (
        <button 
          onClick={testAPI}
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            padding: '10px 15px',
            fontSize: '12px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            zIndex: 1000
          }}
        >
          Test API
        </button>
      )}
    </div>
  );
}

export default App;