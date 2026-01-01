import React, { useState } from 'react';
import { useAppContext, Post } from '../../context/AppContext';
import DetectionCard from './DetectionCard';
import DetailModal from './DetailModal';

interface LiveStreamProps {
  maxItems?: number;
  showHeader?: boolean;
}

const LiveStream: React.FC<LiveStreamProps> = ({ maxItems = 20, showHeader = true }) => {
  const { posts, isCollecting } = useAppContext();
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);

  const displayPosts = posts.slice(0, maxItems);

  return (
    <div style={styles.container}>
      {showHeader && (
        <div style={styles.header}>
          <div style={styles.headerLeft}>
            <span style={styles.icon}>📡</span>
            <h2 style={styles.title}>LIVE DETECTION STREAM</h2>
          </div>
          <div style={{
            ...styles.status,
            background: isCollecting 
              ? 'rgba(255,170,0,0.2)' 
              : 'rgba(0,255,136,0.2)',
            borderColor: isCollecting ? '#ffaa00' : '#00ff88',
            color: isCollecting ? '#ffaa00' : '#00ff88',
          }}>
            <span style={{
              ...styles.statusDot,
              background: isCollecting ? '#ffaa00' : '#00ff88',
            }}></span>
            {isCollecting ? 'COLLECTING...' : 'ACTIVE'}
          </div>
        </div>
      )}

      <div style={styles.streamContainer}>
        {displayPosts.length === 0 ? (
          <div style={styles.empty}>
            <span style={styles.emptyIcon}>📭</span>
            <p>No detections yet. Start collecting data to see results.</p>
          </div>
        ) : (
          <div style={styles.stream}>
            {displayPosts.map((post, index) => (
              <div
                key={post.id || index}
                style={{
                  animation: 'slideIn 0.3s ease forwards',
                  animationDelay: `${index * 0.05}s`,
                  opacity: 0,
                }}
              >
                <DetectionCard
                  post={post}
                  compact
                  onClick={() => setSelectedPost(post)}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedPost && (
        <DetailModal
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px 20px',
    background: 'rgba(0,0,0,0.3)',
    borderBottom: '1px solid rgba(0,255,255,0.1)',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  icon: {
    fontSize: '20px',
  },
  title: {
    margin: 0,
    fontSize: '14px',
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
  },
  status: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 14px',
    border: '1px solid',
    borderRadius: '20px',
    fontSize: '10px',
    fontWeight: 700,
    letterSpacing: '1px',
  },
  statusDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
  },
  streamContainer: {
    maxHeight: '500px',
    overflowY: 'auto',
  },
  stream: {
    padding: '10px',
  },
  empty: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 20px',
    color: '#666',
    textAlign: 'center' as const,
  },
  emptyIcon: {
    fontSize: '40px',
    marginBottom: '15px',
    opacity: 0.5,
  },
};

export default LiveStream;

