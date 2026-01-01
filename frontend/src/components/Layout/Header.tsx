import React, { useState, useEffect } from 'react';
import { useAppContext } from '../../context/AppContext';

const Header: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { backendOnline, isCollecting } = useAppContext();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header style={styles.header}>
      <div style={styles.leftSection}>
        <div style={styles.logo}>🎯</div>
        <div style={styles.titleContainer}>
          <h1 style={styles.title}>
            <span style={styles.titleAccent}>TACTICAL</span> DETECTION GRID
          </h1>
          <p style={styles.subtitle}>WEAPONS TRADE DETECTION SYSTEM • ACADEMIC RESEARCH</p>
        </div>
      </div>

      <div style={styles.rightSection}>
        {isCollecting && (
          <div style={styles.collectingIndicator}>
            <span style={styles.pulse}></span>
            COLLECTING...
          </div>
        )}
        <div style={{
          ...styles.statusBadge,
          background: backendOnline 
            ? 'linear-gradient(90deg, rgba(0,255,136,0.2), rgba(0,255,255,0.1))'
            : 'linear-gradient(90deg, rgba(255,0,0,0.2), rgba(255,100,100,0.1))',
          borderColor: backendOnline ? '#00ff88' : '#ff4444',
        }}>
          <span style={{
            ...styles.statusDot,
            background: backendOnline ? '#00ff88' : '#ff4444',
            boxShadow: backendOnline 
              ? '0 0 10px #00ff88'
              : '0 0 10px #ff4444',
          }}></span>
          {backendOnline ? 'SYSTEM ONLINE' : 'OFFLINE'}
        </div>
        <div style={styles.timeContainer}>
          <div style={styles.time}>{currentTime.toLocaleTimeString()}</div>
          <div style={styles.date}>{currentTime.toLocaleDateString()}</div>
        </div>
      </div>
    </header>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px 30px',
    background: 'linear-gradient(180deg, rgba(0,20,40,0.95) 0%, rgba(0,10,25,0.9) 100%)',
    borderBottom: '1px solid rgba(0,255,255,0.15)',
    backdropFilter: 'blur(10px)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  leftSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
  },
  logo: {
    fontSize: '32px',
    filter: 'drop-shadow(0 0 10px rgba(0,255,255,0.5))',
  },
  titleContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  title: {
    margin: 0,
    fontSize: '24px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '3px',
    textShadow: '0 0 20px rgba(0,255,255,0.5)',
  },
  titleAccent: {
    color: '#ff0080',
    textShadow: '0 0 20px rgba(255,0,128,0.5)',
  },
  subtitle: {
    margin: 0,
    fontSize: '10px',
    color: '#888',
    letterSpacing: '3px',
    fontFamily: "'Rajdhani', sans-serif",
  },
  rightSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
  },
  collectingIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    background: 'rgba(255,170,0,0.2)',
    border: '1px solid #ffaa00',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: 600,
    color: '#ffaa00',
    letterSpacing: '1px',
  },
  pulse: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: '#ffaa00',
    animation: 'pulse 1s infinite',
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    border: '1px solid',
    borderRadius: '20px',
    fontSize: '11px',
    fontWeight: 600,
    letterSpacing: '1px',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  timeContainer: {
    textAlign: 'right' as const,
  },
  time: {
    fontSize: '20px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
    textShadow: '0 0 15px rgba(0,255,255,0.4)',
  },
  date: {
    fontSize: '11px',
    color: '#888',
    letterSpacing: '2px',
  },
};

export default Header;

