import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import api from '../api';

interface ConfigStatus {
  reddit: {
    configured: boolean;
    clientId?: string;
    userAgent?: string;
  };
  telegram: {
    configured: boolean;
    apiId?: string;
  };
  ollama: {
    available: boolean;
    model?: string;
    baseUrl?: string;
  };
}

const SettingsPage: React.FC = () => {
  const { redditConfigured, telegramConfigured, ollamaAvailable } = useAppContext();
  const [activeTab, setActiveTab] = useState<'reddit' | 'telegram' | 'llm' | 'general'>('reddit');
  const [status, setStatus] = useState<ConfigStatus | null>(null);
  const [loading, setLoading] = useState(true);

  // Default subreddits state
  const [defaultSubreddits, setDefaultSubreddits] = useState<string>(
    'news, worldnews, technology, firearms, guns'
  );

  // Fetch config status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const redditStatus = await api.getRedditStatus();
        setStatus({
          reddit: {
            configured: redditStatus.is_configured,
            clientId: redditStatus.client_id_set ? '••••••••' : undefined,
            userAgent: redditStatus.user_agent,
          },
          telegram: {
            configured: telegramConfigured,
          },
          ollama: {
            available: ollamaAvailable,
            model: 'llama3.1:8b',
            baseUrl: 'http://localhost:11434',
          },
        });
      } catch (error) {
        console.error('Failed to fetch config status:', error);
      }
      setLoading(false);
    };

    fetchStatus();
  }, [telegramConfigured, ollamaAvailable]);

  const tabs = [
    { id: 'reddit', label: 'Reddit API', icon: '🔴' },
    { id: 'telegram', label: 'Telegram API', icon: '✈️' },
    { id: 'llm', label: 'LLM/Ollama', icon: '🧠' },
    { id: 'general', label: 'General', icon: '⚙️' },
  ];

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>⚙️ Settings</h1>
        <p style={styles.subtitle}>
          Configure API integrations and system preferences
        </p>
      </div>

      {/* Tab Navigation */}
      <div style={styles.tabs}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              ...styles.tab,
              ...(activeTab === tab.id ? styles.tabActive : {}),
            }}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={styles.content}>
        {/* Reddit Tab */}
        {activeTab === 'reddit' && (
          <div style={styles.tabContent}>
            <div style={styles.statusBanner}>
              <span style={{
                ...styles.statusDot,
                background: redditConfigured ? '#00ff88' : '#ff4444',
              }}></span>
              {redditConfigured 
                ? 'Reddit API is configured and ready'
                : 'Reddit API is not configured'}
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>Configuration Status</h3>
              <div style={styles.configGrid}>
                <div style={styles.configItem}>
                  <span style={styles.configLabel}>Client ID</span>
                  <span style={styles.configValue}>
                    {status?.reddit.clientId || 'Not set'}
                  </span>
                </div>
                <div style={styles.configItem}>
                  <span style={styles.configLabel}>User Agent</span>
                  <span style={styles.configValue}>
                    {status?.reddit.userAgent || 'Not set'}
                  </span>
                </div>
              </div>
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>How to Configure</h3>
              <div style={styles.instructions}>
                <p>1. Go to <a href="https://www.reddit.com/prefs/apps" target="_blank" rel="noopener noreferrer" style={styles.link}>Reddit App Preferences</a></p>
                <p>2. Create a new "script" type application</p>
                <p>3. Copy the Client ID and Client Secret</p>
                <p>4. Add the following to your <code style={styles.code}>backend/.env</code> file:</p>
                <pre style={styles.codeBlock}>
{`REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=WeaponsDetection/1.0`}
                </pre>
                <p>5. Restart the backend server</p>
              </div>
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>Default Subreddits</h3>
              <textarea
                value={defaultSubreddits}
                onChange={(e) => setDefaultSubreddits(e.target.value)}
                style={styles.textarea}
                rows={3}
                placeholder="news, worldnews, technology..."
              />
              <p style={styles.hint}>Comma-separated list of subreddits to monitor by default</p>
            </div>
          </div>
        )}

        {/* Telegram Tab */}
        {activeTab === 'telegram' && (
          <div style={styles.tabContent}>
            <div style={styles.statusBanner}>
              <span style={{
                ...styles.statusDot,
                background: telegramConfigured ? '#00ff88' : '#ff4444',
              }}></span>
              {telegramConfigured 
                ? 'Telegram API is configured'
                : 'Telegram API is not configured'}
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>How to Configure</h3>
              <div style={styles.instructions}>
                <p>1. Go to <a href="https://my.telegram.org/apps" target="_blank" rel="noopener noreferrer" style={styles.link}>Telegram API Development Tools</a></p>
                <p>2. Create a new application to get API ID and API Hash</p>
                <p>3. Add the following to your <code style={styles.code}>backend/.env</code> file:</p>
                <pre style={styles.codeBlock}>
{`TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_NAME=detector_session`}
                </pre>
                <p>4. Restart the backend server</p>
                <p>5. On first run, you'll need to authenticate with your phone number</p>
              </div>
            </div>

            <div style={styles.warningBox}>
              <span style={styles.warningIcon}>⚠️</span>
              <div>
                <strong>Note:</strong> Telegram collection requires careful use. Only monitor public channels and groups you have legitimate research access to.
              </div>
            </div>
          </div>
        )}

        {/* LLM Tab */}
        {activeTab === 'llm' && (
          <div style={styles.tabContent}>
            <div style={styles.statusBanner}>
              <span style={{
                ...styles.statusDot,
                background: ollamaAvailable ? '#00ff88' : '#ff4444',
              }}></span>
              {ollamaAvailable 
                ? 'Ollama LLM is connected'
                : 'Ollama LLM is not available'}
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>Current Configuration</h3>
              <div style={styles.configGrid}>
                <div style={styles.configItem}>
                  <span style={styles.configLabel}>Model</span>
                  <span style={styles.configValue}>
                    {status?.ollama.model || 'llama3.1:8b'}
                  </span>
                </div>
                <div style={styles.configItem}>
                  <span style={styles.configLabel}>Base URL</span>
                  <span style={styles.configValue}>
                    {status?.ollama.baseUrl || 'http://localhost:11434'}
                  </span>
                </div>
              </div>
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>How to Setup Ollama</h3>
              <div style={styles.instructions}>
                <p>1. Install Ollama from <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" style={styles.link}>ollama.ai</a></p>
                <p>2. Pull the recommended model:</p>
                <pre style={styles.codeBlock}>ollama pull llama3.1:8b</pre>
                <p>3. Ensure Ollama is running (it starts automatically)</p>
                <p>4. Optionally configure in <code style={styles.code}>backend/.env</code>:</p>
                <pre style={styles.codeBlock}>
{`OLLAMA_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b`}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* General Tab */}
        {activeTab === 'general' && (
          <div style={styles.tabContent}>
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>Risk Thresholds</h3>
              <div style={styles.thresholdGrid}>
                <div style={styles.thresholdItem}>
                  <label style={styles.thresholdLabel}>High Risk Threshold</label>
                  <div style={styles.thresholdControl}>
                    <input
                      type="range"
                      min="50"
                      max="100"
                      defaultValue="70"
                      style={styles.slider}
                    />
                    <span style={{ color: '#ff0080' }}>70%</span>
                  </div>
                </div>
                <div style={styles.thresholdItem}>
                  <label style={styles.thresholdLabel}>Medium Risk Threshold</label>
                  <div style={styles.thresholdControl}>
                    <input
                      type="range"
                      min="20"
                      max="70"
                      defaultValue="40"
                      style={styles.slider}
                    />
                    <span style={{ color: '#ffaa00' }}>40%</span>
                  </div>
                </div>
              </div>
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>Data Management</h3>
              <div style={styles.dataButtons}>
                <button style={styles.dataButton}>
                  📥 Export All Data
                </button>
                <button style={{ ...styles.dataButton, borderColor: '#ff4444', color: '#ff4444' }}>
                  🗑️ Clear Collection History
                </button>
              </div>
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>System Information</h3>
              <div style={styles.configGrid}>
                <div style={styles.configItem}>
                  <span style={styles.configLabel}>Version</span>
                  <span style={styles.configValue}>2.1.0</span>
                </div>
                <div style={styles.configItem}>
                  <span style={styles.configLabel}>Backend API</span>
                  <span style={styles.configValue}>http://localhost:9000</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '25px',
  },
  header: {
    marginBottom: '10px',
  },
  title: {
    margin: 0,
    fontSize: '28px',
    fontWeight: 700,
    color: '#00ffff',
  },
  subtitle: {
    margin: '5px 0 0 0',
    fontSize: '14px',
    color: '#888',
  },
  tabs: {
    display: 'flex',
    gap: '10px',
    borderBottom: '1px solid rgba(0,255,255,0.1)',
    paddingBottom: '15px',
  },
  tab: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 20px',
    background: 'transparent',
    border: '1px solid transparent',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#888',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  tabActive: {
    background: 'rgba(0,255,255,0.1)',
    borderColor: 'rgba(0,255,255,0.3)',
    color: '#00ffff',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '25px',
  },
  statusBanner: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '15px 20px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '10px',
    fontSize: '14px',
    color: '#fff',
  },
  statusDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
  },
  section: {
    padding: '25px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
  },
  sectionTitle: {
    margin: '0 0 20px 0',
    fontSize: '14px',
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
  },
  configGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '15px',
  },
  configItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  configLabel: {
    fontSize: '11px',
    color: '#666',
    letterSpacing: '1px',
  },
  configValue: {
    fontSize: '14px',
    color: '#fff',
    fontFamily: 'monospace',
  },
  instructions: {
    fontSize: '14px',
    color: '#aaa',
    lineHeight: 2,
  },
  link: {
    color: '#00ffff',
    textDecoration: 'none',
  },
  code: {
    padding: '2px 8px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '4px',
    fontFamily: 'monospace',
    color: '#ffaa00',
  },
  codeBlock: {
    padding: '15px',
    background: 'rgba(0,0,0,0.4)',
    borderRadius: '8px',
    fontFamily: 'monospace',
    fontSize: '12px',
    color: '#00ff88',
    overflow: 'auto',
    margin: '10px 0',
  },
  textarea: {
    width: '100%',
    padding: '15px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#fff',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  hint: {
    fontSize: '12px',
    color: '#666',
    marginTop: '8px',
  },
  warningBox: {
    display: 'flex',
    gap: '15px',
    padding: '20px',
    background: 'rgba(255,170,0,0.1)',
    border: '1px solid rgba(255,170,0,0.3)',
    borderRadius: '10px',
    fontSize: '13px',
    color: '#ffaa00',
  },
  warningIcon: {
    fontSize: '24px',
  },
  thresholdGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  thresholdItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  thresholdLabel: {
    fontSize: '13px',
    color: '#aaa',
  },
  thresholdControl: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
  },
  slider: {
    flex: 1,
    height: '4px',
    appearance: 'none',
    background: 'rgba(0,255,255,0.2)',
    borderRadius: '2px',
    cursor: 'pointer',
  },
  dataButtons: {
    display: 'flex',
    gap: '15px',
  },
  dataButton: {
    padding: '12px 24px',
    background: 'transparent',
    border: '1px solid rgba(0,255,255,0.3)',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#00ffff',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
};

export default SettingsPage;

