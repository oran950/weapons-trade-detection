import { useEffect, useRef, useCallback, useState } from 'react';

interface SSEEvent {
  event: string;
  data: any;
}

interface UseSSEOptions {
  onPost?: (post: any) => void;
  onStart?: (data: any) => void;
  onComplete?: (data: any) => void;
  onError?: (error: any) => void;
  onInfo?: (data: any) => void;
  onPhase?: (data: any) => void;  // New: phase change event (collecting -> analyzing)
}

interface UseSSEReturn {
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  connect: (url: string) => void;
  disconnect: () => void;
}

export function useSSE(options: UseSSEOptions = {}): UseSSEReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const optionsRef = useRef(options);
  
  // Keep options ref updated
  optionsRef.current = options;

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      setIsLoading(false);
    }
  }, []);

  const connect = useCallback((url: string) => {
    // Close existing connection
    disconnect();
    
    setIsLoading(true);
    setError(null);

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        setIsLoading(true);
      };

      eventSource.onerror = (e) => {
        console.error('SSE Error:', e);
        setError('Connection error');
        setIsLoading(false);
        if (optionsRef.current.onError) {
          optionsRef.current.onError({ message: 'Connection failed' });
        }
        disconnect();
      };

      // Handle named events
      eventSource.addEventListener('start', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (optionsRef.current.onStart) {
            optionsRef.current.onStart(data);
          }
        } catch (err) {
          console.error('Failed to parse start event:', err);
        }
      });

      eventSource.addEventListener('post', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (optionsRef.current.onPost) {
            optionsRef.current.onPost(data);
          }
        } catch (err) {
          console.error('Failed to parse post event:', err);
        }
      });

      eventSource.addEventListener('complete', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (optionsRef.current.onComplete) {
            optionsRef.current.onComplete(data);
          }
          setIsLoading(false);
          disconnect();
        } catch (err) {
          console.error('Failed to parse complete event:', err);
        }
      });

      eventSource.addEventListener('error', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (optionsRef.current.onError) {
            optionsRef.current.onError(data);
          }
        } catch (err) {
          console.error('Failed to parse error event:', err);
        }
      });

      eventSource.addEventListener('info', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (optionsRef.current.onInfo) {
            optionsRef.current.onInfo(data);
          }
        } catch (err) {
          console.error('Failed to parse info event:', err);
        }
      });

      // Handle phase change event (collecting -> analyzing)
      eventSource.addEventListener('phase', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (optionsRef.current.onPhase) {
            optionsRef.current.onPhase(data);
          }
        } catch (err) {
          console.error('Failed to parse phase event:', err);
        }
      });

    } catch (err) {
      setError('Failed to create connection');
      setIsLoading(false);
    }
  }, [disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isLoading,
    error,
    connect,
    disconnect,
  };
}

export default useSSE;

