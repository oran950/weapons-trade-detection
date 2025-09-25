import React from 'react';

const Dashboard = () => {
  return (
    <div style={{ padding: '30px' }}>
      <h2 style={{ color: '#1f2937', marginBottom: '30px' }}>
        System Dashboard
      </h2>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '20px',
        marginBottom: '30px'
      }}>
        {/* Stats Cards */}
        <div style={{
          backgroundColor: '#fff',
          padding: '25px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ color: '#374151', marginBottom: '10px' }}>Total Analyses</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
            1,247
          </p>
          <p style={{ color: '#6b7280', fontSize: '14px', margin: '5px 0 0 0' }}>
            +12% from last week
          </p>
        </div>

        <div style={{
          backgroundColor: '#fff',
          padding: '25px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ color: '#374151', marginBottom: '10px' }}>High Risk Detected</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc2626', margin: 0 }}>
            89
          </p>
          <p style={{ color: '#6b7280', fontSize: '14px', margin: '5px 0 0 0' }}>
            7.1% of total analyses
          </p>
        </div>

        <div style={{
          backgroundColor: '#fff',
          padding: '25px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ color: '#374151', marginBottom: '10px' }}>Generated Content</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#059669', margin: 0 }}>
            2,456
          </p>
          <p style={{ color: '#6b7280', fontSize: '14px', margin: '5px 0 0 0' }}>
            For research testing
          </p>
        </div>
      </div>

      {/* Recent Activity */}
      <div style={{
        backgroundColor: '#fff',
        padding: '25px',
        borderRadius: '8px',
        border: '1px solid #e5e7eb',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <h3 style={{ color: '#374151', marginBottom: '20px' }}>Recent Activity</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {[
            { type: 'HIGH', text: 'Detected firearms keyword in social media post', time: '2 minutes ago' },
            { type: 'MEDIUM', text: 'Tactical gear reference found in forum discussion', time: '15 minutes ago' },
            { type: 'HIGH', text: 'Multiple weapon terms detected in message', time: '23 minutes ago' },
            { type: 'LOW', text: 'Sporting goods content analyzed', time: '1 hour ago' }
          ].map((activity, index) => (
            <div key={index} style={{
              display: 'flex',
              alignItems: 'center',
              padding: '12px',
              backgroundColor: '#f9fafb',
              borderRadius: '6px',
              borderLeft: `4px solid ${activity.type === 'HIGH' ? '#dc2626' : activity.type === 'MEDIUM' ? '#f59e0b' : '#10b981'}`
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: activity.type === 'HIGH' ? '#dc2626' : activity.type === 'MEDIUM' ? '#f59e0b' : '#10b981',
                marginRight: '12px'
              }} />
              <div style={{ flex: 1 }}>
                <p style={{ margin: 0, color: '#374151', fontSize: '14px' }}>{activity.text}</p>
                <p style={{ margin: '2px 0 0 0', color: '#6b7280', fontSize: '12px' }}>{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;