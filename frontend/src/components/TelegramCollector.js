import React, { useState, useEffect } from 'react';

const TelegramCollector = () => {
  const [isCollecting, setIsCollecting] = useState(false);
  const [collectionResults, setCollectionResults] = useState(null);
  const [configStatus, setConfigStatus] = useState(null);

  const [collectionParams, setCollectionParams] = useState({
    channels: [],
    groups: [],
    keywords: [],
    limit_per_source: 50,
    search_globally: false
  });

  const [newChannel, setNewChannel] = useState('');
  const [newKeyword, setNewKeyword] = useState('');

  // Check Telegram configuration status on component load
  useEffect(() => {
    checkConfigStatus();
  }, []);

  const checkConfigStatus = async () => {
    try {
      const response = await fetch('http://localhost:9000/api/telegram/config-status');
      const status = await response.json();
      setConfigStatus(status);
    } catch (error) {
      console.error('Failed to check config status:', error);
      setConfigStatus({ is_configured: false, missing_config: ['API connection failed'] });
    }
  };

  const addChannel = () => {
    if (newChannel.trim() && !collectionParams.channels.includes(newChannel.trim())) {
      setCollectionParams({
        ...collectionParams,
        channels: [...collectionParams.channels, newChannel.trim().replace('@', '')]
      });
      setNewChannel('');
    }
  };

  const removeChannel = (channel) => {
    setCollectionParams({
      ...collectionParams,
      channels: collectionParams.channels.filter(c => c !== channel)
    });
  };

  const addKeyword = () => {
    if (newKeyword.trim() && !collectionParams.keywords.includes(newKeyword.trim())) {
      setCollectionParams({
        ...collectionParams,
        keywords: [...collectionParams.keywords, newKeyword.trim()]
      });
      setNewKeyword('');
    }
  };

  const removeKeyword = (keyword) => {
    setCollectionParams({
      ...collectionParams,
      keywords: collectionParams.keywords.filter(k => k !== keyword)
    });
  };

  const handleCollection = async () => {
    if (!configStatus?.is_configured) {
      alert('Telegram API is not configured. Please check your backend .env file.');
      return;
    }

    if (collectionParams.channels.length === 0 && !collectionParams.search_globally) {
      alert('Please add at least one channel to collect from, or enable global search.');
      return;
    }

    setIsCollecting(true);
    try {
      const response = await fetch('http://localhost:9000/api/telegram/collect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          parameters: collectionParams
        })
      });

      const data = await response.json();
      setCollectionResults(data);
    } catch (error) {
      console.error('Collection failed:', error);
      alert('Collection failed: ' + error.message);
    } finally {
      setIsCollecting(false);
    }
  };

  return (
    <div style={{ padding: '30px', maxWidth: '1200px' }}>
      <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>
        Telegram Data Collection
      </h2>

      {/* Configuration Status */}
      <div style={{
        backgroundColor: configStatus?.is_configured ? '#dbeafe' : '#fee2e2',
        border: `1px solid ${configStatus?.is_configured ? '#3b82f6' : '#ef4444'}`,
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '25px'
      }}>
        <h3 style={{ 
          color: configStatus?.is_configured ? '#1e40af' : '#991b1b', 
          marginBottom: '10px' 
        }}>
          {configStatus?.is_configured ? '✅ Telegram API Configured' : '❌ Telegram API Not Configured'}
        </h3>
        
        {configStatus?.is_configured ? (
          <div>
            <p style={{ color: '#1e40af', marginBottom: '10px' }}>
              Your Telegram API credentials are properly configured in the backend.
            </p>
            <p style={{ fontSize: '14px', color: '#3b82f6' }}>
              Ready to collect from public channels and groups.
            </p>
          </div>
        ) : (
          <div>
            <p style={{ color: '#991b1b', marginBottom: '10px' }}>
              Please configure your Telegram API credentials in the backend .env file.
            </p>
            {configStatus?.missing_config && (
              <div style={{ fontSize: '14px', color: '#7f1d1d' }}>
                <strong>Missing:</strong> {configStatus.missing_config.join(', ')}
              </div>
            )}
            <div style={{ marginTop: '15px', padding: '15px', backgroundColor: '#fef3c7', borderRadius: '6px' }}>
              <h4 style={{ color: '#92400e', marginBottom: '10px' }}>Setup Instructions:</h4>
              <ol style={{ color: '#78350f', fontSize: '14px', margin: 0, paddingLeft: '20px' }}>
                <li>Go to <a href="https://my.telegram.org" target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb' }}>my.telegram.org</a></li>
                <li>Log in with your phone number</li>
                <li>Go to "API development tools"</li>
                <li>Create a new application to get api_id and api_hash</li>
                <li>Add TELEGRAM_API_ID and TELEGRAM_API_HASH to your .env file</li>
              </ol>
            </div>
          </div>
        )}
        
        <button 
          onClick={checkConfigStatus}
          style={{
            marginTop: '10px',
            padding: '6px 12px',
            backgroundColor: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Refresh Status
        </button>
      </div>

      <div style={{
        backgroundColor: '#fff',
        padding: '25px',
        borderRadius: '8px',
        border: '1px solid #e5e7eb',
        marginBottom: '25px'
      }}>
        <h3 style={{ color: '#374151', marginBottom: '20px' }}>Collection Parameters</h3>
        
        {/* Channels */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#374151' }}>
            Channels to Collect ({collectionParams.channels.length}):
          </label>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input 
              type="text"
              placeholder="Enter channel username (e.g., channelname)"
              value={newChannel}
              onChange={(e) => setNewChannel(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addChannel()}
              style={{ 
                flex: 1,
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '6px'
              }}
            />
            <button 
              onClick={addChannel}
              style={{
                padding: '8px 16px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Add
            </button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {collectionParams.channels.map(channel => (
              <span key={channel} style={{
                padding: '4px 12px',
                backgroundColor: '#dbeafe',
                borderRadius: '20px',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                @{channel}
                <button 
                  onClick={() => removeChannel(channel)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#3b82f6',
                    fontWeight: 'bold'
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Keywords */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#374151' }}>
            Search Keywords ({collectionParams.keywords.length}):
          </label>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input 
              type="text"
              placeholder="Enter keyword to search"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
              style={{ 
                flex: 1,
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '6px'
              }}
            />
            <button 
              onClick={addKeyword}
              style={{
                padding: '8px 16px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Add
            </button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {collectionParams.keywords.map(keyword => (
              <span key={keyword} style={{
                padding: '4px 12px',
                backgroundColor: '#fef3c7',
                borderRadius: '20px',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                {keyword}
                <button 
                  onClick={() => removeKeyword(keyword)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#d97706',
                    fontWeight: 'bold'
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Messages per Source:
            </label>
            <input 
              type="number"
              min="1"
              max="200"
              value={collectionParams.limit_per_source}
              onChange={(e) => setCollectionParams({...collectionParams, limit_per_source: parseInt(e.target.value)})}
              style={{ 
                width: '100%', 
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '6px'
              }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input 
                type="checkbox"
                checked={collectionParams.search_globally}
                onChange={(e) => setCollectionParams({...collectionParams, search_globally: e.target.checked})}
              />
              <span style={{ fontWeight: 'bold', color: '#374151' }}>Search Globally</span>
            </label>
            <span style={{ fontSize: '12px', color: '#6b7280', marginLeft: '8px' }}>
              (Search across all accessible chats)
            </span>
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <button 
          onClick={handleCollection}
          disabled={isCollecting || !configStatus?.is_configured}
          style={{
            padding: '12px 24px',
            backgroundColor: isCollecting || !configStatus?.is_configured ? '#6b7280' : '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isCollecting || !configStatus?.is_configured ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {isCollecting ? 'Collecting & Analyzing...' : 'Start Telegram Collection'}
        </button>
      </div>

      {collectionResults && (
        <div style={{
          backgroundColor: '#fff',
          padding: '25px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ color: '#374151', marginBottom: '20px' }}>Collection Results</h3>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
            gap: '15px',
            marginBottom: '25px'
          }}>
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f3f4f6', borderRadius: '6px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#374151' }}>
                {collectionResults.total_collected || 0}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Total Messages</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#fef2f2', borderRadius: '6px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc2626' }}>
                {collectionResults.high_risk_count || 0}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>High Risk</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#fefbf2', borderRadius: '6px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>
                {collectionResults.medium_risk_count || 0}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Medium Risk</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f0fdf4', borderRadius: '6px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#16a34a' }}>
                {collectionResults.low_risk_count || 0}
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Low Risk</div>
            </div>
          </div>

          {collectionResults.collection_summary && (
            <div style={{ marginTop: '20px' }}>
              <h4 style={{ color: '#374151', marginBottom: '10px' }}>Collection Summary:</h4>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
                gap: '8px' 
              }}>
                {Object.entries(collectionResults.collection_summary).map(([source, count]) => (
                  <div key={source} style={{
                    padding: '8px',
                    backgroundColor: count > 0 ? '#dbeafe' : '#fef2f2',
                    borderRadius: '4px',
                    textAlign: 'center',
                    fontSize: '12px'
                  }}>
                    <div style={{ fontWeight: 'bold' }}>@{source}</div>
                    <div style={{ color: count > 0 ? '#2563eb' : '#dc2626' }}>{count} messages</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {collectionResults.saved_files && (
            <div style={{ marginTop: '20px' }}>
              <h4 style={{ color: '#374151', marginBottom: '10px' }}>Saved Files:</h4>
              <ul style={{ color: '#6b7280', fontSize: '14px' }}>
                {collectionResults.saved_files.map((file, index) => (
                  <li key={index} style={{ marginBottom: '5px' }}>
                    {file}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Info Box */}
      <div style={{
        marginTop: '30px',
        padding: '20px',
        backgroundColor: '#eff6ff',
        borderRadius: '8px',
        border: '1px solid #bfdbfe'
      }}>
        <h4 style={{ color: '#1e40af', marginBottom: '10px' }}>Why Telegram?</h4>
        <ul style={{ color: '#1e3a8a', fontSize: '14px', margin: 0, paddingLeft: '20px' }}>
          <li>Free API access with no rate limiting charges</li>
          <li>Commonly used for encrypted communications</li>
          <li>Public channels provide rich data for research</li>
          <li>Full message history access for public channels</li>
          <li>Media detection (photos, videos, documents)</li>
          <li>Forward tracking to identify original sources</li>
        </ul>
      </div>
    </div>
  );
};

export default TelegramCollector;

