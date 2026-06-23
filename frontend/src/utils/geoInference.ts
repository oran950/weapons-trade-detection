import type { GeoLocation, Post } from '../context/AppContext';

const KNOWN_LOCATIONS: Record<string, GeoLocation & { label: string }> = {
  ukraine: { latitude: 48.3794, longitude: 31.1656, label: 'Ukraine', source: 'subreddit' },
  gaza: { latitude: 31.3547, longitude: 34.3088, label: 'Gaza', source: 'text' },
  israel: { latitude: 31.0461, longitude: 34.8516, label: 'Israel', source: 'text' },
  russia: { latitude: 61.5240, longitude: 105.3188, label: 'Russia', source: 'text' },
  syria: { latitude: 34.8021, longitude: 38.9968, label: 'Syria', source: 'text' },
  iraq: { latitude: 33.2232, longitude: 43.6793, label: 'Iraq', source: 'text' },
  iran: { latitude: 32.4279, longitude: 53.6880, label: 'Iran', source: 'text' },
  usa: { latitude: 39.8283, longitude: -98.5795, label: 'United States', source: 'subreddit' },
  'united states': { latitude: 39.8283, longitude: -98.5795, label: 'United States', source: 'subreddit' },
};

const SOURCE_LOCATIONS: Record<string, GeoLocation & { label: string }> = {
  uaweapons: { latitude: 48.3794, longitude: 31.1656, label: 'Ukraine (channel)', source: 'channel' },
  russianarms: { latitude: 55.7558, longitude: 37.6173, label: 'Russia (channel)', source: 'channel' },
  rybar: { latitude: 55.7558, longitude: 37.6173, label: 'Russia (Rybar)', source: 'channel' },
  nexta_tv: { latitude: 53.9006, longitude: 27.5590, label: 'Belarus (NEXTA)', source: 'channel' },
  comblocmarket: { latitude: 50.0, longitude: 30.0, label: 'Eastern Europe', source: 'subreddit' },
  ak47: { latitude: 50.0, longitude: 30.0, label: 'AK / Eastern bloc', source: 'subreddit' },
};

const US_SUBREDDITS = new Set([
  'gundeals', 'guns', 'firearms', 'ar15', 'glocks', 'nfa', 'gunporn', 'ccw', 'edc',
  'gunsforsale', 'gunaccessoriesforsale', 'tacticalgear', 'ammo', 'reloading',
]);

function normalizeKey(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/^r/, '');
}

export function inferGeoFromPost(post: Post): GeoLocation | null {
  if (post.geo_location?.latitude != null && post.geo_location?.longitude != null) {
    return post.geo_location;
  }

  const text = `${post.title} ${post.content} ${post.subreddit || ''} ${post.channel || ''}`.toLowerCase();

  for (const [name, loc] of Object.entries(KNOWN_LOCATIONS).sort((a, b) => b[0].length - a[0].length)) {
    if (new RegExp(`\\b${name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`).test(text)) {
      return { latitude: loc.latitude, longitude: loc.longitude, label: loc.label, source: loc.source };
    }
  }

  const coordMatch = text.match(/(-?\d{1,2}\.\d{3,8})\s*[,;/]\s*(-?\d{1,3}\.\d{3,8})/);
  if (coordMatch) {
    const lat = parseFloat(coordMatch[1]);
    const lng = parseFloat(coordMatch[2]);
    if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
      return { latitude: lat, longitude: lng, label: `Coordinates (${lat.toFixed(4)}, ${lng.toFixed(4)})`, source: 'coordinates' };
    }
  }

  for (const raw of [post.channel, post.subreddit?.replace(/^@/, ''), post.subreddit]) {
    if (!raw) continue;
    const key = normalizeKey(raw);
    if (SOURCE_LOCATIONS[key]) {
      const loc = SOURCE_LOCATIONS[key];
      return { latitude: loc.latitude, longitude: loc.longitude, label: loc.label, source: loc.source };
    }
    if (US_SUBREDDITS.has(key)) {
      return { latitude: 39.8283, longitude: -98.5795, label: `United States (r/${key})`, source: 'subreddit' };
    }
  }

  if (post.platform === 'reddit') {
    return { latitude: 39.8283, longitude: -98.5795, label: 'United States (Reddit firearms community)', source: 'subreddit' };
  }

  return null;
}

export function formatGeoSource(source: string): string {
  const labels: Record<string, string> = {
    metadata: 'Post Metadata',
    photo_exif: 'Photo EXIF',
    ip: 'IP Geolocation',
    text: 'Text Location',
    coordinates: 'Coordinates in Text',
    subreddit: 'Subreddit / Source',
    channel: 'Telegram Channel',
    link_domain: 'Link Domain',
    geocoded: 'Geocoded Place',
  };
  return labels[source] || source;
}
