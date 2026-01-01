import React, { useState, useMemo } from 'react';
import { useAppContext } from '../context/AppContext';
import type { RedditPost } from '../types';

interface ImageModalProps {
  post: RedditPost;
  onClose: () => void;
  onPrev: () => void;
  onNext: () => void;
  hasPrev: boolean;
  hasNext: boolean;
}

const ImageModal: React.FC<ImageModalProps> = ({ 
  post, 
  onClose, 
  onPrev, 
  onNext, 
  hasPrev, 
  hasNext 
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const images = post.gallery_images || (post.image_url ? [post.image_url] : []);
  
  const riskLevel = post.risk_analysis?.risk_score 
    ? post.risk_analysis.risk_score >= 0.7 ? 'HIGH' 
    : post.risk_analysis.risk_score >= 0.4 ? 'MEDIUM' 
    : 'LOW'
    : 'LOW';
  
  const riskColor = riskLevel === 'HIGH' ? '#ff3366' 
    : riskLevel === 'MEDIUM' ? '#ffaa00' 
    : '#00ff88';

  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modalContent} onClick={e => e.stopPropagation()}>
        {/* Navigation arrows */}
        {hasPrev && (
          <button style={{...styles.navArrow, left: '-60px'}} onClick={onPrev}>
            ‹
          </button>
        )}
        {hasNext && (
          <button style={{...styles.navArrow, right: '-60px'}} onClick={onNext}>
            ›
          </button>
        )}
        
        {/* Close button */}
        <button style={styles.closeBtn} onClick={onClose}>×</button>
        
        {/* Image container */}
        <div style={styles.imageContainer}>
          {post.is_video && post.video_url ? (
            <video 
              src={post.video_url} 
              controls 
              autoPlay 
              muted
              style={styles.modalImage}
            />
          ) : (
            <img 
              src={images[currentImageIndex]} 
              alt={post.title}
              style={styles.modalImage}
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/800x600?text=Image+Not+Available';
              }}
            />
          )}
          
          {/* Gallery navigation */}
          {images.length > 1 && (
            <div style={styles.galleryNav}>
              {images.map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentImageIndex(idx)}
                  style={{
                    ...styles.galleryDot,
                    background: idx === currentImageIndex ? '#00ffff' : 'rgba(255,255,255,0.3)'
                  }}
                />
              ))}
            </div>
          )}
        </div>
        
        {/* Post info panel */}
        <div style={styles.infoPanel}>
          <div style={styles.riskBadge}>
            <span style={{...styles.riskIndicator, background: riskColor}} />
            {riskLevel} RISK
            <span style={styles.riskScore}>
              {((post.risk_analysis?.risk_score || 0) * 100).toFixed(0)}%
            </span>
          </div>
          
          <h3 style={styles.modalTitle}>{post.title}</h3>
          
          <div style={styles.metaRow}>
            <span style={styles.subredditBadge}>r/{post.subreddit}</span>
            <span style={styles.metaItem}>⬆️ {post.score}</span>
            <span style={styles.metaItem}>💬 {post.num_comments}</span>
          </div>
          
          {post.content && (
            <p style={styles.modalContent}>{post.content.slice(0, 300)}...</p>
          )}
          
          {post.risk_analysis?.detected_keywords && post.risk_analysis.detected_keywords.length > 0 && (
            <div style={styles.keywordsSection}>
              <span style={styles.keywordsLabel}>🔍 Detected Keywords:</span>
              <div style={styles.keywords}>
                {post.risk_analysis.detected_keywords.map((kw, i) => (
                  <span key={i} style={styles.keyword}>{kw}</span>
                ))}
              </div>
            </div>
          )}
          
          <a 
            href={post.url} 
            target="_blank" 
            rel="noopener noreferrer"
            style={styles.viewOriginal}
          >
            View on Reddit →
          </a>
        </div>
      </div>
    </div>
  );
};

