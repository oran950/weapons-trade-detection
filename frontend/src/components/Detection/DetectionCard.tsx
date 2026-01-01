import React from 'react';
import { Post } from '../../context/AppContext';
import RiskBadge from '../shared/RiskBadge';

interface DetectionCardProps {
  post: Post;
  onClick?: () => void;
  compact?: boolean;
}

const DetectionCard: React.FC<DetectionCardProps> = ({ post, onClick, compact = false }) => {
  const riskLevel = post.risk_analysis?.risk_level || 'LOW';
  const riskScore = post.risk_analysis?.risk_score || 0;
  const isIllegalTrade = post.llm_analysis?.is_potentially_illegal;
  const llmSummary = post.llm_analysis?.summary;

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now.getTime() - then.getTime()) / 1000);
    
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  const getBorderColor = () => {
    if (isIllegalTrade) return '#ff0000';  // Red for illegal trade
    switch (riskLevel) {
      case 'HIGH': return '#ff0080';
      case 'MEDIUM': return '#ffaa00';
      case 'LOW': return '#00ff88';
    }
  };

  if (compact) {
    return (
      <div
        onClick={onClick}
        style={{
          ...styles.compactCard,
          borderLeftColor: getBorderColor(),
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(0,255,255,0.08)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
        }}
      >
        <div style={styles.compactHeader}>
          {isIllegalTrade ? (
            <span style={styles.illegalBadge}>🚨 ILLEGAL</span>
          ) : (
            <RiskBadge level={riskLevel} size="small" />
          )}
          <span style={styles.platform}>
            {post.platform === 'reddit' ? `r/${post.subreddit}` : post.channel}
          </span>
        </div>
        <div style={styles.compactTitle}>{post.title}</div>
        {llmSummary && (
          <div style={styles.llmSummary}>{llmSummary.slice(0, 80)}...</div>
        )}
        <div style={styles.compactMeta}>
          {getTimeAgo(post.collected_at)} • 
          Score: {Math.round(riskScore * 100)}%
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={onClick}
      style={{
        ...styles.card,
        borderColor: `${getBorderColor()}33`,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = getBorderColor();
        e.currentTarget.style.transform = 'translateX(5px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = `${getBorderColor()}33`;
        e.currentTarget.style.transform = 'translateX(0)';
      }}
    >
      <div style={styles.header}>
        <RiskBadge level={riskLevel} score={riskScore} />
        <span style={styles.platform}>
          {post.platform === 'reddit' ? 'REDDIT' : 'TELEGRAM'}
        </span>
      </div>

      <div style={styles.source}>
        {post.platform === 'reddit' ? `r/${post.subreddit}` : post.channel}
      </div>

      <h3 style={styles.title}>{post.title}</h3>

      {post.content && (
        <p style={styles.content}>
          {post.content.length > 150 
            ? `${post.content.substring(0, 150)}...` 
            : post.content}
        </p>
      )}

      <div style={styles.footer}>
        <span style={styles.time}>{getTimeAgo(post.collected_at)}</span>
        {post.score !== undefined && (
          <span style={styles.meta}>
            ↑ {post.score} • 💬 {post.num_comments}
          </span>
        )}
      </div>

      {post.risk_analysis?.detected_keywords && post.risk_analysis.detected_keywords.length > 0 && (
        <div style={styles.keywords}>
          {post.risk_analysis.detected_keywords.slice(0, 4).map((kw, i) => (
            <span key={i} style={styles.keyword}>{kw}</span>
          ))}
        </div>
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  card: {
    padding: '18px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  compactCard: {
    padding: '12px 15px',
    background: 'rgba(255,255,255,0.02)',
    borderLeft: '3px solid',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    marginBottom: '2px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
  },
  compactHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '5px',
  },
  platform: {
    fontSize: '10px',
    color: '#888',
    letterSpacing: '1px',
    textTransform: 'uppercase',
  },
  source: {
    fontSize: '12px',
    color: '#00ffff',
    marginBottom: '8px',
  },
  title: {
    margin: '0 0 10px 0',
    fontSize: '15px',
    fontWeight: 600,
    color: '#fff',
    lineHeight: 1.4,
  },
  compactTitle: {
    fontSize: '13px',
    color: '#fff',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    marginBottom: '5px',
  },
  content: {
    margin: '0 0 12px 0',
    fontSize: '13px',
    color: '#aaa',
    lineHeight: 1.5,
  },
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  time: {
    fontSize: '11px',
    color: '#666',
  },
  compactMeta: {
    fontSize: '10px',
    color: '#666',
  },
  illegalBadge: {
    padding: '3px 8px',
    background: 'linear-gradient(90deg, #ff0000 0%, #cc0000 100%)',
    borderRadius: '4px',
    fontSize: '10px',
    fontWeight: 700,
    color: '#fff',
    letterSpacing: '0.5px',
    animation: 'pulse 2s infinite',
  },
  llmSummary: {
    fontSize: '11px',
    color: '#888',
    fontStyle: 'italic',
    marginBottom: '5px',
    lineHeight: 1.3,
  },
  meta: {
    fontSize: '11px',
    color: '#888',
  },
  keywords: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '5px',
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid rgba(0,255,255,0.1)',
  },
  keyword: {
    padding: '3px 8px',
    background: 'rgba(0,255,255,0.1)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '4px',
    fontSize: '10px',
    color: '#00ffff',
  },
};

export default DetectionCard;

