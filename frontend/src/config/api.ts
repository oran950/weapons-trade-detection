/**
 * Backend origin (scheme + host + optional port), no trailing slash.
 * Cloudflare Pages: set REACT_APP_API_URL to your deployed API, e.g. https://api.example.com
 * Accepts legacy values ending in /api (stripped).
 */
function normalizeApiOrigin(): string {
  const raw = (process.env.REACT_APP_API_URL || 'http://localhost:9000').trim();
  if (!raw) return 'http://localhost:9000';
  const withoutApiSuffix = raw.replace(/\/api\/?$/i, '');
  const origin = withoutApiSuffix.replace(/\/$/, '');
  return origin || 'http://localhost:9000';
}

export const API_ORIGIN = normalizeApiOrigin();
