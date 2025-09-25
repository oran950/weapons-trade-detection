import React, { useState, useEffect } from 'react';

const RedditCollector = () => {
  const [isCollecting, setIsCollecting] = useState(false);
  const [collectionResults, setCollectionResults] = useState(null);
  const [configStatus, setConfigStatus] = useState(null);

  const [collectionParams, setCollectionParams] = useState({
    subreddits: ['news', 'worldnews', 'politics'],
    timeFilter: 'day',
    sortMethod: 'hot',
    limit_per_subreddit: 15,
    keywords: '',
    include_all_defaults: false
  });

  const defaultSubreddits = [
    'news', 'worldnews', 'politics', 'PublicFreakout', 'Conservative', 
    'liberal', 'conspiracy', 'AskReddit', 'technology', 'science',
    'todayilearned', 'explainlikeimfive', 'changemyview', 'unpopularopinion',
    'legaladvice', 'relationship_advice', 'amitheasshole', 'offmychest'
  ];

  const availableSubreddits = [
    'news', 'worldnews', 'politics', 'PublicFreakout', 'Conservative', 
    'liberal', 'conspiracy', 'technology', 'science', 'AskReddit',
    'todayilearned', 'explainlikeimfive', 'changemyview', 'unpopularopinion',
    'legaladvice', 'relationship_advice', 'amitheasshole', 'offmychest',
    'funny', 'pics', 'gaming', 'movies', 'books', 'music', 'sports'
  ];

  const handleSubredditToggle = (subreddit) => {
    const currentSubs = collectionParams.subreddits;
    if (currentSubs.includes(subreddit)) {
      setCollectionParams({
        ...collectionParams, 
        subreddits: currentSubs.filter(s => s !== subreddit)
      });
    } else {
      setCollectionParams({
        ...collectionParams, 
        subreddits: [...currentSubs, subreddit]
      });
    }
  };

  // Check Reddit configuration status on component load
  useEffect(() => {
    checkConfigStatus();
  }, []);

  const checkConfigStatus = async () => {
    try {
      const response = await fetch('http://localhost:9000/api/reddit/config-status');
      const status = await response.json();
      setConfigStatus(status);
    } catch (error) {
      console.error('Failed to check config status:', error);
    }
  };

  const handleCollection = async () => {
    if (!configStatus?.is_configured) {
      alert('Reddit API is not configured. Please check your backend .env file.');
      return;
    }

    setIsCollecting(true);
    try {
      const response = await fetch('http://localhost:9000/api/reddit/collect', {
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
        Reddit Data Collection
      </h2>
      
      <div style={{ 
        backgroundColor: '#fef3c7', 
        border: '1px solid #f59e0b', 
        borderRadius: '8px', 
        padding: '20px', 
        marginBottom: '30px' 
      }}>
        <h3 style={{ color: '#92400e', marginBottom: '10px' }}>Academic Research Only</h3>
        <p style={{ color: '#92400e', marginBottom: '10px' }}>
          This tool is designed for legitimate academic research with proper authorization.
        </p>
        <p style={{ color: '#92400e', fontSize: '14px' }}>
          <strong>Requirements:</strong> Reddit API credentials, academic approval, compliance with Terms of Service
        </p>
      </div>

      {/* Configuration Status */}
      <div style={{
        backgroundColor: configStatus?.is_configured ? '#d1fae5' : '#fee2e2',
        border: `1px solid ${configStatus?.is_configured ? '#10b981' : '#ef4444'}`,
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '25px'
      }}>
        <h3 style={{ 
          color: configStatus?.is_configured ? '#065f46' : '#991b1b', 
          marginBottom: '10px' 
        }}>
          {configStatus?.is_configured ? '✅ Reddit API Configured' : '❌ Reddit API Not Configured'}
        </h3>
        
        {configStatus?.is_configured ? (
          <div>
            <p style={{ color: '#065f46', marginBottom: '10px' }}>
              Your Reddit API credentials are properly configured in the backend.
            </p>
            <div style={{ fontSize: '14px', color: '#047857' }}>
              <div><strong>User Agent:</strong> {configStatus.user_agent}</div>
              <div><strong>Rate Limit:</strong> {configStatus.rate_limit_delay}s between requests</div>
              <div><strong>Max Posts:</strong> {configStatus.max_posts_per_request} per request</div>
            </div>
          </div>
        ) : (
          <div>
            <p style={{ color: '#991b1b', marginBottom: '10px' }}>
              Please configure your Reddit API credentials in the backend .env file.
            </p>
            {configStatus?.missing_config && (
              <div style={{ fontSize: '14px', color: '#7f1d1d' }}>
                <strong>Missing:</strong> {configStatus.missing_config.join(', ')}
              </div>
            )}
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
        
        {/* Quick Options */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
            <input 
              type="checkbox"
              checked={collectionParams.include_all_defaults}
              onChange={(e) => setCollectionParams({
                ...collectionParams, 
                include_all_defaults: e.target.checked,
                subreddits: e.target.checked ? defaultSubreddits : ['news', 'worldnews', 'politics']
              })}
            />
            <strong>Collect from all default subreddits ({defaultSubreddits.length} total)</strong>
          </label>
          <p style={{ fontSize: '12px', color: '#6b7280', marginLeft: '24px' }}>
            Comprehensive collection from: news, worldnews, politics, PublicFreakout, Conservative, liberal, conspiracy, technology, science, AskReddit, and more...
          </p>
        </div>

        {!collectionParams.include_all_defaults && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#374151', marginBottom: '15px' }}>Select Subreddits ({collectionParams.subreddits.length} selected):</h4>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', 
              gap: '8px',
              maxHeight: '200px',
              overflowY: 'auto',
              padding: '10px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px'
            }}>
              {availableSubreddits.map(subreddit => (
                <label key={subreddit} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '6px',
                  fontSize: '14px',
                  cursor: 'pointer',
                  padding: '4px'
                }}>
                  <input 
                    type="checkbox"
                    checked={collectionParams.subreddits.includes(subreddit)}
                    onChange={() => handleSubredditToggle(subreddit)}
                  />
                  r/{subreddit}
                </label>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Time Filter:
            </label>
            <select 
              value={collectionParams.timeFilter}
              onChange={(e) => setCollectionParams({...collectionParams, timeFilter: e.target.value})}
              style={{ 
                width: '100%', 
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '6px'
              }}
            >
              <option value="hour">Past Hour</option>
              <option value="day">Past Day</option>
              <option value="week">Past Week</option>
              <option value="month">Past Month</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Sort Method:
            </label>
            <select 
              value={collectionParams.sortMethod}
              onChange={(e) => setCollectionParams({...collectionParams, sortMethod: e.target.value})}
              style={{ 
                width: '100%', 
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '6px'
              }}
            >
              <option value="hot">Hot</option>
              <option value="top">Top</option>
              <option value="new">New</option>
              <option value="rising">Rising</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
              Posts per Subreddit:
            </label>
            <input 
              type="number"
              min="1"
              max="50"
              value={collectionParams.limit_per_subreddit}
              onChange={(e) => setCollectionParams({...collectionParams, limit_per_subreddit: parseInt(e.target.value)})}
              style={{ 
                width: '100%', 
                padding: '8px 12px', 
                border: '1px solid #d1d5db', 
                borderRadius: '6px'
              }}
            />
            <p style={{ fontSize: '11px', color: '#6b7280', marginTop: '2px' }}>
              Total posts: ~{collectionParams.include_all_defaults ? defaultSubreddits.length * collectionParams.limit_per_subreddit : collectionParams.subreddits.length * collectionParams.limit_per_subreddit}
            </p>
          </div>
        </div>

        <div style={{ marginTop: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#374151' }}>
            Search Keywords (optional):
          </label>
          <input 
            type="text"
            placeholder="violence, weapons, trade, etc. (comma-separated)"
            value={collectionParams.keywords}
            onChange={(e) => setCollectionParams({...collectionParams, keywords: e.target.value})}
            style={{ 
              width: '100%', 
              padding: '8px 12px', 
              border: '1px solid #d1d5db', 
              borderRadius: '6px'
            }}
          />
        </div>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <button 
          onClick={handleCollection}
          disabled={isCollecting}
          style={{
            padding: '12px 24px',
            backgroundColor: isCollecting ? '#6b7280' : '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: isCollecting ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {isCollecting ? 'Collecting & Analyzing...' : 'Start Collection & Analysis'}
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
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Total Posts</div>
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
              <h4 style={{ color: '#374151', marginBottom: '10px' }}>Collection Summary by Subreddit:</h4>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
                gap: '8px' 
              }}>
                {Object.entries(collectionResults.collection_summary).map(([subreddit, count]) => (
                  <div key={subreddit} style={{
                    padding: '8px',
                    backgroundColor: count > 0 ? '#f0fdf4' : '#fef2f2',
                    borderRadius: '4px',
                    textAlign: 'center',
                    fontSize: '12px'
                  }}>
                    <div style={{ fontWeight: 'bold' }}>r/{subreddit}</div>
                    <div style={{ color: count > 0 ? '#16a34a' : '#dc2626' }}>{count} posts</div>
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

      <div style={{
        backgroundColor: '#f3f4f6',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '30px'
      }}>
        <h4 style={{ color: '#374151', marginBottom: '15px' }}>Backend Configuration Setup:</h4>
        <ol style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.6' }}>
          <li>Create a <code>.env</code> file in your backend directory</li>
          <li>Add your Reddit API credentials:
            <pre style={{ 
              backgroundColor: '#1f2937', 
              color: '#f9fafb', 
              padding: '10px', 
              borderRadius: '4px', 
              marginTop: '5px',
              fontSize: '12px'
            }}>
{`REDDIT_CLIENT_ID=dxeHoWo9T02rNkonwS7Ddw
REDDIT_CLIENT_SECRET=LNK6RbRmgf1szuzurp9Ek7c5hq45ow
REDDIT_USER_AGENT=academic_research:weapons_detection:v2.0 (by /u/Rich_Professor6715)`}
            </pre>
          </li>
          <li>Install required packages: <code>pip install praw python-dotenv</code></li>
          <li>Restart your backend server</li>
          <li>Click "Refresh Status" above to verify configuration</li>
        </ol>
        <p style={{ color: '#6b7280', fontSize: '12px', marginTop: '15px' }}>
          <strong>Note:</strong> Never commit your .env file to version control. Add it to .gitignore.
        </p>
      </div>
    </div>
  );
};

export default RedditCollector;