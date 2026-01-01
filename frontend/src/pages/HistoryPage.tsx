import React, { useState } from 'react';
import { useAppContext, CollectionSession, Post } from '../context/AppContext';
import DetailModal from '../components/Detection/DetailModal';
import RiskBadge from '../components/shared/RiskBadge';

const HistoryPage: React.FC = () => {
  const { sessions, posts } = useAppContext();
  const [selectedSession, setSelectedSession] = useState<CollectionSession | null>(null);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>📜 Collection History</h1>
        <p style={styles.subtitle}>
          {sessions.length} collection sessions recorded
        </p>
      </div>

      {/* Content */}
      <div style={styles.content}>
        {/* Sessions List */}
        <div style={styles.sessionsList}>
          {sessions.length === 0 ? (
            <div style={styles.empty}>
              <span style={styles.emptyIcon}>📭</span>
              <p>No collection sessions yet.</p>
              <p style={styles.emptyHint}>
                Start collecting data from the Dashboard to see history here.
              </p>
            </div>
          ) : (
            sessions.map((session, index) => (
              <div
                key={session.id || index}
                onClick={() => setSelectedSession(
                  selectedSession?.id === session.id ? null : session
                )}
                style={{
                  ...styles.sessionCard,
                  borderColor: selectedSession?.id === session.id
                    ? '#00ffff'
                    : 'rgba(0,255,255,0.15)',
                }}
              >
                <div style={styles.sessionHeader}>
                  <div style={styles.sessionPlatform}>
                    {session.platform === 'reddit' ? '🔴' : '✈️'}
                    {session.platform.toUpperCase()}
                  </div>
                  <div style={styles.sessionTime}>
                    {formatDate(session.timestamp)}
                  </div>
                </div>

                <div style={styles.sessionSources}>
                  {session.sources.slice(0, 5).join(', ')}
                  {session.sources.length > 5 && ` +${session.sources.length - 5} more`}
                </div>

                <div style={styles.sessionStats}>
                  <div style={styles.sessionStat}>
                    <span style={styles.statLabel}>Collected</span>
                    <span style={styles.statValue}>{session.total_collected}</span>
                  </div>
                  <div style={styles.sessionStat}>
                    <span style={{ ...styles.statLabel, color: '#ff0080' }}>High</span>
                    <span style={{ ...styles.statValue, color: '#ff0080' }}>{session.high_risk}</span>
                  </div>
                  <div style={styles.sessionStat}>
                    <span style={{ ...styles.statLabel, color: '#ffaa00' }}>Medium</span>
                    <span style={{ ...styles.statValue, color: '#ffaa00' }}>{session.medium_risk}</span>
                  </div>
                  <div style={styles.sessionStat}>
                    <span style={{ ...styles.statLabel, color: '#00ff88' }}>Low</span>
                    <span style={{ ...styles.statValue, color: '#00ff88' }}>{session.low_risk}</span>
                  </div>
                </div>

                {/* Expanded Session Details */}
                {selectedSession?.id === session.id && session.posts.length > 0 && (
                  <div style={styles.sessionPosts}>
                    <div style={styles.postsHeader}>
                      Posts from this session ({session.posts.length})
                    </div>
                    <div style={styles.postsList}>
                      {session.posts.slice(0, 10).map((post, i) => (
                        <div
                          key={post.id || i}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedPost(post);
                          }}
                          style={styles.postItem}
                        >
                          <RiskBadge
                            level={post.risk_analysis?.risk_level || 'LOW'}
                            size="small"
                          />
                          <span style={styles.postTitle}>
                            {post.title.length > 60
                              ? `${post.title.substring(0, 60)}...`
                              : post.title}
                          </span>
                        </div>
                      ))}
                      {session.posts.length > 10 && (
                        <div style={styles.morePosts}>
                          +{session.posts.length - 10} more posts
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Recent Posts Summary */}
        <div style={styles.recentPosts}>
          <h3 style={styles.sectionTitle}>Recent Detections</h3>
          <div style={styles.recentList}>
            {posts.slice(0, 15).map((post, index) => (
              <div
                key={post.id || index}
                onClick={() => setSelectedPost(post)}
                style={styles.recentItem}
              >
                <div style={styles.recentHeader}>
                  <RiskBadge
                    level={post.risk_analysis?.risk_level || 'LOW'}
                    size="small"
                  />
                  <span style={styles.recentPlatform}>
                    {post.platform === 'reddit' ? `r/${post.subreddit}` : post.channel}
                  </span>
                </div>
                <div style={styles.recentTitle}>{post.title}</div>
              </div>
            ))}
          </div>
        </div>
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
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  header: {
    marginBottom: '10px',
  },
  title: {
    margin: 0,
    fontSize: '28px',
    fontWeight: 700,
    color: '#00ffff',
  },
  subtitle: {
    margin: '5px 0 0 0',
    fontSize: '14px',
    color: '#888',
  },
  content: {
    display: 'grid',
    gridTemplateColumns: '1fr 350px',
    gap: '20px',
  },
  sessionsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  sessionCard: {
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  sessionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
  },
  sessionPlatform: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    fontWeight: 600,
    color: '#00ffff',
    letterSpacing: '1px',
  },
  sessionTime: {
    fontSize: '12px',
    color: '#666',
  },
  sessionSources: {
    fontSize: '13px',
    color: '#888',
    marginBottom: '15px',
  },
  sessionStats: {
    display: 'flex',
    gap: '20px',
  },
  sessionStat: {
    display: 'flex',
    flexDirection: 'column',
    gap: '3px',
  },
  statLabel: {
    fontSize: '10px',
    color: '#666',
    letterSpacing: '1px',
  },
  statValue: {
    fontSize: '18px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#fff',
  },
  sessionPosts: {
    marginTop: '20px',
    paddingTop: '20px',
    borderTop: '1px solid rgba(0,255,255,0.1)',
  },
  postsHeader: {
    fontSize: '12px',
    color: '#666',
    marginBottom: '10px',
    letterSpacing: '1px',
  },
  postsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  postItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  postTitle: {
    fontSize: '12px',
    color: '#ccc',
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  morePosts: {
    fontSize: '12px',
    color: '#666',
    textAlign: 'center',
    padding: '10px',
  },
  recentPosts: {
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
    padding: '20px',
  },
  sectionTitle: {
    margin: '0 0 15px 0',
    fontSize: '14px',
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
  },
  recentList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    maxHeight: '600px',
    overflowY: 'auto',
  },
  recentItem: {
    padding: '12px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  recentHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '8px',
  },
  recentPlatform: {
    fontSize: '11px',
    color: '#666',
  },
  recentTitle: {
    fontSize: '12px',
    color: '#ccc',
    lineHeight: 1.4,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
  },
  empty: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '80px 20px',
    color: '#666',
    textAlign: 'center',
  },
  emptyIcon: {
    fontSize: '50px',
    marginBottom: '20px',
    opacity: 0.5,
  },
  emptyHint: {
    fontSize: '13px',
    color: '#444',
    marginTop: '5px',
  },
};

export default HistoryPage;

