import { useState, useEffect, useCallback, useRef } from 'react';
import { useAppContext, Post } from '../context/AppContext';
import { API_ORIGIN } from '../config/api';

const API_BASE = API_ORIGIN;

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

function mapApiPostToPost(postData: Record<string, unknown>): Post {
  return {
    id: String(postData.id),
    title: String(postData.title ?? ''),
    content: String(postData.content ?? ''),
    subreddit: postData.subreddit as string | undefined,
    channel: postData.channel as string | undefined,
    author_hash: String(postData.author_hash ?? ''),
    score: postData.score as number | undefined,
    num_comments: postData.num_comments as number | undefined,
    url: String(postData.url ?? ''),
    created_utc: postData.created_utc as number | undefined,
    collected_at: String(postData.collected_at ?? ''),
    platform: (postData.platform as Post['platform']) || 'reddit',
    image_url: postData.image_url as string | null | undefined,
    thumbnail: postData.thumbnail as string | null | undefined,
    media_type: postData.media_type as Post['media_type'] | undefined,
    gallery_images: postData.gallery_images as string[] | null | undefined,
    is_video: postData.is_video as boolean | undefined,
    video_url: postData.video_url as string | null | undefined,
    image_analysis: postData.image_analysis as Post['image_analysis'],
    annotated_image: postData.annotated_image as string | null | undefined,
    llm_analysis: postData.llm_analysis as Post['llm_analysis'],
    risk_analysis: postData.risk_analysis as Post['risk_analysis'],
  };
}

export function useBackgroundJob(): UseBackgroundJobReturn {
  const { addPost, addPosts, startCollection, stopCollection } = useAppContext();
  
  const [currentJob, setCurrentJob] = useState<JobStatus | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const lastPostCountRef = useRef<number>(0);

  const isRunning = currentJob?.status === 'pending' || 
                    currentJob?.status === 'collecting' || 
                    currentJob?.status === 'analyzing';

  // Poll for job updates
  const pollJobStatus = useCallback(async (jobId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch job status');
      }
      const data = await response.json();
      setCurrentJob(data.job);
      
      // Add new posts to the context
      if (data.posts && data.posts.length > lastPostCountRef.current) {
        const newPosts = data.posts.slice(lastPostCountRef.current);
        const mapped = newPosts.map((p: Record<string, unknown>) => mapApiPostToPost(p));
        mapped.forEach((post: Post) => addPost(post));
        lastPostCountRef.current = data.posts.length;
        setPosts(data.posts as unknown as Post[]);
      }
      
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
  }, [addPost, stopCollection]);

  // Start polling for a job
  const startPolling = useCallback((jobId: string) => {
    // Clear any existing polling
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    
    // Poll immediately
    pollJobStatus(jobId);
    
    // Then poll every 2 seconds
    pollingRef.current = setInterval(() => {
      pollJobStatus(jobId);
    }, 2000);
  }, [pollJobStatus]);

  // Check for active job on mount (for page refresh reconnection)
  const checkForActiveJob = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/jobs/current`);
      if (!response.ok) return;
      
      const data = await response.json();
      if (data.has_active_job && data.job) {
        setCurrentJob(data.job);
        setPosts(data.posts || []);
        lastPostCountRef.current = data.posts?.length || 0;
        
        // Start polling for updates
        startPolling(data.job.id);
        const plat = (data.job.platform as 'reddit' | 'telegram') || 'reddit';
        startCollection(plat);
      } else if (data.latest_job) {
        // Restore last finished job from local DB (backend SQLite) after page refresh
        setCurrentJob(data.latest_job as JobStatus);
        const lp = (data.latest_posts || []).map((p: Record<string, unknown>) => mapApiPostToPost(p));
        setPosts(lp);
        lastPostCountRef.current = lp.length;
        if (lp.length > 0) {
          addPosts(lp);
        }
        stopCollection();
      }
    } catch (err) {
      console.error('Error checking for active job:', err);
    }
  }, [startPolling, startCollection, addPosts, stopCollection]);

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
      lastPostCountRef.current = 0;
      
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
      startCollection(platform);
      
      // Start polling for the new job
      startPolling(data.job_id);
      
      return data.job_id;
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, [startPolling, startCollection]);

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

