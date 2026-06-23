import { useState, useEffect, useCallback, useRef } from 'react';
import { useAppContext, Post } from '../context/AppContext';

const API_BASE = 'http://localhost:9000';

interface JobStatus {
  id: string;
  platform: string;
  sources: string[];
  limit: number;
  status: 'pending' | 'collecting' | 'analyzing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  total: number;
  phase_message: string;
  posts_count: number;
  summary: any;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

interface UseBackgroundJobReturn {
  // State
  currentJob: JobStatus | null;
  isRunning: boolean;
  posts: Post[];
  error: string | null;
  
  // Actions
  startJob: (
    platform: 'reddit' | 'telegram',
    sources: string[],
    limit?: number,
    analyzeImages?: boolean,
    llmAnalysis?: boolean
  ) => Promise<string | null>;
  cancelJob: () => Promise<void>;
  checkForActiveJob: () => Promise<void>;
}

function mapPostData(postData: any): Post {
  return {
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
    image_url: postData.image_url,
    thumbnail: postData.thumbnail,
    media_type: postData.media_type,
    gallery_images: postData.gallery_images,
    is_video: postData.is_video,
    video_url: postData.video_url,
    image_analysis: postData.image_analysis,
    annotated_image: postData.annotated_image,
    llm_analysis: postData.llm_analysis,
    risk_analysis: postData.risk_analysis,
    geo_location: postData.geo_location || null,
  };
}

export function useBackgroundJob(): UseBackgroundJobReturn {
  const { addPost, startCollection, stopCollection } = useAppContext();
  
  const [currentJob, setCurrentJob] = useState<JobStatus | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const pollingJobIdRef = useRef<string | null>(null);
  const syncedPostIdsRef = useRef<Set<string>>(new Set());

  const isRunning = currentJob?.status === 'pending' || 
                    currentJob?.status === 'collecting' || 
                    currentJob?.status === 'analyzing';

  const syncPostsToContext = useCallback((rawPosts: any[], jobId: string) => {
    if (pollingJobIdRef.current !== jobId) return;

    rawPosts.forEach((postData) => {
      const id = postData?.id;
      if (!id || syncedPostIdsRef.current.has(id)) return;
      syncedPostIdsRef.current.add(id);
      addPost(mapPostData(postData));
    });
  }, [addPost]);

  const beginTrackingJob = useCallback((jobId: string) => {
    if (pollingJobIdRef.current !== jobId) {
      pollingJobIdRef.current = jobId;
      syncedPostIdsRef.current = new Set();
    }
  }, []);

  // Poll for job updates
  const pollJobStatus = useCallback(async (jobId: string) => {
    if (pollingJobIdRef.current !== jobId) return;

    try {
      const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch job status');
      }
      const data = await response.json();
      if (pollingJobIdRef.current !== jobId) return;

      setCurrentJob(data.job);
      syncPostsToContext(data.posts || [], jobId);
      setPosts(data.posts || []);
      
      // Stop polling if job is done
      if (data.job.status === 'completed' || data.job.status === 'failed' || data.job.status === 'cancelled') {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        stopCollection();
      }
    } catch (err) {
      console.error('Error polling job status:', err);
    }
  }, [syncPostsToContext, stopCollection]);

  // Start polling for a job
  const startPolling = useCallback((jobId: string) => {
    beginTrackingJob(jobId);

    // Clear any existing polling
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    
    // Poll immediately
    pollJobStatus(jobId);
    
    // Then poll every second for live UI updates
    pollingRef.current = setInterval(() => {
      pollJobStatus(jobId);
    }, 1000);
  }, [pollJobStatus, beginTrackingJob]);

  // Check for active job on mount (for page refresh reconnection)
  const checkForActiveJob = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/jobs/current`);
      if (!response.ok) return;
      
      const data = await response.json();
      if (data.has_active_job && data.job) {
        beginTrackingJob(data.job.id);
        setCurrentJob(data.job);
        syncPostsToContext(data.posts || [], data.job.id);
        setPosts(data.posts || []);
        
        // Start polling for updates
        startPolling(data.job.id);
        const plat = (data.job.platform as 'reddit' | 'telegram') || 'reddit';
        startCollection(plat);
      }
    } catch (err) {
      console.error('Error checking for active job:', err);
    }
  }, [startPolling, startCollection, beginTrackingJob, syncPostsToContext]);

  // Start a new job
  const startJob = useCallback(async (
    platform: 'reddit' | 'telegram',
    sources: string[], 
    limit: number = 10,
    analyzeImages: boolean = true,
    llmAnalysis: boolean = true
  ): Promise<string | null> => {
    try {
      setError(null);
      setPosts([]);
      
      const response = await fetch(`${API_BASE}/api/jobs/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform,
          sources,
          limit,
          analyze_images: analyzeImages,
          llm_analysis: llmAnalysis
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start job');
      }
      
      const data = await response.json();
      beginTrackingJob(data.job_id);
      startCollection(platform);
      startPolling(data.job_id);
      
      return data.job_id;
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [startPolling, startCollection, beginTrackingJob]);

  // Cancel current job
  const cancelJob = useCallback(async () => {
    if (!currentJob) return;
    
    try {
      await fetch(`${API_BASE}/api/jobs/${currentJob.id}/cancel`, {
        method: 'POST'
      });
      
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      
      setCurrentJob(prev => prev ? { ...prev, status: 'cancelled' } : null);
      stopCollection();
    } catch (err) {
      console.error('Error cancelling job:', err);
    }
  }, [currentJob, stopCollection]);

  // Check for active job on mount
  useEffect(() => {
    checkForActiveJob();
    
    // Cleanup on unmount
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [checkForActiveJob]);

  return {
    currentJob,
    isRunning,
    posts,
    error,
    startJob,
    cancelJob,
    checkForActiveJob
  };
}

export default useBackgroundJob;
