import type { 
  HealthResponse, 
  AnalysisResult, 
  RedditPost,
  OsintPdfPayload,
} from '../types';

const API_BASE = 'http://localhost:9000';

/** Backend routes live under /api. Env may be origin only (e.g. Docker) or include /api. */
function apiRootWithPrefix(): string {
  const raw = (process.env.REACT_APP_API_URL || 'http://localhost:9000').replace(/\/+$/, '');
  if (raw.endsWith('/api')) {
    return raw;
  }
  return `${raw}/api`;
}

const API_ROOT = apiRootWithPrefix();

async function parseApiError(response: Response): Promise<string> {
  const err = (await response.json().catch(() => ({}))) as {
    detail?: string | Array<{ msg?: string }>;
  };
  const d = err.detail;
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) return d.map((x) => x.msg || JSON.stringify(x)).join('; ');
  return `Request failed (${response.status})`;
}

/** Download OSINT-style PDF from POST /api/reports/osint-pdf */
export async function exportOsintPdf(payload: OsintPdfPayload): Promise<void> {
  const response = await fetch(`${API_ROOT}/reports/osint-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }
  const blob = await response.blob();
  const cd = response.headers.get('Content-Disposition');
  let filename = 'OSINT-Report.pdf';
  const m = cd?.match(/filename="([^"]+)"/i);
  if (m) filename = m[1];
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export const api = {
  // Health check
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Backend not available');
    return response.json();
  },

  // Analyze text
  async analyze(text: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE}/api/detection/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text })
    });
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
  },

  // Collect from Reddit
  async collectReddit(subreddits: string[], limit: number = 25): Promise<any> {
    const response = await fetch(`${API_BASE}/api/reddit/collect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        parameters: {
          subreddits,
          timeFilter: 'day',
          sortMethod: 'hot',
          limit_per_subreddit: limit,
          keywords: '',
          include_all_defaults: false
        }
      })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Reddit collection failed');
    }
    return response.json();
  },

  /** Start background Telegram collection (same job API as Dashboard). */
  async collectTelegram(
    channels: string[],
    limit: number = 50
  ): Promise<{ success: boolean; job_id: string; message?: string }> {
    const response = await fetch(`${API_BASE}/api/jobs/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform: 'telegram',
        sources: channels,
        limit,
        analyze_images: true,
        llm_analysis: true,
      }),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error((err as { detail?: string }).detail || 'Telegram job start failed');
    }
    return response.json();
  },

  // Get Reddit config status
  async getRedditStatus(): Promise<any> {
    const response = await fetch(`${API_BASE}/api/reddit/config-status`);
    if (!response.ok) throw new Error('Failed to get Reddit status');
    return response.json();
  },

  async getTelegramConfigStatus(): Promise<{
    is_configured?: boolean;
    user_api_ready_for_collection?: boolean;
    session_file_exists?: boolean;
    session_file_path?: string;
    missing_user_api_config?: string[];
  }> {
    const response = await fetch(`${API_BASE}/api/telegram/config-status`);
    if (!response.ok) throw new Error('Failed to get Telegram status');
    return response.json();
  },

  // Get recent high-risk posts
  async getRecentPosts(): Promise<RedditPost[]> {
    try {
      const response = await fetch(`${API_BASE}/api/reddit/files`);
      if (!response.ok) return [];
      return response.json();
    } catch {
      return [];
    }
  },

  // Generate synthetic content
  async generateContent(contentType: string, intensity: string): Promise<any> {
    const response = await fetch(`${API_BASE}/api/generation/content`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        content_type: contentType,
        intensity_level: intensity,
        quantity: 1
      })
    });
    if (!response.ok) throw new Error('Generation failed');
    return response.json();
  }
};

export default api;

