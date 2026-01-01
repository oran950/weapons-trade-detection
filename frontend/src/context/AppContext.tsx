import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

// Types
export interface WeaponDetection {
  weapon_type: string;
  confidence: number;
  description: string;
  location_hint: string;
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface ImageAnalysis {
  contains_weapons: boolean;
  weapon_count: number;
  detections?: WeaponDetection[];
  overall_risk?: 'HIGH' | 'MEDIUM' | 'LOW';
  analysis_notes?: string;
  processing_time_ms?: number;
  error?: string;
  // When no weapons detected
  image_verified_safe?: boolean;
  risk_reduction_applied?: number;
}

// LLM illegal trade analysis
export interface LLMAnalysis {
  is_weapon_related: boolean;
  is_trade_related: boolean;
  is_potentially_illegal: boolean;
  illegality_reason?: string | null;
  weapon_types_mentioned: string[];
  trade_indicators: string[];
  risk_assessment: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
  confidence: number;
  summary: string;
  recommendation: 'INVESTIGATE' | 'FLAG' | 'MONITOR' | 'IGNORE' | 'RETRY';
  processing_time_ms: number;
  error?: string;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  subreddit?: string;
  channel?: string;
  author_hash: string;
  score?: number;
  num_comments?: number;
  url: string;
  created_utc?: number;
  collected_at: string;
  platform: 'reddit' | 'telegram';
  // Media fields for images/videos
  image_url?: string | null;
  thumbnail?: string | null;
  media_type?: 'image' | 'video' | 'gallery' | 'link' | 'text';
  gallery_images?: string[] | null;
  is_video?: boolean;
  video_url?: string | null;
  // Weapon detection fields
  image_analysis?: ImageAnalysis | null;
  annotated_image?: string | null;
  // LLM illegal trade analysis
  llm_analysis?: LLMAnalysis | null;
  risk_analysis?: {
    risk_score: number;
    risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
    confidence: number;
    flags: string[];
    detected_keywords: string[];
    detected_patterns: string[];
  };
}

export interface CollectionSession {
  id: string;
  platform: 'reddit' | 'telegram';
  timestamp: string;
  sources: string[];
  total_collected: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  posts: Post[];
}

export interface AppState {
  // Collection state
  isCollecting: boolean;
  collectionPlatform: 'reddit' | 'telegram' | null;
  collectionProgress: number;
  
  // Data
  posts: Post[];
  sessions: CollectionSession[];
  
  // Stats
  stats: {
    totalAnalyzed: number;
    highRiskCount: number;
    mediumRiskCount: number;
    lowRiskCount: number;
    platformsMonitored: number;
  };
  
  // Backend status
  backendOnline: boolean;
  redditConfigured: boolean;
  telegramConfigured: boolean;
  ollamaAvailable: boolean;
}

interface AppContextType extends AppState {
  // Actions
  startCollection: (platform: 'reddit' | 'telegram') => void;
  stopCollection: () => void;
  addPost: (post: Post) => void;
  addPosts: (posts: Post[]) => void;
  clearPosts: () => void;
  addSession: (session: CollectionSession) => void;
  updateStats: (stats: Partial<AppState['stats']>) => void;
  setBackendStatus: (online: boolean, config?: {
    reddit?: boolean;
    telegram?: boolean;
    ollama?: boolean;
  }) => void;
}

const defaultState: AppState = {
  isCollecting: false,
  collectionPlatform: null,
  collectionProgress: 0,
  posts: [],
  sessions: [],
  stats: {
    totalAnalyzed: 0,
    highRiskCount: 0,
    mediumRiskCount: 0,
    lowRiskCount: 0,
    platformsMonitored: 4,
  },
  backendOnline: false,
  redditConfigured: false,
  telegramConfigured: false,
  ollamaAvailable: false,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>(defaultState);

  const startCollection = useCallback((platform: 'reddit' | 'telegram') => {
    setState(prev => ({
      ...prev,
      isCollecting: true,
      collectionPlatform: platform,
      collectionProgress: 0,
    }));
  }, []);

  const stopCollection = useCallback(() => {
    setState(prev => ({
      ...prev,
      isCollecting: false,
      collectionPlatform: null,
      collectionProgress: 100,
    }));
  }, []);

  const addPost = useCallback((post: Post) => {
    setState(prev => {
      const riskLevel = post.risk_analysis?.risk_level || 'LOW';
      return {
        ...prev,
        posts: [post, ...prev.posts].slice(0, 500), // Keep max 500 posts
        stats: {
          ...prev.stats,
          totalAnalyzed: prev.stats.totalAnalyzed + 1,
          highRiskCount: prev.stats.highRiskCount + (riskLevel === 'HIGH' ? 1 : 0),
          mediumRiskCount: prev.stats.mediumRiskCount + (riskLevel === 'MEDIUM' ? 1 : 0),
          lowRiskCount: prev.stats.lowRiskCount + (riskLevel === 'LOW' ? 1 : 0),
        },
      };
    });
  }, []);

  const addPosts = useCallback((posts: Post[]) => {
    setState(prev => {
      let highDelta = 0, mediumDelta = 0, lowDelta = 0;
      posts.forEach(p => {
        const level = p.risk_analysis?.risk_level || 'LOW';
        if (level === 'HIGH') highDelta++;
        else if (level === 'MEDIUM') mediumDelta++;
        else lowDelta++;
      });
      return {
        ...prev,
        posts: [...posts, ...prev.posts].slice(0, 500),
        stats: {
          ...prev.stats,
          totalAnalyzed: prev.stats.totalAnalyzed + posts.length,
          highRiskCount: prev.stats.highRiskCount + highDelta,
          mediumRiskCount: prev.stats.mediumRiskCount + mediumDelta,
          lowRiskCount: prev.stats.lowRiskCount + lowDelta,
        },
      };
    });
  }, []);

  const clearPosts = useCallback(() => {
    setState(prev => ({ ...prev, posts: [] }));
  }, []);

  const addSession = useCallback((session: CollectionSession) => {
    setState(prev => ({
      ...prev,
      sessions: [session, ...prev.sessions].slice(0, 50),
    }));
  }, []);

  const updateStats = useCallback((stats: Partial<AppState['stats']>) => {
    setState(prev => ({
      ...prev,
      stats: { ...prev.stats, ...stats },
    }));
  }, []);

  const setBackendStatus = useCallback((online: boolean, config?: {
    reddit?: boolean;
    telegram?: boolean;
    ollama?: boolean;
  }) => {
    setState(prev => ({
      ...prev,
      backendOnline: online,
      redditConfigured: config?.reddit ?? prev.redditConfigured,
      telegramConfigured: config?.telegram ?? prev.telegramConfigured,
      ollamaAvailable: config?.ollama ?? prev.ollamaAvailable,
    }));
  }, []);

  return (
    <AppContext.Provider
      value={{
        ...state,
        startCollection,
        stopCollection,
        addPost,
        addPosts,
        clearPosts,
        addSession,
        updateStats,
        setBackendStatus,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

export default AppContext;

