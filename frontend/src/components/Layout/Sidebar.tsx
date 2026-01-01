import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';

interface NavItem {
  path: string;
  label: string;
  icon: string;
  badge?: number;
}

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { stats, redditConfigured, telegramConfigured } = useAppContext();

  // Count posts with media
  const { posts } = useAppContext();
  const mediaCount = posts.filter((p: any) => p.image_url || p.video_url || (p.gallery_images && p.gallery_images.length > 0)).length;

  const navItems: NavItem[] = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/threats', label: 'Active Threats', icon: '⚠️', badge: stats.highRiskCount },
    { path: '/media', label: 'Media Library', icon: '🖼️', badge: mediaCount > 0 ? mediaCount : undefined },
    { path: '/history', label: 'Collection History', icon: '📜' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <aside style={styles.sidebar}>
      <nav style={styles.nav}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              style={{
                ...styles.navItem,
                ...(isActive ? styles.navItemActive : {}),
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(0,255,255,0.1)';
                  e.currentTarget.style.borderColor = 'rgba(0,255,255,0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'transparent';
                }
              }}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              <span style={styles.navLabel}>{item.label}</span>
              {item.badge !== undefined && item.badge > 0 && (
                <span style={styles.badge}>{item.badge}</span>
              )}
            </button>
          );
        })}
      </nav>

      <div style={styles.statusSection}>
        <div style={styles.statusTitle}>INTEGRATIONS</div>
        <div style={styles.statusItem}>
          <span style={styles.statusLabel}>Reddit API</span>
          <span style={{
            ...styles.statusValue,
            color: redditConfigured ? '#00ff88' : '#888',
          }}>
            {redditConfigured ? 'READY' : 'NOT SET'}
          </span>
        </div>
        <div style={styles.statusItem}>
          <span style={styles.statusLabel}>Telegram API</span>
          <span style={{
            ...styles.statusValue,
            color: telegramConfigured ? '#00ff88' : '#888',
          }}>
            {telegramConfigured ? 'READY' : 'NOT SET'}
          </span>
        </div>
      </div>
    </aside>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  sidebar: {
    width: '220px',
    minWidth: '220px',
    background: 'linear-gradient(180deg, rgba(0,15,30,0.98) 0%, rgba(0,10,20,0.95) 100%)',
    borderRight: '1px solid rgba(0,255,255,0.1)',
    display: 'flex',
    flexDirection: 'column',
    padding: '20px 0',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
    padding: '0 10px',
    flex: 1,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 15px',
    background: 'transparent',
    border: '1px solid transparent',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    color: '#aaa',
    fontFamily: "'Rajdhani', sans-serif",
    fontSize: '14px',
    fontWeight: 500,
    letterSpacing: '0.5px',
    textAlign: 'left' as const,
  },
  navItemActive: {
    background: 'linear-gradient(90deg, rgba(0,255,255,0.15) 0%, rgba(0,255,255,0.05) 100%)',
    borderColor: '#00ffff',
    color: '#00ffff',
    boxShadow: '0 0 20px rgba(0,255,255,0.1)',
  },
  navIcon: {
    fontSize: '18px',
  },
  navLabel: {
    flex: 1,
  },
  badge: {
    padding: '2px 8px',
    background: 'rgba(255,0,128,0.2)',
    border: '1px solid #ff0080',
    borderRadius: '10px',
    fontSize: '11px',
    fontWeight: 700,
    color: '#ff0080',
  },
  statusSection: {
    padding: '20px 15px',
    borderTop: '1px solid rgba(0,255,255,0.1)',
    marginTop: 'auto',
  },
  statusTitle: {
    fontSize: '10px',
    color: '#666',
    letterSpacing: '2px',
    marginBottom: '15px',
    fontWeight: 600,
  },
  statusItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
  },
  statusLabel: {
    fontSize: '12px',
    color: '#888',
  },
  statusValue: {
    fontSize: '10px',
    fontWeight: 600,
    letterSpacing: '1px',
  },
};

export default Sidebar;

