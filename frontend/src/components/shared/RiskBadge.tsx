import React from 'react';

interface RiskBadgeProps {
  level: 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE' | 'CRITICAL';
  score?: number;
  size?: 'small' | 'medium' | 'large';
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, size = 'medium' }) => {
  const getColor = () => {
    switch (level) {
      case 'CRITICAL': return '#ff0000';
      case 'HIGH': return '#ff0080';
      case 'MEDIUM': return '#ffaa00';
      case 'LOW': return '#00ff88';
      case 'NONE': return '#666666';
      default: return '#666666';
    }
  };

  const getSizes = () => {
    switch (size) {
      case 'small': return { padding: '3px 8px', fontSize: '10px' };
      case 'large': return { padding: '8px 16px', fontSize: '14px' };
      default: return { padding: '5px 12px', fontSize: '11px' };
    }
  };

  const color = getColor();
  const sizes = getSizes();

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      padding: sizes.padding,
      background: `${color}22`,
      border: `1px solid ${color}`,
      borderRadius: '4px',
      fontSize: sizes.fontSize,
      fontWeight: 700,
      color: color,
      letterSpacing: '1px',
      textTransform: 'uppercase',
    }}>
      {level} RISK
      {score !== undefined && (
        <span style={{
          fontFamily: "'Orbitron', sans-serif",
          fontWeight: 700,
        }}>
          {Math.round(score * 100)}%
        </span>
      )}
    </span>
  );
};

export default RiskBadge;

