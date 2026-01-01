import React, { useMemo } from 'react';
import { useAppContext } from '../context/AppContext';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend } from 'recharts';

const AnalyticsPage: React.FC = () => {
  const { posts, stats, sessions } = useAppContext();

  // Risk distribution data
  const riskDistribution = useMemo(() => [
    { name: 'High Risk', value: stats.highRiskCount, color: '#ff0080' },
    { name: 'Medium Risk', value: stats.mediumRiskCount, color: '#ffaa00' },
    { name: 'Low Risk', value: stats.lowRiskCount, color: '#00ff88' },
  ], [stats]);

  // Platform distribution
  const platformDistribution = useMemo(() => {
    const platforms: { [key: string]: number } = {};
    posts.forEach(p => {
      const platform = p.platform || 'unknown';
      platforms[platform] = (platforms[platform] || 0) + 1;
    });
    return Object.entries(platforms).map(([name, value]) => ({ name, value }));
  }, [posts]);

  // Top subreddits
  const topSubreddits = useMemo(() => {
    const subreddits: { [key: string]: number } = {};
    posts.filter(p => p.subreddit).forEach(p => {
      subreddits[p.subreddit!] = (subreddits[p.subreddit!] || 0) + 1;
    });
    return Object.entries(subreddits)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name, count]) => ({ name: `r/${name}`, count }));
  }, [posts]);

  // Top keywords
  const topKeywords = useMemo(() => {
    const keywords: { [key: string]: number } = {};
    posts.forEach(p => {
      p.risk_analysis?.detected_keywords?.forEach(kw => {
        keywords[kw] = (keywords[kw] || 0) + 1;
      });
    });
    return Object.entries(keywords)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([keyword, count]) => ({ keyword, count }));
  }, [posts]);

  // Collection timeline
  const collectionTimeline = useMemo(() => {
    return sessions.slice(0, 10).reverse().map(s => ({
      date: new Date(s.timestamp).toLocaleDateString(),
      total: s.total_collected,
      high: s.high_risk,
      medium: s.medium_risk,
    }));
  }, [sessions]);

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>📈 Analytics Dashboard</h1>
        <p style={styles.subtitle}>
          Insights from {stats.totalAnalyzed} analyzed posts
        </p>
      </div>

      {/* Overview Stats */}
      <div style={styles.overviewGrid}>
        <div style={styles.overviewCard}>
          <div style={styles.overviewLabel}>Total Analyzed</div>
          <div style={styles.overviewValue}>{stats.totalAnalyzed}</div>
        </div>
        <div style={styles.overviewCard}>
          <div style={styles.overviewLabel}>High Risk Rate</div>
          <div style={{ ...styles.overviewValue, color: '#ff0080' }}>
            {stats.totalAnalyzed > 0 
              ? `${Math.round((stats.highRiskCount / stats.totalAnalyzed) * 100)}%`
              : '0%'}
          </div>
        </div>
        <div style={styles.overviewCard}>
          <div style={styles.overviewLabel}>Sessions</div>
          <div style={styles.overviewValue}>{sessions.length}</div>
        </div>
        <div style={styles.overviewCard}>
          <div style={styles.overviewLabel}>Unique Keywords</div>
          <div style={styles.overviewValue}>{topKeywords.length}</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div style={styles.chartsGrid}>
        {/* Risk Distribution Pie Chart */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Risk Distribution</h3>
          {stats.totalAnalyzed > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#001a2e',
                    border: '1px solid rgba(0,255,255,0.2)',
                    borderRadius: '8px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={styles.noData}>No data yet</div>
          )}
          <div style={styles.legend}>
            {riskDistribution.map((item, i) => (
              <div key={i} style={styles.legendItem}>
                <span style={{ ...styles.legendDot, background: item.color }}></span>
                {item.name}: {item.value}
              </div>
            ))}
          </div>
        </div>

        {/* Top Subreddits Bar Chart */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Top Sources</h3>
          {topSubreddits.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topSubreddits} layout="vertical">
                <XAxis type="number" stroke="#666" />
                <YAxis type="category" dataKey="name" width={100} stroke="#888" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: '#001a2e',
                    border: '1px solid rgba(0,255,255,0.2)',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="count" fill="#00ffff" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={styles.noData}>No data yet</div>
          )}
        </div>

        {/* Collection Timeline */}
        <div style={{ ...styles.chartCard, gridColumn: 'span 2' }}>
          <h3 style={styles.chartTitle}>Collection Timeline</h3>
          {collectionTimeline.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={collectionTimeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="#666" fontSize={11} />
                <YAxis stroke="#666" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: '#001a2e',
                    border: '1px solid rgba(0,255,255,0.2)',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="total" stroke="#00ffff" strokeWidth={2} name="Total" />
                <Line type="monotone" dataKey="high" stroke="#ff0080" strokeWidth={2} name="High Risk" />
                <Line type="monotone" dataKey="medium" stroke="#ffaa00" strokeWidth={2} name="Medium" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={styles.noData}>No collection sessions yet</div>
          )}
        </div>
      </div>

      {/* Keywords Section */}
      <div style={styles.keywordsSection}>
        <h3 style={styles.sectionTitle}>🔑 Top Detected Keywords</h3>
        <div style={styles.keywordsGrid}>
          {topKeywords.length > 0 ? (
            topKeywords.map((item, i) => (
              <div
                key={i}
                style={{
                  ...styles.keywordTag,
                  fontSize: `${Math.max(11, 16 - i * 0.3)}px`,
                  opacity: Math.max(0.5, 1 - i * 0.05),
                }}
              >
                {item.keyword}
                <span style={styles.keywordCount}>{item.count}</span>
              </div>
            ))
          ) : (
            <div style={styles.noData}>No keywords detected yet</div>
          )}
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '25px',
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
  overviewGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '15px',
  },
  overviewCard: {
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
    textAlign: 'center',
  },
  overviewLabel: {
    fontSize: '11px',
    color: '#666',
    letterSpacing: '2px',
    marginBottom: '8px',
  },
  overviewValue: {
    fontSize: '32px',
    fontFamily: "'Orbitron', sans-serif",
    fontWeight: 700,
    color: '#00ffff',
  },
  chartsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '20px',
  },
  chartCard: {
    padding: '25px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
  },
  chartTitle: {
    margin: '0 0 20px 0',
    fontSize: '14px',
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
  },
  legend: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginTop: '15px',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px',
    color: '#888',
  },
  legendDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
  },
  noData: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '200px',
    color: '#666',
    fontSize: '14px',
  },
  keywordsSection: {
    padding: '25px',
    background: 'linear-gradient(135deg, rgba(0,30,60,0.4) 0%, rgba(0,20,40,0.2) 100%)',
    border: '1px solid rgba(0,255,255,0.15)',
    borderRadius: '12px',
  },
  sectionTitle: {
    margin: '0 0 20px 0',
    fontSize: '14px',
    fontWeight: 700,
    color: '#00ffff',
    letterSpacing: '2px',
  },
  keywordsGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    justifyContent: 'center',
  },
  keywordTag: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    background: 'rgba(0,255,255,0.1)',
    border: '1px solid rgba(0,255,255,0.2)',
    borderRadius: '20px',
    color: '#00ffff',
    fontWeight: 500,
  },
  keywordCount: {
    fontSize: '10px',
    color: '#666',
    background: 'rgba(0,0,0,0.3)',
    padding: '2px 6px',
    borderRadius: '10px',
  },
};

export default AnalyticsPage;

