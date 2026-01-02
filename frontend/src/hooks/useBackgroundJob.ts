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
  error: string | null;
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
  startJob: (sources: string[], limit?: number, analyzeImages?: boolean, llmAnalysis?: boolean) => Promise<string | null>;
  cancelJob: () => Promise<void>;
  checkForActiveJob: () => Promise<void>;
}

export function useBackgroundJob(): UseBackgroundJobReturn {
  const { addPost, startCollection, stopCollection } = useAppContext();
  
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
        newPosts.forEach((postData: any) => {
          const post: Post = {
            id: postData.id,
            title: postData.title,
            content: postData.content,
            subreddit: postData.subreddit,
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
          };
          addPost(post);
        });
        lastPostCountRef.current = data.posts.length;
        setPosts(data.posts);
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
        startCollection('reddit');
      }
    } catch (err) {
      console.error('Error checking for active job:', err);
    }
  }, [startPolling, startCollection]);

  // Start a new job
  const startJob = useCallback(async (
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
          platform: 'reddit',
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
      startCollection('reddit');
      
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

