import React, { useState } from 'react';
import { useAppContext, Post } from '../../context/AppContext';
import DetectionCard from './DetectionCard';
import DetailModal from './DetailModal';

interface LiveStreamProps {
  maxItems?: number;
  showHeader?: boolean;
}

type StreamFilter = 'all' | 'reddit' | 'telegram';

const LiveStream: React.FC<LiveStreamProps> = ({ maxItems = 20, showHeader = true }) => {
  const { posts, isCollecting } = useAppContext();
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [streamFilter, setStreamFilter] = useState<StreamFilter>('all');

  const filtered =
    streamFilter === 'all'
      ? posts
      : posts.filter((p) => p.platform === streamFilter);
  const displayPosts = filtered.slice(0, maxItems);

  return (
    <div style={styles.container}>
      {showHeader && (
        <div style={styles.header}>
          <div style={styles.headerLeft}>
            <h2 style={styles.title}>LIVE DETECTION STREAM</h2>
          </div>
          <div style={styles.headerRight}>
            <div style={styles.filterRow}>
              {(['all', 'reddit', 'telegram'] as const).map((key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setStreamFilter(key)}
                  style={{
                    ...styles.filterBtn,
                    ...(streamFilter === key ? styles.filterBtnActive : {}),
                  }}
                >
                  {key === 'all' ? 'All' : key === 'reddit' ? 'Reddit' : 'Telegram'}
                </button>
              ))}
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
        </div>
      )}

      <div style={styles.streamContainer}>
        {displayPosts.length === 0 ? (
          <div style={styles.empty}>
            <p>
              {posts.length === 0
                ? 'No detections yet. Start collecting data to see results.'
                : streamFilter === 'all'
                  ? 'No posts to show.'
                  : `No ${streamFilter} posts in the stream yet. Try "All" or run a ${streamFilter} collection.`}
            </p>
          </div>
        ) : (
          <div style={styles.stream}>
            {displayPosts.map((post, index) => (
              <div
                key={post.id || index}
                style={{
                  animation: 'slideIn 0.3s ease forwards',
                  animationDelay: `${index * 0.05}s`,
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
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flexWrap: 'wrap' as const,
    justifyContent: 'flex-end',
  },
  filterRow: {
    display: 'flex',
    gap: '6px',
  },
  filterBtn: {
    padding: '4px 10px',
    fontSize: '10px',
    fontWeight: 600,
    letterSpacing: '0.5px',
    border: '1px solid rgba(0,255,255,0.25)',
    borderRadius: '6px',
    background: 'rgba(0,0,0,0.25)',
    color: '#888',
    cursor: 'pointer',
  },
  filterBtnActive: {
    borderColor: '#00ffff',
    color: '#00ffff',
    background: 'rgba(0,255,255,0.12)',
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
};

export default LiveStream;

