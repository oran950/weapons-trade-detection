import React, { useState, useMemo } from 'react';
import { useAppContext, Post } from '../context/AppContext';
import DetectionCard from '../components/Detection/DetectionCard';
import DetailModal from '../components/Detection/DetailModal';
import RiskBadge from '../components/shared/RiskBadge';

type FilterLevel = 'all' | 'HIGH' | 'MEDIUM' | 'LOW' | 'ILLEGAL';
type SortOption = 'risk' | 'time' | 'score';

const ThreatsPage: React.FC = () => {
  const { posts, stats } = useAppContext();
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [filterLevel, setFilterLevel] = useState<FilterLevel>('all');
  const [sortBy, setSortBy] = useState<SortOption>('risk');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredPosts = useMemo(() => {
    let result = [...posts];

    // Filter by risk level or illegal trade
    if (filterLevel === 'ILLEGAL') {
      result = result.filter(p => p.llm_analysis?.is_potentially_illegal);
    } else if (filterLevel !== 'all') {
      result = result.filter(p => p.risk_analysis?.risk_level === filterLevel);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(p =>
        p.title.toLowerCase().includes(query) ||
        p.content?.toLowerCase().includes(query) ||
        p.subreddit?.toLowerCase().includes(query) ||
        p.risk_analysis?.detected_keywords?.some(k => k.toLowerCase().includes(query)) ||
        p.llm_analysis?.summary?.toLowerCase().includes(query)
      );
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'risk':
          // Prioritize illegal trade posts
          const aIllegal = a.llm_analysis?.is_potentially_illegal ? 1 : 0;
          const bIllegal = b.llm_analysis?.is_potentially_illegal ? 1 : 0;
          if (aIllegal !== bIllegal) return bIllegal - aIllegal;
          return (b.risk_analysis?.risk_score || 0) - (a.risk_analysis?.risk_score || 0);
        case 'time':
          return new Date(b.collected_at).getTime() - new Date(a.collected_at).getTime();
        case 'score':
          return (b.score || 0) - (a.score || 0);
        default:
          return 0;
      }
    });

    return result;
  }, [posts, filterLevel, sortBy, searchQuery]);

  const filterCounts = useMemo(() => ({
    all: posts.length,
    HIGH: posts.filter(p => p.risk_analysis?.risk_level === 'HIGH').length,
    MEDIUM: posts.filter(p => p.risk_analysis?.risk_level === 'MEDIUM').length,
    LOW: posts.filter(p => p.risk_analysis?.risk_level === 'LOW').length,
    ILLEGAL: posts.filter(p => p.llm_analysis?.is_potentially_illegal).length,
  }), [posts]);

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>⚠️ Active Threats</h1>
          <p style={styles.subtitle}>
            Monitoring {stats.highRiskCount} high-risk detections
          </p>
        </div>
        <div style={styles.headerStats}>
          <div style={{...styles.statBadge, borderColor: '#ff0000', background: 'rgba(255,0,0,0.1)'}}>
            <span style={{ color: '#ff0000', fontWeight: 700 }}>🚨 {filterCounts.ILLEGAL}</span> ILLEGAL TRADE
          </div>
          <div style={styles.statBadge}>
            <span style={{ color: '#ff0080' }}>{stats.highRiskCount}</span> HIGH
          </div>
          <div style={styles.statBadge}>
            <span style={{ color: '#ffaa00' }}>{stats.mediumRiskCount}</span> MEDIUM
          </div>
          <div style={styles.statBadge}>
            <span style={{ color: '#00ff88' }}>{stats.lowRiskCount}</span> LOW
          </div>
        </div>
      </div>

      {/* Filters */}
      <div style={styles.filters}>
        <div style={styles.filterGroup}>
          <input
            type="text"
            placeholder="Search threats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={styles.searchInput}
          />
        </div>

        <div style={styles.filterGroup}>
          <span style={styles.filterLabel}>Filter:</span>
          {/* Illegal Trade filter - prominent */}
          <button
            onClick={() => setFilterLevel('ILLEGAL')}
            style={{
              ...styles.filterButton,
              ...(filterLevel === 'ILLEGAL' ? styles.filterButtonActive : {}),
              borderColor: '#ff0000',
              background: filterLevel === 'ILLEGAL' ? 'rgba(255,0,0,0.2)' : 'rgba(255,0,0,0.05)',
            }}
          >
            🚨 ILLEGAL TRADE ({filterCounts.ILLEGAL})
          </button>
          {(['all', 'HIGH', 'MEDIUM', 'LOW'] as FilterLevel[]).map((level) => (
            <button
              key={level}
              onClick={() => setFilterLevel(level)}
              style={{
                ...styles.filterButton,
                ...(filterLevel === level ? styles.filterButtonActive : {}),
                borderColor: level === 'HIGH' ? '#ff0080' :
                             level === 'MEDIUM' ? '#ffaa00' :
                             level === 'LOW' ? '#00ff88' : '#00ffff',
              }}
            >
              {level === 'all' ? 'ALL' : level} ({filterCounts[level]})
            </button>
          ))}
        </div>

        <div style={styles.filterGroup}>
          <span style={styles.filterLabel}>Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            style={styles.select}
          >
            <option value="risk">Risk Score</option>
            <option value="time">Most Recent</option>
            <option value="score">Reddit Score</option>
          </select>
        </div>
      </div>

      {/* Results */}
      <div style={styles.results}>
        {filteredPosts.length === 0 ? (
          <div style={styles.empty}>
            <span style={styles.emptyIcon}>🔍</span>
            <p>No threats found matching your criteria.</p>
            <p style={styles.emptyHint}>Try adjusting your filters or collect more data.</p>
          </div>
        ) : (
          <div style={styles.grid}>
            {filteredPosts.map((post, index) => (
              <DetectionCard
                key={post.id || index}
                post={post}
                onClick={() => setSelectedPost(post)}
              />
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
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  title: {
    margin: 0,
    fontSize: '28px',
    fontWeight: 700,
    color: '#ff0080',
    textShadow: '0 0 30px rgba(255,0,128,0.3)',
  },
  subtitle: {
    margin: '5px 0 0 0',
    fontSize: '14px',
    color: '#888',
  },
  headerStats: {
    display: 'flex',
    gap: '15px',
  },
  statBadge: {
    padding: '10px 20px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#888',
    letterSpacing: '1px',
  },
  filters: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '20px',
    padding: '20px',
    background: 'rgba(0,0,0,0.2)',
    borderRadius: '12px',
    border: '1px solid rgba(0,255,255,0.1)',
  },
  filterGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  filterLabel: {
    fontSize: '12px',
    color: '#666',
    letterSpacing: '1px',
  },
  searchInput: {
    width: '250px',
    padding: '10px 15px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#fff',
    fontFamily: 'inherit',
  },
  filterButton: {
    padding: '8px 16px',
    background: 'transparent',
    border: '1px solid',
    borderRadius: '6px',
    fontSize: '11px',
    fontWeight: 600,
    color: '#888',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    letterSpacing: '1px',
  },
  filterButtonActive: {
    background: 'rgba(0,255,255,0.1)',
    color: '#fff',
  },
  select: {
    padding: '10px 15px',
    background: 'rgba(0,0,0,0.3)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '8px',
    fontSize: '13px',
    color: '#fff',
    fontFamily: 'inherit',
    cursor: 'pointer',
  },
  results: {
    flex: 1,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '15px',
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

export default ThreatsPage;

