"""
Metrics and telemetry for the backend service
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class MetricsCollector:
    """
    Collects and aggregates metrics for the weapons detection system
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._start_time = datetime.now()
    
    def increment(self, name: str, value: int = 1):
        """Increment a counter"""
        with self._lock:
            self._counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge value"""
        with self._lock:
            self._gauges[name] = value
    
    def record_histogram(self, name: str, value: float):
        """Record a value in a histogram"""
        with self._lock:
            self._histograms[name].append(value)
            # Keep only last 1000 values
            if len(self._histograms[name]) > 1000:
                self._histograms[name] = self._histograms[name][-1000:]
    
    def get_counter(self, name: str) -> int:
        """Get counter value"""
        return self._counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value"""
        return self._gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        values = self._histograms.get(name, [])
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0}
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        return {
            "count": n,
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "avg": sum(sorted_vals) / n,
            "p50": sorted_vals[n // 2],
            "p95": sorted_vals[int(n * 0.95)] if n > 20 else sorted_vals[-1]
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self._lock:
            histograms = {
                name: self.get_histogram_stats(name)
                for name in self._histograms
            }
            
            return {
                "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": histograms,
                "collected_at": datetime.now().isoformat()
            }
    
    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._start_time = datetime.now()


# Predefined metric names
class MetricNames:
    # Counters
    ANALYSES_TOTAL = "analyses_total"
    ANALYSES_HIGH_RISK = "analyses_high_risk"
    ANALYSES_MEDIUM_RISK = "analyses_medium_risk"
    ANALYSES_LOW_RISK = "analyses_low_risk"
    COLLECTIONS_TOTAL = "collections_total"
    COLLECTIONS_REDDIT = "collections_reddit"
    COLLECTIONS_TELEGRAM = "collections_telegram"
    LLM_CALLS_TOTAL = "llm_calls_total"
    LLM_CALLS_FAILED = "llm_calls_failed"
    ERRORS_TOTAL = "errors_total"
    
    # Gauges
    ACTIVE_CONNECTIONS = "active_connections"
    QUEUE_SIZE = "queue_size"
    
    # Histograms
    ANALYSIS_DURATION_MS = "analysis_duration_ms"
    LLM_LATENCY_MS = "llm_latency_ms"
    COLLECTION_DURATION_S = "collection_duration_s"


# Global metrics instance
metrics = MetricsCollector()

