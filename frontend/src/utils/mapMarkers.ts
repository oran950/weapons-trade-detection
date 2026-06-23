import type { Post } from '../context/AppContext';
import { inferGeoFromPost } from './geoInference';

export interface MapMarker {
  post: Post;
  lat: number;
  lng: number;
  label: string;
  source: string;
  riskLevel: string;
}

type RawMarker = MapMarker;

/** Spread overlapping posts into a visible ring so each has its own dot. */
function spreadOverlapping(markers: RawMarker[]): MapMarker[] {
  const groups = new Map<string, RawMarker[]>();
  for (const m of markers) {
    const key = `${m.lat.toFixed(3)},${m.lng.toFixed(3)}`;
    const list = groups.get(key) || [];
    list.push(m);
    groups.set(key, list);
  }

  const result: MapMarker[] = [];
  for (const group of groups.values()) {
    const n = group.length;
    const centerLat = group[0].lat;
    const centerLng = group[0].lng;
    if (n === 1) {
      result.push(group[0]);
      continue;
    }
    const radius = Math.min(0.15 + n * 0.04, 1.2);
    group.forEach((item, i) => {
      const angle = (2 * Math.PI * i) / n;
      result.push({
        ...item,
        lat: centerLat + Math.sin(angle) * radius,
        lng: centerLng + Math.cos(angle) * radius,
      });
    });
  }
  return result;
}

export function buildMapMarkers(posts: Post[]): MapMarker[] {
  const raw: RawMarker[] = [];
  for (const post of posts) {
    const geo = post.geo_location || inferGeoFromPost(post);
    if (!geo || typeof geo.latitude !== 'number' || typeof geo.longitude !== 'number') continue;
    raw.push({
      post,
      lat: geo.latitude,
      lng: geo.longitude,
      label: geo.label,
      source: geo.source,
      riskLevel: post.risk_analysis?.risk_level || 'LOW',
    });
  }
  return spreadOverlapping(raw);
}

export function markerColor(riskLevel: string): string {
  if (riskLevel === 'CRITICAL' || riskLevel === 'HIGH') return '#ff3366';
  if (riskLevel === 'MEDIUM') return '#ffaa00';
  return '#00ffff';
}

export function getPostImageSrc(post: Post): string | null {
  if (post.annotated_image) {
    return post.annotated_image.startsWith('data:')
      ? post.annotated_image
      : `data:image/jpeg;base64,${post.annotated_image}`;
  }
  if (post.image_url) return post.image_url;
  if (post.gallery_images?.length) return post.gallery_images[0];
  if (post.thumbnail && post.thumbnail.startsWith('http')) return post.thumbnail;
  return null;
}
