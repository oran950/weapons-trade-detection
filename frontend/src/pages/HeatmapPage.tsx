import React, { useEffect, useRef, useMemo, useState } from 'react';
import { useAppContext, Post } from '../context/AppContext';
import { formatGeoSource } from '../utils/geoInference';
import { buildMapMarkers, markerColor } from '../utils/mapMarkers';
import DetailModal from '../components/Detection/DetailModal';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const HeatmapPage: React.FC = () => {
  const { posts, clearPosts } = useAppContext();
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const mapMarkers = useMemo(() => buildMapMarkers(posts), [posts]);

  const sourceBreakdown = useMemo(() => {
    const counts: Record<string, number> = {};
    mapMarkers.forEach(m => { counts[m.source] = (counts[m.source] || 0) + 1; });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [mapMarkers]);

  const platformBreakdown = useMemo(() => {
    const counts: Record<string, number> = {};
    mapMarkers.forEach(m => { counts[m.post.platform] = (counts[m.post.platform] || 0) + 1; });
    return counts;
  }, [mapMarkers]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = L.map(containerRef.current, { center: [30, 10], zoom: 2, minZoom: 2, worldCopyJump: true });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 19,
    }).addTo(map);
    markersLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
      markersLayerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = markersLayerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    if (mapMarkers.length === 0) {
      map.setView([30, 10], 2);
      return;
    }

    const bounds: L.LatLngExpression[] = [];

    mapMarkers.forEach(marker => {
      bounds.push([marker.lat, marker.lng]);
      const color = markerColor(marker.riskLevel);
      const circle = L.circleMarker([marker.lat, marker.lng], {
        radius: 8,
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
      });

      circle.bindTooltip(marker.post.title || 'Post', {
        direction: 'top',
        offset: [0, -8],
        className: 'heatmap-tooltip',
      });

      circle.on('click', () => setSelectedPost(marker.post));
      circle.addTo(layer);
    });

    if (bounds.length > 0) {
      map.fitBounds(L.latLngBounds(bounds).pad(0.2));
    }
  }, [mapMarkers]);

  const handleClearMap = () => {
    if (mapMarkers.length === 0) return;
    if (!window.confirm('Clear all posts from the map? This removes collected posts for this session.')) return;
    clearPosts();
    setSelectedPost(null);
    mapRef.current?.setView([30, 10], 2);
    markersLayerRef.current?.clearLayers();
  };

  return (
    <div style={styles.page}>
      <style>{`
        .heatmap-tooltip {
          background: rgba(0, 20, 40, 0.95) !important;
          border: 1px solid rgba(0, 255, 255, 0.4) !important;
          color: #e0e0e0 !important;
          font-family: Rajdhani, sans-serif !important;
          font-size: 12px !important;
          border-radius: 6px !important;
          padding: 6px 10px !important;
        }
        .leaflet-container { background: #0a1628; font-family: Rajdhani, sans-serif; }
      `}</style>

      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>GEO HEATMAP</h1>
          <p style={styles.subtitle}>
            Click any dot to view the post and image. Use Clear Map to remove all markers for this session.
          </p>
        </div>
        <div style={styles.headerStats}>
          <button
            type="button"
            style={{
              ...styles.clearButton,
              opacity: mapMarkers.length === 0 ? 0.45 : 1,
              cursor: mapMarkers.length === 0 ? 'not-allowed' : 'pointer',
            }}
            disabled={mapMarkers.length === 0}
            onClick={handleClearMap}
          >
            CLEAR MAP
          </button>
          <div style={styles.statBox}>
            <span style={styles.statValue}>{mapMarkers.length}</span>
            <span style={styles.statLabel}>Posts on Map</span>
          </div>
          <div style={styles.statBox}>
            <span style={styles.statValue}>{posts.length}</span>
            <span style={styles.statLabel}>Total Collected</span>
          </div>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.mapPanel}>
          <div ref={containerRef} style={styles.map} />
          {mapMarkers.length === 0 && (
            <div style={styles.emptyOverlay}>
              <span style={styles.emptyIcon}>🗺️</span>
              <p style={styles.emptyTitle}>No location data yet</p>
              <p style={styles.emptyText}>
                Collect posts from Reddit or Telegram. Each located post appears as its own clickable dot.
              </p>
            </div>
          )}
        </div>

        <aside style={styles.sidebar}>
          <h3 style={styles.sideTitle}>LOCATION SOURCES</h3>
          {sourceBreakdown.length === 0 ? (
            <p style={styles.sideEmpty}>No sources yet</p>
          ) : (
            sourceBreakdown.map(([source, count]) => (
              <div key={source} style={styles.sourceRow}>
                <span style={styles.sourceName}>{formatGeoSource(source)}</span>
                <span style={styles.sourceCount}>{count}</span>
              </div>
            ))
          )}

          <h3 style={{ ...styles.sideTitle, marginTop: '24px' }}>PLATFORMS</h3>
          <div style={styles.sourceRow}>
            <span style={styles.sourceName}>Reddit</span>
            <span style={styles.sourceCount}>{platformBreakdown.reddit || 0}</span>
          </div>
          <div style={styles.sourceRow}>
            <span style={styles.sourceName}>Telegram</span>
            <span style={styles.sourceCount}>{platformBreakdown.telegram || 0}</span>
          </div>

          <h3 style={{ ...styles.sideTitle, marginTop: '24px' }}>ALL POSTS ({mapMarkers.length})</h3>
          <div style={styles.pointList}>
            {mapMarkers.map(marker => (
              <button
                key={marker.post.id}
                type="button"
                style={styles.pointCard}
                onClick={() => setSelectedPost(marker.post)}
              >
                <div style={styles.pointTitle}>{marker.post.title || 'Untitled'}</div>
                <div style={styles.pointMeta}>
                  <span>{marker.post.platform.toUpperCase()}</span>
                  <span>•</span>
                  <span>{formatGeoSource(marker.source)}</span>
                </div>
                <div style={styles.pointLabel}>{marker.label}</div>
                <div style={{
                  ...styles.riskBadge,
                  color: markerColor(marker.riskLevel),
                  borderColor: markerColor(marker.riskLevel),
                }}>
                  {marker.riskLevel}
                </div>
              </button>
            ))}
          </div>
        </aside>
      </div>

      {selectedPost && (
        <DetailModal post={selectedPost} onClose={() => setSelectedPost(null)} />
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  page: { padding: '24px', height: '100%', display: 'flex', flexDirection: 'column', gap: '20px', overflow: 'hidden' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '20px', flexWrap: 'wrap' as const },
  title: { margin: 0, fontSize: '28px', fontWeight: 700, color: '#00ffff', letterSpacing: '3px', fontFamily: "'Orbitron', sans-serif" },
  subtitle: { margin: '8px 0 0', color: '#888', fontSize: '14px', maxWidth: '520px' },
  headerStats: { display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' as const },
  clearButton: {
    padding: '12px 20px',
    background: 'transparent',
    border: '1px solid rgba(255,68,68,0.5)',
    borderRadius: '8px',
    color: '#ff6666',
    fontSize: '12px',
    fontWeight: 700,
    letterSpacing: '1px',
    fontFamily: "'Rajdhani', sans-serif",
    transition: 'all 0.2s ease',
  },
  statBox: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '12px 20px', background: 'rgba(0,255,255,0.05)', border: '1px solid rgba(0,255,255,0.2)', borderRadius: '8px' },
  statValue: { fontSize: '24px', fontWeight: 700, color: '#00ffff' },
  statLabel: { fontSize: '11px', color: '#888', letterSpacing: '1px', marginTop: '4px' },
  content: { display: 'flex', gap: '20px', flex: 1, minHeight: 0 },
  mapPanel: { flex: 1, position: 'relative', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(0,255,255,0.15)', minHeight: '480px' },
  map: { width: '100%', height: '100%', minHeight: '480px', background: '#0a1628' },
  emptyOverlay: { position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,10,20,0.75)', pointerEvents: 'none', padding: '40px', textAlign: 'center' as const },
  emptyIcon: { fontSize: '48px', marginBottom: '16px' },
  emptyTitle: { fontSize: '20px', color: '#00ffff', margin: '0 0 8px', fontWeight: 600 },
  emptyText: { color: '#888', fontSize: '14px', maxWidth: '400px', margin: 0, lineHeight: 1.6 },
  sidebar: { width: '300px', minWidth: '300px', background: 'rgba(0,15,30,0.6)', border: '1px solid rgba(0,255,255,0.1)', borderRadius: '12px', padding: '20px', overflowY: 'auto' as const },
  sideTitle: { margin: '0 0 12px', fontSize: '11px', color: '#666', letterSpacing: '2px', fontWeight: 600 },
  sideEmpty: { color: '#666', fontSize: '13px', margin: 0 },
  sourceRow: { display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' },
  sourceName: { color: '#aaa', fontSize: '13px' },
  sourceCount: { color: '#00ffff', fontWeight: 700, fontSize: '14px' },
  pointList: { display: 'flex', flexDirection: 'column', gap: '10px' },
  pointCard: {
    padding: '12px',
    background: 'rgba(0,255,255,0.03)',
    border: '1px solid rgba(0,255,255,0.1)',
    borderRadius: '8px',
    cursor: 'pointer',
    textAlign: 'left' as const,
    width: '100%',
  },
  pointTitle: { color: '#ddd', fontSize: '13px', fontWeight: 600, marginBottom: '6px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const },
  pointMeta: { display: 'flex', gap: '6px', color: '#666', fontSize: '11px', marginBottom: '4px' },
  pointLabel: { color: '#888', fontSize: '11px', marginBottom: '8px' },
  riskBadge: { display: 'inline-block', padding: '2px 8px', border: '1px solid', borderRadius: '4px', fontSize: '10px', fontWeight: 700 },
};

export default HeatmapPage;
