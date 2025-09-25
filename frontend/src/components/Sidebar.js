import React, { useState } from 'react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: '📊'
    },
    {
      id: 'analysis',
      name: 'Content Analysis',
      icon: '🔍'
    },
    {
      id: 'playground',
      name: 'Content Playground',
      icon: '🎮'
    },
    {
      id: 'reddit',
      name: 'Reddit Collection',
      icon: '🔴',
      badge: 'NEW'
    },
    {
      id: 'datasets',
      name: 'Datasets',
      icon: '📁'
    },
    {
      id: 'reports',
      name: 'Reports',
      icon: '📈'
    },
    {
      id: 'settings',
      name: 'Settings',
      icon: '⚙️'
    }
  ];

  return (
    <div style={{
      width: '250px',
      height: '100vh',
      backgroundColor: '#1f2937',
      color: '#fff',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0,
      top: 0,
      zIndex: 1000
    }}>
      {/* Header */}
      <div style={{
        padding: '20px',
        borderBottom: '1px solid #374151',
        marginBottom: '20px'
      }}>
        <h2 style={{
          margin: 0,
          fontSize: '18px',
          fontWeight: 'bold',
          color: '#f9fafb'
        }}>
          🛡️ Weapons Detection
        </h2>
        <p style={{
          margin: '5px 0 0 0',
          fontSize: '12px',
          color: '#9ca3af'
        }}>
          Academic Research Platform
        </p>
      </div>

      {/* Menu Items */}
      <nav style={{ flex: 1 }}>
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            style={{
              width: '100%',
              padding: '12px 20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: activeTab === item.id ? '#374151' : 'transparent',
              color: activeTab === item.id ? '#f9fafb' : '#d1d5db',
              border: 'none',
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'all 0.2s ease',
              borderLeft: activeTab === item.id ? '3px solid #3b82f6' : '3px solid transparent',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== item.id) {
                e.target.style.backgroundColor = '#374151';
                e.target.style.color = '#f9fafb';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== item.id) {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = '#d1d5db';
              }
            }}
          >
            <span style={{ fontSize: '16px' }}>{item.icon}</span>
            <span style={{ flex: 1, textAlign: 'left' }}>{item.name}</span>
            {item.badge && (
              <span style={{
                fontSize: '10px',
                padding: '2px 6px',
                backgroundColor: '#dc2626',
                color: 'white',
                borderRadius: '10px',
                fontWeight: 'bold'
              }}>
                {item.badge}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div style={{
        padding: '20px',
        borderTop: '1px solid #374151',
        fontSize: '12px',
        color: '#6b7280'
      }}>
        <div style={{ marginBottom: '8px' }}>
          <strong>Status:</strong> Connected
        </div>
        <div style={{ marginBottom: '8px' }}>
          <strong>Version:</strong> 2.1.0
        </div>
        <div>
          <strong>Python:</strong> 3.13
        </div>
      </div>
    </div>
  );
};

export default Sidebar;