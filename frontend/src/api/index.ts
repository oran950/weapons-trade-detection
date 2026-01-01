import type { 
  HealthResponse, 
  AnalysisResult, 
  CollectionResult,
  RedditPost 
} from '../types';

const API_BASE = 'http://localhost:9000';

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

  // Collect from Telegram
  async collectTelegram(channels: string[], limit: number = 50): Promise<CollectionResult> {
    const response = await fetch(`${API_BASE}/api/collection/telegram`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channels, limit })
    });
    if (!response.ok) throw new Error('Telegram collection failed');
    return response.json();
  },

  // Get Reddit config status
  async getRedditStatus(): Promise<any> {
    const response = await fetch(`${API_BASE}/api/reddit/config-status`);
    if (!response.ok) throw new Error('Failed to get Reddit status');
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