const MediaLibraryPage: React.FC = () => {
  const { posts } = useAppContext();
  const [selectedPost, setSelectedPost] = useState<RedditPost | null>(null);
  const [filter, setFilter] = useState<'all' | 'image' | 'video' | 'gallery'>('all');
  const [riskFilter, setRiskFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [sortBy, setSortBy] = useState<'recent' | 'risk' | 'score'>('recent');
  
  // Filter posts that have images/media
  const mediaPosts = useMemo(() => {
    return (posts as RedditPost[])
      .filter(post => {
        // Must have some media
        if (!post.image_url && !post.video_url && (!post.gallery_images || post.gallery_images.length === 0)) {
          return false;
        }
        
        // Apply media type filter
        if (filter !== 'all') {
          if (filter === 'image' && post.media_type !== 'image') return false;
          if (filter === 'video' && !post.is_video) return false;
          if (filter === 'gallery' && post.media_type !== 'gallery') return false;
        }
        
        // Apply risk filter
        if (riskFilter !== 'all') {
          const score = post.risk_analysis?.risk_score || 0;
          if (riskFilter === 'high' && score < 0.7) return false;
          if (riskFilter === 'medium' && (score < 0.4 || score >= 0.7)) return false;
          if (riskFilter === 'low' && score >= 0.4) return false;
        }
        
        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'risk') {
          return (b.risk_analysis?.risk_score || 0) - (a.risk_analysis?.risk_score || 0);
        }
        if (sortBy === 'score') {
          return b.score - a.score;
        }
        return (b.created_utc || 0) - (a.created_utc || 0);
      });
  }, [posts, filter, riskFilter, sortBy]);
  
  const selectedIndex = selectedPost 
    ? mediaPosts.findIndex(p => p.id === selectedPost.id) 
    : -1;
  
  const handlePrev = () => {
    if (selectedIndex > 0) {
      setSelectedPost(mediaPosts[selectedIndex - 1]);
    }
  };
  
  const handleNext = () => {
    if (selectedIndex < mediaPosts.length - 1) {
      setSelectedPost(mediaPosts[selectedIndex + 1]);
    }
  };

  const stats = useMemo(() => ({
    total: mediaPosts.length,
    images: mediaPosts.filter(p => p.media_type === 'image').length,
    videos: mediaPosts.filter(p => p.is_video).length,
    galleries: mediaPosts.filter(p => p.media_type === 'gallery').length,
    highRisk: mediaPosts.filter(p => (p.risk_analysis?.risk_score || 0) >= 0.7).length,
    weaponsDetected: mediaPosts.filter(p => p.image_analysis?.contains_weapons).length,
    verifiedSafe: mediaPosts.filter(p => p.image_analysis?.image_verified_safe).length,
  }), [mediaPosts]);

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.title}>
            <span style={styles.titleIcon}>🖼️</span>
            MEDIA LIBRARY
          </h1>
          <p style={styles.subtitle}>
            Visual content extracted from collected posts • {stats.total} items
          </p>
        </div>
        
        <div style={styles.statsRow}>
          <div style={styles.statBadge}>
            <span style={styles.statIcon}>📷</span>
            <span style={styles.statValue}>{stats.images}</span>
            <span style={styles.statLabel}>Images</span>
          </div>
          <div style={styles.statBadge}>
            <span style={styles.statIcon}>🎬</span>
            <span style={styles.statValue}>{stats.videos}</span>
            <span style={styles.statLabel}>Videos</span>
          </div>
          <div style={styles.statBadge}>
            <span style={styles.statIcon}>📚</span>
            <span style={styles.statValue}>{stats.galleries}</span>
            <span style={styles.statLabel}>Galleries</span>
          </div>
          <div style={{...styles.statBadge, borderColor: '#ff3366'}}>
            <span style={styles.statIcon}>⚠️</span>
            <span style={{...styles.statValue, color: '#ff3366'}}>{stats.highRisk}</span>
            <span style={styles.statLabel}>High Risk</span>
          </div>
          <div style={{...styles.statBadge, borderColor: '#ff0000'}}>
            <span style={styles.statIcon}>🔫</span>
            <span style={{...styles.statValue, color: '#ff0000'}}>{stats.weaponsDetected}</span>
            <span style={styles.statLabel}>Weapons Found</span>
          </div>
          <div style={{...styles.statBadge, borderColor: '#00cc66'}}>
            <span style={styles.statIcon}>✓</span>
            <span style={{...styles.statValue, color: '#00cc66'}}>{stats.verifiedSafe}</span>
            <span style={styles.statLabel}>Verified Safe</span>
          </div>
        </div>
      </div>
      
      {/* Filters */}
      <div style={styles.filters}>
        <div style={styles.filterGroup}>
          <span style={styles.filterLabel}>Media Type:</span>
          {(['all', 'image', 'video', 'gallery'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                ...styles.filterBtn,
                background: filter === f ? 'rgba(0,255,255,0.2)' : 'transparent',
                borderColor: filter === f ? '#00ffff' : 'rgba(255,255,255,0.1)'
              }}
            >
              {f === 'all' ? '🌐 All' : f === 'image' ? '📷 Images' : f === 'video' ? '🎬 Videos' : '📚 Galleries'}
            </button>
          ))}
        </div>
        
        <div style={styles.filterGroup}>
          <span style={styles.filterLabel}>Risk Level:</span>
          {(['all', 'high', 'medium', 'low'] as const).map(f => (
            <button
              key={f}
              onClick={() => setRiskFilter(f)}
              style={{
                ...styles.filterBtn,
                background: riskFilter === f ? 'rgba(0,255,255,0.2)' : 'transparent',
                borderColor: riskFilter === f ? '#00ffff' : 'rgba(255,255,255,0.1)'
              }}
            >
              {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        
        <div style={styles.filterGroup}>
          <span style={styles.filterLabel}>Sort:</span>
          <select 
            value={sortBy} 
            onChange={e => setSortBy(e.target.value as any)}
            style={styles.sortSelect}
          >
            <option value="recent">Most Recent</option>
            <option value="risk">Highest Risk</option>
            <option value="score">Most Popular</option>
          </select>
        </div>
      </div>
      
      {/* Gallery Grid */}
      {mediaPosts.length === 0 ? (
        <div style={styles.emptyState}>
          <div style={styles.emptyIcon}>📷</div>
          <h3 style={styles.emptyTitle}>No Media Found</h3>
          <p style={styles.emptyText}>
            Collect posts from Reddit to see images and videos here.
            <br />
            Go to Dashboard and click "COLLECT FROM REDDIT" to start.
          </p>
        </div>
      ) : (
        <div style={styles.gallery}>
          {mediaPosts.map(post => {
            // Use annotated image if weapons were detected, otherwise original
            const hasWeapons = post.image_analysis?.contains_weapons;
            const annotatedSrc = post.annotated_image ? `data:image/jpeg;base64,${post.annotated_image}` : null;
            const originalUrl = post.image_url || (post.gallery_images && post.gallery_images[0]) || post.thumbnail;
            const imageUrl = (hasWeapons && annotatedSrc) ? annotatedSrc : originalUrl;
            
            const riskScore = post.risk_analysis?.risk_score || 0;
            const riskColor = riskScore >= 0.7 ? '#ff3366' : riskScore >= 0.4 ? '#ffaa00' : '#00ff88';
            const weaponCount = post.image_analysis?.weapon_count || 0;
            
            return (
              <div 
                key={post.id}
                style={{
                  ...styles.galleryItem,
                  border: hasWeapons ? '2px solid #ff0000' : undefined,
                  boxShadow: hasWeapons ? '0 0 20px rgba(255,0,0,0.4)' : undefined,
                }}
                onClick={() => setSelectedPost(post)}
              >
                <div style={styles.imageWrapper}>
                  {post.is_video && (
                    <div style={styles.videoIndicator}>▶️</div>
                  )}
                  {post.gallery_images && post.gallery_images.length > 1 && (
                    <div style={styles.galleryIndicator}>
                      📚 {post.gallery_images.length}
                    </div>
                  )}
                  {/* Weapon detection badge */}
                  {hasWeapons && (
                    <div style={styles.weaponBadge}>
                      🔫 {weaponCount} WEAPON{weaponCount > 1 ? 'S' : ''}
                    </div>
                  )}
                  {/* Verified safe badge - when image analyzed and no weapons */}
                  {post.image_analysis?.image_verified_safe && !hasWeapons && (
                    <div style={styles.safeBadge}>
                      ✓ VERIFIED
                    </div>
                  )}
                  <img 
                    src={imageUrl || 'https://via.placeholder.com/300x200?text=No+Preview'}
                    alt={post.title}
                    style={styles.galleryImage}
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x200?text=Error';
                    }}
                  />
                  <div style={{...styles.riskOverlay, borderColor: riskColor}}>
                    <span style={{...styles.riskDot, background: riskColor}} />
                    {(riskScore * 100).toFixed(0)}%
                  </div>
                </div>
                <div style={styles.itemInfo}>
                  <h4 style={styles.itemTitle}>
                    {post.title.length > 50 ? post.title.slice(0, 50) + '...' : post.title}
                  </h4>
                  <div style={styles.itemMeta}>
                    <span style={styles.subreddit}>r/{post.subreddit}</span>
                    <span style={styles.score}>⬆️ {post.score}</span>
                  </div>
                  {/* Weapon detection info */}
                  {hasWeapons && post.image_analysis?.detections && (
                    <div style={styles.weaponInfo}>
                      {post.image_analysis.detections.slice(0, 2).map((d, i) => (
                        <span key={i} style={styles.weaponType}>
                          {d.weapon_type}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {/* Image Modal */}
      {selectedPost && (
        <ImageModal
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
          onPrev={handlePrev}
          onNext={handleNext}
          hasPrev={selectedIndex > 0}
          hasNext={selectedIndex < mediaPosts.length - 1}
        />
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    padding: '20px',
    minHeight: '100%',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '25px',
    flexWrap: 'wrap',
    gap: '20px',
  },
  headerLeft: {},
  title: {
    fontSize: '28px',
    fontWeight: 700,
    color: '#fff',
    margin: 0,
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  titleIcon: {
    fontSize: '32px',
  },
  subtitle: {
    color: '#666',
    fontSize: '14px',
    marginTop: '5px',
  },
  statsRow: {
    display: 'flex',
    gap: '15px',
    flexWrap: 'wrap',
  },
  statBadge: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '12px 20px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '10px',
    minWidth: '80px',
  },
  statIcon: {
    fontSize: '20px',
    marginBottom: '5px',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#00ffff',
  },
  statLabel: {
    fontSize: '11px',
    color: '#666',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  filters: {
    display: 'flex',
    gap: '20px',
    marginBottom: '25px',
    flexWrap: 'wrap',
    padding: '15px 20px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '12px',
    border: '1px solid rgba(255,255,255,0.05)',
  },
  filterGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  filterLabel: {
    color: '#666',
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  filterBtn: {
    padding: '8px 14px',
    border: '1px solid',
    borderRadius: '6px',
    background: 'transparent',
    color: '#fff',
    fontSize: '12px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  sortSelect: {
    padding: '8px 12px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '6px',
    color: '#fff',
    fontSize: '12px',
    cursor: 'pointer',
  },
  gallery: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '20px',
  },
  galleryItem: {
    background: 'linear-gradient(135deg, rgba(0,30,60,0.8) 0%, rgba(0,15,30,0.9) 100%)',
    border: '1px solid rgba(0,255,255,0.1)',
    borderRadius: '12px',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  imageWrapper: {
    position: 'relative',
    width: '100%',
    height: '200px',
    overflow: 'hidden',
    background: '#000',
  },
  galleryImage: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transition: 'transform 0.3s ease',
  },
  videoIndicator: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    fontSize: '40px',
    zIndex: 2,
    textShadow: '0 2px 10px rgba(0,0,0,0.5)',
  },
  galleryIndicator: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    padding: '5px 10px',
    background: 'rgba(0,0,0,0.7)',
    borderRadius: '5px',
    fontSize: '12px',
    color: '#fff',
    zIndex: 2,
  },
  weaponBadge: {
    position: 'absolute',
    top: '10px',
    left: '10px',
    padding: '6px 12px',
    background: 'linear-gradient(135deg, #ff0000 0%, #cc0000 100%)',
    borderRadius: '5px',
    fontSize: '11px',
    fontWeight: 700,
    color: '#fff',
    zIndex: 3,
    letterSpacing: '1px',
    boxShadow: '0 2px 10px rgba(255,0,0,0.5)',
    animation: 'pulse 2s infinite',
  },
  safeBadge: {
    position: 'absolute',
    top: '10px',
    left: '10px',
    padding: '6px 12px',
    background: 'linear-gradient(135deg, #00cc66 0%, #009944 100%)',
    borderRadius: '5px',
    fontSize: '11px',
    fontWeight: 700,
    color: '#fff',
    zIndex: 3,
    letterSpacing: '1px',
    boxShadow: '0 2px 10px rgba(0,204,102,0.5)',
  },
  weaponInfo: {
    display: 'flex',
    gap: '5px',
    marginTop: '8px',
    flexWrap: 'wrap',
  },
  weaponType: {
    padding: '3px 8px',
    background: 'rgba(255,0,0,0.2)',
    border: '1px solid #ff0000',
    borderRadius: '4px',
    fontSize: '10px',
    color: '#ff6666',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  riskOverlay: {
    position: 'absolute',
    bottom: '10px',
    left: '10px',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '5px 10px',
    background: 'rgba(0,0,0,0.8)',
    border: '1px solid',
    borderRadius: '5px',
    fontSize: '12px',
    fontWeight: 700,
    color: '#fff',
  },
  riskDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  itemInfo: {
    padding: '15px',
  },
  itemTitle: {
    margin: '0 0 10px 0',
    fontSize: '14px',
    fontWeight: 600,
    color: '#fff',
    lineHeight: 1.4,
  },
  itemMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    color: '#666',
  },
  subreddit: {
    color: '#00ffff',
  },
  score: {},
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '80px 20px',
    textAlign: 'center',
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '20px',
    opacity: 0.5,
  },
  emptyTitle: {
    fontSize: '24px',
    color: '#fff',
    margin: '0 0 10px 0',
  },
  emptyText: {
    color: '#666',
    fontSize: '14px',
    lineHeight: 1.6,
  },
  // Modal styles
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.95)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '40px',
  },
  modalContent: {
    position: 'relative',
    display: 'flex',
    maxWidth: '1200px',
    maxHeight: '90vh',
    background: 'linear-gradient(135deg, #001a2e 0%, #000a14 100%)',
    borderRadius: '15px',
    overflow: 'hidden',
    border: '1px solid rgba(0,255,255,0.2)',
  },
  closeBtn: {
    position: 'absolute',
    top: '15px',
    right: '15px',
    width: '36px',
    height: '36px',
    border: 'none',
    borderRadius: '50%',
    background: 'rgba(255,255,255,0.1)',
    color: '#fff',
    fontSize: '24px',
    cursor: 'pointer',
    zIndex: 10,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  navArrow: {
    position: 'absolute',
    top: '50%',
    transform: 'translateY(-50%)',
    width: '50px',
    height: '50px',
    border: 'none',
    borderRadius: '50%',
    background: 'rgba(0,255,255,0.2)',
    color: '#00ffff',
    fontSize: '30px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s',
  },
  imageContainer: {
    flex: '1 1 60%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#000',
    minHeight: '400px',
  },
  modalImage: {
    maxWidth: '100%',
    maxHeight: '70vh',
    objectFit: 'contain',
  },
  galleryNav: {
    display: 'flex',
    gap: '8px',
    marginTop: '15px',
  },
  galleryDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    border: 'none',
    cursor: 'pointer',
  },
  infoPanel: {
    flex: '0 0 350px',
    padding: '25px',
    overflowY: 'auto',
  },
  riskBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 15px',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '15px',
  },
  riskIndicator: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
  },
  riskScore: {
    marginLeft: '5px',
    opacity: 0.7,
  },
  modalTitle: {
    fontSize: '18px',
    fontWeight: 600,
    color: '#fff',
    margin: '0 0 15px 0',
    lineHeight: 1.4,
  },
  metaRow: {
    display: 'flex',
    gap: '15px',
    marginBottom: '15px',
    flexWrap: 'wrap',
  },
  subredditBadge: {
    padding: '5px 12px',
    background: 'rgba(0,255,255,0.1)',
    border: '1px solid rgba(0,255,255,0.3)',
    borderRadius: '15px',
    fontSize: '12px',
    color: '#00ffff',
  },
  metaItem: {
    fontSize: '13px',
    color: '#888',
  },
  modalContentText: {
    fontSize: '14px',
    color: '#aaa',
    lineHeight: 1.6,
    marginBottom: '20px',
  },
  keywordsSection: {
    marginTop: '20px',
    paddingTop: '15px',
    borderTop: '1px solid rgba(255,255,255,0.1)',
  },
  keywordsLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#666',
    marginBottom: '10px',
  },
  keywords: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  keyword: {
    padding: '5px 10px',
    background: 'rgba(255,51,102,0.1)',
    border: '1px solid rgba(255,51,102,0.3)',
    borderRadius: '5px',
    fontSize: '11px',
    color: '#ff3366',
  },
  viewOriginal: {
    display: 'inline-block',
    marginTop: '20px',
    padding: '12px 20px',
    background: 'linear-gradient(90deg, #00ffff, #0088cc)',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: 600,
    color: '#000',
    textDecoration: 'none',
  },
};

export default MediaLibraryPage;

