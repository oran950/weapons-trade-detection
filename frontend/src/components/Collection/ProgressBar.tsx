import React from 'react';

interface ProgressBarProps {
  current: number;
  total: number;
  label?: string;
  showPercentage?: boolean;
  color?: string;
  animated?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  label,
  showPercentage = true,
  color = '#00ffff',
  animated = true,
}) => {
  const percentage = total > 0 ? Math.min((current / total) * 100, 100) : 0;

  return (
    <div style={styles.container}>
      {label && (
        <div style={styles.header}>
          <span style={styles.label}>{label}</span>
          {showPercentage && (
            <span style={styles.percentage}>{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div style={styles.track}>
        <div
          style={{
            ...styles.fill,
            width: `${percentage}%`,
            background: `linear-gradient(90deg, ${color}, ${adjustColor(color, 30)})`,
            ...(animated ? styles.animated : {}),
          }}
        >
          {animated && <div style={styles.shimmer}></div>}
        </div>
      </div>
      <div style={styles.stats}>
        <span style={styles.statText}>
          {current} / {total} collected
        </span>
      </div>
    </div>
  );
};

// Helper function to adjust color brightness
function adjustColor(color: string, amount: number): string {
  // Simple hex color adjustment
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    const num = parseInt(hex, 16);
    const r = Math.min(255, ((num >> 16) & 0xff) + amount);
    const g = Math.min(255, ((num >> 8) & 0xff) + amount);
    const b = Math.min(255, (num & 0xff) + amount);
    return `rgb(${r}, ${g}, ${b})`;
  }
  return color;
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: '100%',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  label: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#888',
    letterSpacing: '1px',
    textTransform: 'uppercase' as const,
  },
  percentage: {
    fontSize: '14px',
    fontWeight: 700,
    color: '#00ffff',
    fontFamily: "'Orbitron', sans-serif",
  },
  track: {
    height: '8px',
    background: 'rgba(0,0,0,0.4)',
    borderRadius: '4px',
    overflow: 'hidden',
    position: 'relative' as const,
    border: '1px solid rgba(0,255,255,0.1)',
  },
  fill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
    position: 'relative' as const,
    overflow: 'hidden',
  },
  animated: {
    boxShadow: '0 0 10px rgba(0,255,255,0.5)',
  },
  shimmer: {
    position: 'absolute' as const,
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
    animation: 'shimmer 2s infinite',
  },
  stats: {
    marginTop: '6px',
    textAlign: 'right' as const,
  },
  statText: {
    fontSize: '11px',
    color: '#666',
  },
};

export default ProgressBar;

