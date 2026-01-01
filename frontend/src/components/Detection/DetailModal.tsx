import React from 'react';
import { Post } from '../../context/AppContext';
import RiskBadge from '../shared/RiskBadge';

interface DetailModalProps {
  post: Post;
  onClose: () => void;
}

const DetailModal: React.FC<DetailModalProps> = ({ post, onClose }) => {
  const riskLevel = post.risk_analysis?.risk_level || 'LOW';
  const riskScore = post.risk_analysis?.risk_score || 0;

  const getRiskColor = () => {
    switch (riskLevel) {
      case 'HIGH': return '#ff0080';
      case 'MEDIUM': return '#ffaa00';
      case 'LOW': return '#00ff88';
    }
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.headerLeft}>
            <RiskBadge level={riskLevel} score={riskScore} size="large" />
            <span style={styles.platform}>
              {post.platform === 'reddit' ? 'REDDIT' : 'TELEGRAM'}
            </span>
          </div>
          <button style={styles.closeButton} onClick={onClose}>✕</button>
        </div>

        {/* Risk Score Display */}
        <div style={styles.riskDisplay}>
          <div style={styles.riskCircle}>
            <svg width="120" height="120" viewBox="0 0 120 120">
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="8"
              />
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke={getRiskColor()}
                strokeWidth="8"
                strokeDasharray={`${riskScore * 314} 314`}
                strokeLinecap="round"
                transform="rotate(-90 60 60)"
                style={{ filter: `drop-shadow(0 0 10px ${getRiskColor()})` }}
              />
            </svg>
            <div style={styles.riskValue}>
              <span style={{ ...styles.riskNumber, color: getRiskColor() }}>
                {Math.round(riskScore * 100)}
              </span>
              <span style={styles.riskPercent}>%</span>
            </div>
          </div>
          <div style={styles.riskLabel}>RISK SCORE</div>
        </div>

        {/* Source */}
        <div style={styles.source}>
          {post.platform === 'reddit' ? `r/${post.subreddit}` : post.channel}
          {post.score !== undefined && (
            <span style={styles.sourceMeta}>
              • ↑ {post.score} • 💬 {post.num_comments}
            </span>
          )}
        </div>

        {/* Title */}
        <h2 style={styles.title}>{post.title}</h2>

        {/* LLM Analysis - Illegal Trade Detection */}
        {post.llm_analysis && (
          <div style={{
            ...styles.llmSection,
            borderColor: post.llm_analysis.is_potentially_illegal ? '#ff0000' : '#00ffff',
            background: post.llm_analysis.is_potentially_illegal 
              ? 'rgba(255,0,0,0.1)' 
              : 'rgba(0,255,255,0.05)',
          }}>
            <div style={styles.llmHeader}>
              <span style={styles.llmIcon}>
                {post.llm_analysis.is_potentially_illegal ? '🚨' : '🧠'}
              </span>
              <span style={{
                ...styles.llmTitle,
                color: post.llm_analysis.is_potentially_illegal ? '#ff0000' : '#00ffff',
              }}>
                {post.llm_analysis.is_potentially_illegal 
                  ? 'POTENTIALLY ILLEGAL WEAPON TRADE DETECTED' 
                  : 'LLM ANALYSIS'}
              </span>
            </div>
            
            <div style={styles.llmSummary}>{post.llm_analysis.summary}</div>
            
            {post.llm_analysis.is_potentially_illegal && post.llm_analysis.illegality_reason && (
              <div style={styles.illegalReason}>
                <strong>⚠️ Reason:</strong> {post.llm_analysis.illegality_reason}
              </div>
            )}
            
            <div style={styles.llmDetails}>
              <div style={styles.llmDetail}>
                <span style={styles.llmLabel}>Weapon Related:</span>
                <span style={{color: post.llm_analysis.is_weapon_related ? '#ff0080' : '#00ff88'}}>
                  {post.llm_analysis.is_weapon_related ? 'YES' : 'NO'}
                </span>
              </div>
              <div style={styles.llmDetail}>
                <span style={styles.llmLabel}>Trade Related:</span>
                <span style={{color: post.llm_analysis.is_trade_related ? '#ffaa00' : '#00ff88'}}>
                  {post.llm_analysis.is_trade_related ? 'YES' : 'NO'}
                </span>
              </div>
              <div style={styles.llmDetail}>
                <span style={styles.llmLabel}>Risk Assessment:</span>
                <span style={{
                  color: post.llm_analysis.risk_assessment === 'CRITICAL' ? '#ff0000' :
                         post.llm_analysis.risk_assessment === 'HIGH' ? '#ff0080' :
                         post.llm_analysis.risk_assessment === 'MEDIUM' ? '#ffaa00' : '#00ff88'
                }}>
                  {post.llm_analysis.risk_assessment}
                </span>
              </div>
              <div style={styles.llmDetail}>
                <span style={styles.llmLabel}>Recommendation:</span>
                <span style={{
                  color: post.llm_analysis.recommendation === 'INVESTIGATE' ? '#ff0000' :
                         post.llm_analysis.recommendation === 'FLAG' ? '#ffaa00' : '#888'
                }}>
                  {post.llm_analysis.recommendation}
                </span>
              </div>
              <div style={styles.llmDetail}>
                <span style={styles.llmLabel}>LLM Confidence:</span>
                <span>{Math.round(post.llm_analysis.confidence * 100)}%</span>
              </div>
            </div>
            
            {post.llm_analysis.weapon_types_mentioned.length > 0 && (
              <div style={styles.llmTags}>
                <span style={styles.llmLabel}>Weapons:</span>
                {post.llm_analysis.weapon_types_mentioned.map((w, i) => (
                  <span key={i} style={styles.weaponTag}>{w}</span>
                ))}
              </div>
            )}
            
            {post.llm_analysis.trade_indicators.length > 0 && (
              <div style={styles.llmTags}>
                <span style={styles.llmLabel}>Trade Indicators:</span>
                {post.llm_analysis.trade_indicators.map((t, i) => (
                  <span key={i} style={styles.tradeTag}>{t}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Content */}
        {post.content && (
          <div style={styles.contentSection}>
            <div style={styles.sectionLabel}>CONTENT</div>
            <div style={styles.content}>{post.content}</div>
          </div>
        )}

        {/* Detected Flags */}
        {post.risk_analysis?.flags && post.risk_analysis.flags.length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionLabel}>DETECTED FLAGS</div>
            <div style={styles.flagsList}>
              {post.risk_analysis.flags.map((flag, i) => (
                <div key={i} style={styles.flag}>
                  <span style={styles.flagIcon}>⚠️</span>
                  {flag}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Keywords */}
        {post.risk_analysis?.detected_keywords && post.risk_analysis.detected_keywords.length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionLabel}>DETECTED KEYWORDS</div>
            <div style={styles.keywords}>
              {post.risk_analysis.detected_keywords.map((kw, i) => (
                <span key={i} style={styles.keyword}>{kw}</span>
              ))}
            </div>
          </div>
        )}

        {/* Patterns */}
        {post.risk_analysis?.detected_patterns && post.risk_analysis.detected_patterns.length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionLabel}>DETECTED PATTERNS</div>
            <div style={styles.patterns}>
              {post.risk_analysis.detected_patterns.map((pattern, i) => (
                <span key={i} style={styles.pattern}>{pattern}</span>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div style={styles.actions}>
          {post.url && (
            <a
              href={post.url}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.primaryButton}
            >
              🔗 VIEW ORIGINAL SOURCE
            </a>
          )}
          <button style={styles.secondaryButton} onClick={onClose}>
            CLOSE
          </button>
        </div>

        {/* Metadata */}
        <div style={styles.metadata}>
          <div>ID: {post.id}</div>
          <div>Collected: {new Date(post.collected_at).toLocaleString()}</div>
          <div>Confidence: {Math.round((post.risk_analysis?.confidence || 0) * 100)}%</div>
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.85)',
    backdropFilter: 'blur(5px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '20px',
  },
  modal: {
    width: '100%',
    maxWidth: '700px',
    maxHeight: '90vh',
    overflow: 'auto',
    background: 'linear-gradient(135deg, #001a2e 0%, #000a14 100%)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '15px',
    padding: '30px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '25px',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
  },
  platform: {
    fontSize: '12px',
    color: '#888',
    letterSpacing: '2px',
  },
  closeButton: {
    width: '40px',
    height: '40px',
    background: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '50%',
    color: '#888',
    fontSize: '18px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  riskDisplay: {
    textAlign: 'center' as const,
    marginBottom: '25px',
  },
  riskCircle: {
    position: 'relative' as const,
    display: 'inline-block',
  },
  riskValue: {
    position: 'absolute' as const,
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    display: 'flex',
    alignItems: 'baseline',
  },
  riskNumber: {
    fontSize: '36px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
  },
  riskPercent: {
    fontSize: '18px',
    color: '#888',
    marginLeft: '2px',
  },
  riskLabel: {
    fontSize: '11px',
    color: '#666',
    letterSpacing: '3px',
    marginTop: '10px',
  },
  source: {
    fontSize: '14px',
    color: '#00ffff',
    marginBottom: '15px',
  },
  sourceMeta: {
    color: '#666',
    marginLeft: '10px',
  },
  title: {
    margin: '0 0 20px 0',
    fontSize: '20px',
    fontWeight: 600,
    color: '#fff',
    lineHeight: 1.4,
  },
  contentSection: {
    marginBottom: '20px',
  },
  sectionLabel: {
    fontSize: '10px',
    color: '#666',
    letterSpacing: '2px',
    marginBottom: '10px',
  },
  content: {
    padding: '15px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#ccc',
    lineHeight: 1.6,
    maxHeight: '200px',
    overflow: 'auto',
  },
  section: {
    marginBottom: '20px',
  },
  flagsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
  },
  flag: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 15px',
    background: 'rgba(255,0,128,0.1)',
    borderLeft: '3px solid #ff0080',
    fontSize: '13px',
    color: '#ff8080',
  },
  flagIcon: {
    fontSize: '14px',
  },
  keywords: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '8px',
  },
  keyword: {
    padding: '6px 12px',
    background: 'rgba(0,255,255,0.1)',
    border: '1px solid rgba(0,255,255,0.3)',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#00ffff',
  },
  patterns: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '8px',
  },
  pattern: {
    padding: '6px 12px',
    background: 'rgba(255,170,0,0.1)',
    border: '1px solid rgba(255,170,0,0.3)',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#ffaa00',
  },
  actions: {
    display: 'flex',
    gap: '15px',
    marginTop: '25px',
    paddingTop: '25px',
    borderTop: '1px solid rgba(0,255,255,0.1)',
  },
  primaryButton: {
    flex: 1,
    padding: '14px 24px',
    background: 'linear-gradient(90deg, #ff0080, #00ffff)',
    border: 'none',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 700,
    color: '#000',
    textDecoration: 'none',
    textAlign: 'center' as const,
    letterSpacing: '1px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  secondaryButton: {
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
  metadata: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '20px',
    paddingTop: '15px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
    fontSize: '10px',
    color: '#444',
    letterSpacing: '1px',
  },
  // LLM Analysis styles
  llmSection: {
    padding: '20px',
    border: '2px solid',
    borderRadius: '12px',
    marginBottom: '20px',
  },
  llmHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '15px',
  },
  llmIcon: {
    fontSize: '24px',
  },
  llmTitle: {
    fontSize: '14px',
    fontWeight: 700,
    letterSpacing: '1px',
  },
  llmSummary: {
    fontSize: '14px',
    color: '#ccc',
    lineHeight: 1.5,
    marginBottom: '15px',
    fontStyle: 'italic',
  },
  illegalReason: {
    padding: '12px',
    background: 'rgba(255,0,0,0.15)',
    border: '1px solid rgba(255,0,0,0.3)',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#ff6666',
    marginBottom: '15px',
  },
  llmDetails: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px',
    marginBottom: '15px',
  },
  llmDetail: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '3px',
  },
  llmLabel: {
    fontSize: '10px',
    color: '#666',
    letterSpacing: '1px',
    textTransform: 'uppercase' as const,
  },
  llmTags: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    alignItems: 'center',
    gap: '8px',
    marginTop: '10px',
  },
  weaponTag: {
    padding: '4px 10px',
    background: 'rgba(255,0,128,0.15)',
    border: '1px solid rgba(255,0,128,0.3)',
    borderRadius: '4px',
    fontSize: '11px',
    color: '#ff0080',
  },
  tradeTag: {
    padding: '4px 10px',
    background: 'rgba(255,170,0,0.15)',
    border: '1px solid rgba(255,170,0,0.3)',
    borderRadius: '4px',
    fontSize: '11px',
    color: '#ffaa00',
  },
};

export default DetailModal;

