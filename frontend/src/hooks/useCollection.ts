import { useState, useCallback } from 'react';
import { useSSE } from './useSSE';
import { useAppContext, Post, CollectionSession } from '../context/AppContext';
import { API_ORIGIN } from '../config/api';

const API_BASE = API_ORIGIN;

interface CollectionConfig {
  platform: 'reddit' | 'telegram';
  sources: string[]; // subreddits or channels
  limit: number;
}

export function useCollection() {
  const {
    isCollecting,
    collectionPlatform,
    startCollection,
    stopCollection,
    addPost,
    addSession,
  } = useAppContext();

  const [collectedPosts, setCollectedPosts] = useState<Post[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [progress, setProgress] = useState<{ current: number; total: number }>({ current: 0, total: 0 });
  const [phase, setPhase] = useState<'idle' | 'collecting' | 'analyzing' | 'complete'>('idle');
  const [phaseMessage, setPhaseMessage] = useState<string>('');

  const handleStart = useCallback((data: any) => {
    const sourceCount =
      (data.subreddits?.length ?? 0) ||
      (data.channels?.length ?? 0) ||
      0;
    const total = data.total_posts || 50;
    setProgress({ current: 0, total });
    setPhase('collecting');
    setPhaseMessage(
      `Collecting ${total} items from ${sourceCount} source(s)...`
    );
  }, []);

  const handlePhase = useCallback((data: any) => {
    // Phase change: collecting -> analyzing
    setPhase(data.phase || 'analyzing');
    setPhaseMessage(data.message || 'Analyzing posts with AI...');
    if (data.total_to_analyze) {
      setProgress(prev => ({ current: 0, total: data.total_to_analyze }));
    }
  }, []);

  const handlePost = useCallback((postData: any) => {
    const post: Post = {
      id: postData.id,
      title: postData.title,
      content: postData.content,
      subreddit: postData.subreddit,
      channel: postData.channel ?? postData.chat_title,
      author_hash: postData.author_hash,
      score: postData.score,
      num_comments: postData.num_comments,
      url: postData.url,
      created_utc: postData.created_utc,
      collected_at: postData.collected_at,
      platform: postData.platform || 'reddit',
      // Media fields - IMPORTANT for Media Library
      image_url: postData.image_url,
      thumbnail: postData.thumbnail,
      media_type: postData.media_type,
      gallery_images: postData.gallery_images,
      is_video: postData.is_video,
      video_url: postData.video_url,
      // Weapon detection fields
      image_analysis: postData.image_analysis,
      annotated_image: postData.annotated_image,
      // LLM illegal trade analysis
      llm_analysis: postData.llm_analysis,
      risk_analysis: postData.risk_analysis,
    };
    
    addPost(post);
    setCollectedPosts(prev => [post, ...prev]);
    setProgress(prev => ({ ...prev, current: prev.current + 1 }));
  }, [addPost]);

  const handleComplete = useCallback((data: any) => {
    setSummary(data);
    setPhase('complete');
    setPhaseMessage('Analysis complete!');
    stopCollection();

    // Create session record
    const platform =
      collectionPlatform ||
      (data.channels_collected?.length ? 'telegram' : 'reddit');
    const session: CollectionSession = {
      id: `session_${Date.now()}`,
      platform,
      timestamp: data.timestamp,
      sources: data.channels_collected || data.subreddits_collected || [],
      total_collected: data.total_collected,
      high_risk: data.high_risk_count,
      medium_risk: data.medium_risk_count,
      low_risk: data.low_risk_count,
      posts: [...collectedPosts],
    };
    addSession(session);
  }, [stopCollection, addSession, collectedPosts, collectionPlatform]);

  const handleError = useCallback((error: any) => {
    console.error('Collection error:', error);
    stopCollection();
    setPhase('idle');
  }, [stopCollection]);

  const handleDisconnect = useCallback(() => {
    // Clean up collection state when SSE connection is closed (e.g., navigation away)
    stopCollection();
    setPhase('idle');
  }, [stopCollection]);

  const { connect, disconnect, isLoading, error } = useSSE({
    onPost: handlePost,
    onComplete: handleComplete,
    onError: handleError,
    onStart: handleStart,
    onPhase: handlePhase,
    onDisconnect: handleDisconnect,
  });

  const startRedditCollection = useCallback((subreddits: string[], limit: number = 10) => {
    setCollectedPosts([]);
    setSummary(null);
    setProgress({ current: 0, total: subreddits.length * limit });
    setPhase('collecting');
    setPhaseMessage('Scraping posts from Reddit...');
    startCollection('reddit');
    
    const url = `${API_BASE}/api/stream/reddit?subreddits=${encodeURIComponent(subreddits.join(','))}&limit=${limit}`;
    connect(url);
  }, [startCollection, connect]);

  const startTelegramCollection = useCallback((channels: string[], limit: number = 50) => {
    setCollectedPosts([]);
    setSummary(null);
    setProgress({ current: 0, total: channels.length * limit });
    setPhase('collecting');
    setPhaseMessage('Scraping messages from Telegram...');
    startCollection('telegram');
    
    const url = `${API_BASE}/api/stream/telegram?channels=${encodeURIComponent(channels.join(','))}&limit=${limit}`;
    connect(url);
  }, [startCollection, connect]);

  const cancelCollection = useCallback(() => {
    disconnect();
    stopCollection();
  }, [disconnect, stopCollection]);

  return {
    isCollecting: isCollecting || isLoading,
    collectedPosts,
    summary,
    error,
    progress,
    phase,           // 'idle' | 'collecting' | 'analyzing' | 'complete'
    phaseMessage,    // Human-readable phase status
    startRedditCollection,
    startTelegramCollection,
    cancelCollection,
  };
}

export default useCollection;

