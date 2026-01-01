// API Response Types
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  python_version: string;
  reddit_configured: boolean;
  telegram_configured?: boolean;
  ollama_available?: boolean;
}

export interface AnalysisResult {
  risk_score: number;
  confidence: number;
  flags: string[];
  detected_keywords: string[];
  detected_patterns: string[];
  analysis_time: string;
}

// Weapon detection types
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

export interface RedditPost {
  id: string;
  title: string;
  content: string;
  subreddit: string;
  author_hash: string;
  score: number;
  num_comments: number;
  created_utc: number;
  url: string;
  collected_at: string;
  risk_analysis?: AnalysisResult;
  // Media fields
  image_url?: string | null;
  thumbnail?: string | null;
  media_type?: 'image' | 'video' | 'gallery' | 'link' | 'text';
  gallery_images?: string[] | null;
  is_video?: boolean;
  video_url?: string | null;
  platform?: string;
  // Weapon detection fields
  image_analysis?: ImageAnalysis | null;
  annotated_image?: string | null;  // Base64 encoded annotated image
  // LLM illegal trade analysis
  llm_analysis?: LLMAnalysis | null;
}

export interface TelegramMessage {
  id: number;
  channel: string;
  text: string;
  date: string;
  views?: number;
  forwards?: number;
  has_media: boolean;
  collected_at: string;
  risk_analysis?: AnalysisResult;
}

// Dashboard Types
export interface LiveDataEntry {
  id: number;
  type: 'HIGH RISK' | 'MEDIUM RISK' | 'MONITORING';
  location: string;
  threat: string;
  confidence: string;
  timestamp: Date;
}

export interface HighRiskPost {
  id: string;
  title: string;
  content: string;
  subreddit: string;
  risk: number;
  keywords: string[];
  time: string;
  url?: string;
}

export interface StatCard {
  label: string;
  value: string | number;
  color: string;
  icon: string;
}

export interface SystemStats {
  postsAnalyzed: number;
  platformsMonitored: number;
  activeScans: number;
  accuracy: number;
  highRiskCount: number;
  mediumRiskCount: number;
  lowRiskCount: number;
}

// Collection Types
export interface CollectionParams {
  subreddits?: string[];
  channels?: string[];
  keywords?: string[];
  limit: number;
}

export interface CollectionResult {
  success: boolean;
  posts_collected: number;
  high_risk_posts: number;
  medium_risk_posts: number;
  low_risk_posts: number;
  posts: RedditPost[] | TelegramMessage[];
}

