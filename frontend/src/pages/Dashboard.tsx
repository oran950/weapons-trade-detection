import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { useCollection } from '../hooks/useCollection';
import StatCard from '../components/shared/StatCard';
import LiveStream from '../components/Detection/LiveStream';
import CollectButton from '../components/Collection/CollectButton';
import ProgressBar from '../components/Collection/ProgressBar';
import DetailModal from '../components/Detection/DetailModal';
import type { Post } from '../context/AppContext';

const Dashboard: React.FC = () => {
  const { stats, backendOnline, redditConfigured, telegramConfigured, ollamaAvailable } = useAppContext();
  const { isCollecting, startRedditCollection, startTelegramCollection, cancelCollection, summary, progress, phase, phaseMessage } = useCollection();
  const [showAnalyzeModal, setShowAnalyzeModal] = useState(false);
  const [analyzeText, setAnalyzeText] = useState('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!analyzeText.trim()) return;
    
    try {
      const response = await fetch('http://localhost:9000/api/detection/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: analyzeText }),
      });
      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  return (
    <div style={styles.container}>
      {/* Action Buttons */}
      <div style={styles.actions}>
        <CollectButton
          platform="reddit"
          onCollect={startRedditCollection}
          isCollecting={isCollecting}
          disabled={!redditConfigured}
        />
        <CollectButton
          platform="telegram"
          onCollect={startTelegramCollection}
          isCollecting={isCollecting}
          disabled={!telegramConfigured}
        />
        <button
          style={styles.analyzeButton}
          onClick={() => setShowAnalyzeModal(true)}
        >
          🔍 ANALYZE TEXT
        </button>
        {isCollecting && (
          <button style={styles.cancelButton} onClick={cancelCollection}>
            ✕ CANCEL
          </button>
        )}
      </div>

      {/* Stats Grid */}
      <div style={styles.statsGrid}>
        <StatCard
          icon="⚠️"
          label="Active Threats"
          value={stats.highRiskCount}
          color="#ff0080"
          linkTo="/threats"
        />
        <StatCard
          icon="📊"
          label="Posts Analyzed"
          value={stats.totalAnalyzed}
          color="#00ffff"
        />
        <StatCard
          icon="🌐"
          label="Platforms"
          value={stats.platformsMonitored}
          color="#00ff88"
        />
        <StatCard
          icon="🎯"
          label="Accuracy"
          value="94.7%"
          color="#ffaa00"
        />
      </div>

      {/* Main Content */}
      <div style={styles.mainContent}>
        {/* Live Stream */}
        <div style={styles.streamSection}>
          <LiveStream maxItems={30} />
        </div>

        {/* Side Panel */}
        <div style={styles.sidePanel}>
          {/* Collection Progress - Shows different phases */}
          {isCollecting && (
            <div style={{
              ...styles.progressCard,
              borderColor: phase === 'analyzing' ? '#00ffff' : '#ffaa00',
            }}>
              <h3 style={{
                ...styles.cardTitle,
                color: phase === 'analyzing' ? '#00ffff' : '#ffaa00',
              }}>
                {phase === 'collecting' && '📥 COLLECTING...'}
                {phase === 'analyzing' && '🧠 ANALYZING WITH AI...'}
                {phase === 'idle' && '⏳ STARTING...'}
              </h3>
              <div style={styles.phaseMessage}>{phaseMessage}</div>
              <ProgressBar
                current={progress.current}
                total={progress.total}
                label={phase === 'analyzing' ? 'Analyzing' : 'Collecting'}
                color={phase === 'analyzing' ? '#00ffff' : '#ffaa00'}
                animated
              />
            </div>
          )}

          {/* Collection Summary - Shows after collection completes */}
          {summary && !isCollecting && (
            <div style={styles.summaryCard}>
              <h3 style={styles.summaryTitle}>📊 COLLECTION COMPLETE</h3>
              <div style={styles.summaryStats}>
                <div style={styles.summaryRow}>
                  <span style={styles.summaryLabel}>Total Scanned:</span>
                  <span style={styles.summaryValue}>{summary.total_scanned || 0}</span>
                </div>
                <div style={styles.summaryDivider} />
                <div style={styles.summaryRow}>
                  <span style={{...styles.summaryLabel, color: '#ff0080'}}>🔴 HIGH RISK:</span>
                  <span style={{...styles.summaryValue, color: '#ff0080'}}>{summary.high_risk_count || 0}</span>
                </div>
                <div style={styles.summaryRow}>
                  <span style={{...styles.summaryLabel, color: '#ffaa00'}}>🟡 MEDIUM:</span>
                  <span style={{...styles.summaryValue, color: '#ffaa00'}}>{summary.medium_risk_count || 0}</span>
                </div>
                <div style={styles.summaryRow}>
                  <span style={{...styles.summaryLabel, color: '#00ff88'}}>🟢 LOW:</span>
                  <span style={{...styles.summaryValue, color: '#00ff88'}}>{summary.low_risk_count || 0}</span>
                </div>
                <div style={styles.summaryRow}>
                  <span style={{...styles.summaryLabel, color: '#666'}}>⚪ Filtered (0%):</span>
                  <span style={{...styles.summaryValue, color: '#666'}}>{summary.filtered_out || 0}</span>
                </div>
                <div style={styles.summaryDivider} />
                {summary.weapons_detected > 0 && (
                  <div style={styles.summaryRow}>
                    <span style={{...styles.summaryLabel, color: '#ff3366'}}>🔫 Weapons Found:</span>
                    <span style={{...styles.summaryValue, color: '#ff3366'}}>{summary.weapons_detected}</span>
                  </div>
                )}
                {summary.illegal_trade_detected > 0 && (
                  <div style={styles.summaryRow}>
                    <span style={{...styles.summaryLabel, color: '#ff0000'}}>🚨 Illegal Trade:</span>
                    <span style={{...styles.summaryValue, color: '#ff0000'}}>{summary.illegal_trade_detected}</span>
                  </div>
                )}
              </div>
              <div style={styles.summaryFooter}>
                Found <strong style={{color: '#ff0080'}}>{summary.high_risk_count || 0}</strong> high risk from <strong style={{color: '#00ffff'}}>{summary.total_scanned || 0}</strong> posts
              </div>
            </div>
          )}

          {/* Service Status */}
          <div style={styles.statusCard}>
            <h3 style={styles.cardTitle}>🔍 SERVICE STATUS</h3>
            <div style={styles.statusList}>
              <div style={styles.statusItem}>
                <span>Reddit Monitor</span>
                <span style={{
                  ...styles.statusValue,
                  color: redditConfigured ? '#00ff88' : '#666',
                }}>
                  {redditConfigured ? 'READY' : 'NOT SET'}
                </span>
              </div>
              <div style={styles.statusItem}>
                <span>Telegram Sweep</span>
                <span style={{
                  ...styles.statusValue,
                  color: telegramConfigured ? '#00ff88' : '#666',
                }}>
                  {telegramConfigured ? 'READY' : 'OFFLINE'}
                </span>
              </div>
              <div style={styles.statusItem}>
                <span>LLM Analysis</span>
                <span style={{
                  ...styles.statusValue,
                  color: ollamaAvailable ? '#00ff88' : '#666',
                }}>
                  {ollamaAvailable ? 'ACTIVE' : 'OFFLINE'}
                </span>
              </div>
            </div>
          </div>

          {/* Detection Breakdown */}
          <div style={styles.breakdownCard}>
            <h3 style={styles.cardTitle}>📈 DETECTION BREAKDOWN</h3>
            <div style={styles.breakdownList}>
              <div style={styles.breakdownItem}>
                <span style={{ color: '#ff0080' }}>High Risk</span>
                <span style={styles.breakdownValue}>{stats.highRiskCount}</span>
              </div>
              <div style={styles.breakdownItem}>
                <span style={{ color: '#ffaa00' }}>Medium Risk</span>
                <span style={styles.breakdownValue}>{stats.mediumRiskCount}</span>
              </div>
              <div style={styles.breakdownItem}>
                <span style={{ color: '#00ff88' }}>Low Risk</span>
                <span style={styles.breakdownValue}>{stats.lowRiskCount}</span>
              </div>
            </div>
          </div>

          {/* Summary Card (after collection) */}
          {summary && (
            <div style={styles.summaryCard}>
              <h3 style={styles.cardTitle}>✅ COLLECTION COMPLETE</h3>
              <div style={styles.summaryContent}>
                <div>Collected: {summary.total_collected} posts</div>
                <div>High Risk: {summary.high_risk_count}</div>
                <div>Medium Risk: {summary.medium_risk_count}</div>
                <div>Low Risk: {summary.low_risk_count}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Analyze Modal */}
      {showAnalyzeModal && (
        <div style={styles.modalOverlay} onClick={() => setShowAnalyzeModal(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>🔍 Analyze Text for Threats</h3>
            <textarea
              value={analyzeText}
              onChange={(e) => setAnalyzeText(e.target.value)}
              placeholder="Paste text content to analyze..."
              style={styles.textarea}
              rows={6}
            />
            <div style={styles.modalActions}>
              <button onClick={() => setShowAnalyzeModal(false)} style={styles.modalCancel}>
                Cancel
              </button>
              <button onClick={handleAnalyze} style={styles.modalSubmit}>
                Analyze
              </button>
            </div>
            {analysisResult && (
              <div style={styles.analysisResult}>
                <div style={styles.analysisHeader}>
                  <span style={{
                    color: analysisResult.risk_score >= 0.7 ? '#ff0080' :
                           analysisResult.risk_score >= 0.4 ? '#ffaa00' : '#00ff88'
                  }}>
                    Risk Score: {Math.round(analysisResult.risk_score * 100)}%
                  </span>
                </div>
                {analysisResult.flags?.length > 0 && (
                  <div style={styles.analysisFlags}>
                    {analysisResult.flags.map((flag: string, i: number) => (
                      <div key={i} style={styles.flag}>{flag}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  actions: {
    display: 'flex',
    gap: '15px',
    flexWrap: 'wrap',
  },
  analyzeButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '14px 24px',
    background: 'transparent',
    border: '1px solid rgba(0,255,255,0.3)',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 600,
    color: '#00ffff',
    letterSpacing: '1px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  cancelButton: {
    padding: '14px 24px',
    background: 'rgba(255,0,0,0.2)',
    border: '1px solid #ff4444',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 600,
    color: '#ff4444',
    cursor: 'pointer',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '15px',
  },
  mainContent: {
    display: 'grid',
    gridTemplateColumns: '1fr 320px',
    gap: '20px',
  },
  streamSection: {
    minHeight: '400px',
  },
  sidePanel: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  progressCard: {
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(255,170,0,0.1) 0%, rgba(255,170,0,0.05) 100%)',
    border: '1px solid rgba(255,170,0,0.3)',
    borderRadius: '12px',
    transition: 'all 0.3s ease',
  },
  phaseMessage: {
    fontSize: '12px',
    color: '#aaa',
    marginBottom: '12px',
    fontStyle: 'italic',
  },
  progressBar: {
    height: '6px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '3px',
    overflow: 'hidden',
    marginTop: '15px',
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #ffaa00, #ff6600)',
    borderRadius: '3px',
    transition: 'width 0.3s ease',
  },
  progressText: {
    fontSize: '12px',
    color: '#888',
    marginTop: '10px',
  },
  statusCard: {
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
  },
  cardTitle: {
    margin: '0 0 15px 0',
    fontSize: '12px',
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
  },
  statusList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  statusItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
    color: '#888',
  },
  statusValue: {
    fontSize: '11px',
    fontWeight: 700,
    letterSpacing: '1px',
  },
  breakdownCard: {
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
  },
  breakdownList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  breakdownItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
  },
  breakdownValue: {
    fontSize: '16px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#fff',
  },
  summaryCard: {
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(0,255,136,0.1) 0%, rgba(0,255,136,0.05) 100%)',
    border: '1px solid rgba(0,255,136,0.3)',
    borderRadius: '12px',
    marginBottom: '15px',
  },
  summaryTitle: {
    margin: '0 0 15px 0',
    fontSize: '12px',
    fontWeight: 700,
    color: '#00ff88',
    letterSpacing: '2px',
  },
  summaryStats: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
  },
  summaryRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
  },
  summaryLabel: {
    color: '#aaa',
  },
  summaryValue: {
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#fff',
  },
  summaryDivider: {
    height: '1px',
    background: 'rgba(0,255,136,0.2)',
    margin: '8px 0',
  },
  summaryFooter: {
    marginTop: '15px',
    padding: '10px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '8px',
    fontSize: '14px',
    textAlign: 'center' as const,
    color: '#aaa',
  },
  summaryContent: {
    fontSize: '13px',
    color: '#aaa',
    lineHeight: 1.8,
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.85)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    width: '100%',
    maxWidth: '500px',
    background: 'linear-gradient(135deg, #001a2e 0%, #000a14 100%)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '15px',
    padding: '30px',
  },
  modalTitle: {
    margin: '0 0 20px 0',
    fontSize: '18px',
    color: '#00ffff',
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
  modalActions: {
    display: 'flex',
    gap: '15px',
    marginTop: '20px',
  },
  modalCancel: {
    flex: 1,
    padding: '12px',
    background: 'transparent',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '8px',
    color: '#888',
    cursor: 'pointer',
  },
  modalSubmit: {
    flex: 1,
    padding: '12px',
    background: 'linear-gradient(90deg, #ff0080, #00ffff)',
    border: 'none',
    borderRadius: '8px',
    fontWeight: 700,
    color: '#000',
    cursor: 'pointer',
  },
  analysisResult: {
    marginTop: '20px',
    padding: '15px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '8px',
  },
  analysisHeader: {
    fontSize: '16px',
    fontWeight: 700,
    marginBottom: '10px',
  },
  analysisFlags: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  flag: {
    padding: '8px 12px',
    background: 'rgba(255,0,128,0.1)',
    borderLeft: '3px solid #ff0080',
    fontSize: '12px',
    color: '#ff8080',
  },
};

export default Dashboard;

