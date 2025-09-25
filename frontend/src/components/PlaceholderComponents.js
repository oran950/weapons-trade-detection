import React from 'react';

// Datasets Component
const Datasets = () => {
  return (
    <div style={{ padding: '30px' }}>
      <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>Research Datasets</h2>
      <div style={{ 
        backgroundColor: '#f3f4f6', 
        padding: '40px', 
        borderRadius: '8px', 
        textAlign: 'center',
        border: '2px dashed #d1d5db'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>📊</div>
        <h3 style={{ color: '#374151', marginBottom: '10px' }}>Dataset Management</h3>
        <p style={{ color: '#6b7280', marginBottom: '20px' }}>
          Store and manage your research datasets, export analysis results, and organize synthetic content for academic studies.
        </p>
        <p style={{ color: '#9ca3af', fontSize: '14px' }}>
          Coming soon - Dataset storage, export tools, and research data management
        </p>
      </div>
    </div>
  );
};

// Reports Component
const Reports = () => {
  return (
    <div style={{ padding: '30px' }}>
      <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>Analysis Reports</h2>
      <div style={{ 
        backgroundColor: '#f3f4f6', 
        padding: '40px', 
        borderRadius: '8px', 
        textAlign: 'center',
        border: '2px dashed #d1d5db'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>📈</div>
        <h3 style={{ color: '#374151', marginBottom: '10px' }}>Detailed Analytics</h3>
        <p style={{ color: '#6b7280', marginBottom: '20px' }}>
          Generate comprehensive reports on detection performance, accuracy metrics, and research insights.
        </p>
        <p style={{ color: '#9ca3af', fontSize: '14px' }}>
          Coming soon - Performance analytics, accuracy reports, and research summaries
        </p>
      </div>
    </div>
  );
};

// Settings Component
const Settings = () => {
  return (
    <div style={{ padding: '30px' }}>
      <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>System Settings</h2>
      <div style={{ 
        backgroundColor: '#f3f4f6', 
        padding: '40px', 
        borderRadius: '8px', 
        textAlign: 'center',
        border: '2px dashed #d1d5db'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚙️</div>
        <h3 style={{ color: '#374151', marginBottom: '10px' }}>Configuration</h3>
        <p style={{ color: '#6b7280', marginBottom: '20px' }}>
          Configure detection thresholds, API settings, and academic research parameters.
        </p>
        <p style={{ color: '#9ca3af', fontSize: '14px' }}>
          Coming soon - Detection tuning, API configuration, and research settings
        </p>
      </div>
    </div>
  );
};

export { Datasets, Reports, Settings };