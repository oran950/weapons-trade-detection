import React, { useState, useEffect, CSSProperties } from 'react';
import api from '../api';
import type { LiveDataEntry, HighRiskPost, StatCard, SystemStats, HealthResponse } from '../types';

// Extended type for collected posts with full data
interface CollectedPost {
  id: string;
  title: string;
  content: string;
  subreddit: string;
  author_hash: string;
  score: number;
  num_comments: number;
  url: string;
  collected_at: string;
  risk_analysis?: {
    risk_score: number;
    confidence: number;
    flags: string[];
    detected_keywords: string[];
    detected_patterns: string[];
  };
}

interface CollectionResult {
  status: string;
  total_collected: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  subreddits_collected: string[];
  all_posts?: CollectedPost[];
  high_risk_posts?: CollectedPost[];
  saved_files?: string[];
}

const CinematicDashboard: React.FC = () => {
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
  const [activeThreats, setActiveThreats] = useState<number>(0);
  const [scanProgress, setScanProgress] = useState<number>(0);
  const [liveData, setLiveData] = useState<LiveDataEntry[]>([]);
  const [selectedPost, setSelectedPost] = useState<HighRiskPost | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats>({
    postsAnalyzed: 0,
    platformsMonitored: 4,
    activeScans: 0,
    accuracy: 94.7,
    highRiskCount: 0,
    mediumRiskCount: 0,
    lowRiskCount: 0
  });
  const [highRiskPosts, setHighRiskPosts] = useState<HighRiskPost[]>([]);
  const [backendStatus, setBackendStatus] = useState<HealthResponse | null>(null);
  const [isCollecting, setIsCollecting] = useState<boolean>(false);
  const [showAnalyzeModal, setShowAnalyzeModal] = useState<boolean>(false);
  const [analyzeText, setAnalyzeText] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  
  // New states for results view
  const [showResultsModal, setShowResultsModal] = useState<boolean>(false);
  const [lastCollectionResult, setLastCollectionResult] = useState<CollectionResult | null>(null);
  const [collectedPosts, setCollectedPosts] = useState<CollectedPost[]>([]);
  const [selectedCollectedPost, setSelectedCollectedPost] = useState<CollectedPost | null>(null);
  const [resultsFilter, setResultsFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await api.health();
        setBackendStatus(health);
      } catch {
        setBackendStatus(null);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Scan progress animation
  useEffect(() => {
    const interval = setInterval(() => {
      setScanProgress(prev => (prev >= 100 ? 0 : prev + 0.5));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Simulated live data stream (will be replaced with real WebSocket later)
  useEffect(() => {
    const interval = setInterval(() => {
      const types: Array<'HIGH RISK' | 'MEDIUM RISK' | 'MONITORING'> = ['HIGH RISK', 'MEDIUM RISK', 'MONITORING'];
      const locations = ['REDDIT', 'TELEGRAM', 'TWITTER', 'FORUM'];
      const threats = ['Weapons Trade', 'Explosives', 'Illegal Arms', 'Suspicious Activity', 'Ammunition Sale', 'Modified Weapons'];
      
      const newEntry: LiveDataEntry = {
        id: Date.now(),
        type: types[Math.floor(Math.random() * types.length)],
        location: locations[Math.floor(Math.random() * locations.length)],
        threat: threats[Math.floor(Math.random() * threats.length)],
        confidence: (Math.random() * 40 + 60).toFixed(1),
        timestamp: new Date()
      };
      
      setLiveData(prev => [newEntry, ...prev].slice(0, 15));
      
      if (newEntry.type === 'HIGH RISK') {
        setActiveThreats(prev => prev + 1);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Collect data from Reddit
  const handleCollectReddit = async () => {
    setIsCollecting(true);
    try {
      const result = await api.collectReddit(['news', 'worldnews', 'technology', 'firearms', 'guns'], 10);
      
      // Store the collection result
      setLastCollectionResult(result);
      
      // Store collected posts if available
      if (result.all_posts && Array.isArray(result.all_posts)) {
        setCollectedPosts(result.all_posts);
      }
      
      // Handle high risk posts from the response
      if (result.high_risk_count > 0) {
        // Add live feed entry for real detection
        const newEntry: LiveDataEntry = {
          id: Date.now(),
          type: 'HIGH RISK',
          location: 'REDDIT',
          threat: `${result.high_risk_count} high-risk posts detected - Click VIEW RESULTS`,
          confidence: '95.0',
          timestamp: new Date()
        };
        setLiveData(prev => [newEntry, ...prev].slice(0, 15));
      }
      
      // Update stats with actual counts
      setSystemStats(prev => ({
        ...prev,
        postsAnalyzed: prev.postsAnalyzed + (result.total_collected || 0),
        highRiskCount: prev.highRiskCount + (result.high_risk_count || 0),
        mediumRiskCount: prev.mediumRiskCount + (result.medium_risk_count || 0),
        lowRiskCount: prev.lowRiskCount + (result.low_risk_count || 0)
      }));
      setActiveThreats(prev => prev + (result.high_risk_count || 0));

      // Show success notification in live feed with clickable hint
      const successEntry: LiveDataEntry = {
        id: Date.now() + 1,
        type: 'MONITORING',
        location: 'REDDIT',
        threat: `✅ Collected ${result.total_collected} posts - Click VIEW RESULTS to see details`,
        confidence: '100.0',
        timestamp: new Date()
      };
      setLiveData(prev => [successEntry, ...prev].slice(0, 15));
      
    } catch (error: any) {
      console.error('Collection failed:', error);
      // Show error in live feed
      const errorEntry: LiveDataEntry = {
        id: Date.now(),
        type: 'MONITORING',
        location: 'REDDIT',
        threat: `Collection error: ${error.message || 'Unknown error'}`,
        confidence: '0.0',
        timestamp: new Date()
      };
      setLiveData(prev => [errorEntry, ...prev].slice(0, 15));
    }
    setIsCollecting(false);
  };

  // Get filtered posts based on risk level
  const getFilteredPosts = () => {
    if (!collectedPosts.length) return [];
    
    return collectedPosts.filter(post => {
      const riskScore = post.risk_analysis?.risk_score || 0;
      switch (resultsFilter) {
        case 'high': return riskScore >= 0.7;
        case 'medium': return riskScore >= 0.4 && riskScore < 0.7;
        case 'low': return riskScore < 0.4;
        default: return true;
      }
    }).sort((a, b) => (b.risk_analysis?.risk_score || 0) - (a.risk_analysis?.risk_score || 0));
  };

  // Get risk level color
  const getRiskLevelColor = (score: number): string => {
    if (score >= 0.7) return '#ff0080';
    if (score >= 0.4) return '#ffaa00';
    return '#00ff88';
  };

  // Get risk level label
  const getRiskLabel = (score: number): string => {
    if (score >= 0.7) return 'HIGH RISK';
    if (score >= 0.4) return 'MEDIUM RISK';
    return 'LOW RISK';
  };

  // Analyze custom text
  const handleAnalyze = async () => {
    if (!analyzeText.trim()) return;
    try {
      const result = await api.analyze(analyzeText);
      setAnalysisResult(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  const statCards: StatCard[] = [
    { label: 'ACTIVE THREATS', value: activeThreats, color: '#ff0080', icon: '⚠️' },
    { label: 'POSTS ANALYZED', value: systemStats.postsAnalyzed, color: '#00ffff', icon: '📊' },
    { label: 'PLATFORMS', value: systemStats.platformsMonitored, color: '#00ff88', icon: '🌐' },
    { label: 'ACCURACY', value: `${systemStats.accuracy}%`, color: '#ffaa00', icon: '🎯' }
  ];

  const activeScans = [
    { name: 'Reddit Monitor', active: backendStatus?.reddit_configured || false },
    { name: 'Telegram Sweep', active: backendStatus?.telegram_configured || false },
    { name: 'LLM Analysis', active: backendStatus?.ollama_available || false }
  ];

  const getRiskColor = (type: string): string => {
    switch (type) {
      case 'HIGH RISK': return '#ff0080';
      case 'MEDIUM RISK': return '#ffaa00';
      default: return '#00ffff';
    }
  };

  const getRiskBgColor = (type: string): string => {
    switch (type) {
      case 'HIGH RISK': return 'rgba(255, 0, 128, 0.1)';
      case 'MEDIUM RISK': return 'rgba(255, 170, 0, 0.1)';
      default: return 'rgba(0, 255, 255, 0.05)';
    }
  };

  const getRiskBorderColor = (type: string): string => {
    switch (type) {
      case 'HIGH RISK': return 'rgba(255, 0, 128, 0.3)';
      case 'MEDIUM RISK': return 'rgba(255, 170, 0, 0.3)';
      default: return 'rgba(0, 255, 255, 0.2)';
    }
  };

  // Styles
  const styles: { [key: string]: CSSProperties } = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%)',
      color: '#fff',
      fontFamily: '"Rajdhani", "Orbitron", system-ui, sans-serif',
      overflow: 'hidden',
      position: 'relative'
    },
    gridBackground: {
      position: 'absolute',
      inset: 0,
      backgroundImage: `
        linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px)
      `,
      backgroundSize: '50px 50px',
      animation: 'gridMove 20s linear infinite',
      pointerEvents: 'none'
    },
    glowOrb1: {
      position: 'absolute',
      top: '10%',
      right: '15%',
      width: '400px',
      height: '400px',
      background: 'radial-gradient(circle, rgba(0, 255, 255, 0.15) 0%, transparent 70%)',
      filter: 'blur(60px)',
      animation: 'float 8s ease-in-out infinite',
      pointerEvents: 'none'
    },
    glowOrb2: {
      position: 'absolute',
      bottom: '20%',
      left: '10%',
      width: '300px',
      height: '300px',
      background: 'radial-gradient(circle, rgba(255, 0, 128, 0.1) 0%, transparent 70%)',
      filter: 'blur(50px)',
      animation: 'float 10s ease-in-out infinite reverse',
      pointerEvents: 'none'
    },
    header: {
      padding: '20px 40px',
      borderBottom: '1px solid rgba(0, 255, 255, 0.2)',
      backdropFilter: 'blur(10px)',
      background: 'rgba(10, 14, 39, 0.8)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'relative',
      zIndex: 10
    },
    logo: {
      width: '50px',
      height: '50px',
      background: 'linear-gradient(135deg, #00ffff 0%, #ff0080 100%)',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '24px',
      boxShadow: '0 0 30px rgba(0, 255, 255, 0.5)',
      animation: 'pulse 2s ease-in-out infinite'
    },
    mainTitle: {
      margin: 0,
      fontSize: '28px',
      fontWeight: 700,
      letterSpacing: '3px',
      background: 'linear-gradient(90deg, #00ffff, #ff0080)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
      textTransform: 'uppercase' as const
    },
    subtitle: {
      margin: 0,
      fontSize: '11px',
      color: '#00ffff',
      letterSpacing: '2px',
      opacity: 0.7
    },
    statusBadge: {
      padding: '6px 16px',
      borderRadius: '20px',
      fontSize: '12px',
      fontWeight: 600,
      letterSpacing: '1px',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    },
    content: {
      padding: '30px 40px',
      position: 'relative',
      zIndex: 1
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '20px',
      marginBottom: '30px'
    },
    mainGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 400px',
      gap: '20px',
      marginBottom: '30px'
    },
    card: {
      background: 'rgba(255, 255, 255, 0.03)',
      backdropFilter: 'blur(10px)',
      borderRadius: '12px',
      padding: '25px',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    sectionTitle: {
      margin: '0 0 20px 0',
      fontSize: '18px',
      fontWeight: 700,
      letterSpacing: '2px',
      textTransform: 'uppercase' as const
    },
    progressBar: {
      width: '100%',
      height: '8px',
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '4px',
      overflow: 'hidden',
      marginBottom: '15px'
    },
    progressFill: {
      height: '100%',
      background: 'linear-gradient(90deg, #ff0080, #00ffff)',
      borderRadius: '4px',
      transition: 'width 0.1s linear',
      boxShadow: '0 0 10px rgba(255, 0, 128, 0.5)'
    },
    pulsingDot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      background: '#00ff88',
      boxShadow: '0 0 10px #00ff88',
      animation: 'pulse 1s ease-in-out infinite'
    },
    inactiveDot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      background: '#666',
      boxShadow: 'none'
    },
    modal: {
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.9)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      animation: 'fadeIn 0.3s ease-out'
    },
    modalContent: {
      background: 'linear-gradient(135deg, rgba(26, 31, 58, 0.95), rgba(15, 20, 25, 0.95))',
      border: '1px solid rgba(255, 0, 128, 0.5)',
      borderRadius: '15px',
      padding: '40px',
      maxWidth: '700px',
      width: '90%',
      maxHeight: '80vh',
      overflow: 'auto',
      boxShadow: '0 20px 60px rgba(255, 0, 128, 0.3)',
      animation: 'scaleIn 0.3s ease-out'
    },
    button: {
      background: 'linear-gradient(90deg, #ff0080, #00ffff)',
      border: 'none',
      padding: '12px 30px',
      borderRadius: '8px',
      color: '#fff',
      fontSize: '14px',
      fontWeight: 700,
      letterSpacing: '1px',
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    secondaryButton: {
      background: 'transparent',
      border: '1px solid rgba(0, 255, 255, 0.5)',
      padding: '12px 30px',
      borderRadius: '8px',
      color: '#00ffff',
      fontSize: '14px',
      fontWeight: 700,
      letterSpacing: '1px',
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    textarea: {
      width: '100%',
      minHeight: '150px',
      background: 'rgba(0, 0, 0, 0.3)',
      border: '1px solid rgba(0, 255, 255, 0.3)',
      borderRadius: '8px',
      padding: '15px',
      color: '#fff',
      fontSize: '14px',
      fontFamily: 'inherit',
      resize: 'vertical',
      marginBottom: '20px'
    }
  };

  return (
    <div style={styles.container}>
      {/* Animated background grid */}
      <div style={styles.gridBackground} />

      {/* Glowing orbs */}
      <div style={styles.glowOrb1} />
      <div style={styles.glowOrb2} />

      {/* Header */}
      <header style={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={styles.logo}>🎯</div>
          <div>
            <h1 style={styles.mainTitle}>TACTICAL DETECTION GRID</h1>
            <p style={styles.subtitle}>WEAPONS TRADE DETECTION SYSTEM • ACADEMIC RESEARCH</p>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
          <div 
            style={{
              ...styles.statusBadge,
              background: backendStatus ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 0, 128, 0.2)',
              border: `1px solid ${backendStatus ? '#00ff88' : '#ff0080'}`,
              color: backendStatus ? '#00ff88' : '#ff0080'
            }}
          >
            <div style={backendStatus ? styles.pulsingDot : styles.inactiveDot} />
            {backendStatus ? 'SYSTEM ONLINE' : 'OFFLINE'}
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '24px', fontWeight: 700, color: '#00ffff', letterSpacing: '1px' }}>
              {currentTime.toLocaleTimeString()}
            </div>
            <div style={{ fontSize: '11px', color: '#888', letterSpacing: '1px' }}>
              {currentTime.toLocaleDateString()}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={styles.content}>
        
        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '15px', marginBottom: '25px' }}>
          <button 
            style={{
              ...styles.button,
              opacity: isCollecting ? 0.6 : 1
            }}
            onClick={handleCollectReddit}
            disabled={isCollecting}
          >
            {isCollecting ? '⏳ COLLECTING...' : '🔴 COLLECT FROM REDDIT'}
          </button>
          <button 
            style={styles.secondaryButton}
            onClick={() => setShowAnalyzeModal(true)}
          >
            🔍 ANALYZE TEXT
          </button>
          {collectedPosts.length > 0 && (
            <button 
              style={{
                ...styles.button,
                background: 'linear-gradient(90deg, #00ff88, #00ffff)'
              }}
              onClick={() => setShowResultsModal(true)}
            >
              📊 VIEW RESULTS ({collectedPosts.length})
            </button>
          )}
        </div>

        {/* Top Stats Grid */}
        <div style={styles.statsGrid}>
          {statCards.map((stat, idx) => (
            <div 
              key={idx} 
              style={{
                ...styles.card,
                border: `1px solid ${stat.color}33`,
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                const target = e.currentTarget as HTMLDivElement;
                target.style.transform = 'translateY(-5px)';
                target.style.borderColor = stat.color;
                target.style.boxShadow = `0 10px 30px ${stat.color}40`;
              }}
              onMouseLeave={(e) => {
                const target = e.currentTarget as HTMLDivElement;
                target.style.transform = 'translateY(0)';
                target.style.borderColor = `${stat.color}33`;
                target.style.boxShadow = 'none';
              }}
            >
              <div style={{
                position: 'absolute',
                top: 0,
                right: 0,
                fontSize: '60px',
                opacity: 0.05,
                transform: 'rotate(15deg)'
              }}>
                {stat.icon}
              </div>
              <div style={{
                fontSize: '13px',
                color: stat.color,
                letterSpacing: '2px',
                marginBottom: '10px',
                fontWeight: 600
              }}>
                {stat.label}
              </div>
              <div style={{
                fontSize: '36px',
                fontWeight: 700,
                color: '#fff',
                letterSpacing: '1px'
              }}>
                {stat.value}
              </div>
            </div>
          ))}
        </div>

        {/* Main Grid */}
        <div style={styles.mainGrid}>
          
          {/* Live Feed */}
          <div style={{
            ...styles.card,
            border: '1px solid rgba(0, 255, 255, 0.2)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h2 style={{
                ...styles.sectionTitle,
                color: '#00ffff'
              }}>
                <span style={{ marginRight: '10px' }}>📡</span>
                LIVE DETECTION STREAM
              </h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={styles.pulsingDot} />
                <span style={{ fontSize: '12px', color: '#00ff88', letterSpacing: '1px' }}>ACTIVE</span>
              </div>
            </div>

            <div style={{ maxHeight: '400px', overflowY: 'auto', overflowX: 'hidden' }}>
              {liveData.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                  Waiting for detections...
                </div>
              ) : (
                liveData.map((item, idx) => (
                  <div 
                    key={item.id} 
                    style={{
                      background: getRiskBgColor(item.type),
                      border: `1px solid ${getRiskBorderColor(item.type)}`,
                      borderRadius: '8px',
                      padding: '15px',
                      marginBottom: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      const target = e.currentTarget as HTMLDivElement;
                      target.style.transform = 'translateX(5px)';
                      target.style.boxShadow = `0 5px 20px ${getRiskBorderColor(item.type)}`;
                    }}
                    onMouseLeave={(e) => {
                      const target = e.currentTarget as HTMLDivElement;
                      target.style.transform = 'translateX(0)';
                      target.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{
                        fontSize: '11px',
                        color: getRiskColor(item.type),
                        fontWeight: 700,
                        letterSpacing: '1px'
                      }}>
                        {item.type}
                      </span>
                      <span style={{ fontSize: '11px', color: '#888' }}>{item.location}</span>
                    </div>
                    <div style={{ fontSize: '14px', color: '#fff', marginBottom: '5px' }}>
                      {item.threat}
                    </div>
                    <div style={{ fontSize: '11px', color: '#888' }}>
                      Confidence: <span style={{ color: '#00ffff' }}>{item.confidence}%</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* System Status */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* Scan Progress */}
            <div style={{
              ...styles.card,
              border: '1px solid rgba(255, 0, 128, 0.2)'
            }}>
              <h3 style={{
                ...styles.sectionTitle,
                fontSize: '16px',
                color: '#ff0080'
              }}>
                ⚡ SCAN PROGRESS
              </h3>
              <div style={styles.progressBar}>
                <div style={{
                  ...styles.progressFill,
                  width: `${scanProgress}%`
                }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                <span style={{ color: '#888' }}>Continuous scanning...</span>
                <span style={{ color: '#00ffff', fontWeight: 700 }}>{Math.round(scanProgress)}%</span>
              </div>
            </div>

            {/* Active Scans */}
            <div style={{
              ...styles.card,
              border: '1px solid rgba(0, 255, 136, 0.2)'
            }}>
              <h3 style={{
                ...styles.sectionTitle,
                fontSize: '16px',
                color: '#00ff88'
              }}>
                🔍 SERVICE STATUS
              </h3>
              {activeScans.map((scan, idx) => (
                <div 
                  key={idx} 
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '15px',
                    paddingBottom: '15px',
                    borderBottom: idx < activeScans.length - 1 ? '1px solid rgba(255, 255, 255, 0.05)' : 'none'
                  }}
                >
                  <span style={{ fontSize: '13px', color: '#fff' }}>{scan.name}</span>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{ 
                      fontSize: '11px', 
                      color: scan.active ? '#00ff88' : '#666' 
                    }}>
                      {scan.active ? 'READY' : 'OFFLINE'}
                    </span>
                    <div style={scan.active ? styles.pulsingDot : styles.inactiveDot} />
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Stats */}
            <div style={{
              ...styles.card,
              border: '1px solid rgba(255, 170, 0, 0.2)'
            }}>
              <h3 style={{
                ...styles.sectionTitle,
                fontSize: '16px',
                color: '#ffaa00'
              }}>
                📈 DETECTION BREAKDOWN
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#ff0080' }}>High Risk</span>
                  <span style={{ fontWeight: 700 }}>{systemStats.highRiskCount}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#ffaa00' }}>Medium Risk</span>
                  <span style={{ fontWeight: 700 }}>{systemStats.mediumRiskCount}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#00ff88' }}>Low Risk</span>
                  <span style={{ fontWeight: 700 }}>{systemStats.lowRiskCount}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* High Risk Posts */}
        {highRiskPosts.length > 0 && (
          <div style={{
            ...styles.card,
            border: '1px solid rgba(255, 0, 128, 0.2)'
          }}>
            <h2 style={{
              ...styles.sectionTitle,
              color: '#ff0080'
            }}>
              <span style={{ marginRight: '10px' }}>🎯</span>
              HIGH PRIORITY DETECTIONS
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
              {highRiskPosts.slice(0, 6).map((post, idx) => (
                <div 
                  key={post.id} 
                  style={{
                    background: 'rgba(255, 0, 128, 0.05)',
                    border: '1px solid rgba(255, 0, 128, 0.3)',
                    borderRadius: '10px',
                    padding: '20px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => setSelectedPost(post)}
                  onMouseEnter={(e) => {
                    const target = e.currentTarget as HTMLDivElement;
                    target.style.transform = 'translateY(-5px)';
                    target.style.boxShadow = '0 10px 30px rgba(255, 0, 128, 0.3)';
                    target.style.borderColor = '#ff0080';
                  }}
                  onMouseLeave={(e) => {
                    const target = e.currentTarget as HTMLDivElement;
                    target.style.transform = 'translateY(0)';
                    target.style.boxShadow = 'none';
                    target.style.borderColor = 'rgba(255, 0, 128, 0.3)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{
                      fontSize: '12px',
                      color: '#ff0080',
                      fontWeight: 700,
                      letterSpacing: '1px'
                    }}>
                      {post.subreddit}
                    </span>
                    <span style={{ fontSize: '11px', color: '#888' }}>{post.time}</span>
                  </div>
                  <h3 style={{
                    margin: '0 0 15px 0',
                    fontSize: '16px',
                    color: '#fff',
                    fontWeight: 600,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {post.title}
                  </h3>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {post.keywords.slice(0, 3).map((kw, i) => (
                        <span 
                          key={i} 
                          style={{
                            fontSize: '10px',
                            padding: '4px 8px',
                            background: 'rgba(0, 255, 255, 0.1)',
                            border: '1px solid rgba(0, 255, 255, 0.3)',
                            borderRadius: '4px',
                            color: '#00ffff',
                            letterSpacing: '1px'
                          }}
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                    <div style={{
                      fontSize: '20px',
                      fontWeight: 700,
                      color: '#ff0080'
                    }}>
                      {post.risk}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Post Detail Modal */}
      {selectedPost && (
        <div 
          style={styles.modal} 
          onClick={() => setSelectedPost(null)}
        >
          <div 
            style={styles.modalContent} 
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
              <span style={{ color: '#ff0080', fontWeight: 700 }}>{selectedPost.subreddit}</span>
              <span style={{ color: '#888' }}>{selectedPost.time}</span>
            </div>
            <h2 style={{
              margin: '0 0 20px 0',
              fontSize: '24px',
              color: '#fff'
            }}>
              {selectedPost.title}
            </h2>
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '20px',
              maxHeight: '200px',
              overflow: 'auto',
              fontSize: '14px',
              lineHeight: '1.6',
              color: '#ccc'
            }}>
              {selectedPost.content || 'No content available'}
            </div>
            <div style={{
              fontSize: '48px',
              fontWeight: 700,
              color: '#ff0080',
              marginBottom: '20px',
              textAlign: 'center'
            }}>
              Risk Score: {selectedPost.risk}%
            </div>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '30px' }}>
              {selectedPost.keywords.map((kw, i) => (
                <span 
                  key={i} 
                  style={{
                    fontSize: '12px',
                    padding: '6px 12px',
                    background: 'rgba(0, 255, 255, 0.1)',
                    border: '1px solid rgba(0, 255, 255, 0.3)',
                    borderRadius: '4px',
                    color: '#00ffff'
                  }}
                >
                  {kw}
                </span>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              {selectedPost.url && (
                <a 
                  href={selectedPost.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    ...styles.secondaryButton,
                    textDecoration: 'none'
                  }}
                >
                  VIEW SOURCE
                </a>
              )}
              <button 
                style={styles.button}
                onClick={() => setSelectedPost(null)}
              >
                CLOSE
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analyze Modal */}
      {showAnalyzeModal && (
        <div 
          style={styles.modal} 
          onClick={() => {
            setShowAnalyzeModal(false);
            setAnalysisResult(null);
            setAnalyzeText('');
          }}
        >
          <div 
            style={styles.modalContent} 
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{
              margin: '0 0 20px 0',
              fontSize: '24px',
              color: '#00ffff'
            }}>
              🔍 ANALYZE TEXT
            </h2>
            <textarea
              style={styles.textarea as React.CSSProperties}
              placeholder="Enter text to analyze for weapons trade indicators..."
              value={analyzeText}
              onChange={(e) => setAnalyzeText(e.target.value)}
            />
            
            {analysisResult && (
              <div style={{
                background: 'rgba(255, 0, 128, 0.1)',
                border: '1px solid rgba(255, 0, 128, 0.3)',
                borderRadius: '8px',
                padding: '20px',
                marginBottom: '20px'
              }}>
                <div style={{ 
                  fontSize: '32px', 
                  fontWeight: 700, 
                  color: analysisResult.risk_score >= 0.7 ? '#ff0080' : analysisResult.risk_score >= 0.4 ? '#ffaa00' : '#00ff88',
                  marginBottom: '15px',
                  textAlign: 'center'
                }}>
                  Risk Score: {Math.round(analysisResult.risk_score * 100)}%
                </div>
                {analysisResult.flags && analysisResult.flags.length > 0 && (
                  <div>
                    <div style={{ fontSize: '12px', color: '#888', marginBottom: '10px' }}>DETECTED FLAGS:</div>
                    {analysisResult.flags.map((flag: string, i: number) => (
                      <div key={i} style={{ 
                        fontSize: '13px', 
                        color: '#ff0080', 
                        marginBottom: '5px',
                        paddingLeft: '10px',
                        borderLeft: '2px solid #ff0080'
                      }}>
                        {flag}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button 
                style={styles.button}
                onClick={handleAnalyze}
              >
                ANALYZE
              </button>
              <button 
                style={styles.secondaryButton}
                onClick={() => {
                  setShowAnalyzeModal(false);
                  setAnalysisResult(null);
                  setAnalyzeText('');
                }}
              >
                CLOSE
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Modal */}
      {showResultsModal && (
        <div 
          style={styles.modal} 
          onClick={() => {
            setShowResultsModal(false);
            setSelectedCollectedPost(null);
          }}
        >
          <div 
            style={{
              ...styles.modalContent,
              maxWidth: '1000px',
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column'
            }} 
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '20px',
              paddingBottom: '15px',
              borderBottom: '1px solid rgba(0, 255, 255, 0.2)'
            }}>
              <h2 style={{
                margin: 0,
                fontSize: '24px',
                color: '#00ffff'
              }}>
                📊 COLLECTION RESULTS
              </h2>
              <div style={{ display: 'flex', gap: '10px' }}>
                {lastCollectionResult && (
                  <span style={{ color: '#888', fontSize: '14px' }}>
                    {lastCollectionResult.total_collected} posts from {lastCollectionResult.subreddits_collected?.length || 0} subreddits
                  </span>
                )}
              </div>
            </div>

            {/* Filter Buttons */}
            <div style={{ 
              display: 'flex', 
              gap: '10px', 
              marginBottom: '20px',
              flexWrap: 'wrap'
            }}>
              <button 
                style={{
                  ...styles.secondaryButton,
                  padding: '8px 16px',
                  fontSize: '12px',
                  background: resultsFilter === 'all' ? 'rgba(0, 255, 255, 0.2)' : 'transparent'
                }}
                onClick={() => setResultsFilter('all')}
              >
                ALL ({collectedPosts.length})
              </button>
              <button 
                style={{
                  ...styles.secondaryButton,
                  padding: '8px 16px',
                  fontSize: '12px',
                  borderColor: '#ff0080',
                  color: '#ff0080',
                  background: resultsFilter === 'high' ? 'rgba(255, 0, 128, 0.2)' : 'transparent'
                }}
                onClick={() => setResultsFilter('high')}
              >
                HIGH RISK ({collectedPosts.filter(p => (p.risk_analysis?.risk_score || 0) >= 0.7).length})
              </button>
              <button 
                style={{
                  ...styles.secondaryButton,
                  padding: '8px 16px',
                  fontSize: '12px',
                  borderColor: '#ffaa00',
                  color: '#ffaa00',
                  background: resultsFilter === 'medium' ? 'rgba(255, 170, 0, 0.2)' : 'transparent'
                }}
                onClick={() => setResultsFilter('medium')}
              >
                MEDIUM ({collectedPosts.filter(p => {
                  const s = p.risk_analysis?.risk_score || 0;
                  return s >= 0.4 && s < 0.7;
                }).length})
              </button>
              <button 
                style={{
                  ...styles.secondaryButton,
                  padding: '8px 16px',
                  fontSize: '12px',
                  borderColor: '#00ff88',
                  color: '#00ff88',
                  background: resultsFilter === 'low' ? 'rgba(0, 255, 136, 0.2)' : 'transparent'
                }}
                onClick={() => setResultsFilter('low')}
              >
                LOW RISK ({collectedPosts.filter(p => (p.risk_analysis?.risk_score || 0) < 0.4).length})
              </button>
            </div>

            {/* Results List */}
            <div style={{ 
              flex: 1, 
              overflowY: 'auto',
              display: 'grid',
              gridTemplateColumns: selectedCollectedPost ? '1fr 1fr' : '1fr',
              gap: '20px'
            }}>
              {/* Posts List */}
              <div style={{ overflowY: 'auto', maxHeight: '60vh' }}>
                {getFilteredPosts().map((post, idx) => (
                  <div 
                    key={post.id || idx}
                    style={{
                      background: selectedCollectedPost?.id === post.id 
                        ? 'rgba(0, 255, 255, 0.15)' 
                        : 'rgba(255, 255, 255, 0.03)',
                      border: `1px solid ${getRiskLevelColor(post.risk_analysis?.risk_score || 0)}33`,
                      borderRadius: '8px',
                      padding: '15px',
                      marginBottom: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onClick={() => setSelectedCollectedPost(post)}
                    onMouseEnter={(e) => {
                      const target = e.currentTarget as HTMLDivElement;
                      target.style.borderColor = getRiskLevelColor(post.risk_analysis?.risk_score || 0);
                      target.style.transform = 'translateX(5px)';
                    }}
                    onMouseLeave={(e) => {
                      const target = e.currentTarget as HTMLDivElement;
                      target.style.borderColor = `${getRiskLevelColor(post.risk_analysis?.risk_score || 0)}33`;
                      target.style.transform = 'translateX(0)';
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      marginBottom: '8px'
                    }}>
                      <span style={{
                        fontSize: '11px',
                        color: getRiskLevelColor(post.risk_analysis?.risk_score || 0),
                        fontWeight: 700,
                        letterSpacing: '1px'
                      }}>
                        {getRiskLabel(post.risk_analysis?.risk_score || 0)}
                      </span>
                      <span style={{ 
                        fontSize: '20px', 
                        fontWeight: 700, 
                        color: getRiskLevelColor(post.risk_analysis?.risk_score || 0) 
                      }}>
                        {Math.round((post.risk_analysis?.risk_score || 0) * 100)}%
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#00ffff', marginBottom: '5px' }}>
                      r/{post.subreddit}
                    </div>
                    <div style={{ 
                      fontSize: '14px', 
                      color: '#fff',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {post.title}
                    </div>
                  </div>
                ))}
                {getFilteredPosts().length === 0 && (
                  <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
                    No posts match this filter
                  </div>
                )}
              </div>

              {/* Post Detail Panel */}
              {selectedCollectedPost && (
                <div style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  borderRadius: '10px',
                  padding: '20px',
                  overflowY: 'auto',
                  maxHeight: '60vh'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    marginBottom: '15px'
                  }}>
                    <span style={{ 
                      color: getRiskLevelColor(selectedCollectedPost.risk_analysis?.risk_score || 0),
                      fontWeight: 700,
                      fontSize: '14px'
                    }}>
                      {getRiskLabel(selectedCollectedPost.risk_analysis?.risk_score || 0)}
                    </span>
                    <span style={{
                      fontSize: '28px',
                      fontWeight: 700,
                      color: getRiskLevelColor(selectedCollectedPost.risk_analysis?.risk_score || 0)
                    }}>
                      {Math.round((selectedCollectedPost.risk_analysis?.risk_score || 0) * 100)}%
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '12px', color: '#00ffff', marginBottom: '10px' }}>
                    r/{selectedCollectedPost.subreddit} • Score: {selectedCollectedPost.score} • {selectedCollectedPost.num_comments} comments
                  </div>
                  
                  <h3 style={{ 
                    margin: '0 0 15px 0',
                    fontSize: '18px',
                    color: '#fff',
                    lineHeight: 1.4
                  }}>
                    {selectedCollectedPost.title}
                  </h3>
                  
                  <div style={{
                    background: 'rgba(0, 0, 0, 0.3)',
                    borderRadius: '8px',
                    padding: '15px',
                    marginBottom: '15px',
                    maxHeight: '150px',
                    overflowY: 'auto',
                    fontSize: '13px',
                    lineHeight: 1.6,
                    color: '#ccc'
                  }}>
                    {selectedCollectedPost.content || 'No content available'}
                  </div>

                  {/* Detected Flags */}
                  {selectedCollectedPost.risk_analysis?.flags && selectedCollectedPost.risk_analysis.flags.length > 0 && (
                    <div style={{ marginBottom: '15px' }}>
                      <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>
                        DETECTED FLAGS:
                      </div>
                      {selectedCollectedPost.risk_analysis.flags.slice(0, 5).map((flag, i) => (
                        <div key={i} style={{
                          fontSize: '12px',
                          color: '#ff0080',
                          marginBottom: '4px',
                          paddingLeft: '10px',
                          borderLeft: '2px solid #ff0080'
                        }}>
                          {flag}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Keywords */}
                  {selectedCollectedPost.risk_analysis?.detected_keywords && selectedCollectedPost.risk_analysis.detected_keywords.length > 0 && (
                    <div style={{ 
                      display: 'flex', 
                      flexWrap: 'wrap', 
                      gap: '6px',
                      marginBottom: '15px'
                    }}>
                      {selectedCollectedPost.risk_analysis.detected_keywords.map((kw, i) => (
                        <span key={i} style={{
                          fontSize: '10px',
                          padding: '4px 8px',
                          background: 'rgba(0, 255, 255, 0.1)',
                          border: '1px solid rgba(0, 255, 255, 0.3)',
                          borderRadius: '4px',
                          color: '#00ffff'
                        }}>
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Action Button */}
                  <a 
                    href={selectedCollectedPost.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      ...styles.button,
                      display: 'block',
                      textAlign: 'center',
                      textDecoration: 'none',
                      marginTop: '10px'
                    }}
                  >
                    🔗 VIEW ON REDDIT
                  </a>
                </div>
              )}
            </div>

            {/* Close Button */}
            <div style={{ 
              marginTop: '20px', 
              paddingTop: '15px', 
              borderTop: '1px solid rgba(0, 255, 255, 0.2)',
              display: 'flex',
              justifyContent: 'center'
            }}>
              <button 
                style={styles.secondaryButton}
                onClick={() => {
                  setShowResultsModal(false);
                  setSelectedCollectedPost(null);
                }}
              >
                CLOSE
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Orbitron:wght@700&display=swap');
        
        * {
          box-sizing: border-box;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        @keyframes gridMove {
          0% { transform: translateY(0); }
          100% { transform: translateY(50px); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(5deg); }
        }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        ::-webkit-scrollbar {
          width: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: rgba(0, 255, 255, 0.3);
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 255, 255, 0.5);
        }
      `}</style>
    </div>
  );
};

export default CinematicDashboard;

