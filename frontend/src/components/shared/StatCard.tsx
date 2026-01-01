import React from 'react';
import { useNavigate } from 'react-router-dom';

interface StatCardProps {
  icon: string;
  label: string;
  value: string | number;
  color?: string;
  linkTo?: string;
  subLabel?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  label,
  value,
  color = '#00ffff',
  linkTo,
  subLabel,
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (linkTo) {
      navigate(linkTo);
    }
  };

  return (
    <div
      onClick={handleClick}
      style={{
        ...styles.card,
        cursor: linkTo ? 'pointer' : 'default',
        borderColor: `${color}33`,
      }}
      onMouseEnter={(e) => {
        if (linkTo) {
          e.currentTarget.style.borderColor = color;
          e.currentTarget.style.transform = 'translateY(-3px)';
          e.currentTarget.style.boxShadow = `0 10px 40px ${color}22`;
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = `${color}33`;
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={styles.iconContainer}>
        <span style={{ fontSize: '28px' }}>{icon}</span>
      </div>
      <div style={styles.content}>
        <div style={{ ...styles.label, color: color }}>{label}</div>
        <div style={styles.value}>{value}</div>
        {subLabel && <div style={styles.subLabel}>{subLabel}</div>}
      </div>
      {linkTo && (
        <div style={styles.arrow}>→</div>
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  card: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.5) 0%, rgba(0,20,40,0.3) 100%)',
    border: '1px solid',
    borderRadius: '12px',
    transition: 'all 0.3s ease',
    position: 'relative',
  },
  iconContainer: {
    width: '50px',
    height: '50px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '10px',
  },
  content: {
    flex: 1,
  },
  label: {
    fontSize: '11px',
    fontWeight: 600,
    letterSpacing: '2px',
    textTransform: 'uppercase',
    marginBottom: '5px',
  },
  value: {
    fontSize: '28px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#fff',
  },
  subLabel: {
    fontSize: '11px',
    color: '#666',
    marginTop: '3px',
  },
  arrow: {
    fontSize: '20px',
    color: '#666',
    transition: 'all 0.3s ease',
  },
};

export default StatCard;

