"""
Reddit Handler - Reddit data collection and processing
"""
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from ..entities.post import RedditPost
from ..entities.analysis import AnalysisResult
from ..utils.hashing import hash_username
from ..utils.rate_limiter import RateLimiter, RateLimitConfig
from ..utils.file_manager import FileManager
from ..core.analyzer import TextAnalyzer


class RedditHandler:
    """
    Handles Reddit data collection and processing
    """
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        user_agent: str,
        data_dir: str = "collected_data"
    ):
        """
        Initialize Reddit handler with credentials
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for API requests
            data_dir: Directory for storing collected data
        """
        try:
            import praw
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
        except ImportError:
            raise ImportError("PRAW library required. Install with: pip install praw")
        
        self.rate_limiter = RateLimiter(RateLimitConfig(
            requests_per_second=1.0,
            requests_per_minute=60
        ))
        self.file_manager = FileManager(data_dir)
        self.analyzer = TextAnalyzer()
        
        self.disclaimer = """
        ACADEMIC RESEARCH DATA COLLECTION
        This data is collected for legitimate academic research purposes only.
        All data handling follows academic ethics guidelines and privacy laws.
        """
        
        print("RedditHandler initialized successfully")
    
    def collect_subreddit_posts(
        self,
        subreddit_name: str,
        time_filter: str = "week",
        limit: int = 100,
        sort_method: str = "hot"
    ) -> List[RedditPost]:
        """
        Collect posts from a specific subreddit
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            time_filter: "hour", "day", "week", "month", "year", "all"
            limit: Maximum number of posts to collect
            sort_method: "hot", "new", "top", "rising"
            
        Returns:
            List of RedditPost objects
        """
        print(f"Collecting from r/{subreddit_name} (limit: {limit})")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            collected_posts = []
            
            # Choose sorting method
            if sort_method == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort_method == "new":
                posts = subreddit.new(limit=limit)
            elif sort_method == "top":
                posts = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_method == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                posts = subreddit.hot(limit=limit)
            
            for post in posts:
                # Skip stickied/distinguished posts
                if post.stickied or post.distinguished:
                    continue
                
                # Rate limiting
                self.rate_limiter.acquire()
                
                author_hash = hash_username(
                    str(post.author) if post.author else "anonymous"
                )
                
                # Use the enhanced from_praw_submission method for image extraction
                reddit_post = RedditPost.from_praw_submission(post, author_hash)
                
                collected_posts.append(reddit_post)
            
            print(f"Collected {len(collected_posts)} posts from r/{subreddit_name}")
            return collected_posts
            
        except Exception as e:
            print(f"Error collecting from r/{subreddit_name}: {str(e)}")
            return []
    
    def search_posts_by_keywords(
        self,
        subreddit_name: str,
        keywords: List[str],
        time_filter: str = "week",
        limit: int = 50
    ) -> List[RedditPost]:
        """
        Search for posts containing specific keywords
        
        Args:
            subreddit_name: Name of subreddit
            keywords: List of keywords to search
            time_filter: Time filter for search
            limit: Maximum results per keyword
            
        Returns:
            List of unique RedditPost objects
        """
        print(f"Searching r/{subreddit_name} for keywords: {keywords}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            collected_posts = []
            seen_ids = set()
            
            for keyword in keywords:
                self.rate_limiter.acquire()
                
                search_results = subreddit.search(
                    keyword,
                    time_filter=time_filter,
                    limit=limit // len(keywords)
                )
                
                for post in search_results:
                    if post.id in seen_ids:
                        continue
                    
                    if post.stickied or post.distinguished:
                        continue
                    
                    seen_ids.add(post.id)
                    
                    author_hash = hash_username(
                        str(post.author) if post.author else "anonymous"
                    )
                    
                    # Use the enhanced from_praw_submission method for image extraction
                    reddit_post = RedditPost.from_praw_submission(post, author_hash)
                    
                    collected_posts.append(reddit_post)
            
            return collected_posts
            
        except Exception as e:
            print(f"Error searching r/{subreddit_name}: {str(e)}")
            return []
    
    def analyze_posts(self, posts: List[RedditPost]) -> List[RedditPost]:
        """
        Analyze collected posts for weapons trade indicators
        
        Args:
            posts: List of RedditPost objects
            
        Returns:
            List of RedditPost objects with risk_analysis populated
        """
        print(f"Analyzing {len(posts)} posts...")
        
        analyzed_posts = []
        
        for post in posts:
            full_content = f"{post.title}. {post.content}".strip()
            
            if not full_content or full_content == ".":
                continue
            
            try:
                analysis = self.analyzer.analyze_text(full_content)
                post.risk_analysis = analysis.to_dict()
                analyzed_posts.append(post)
                
                if analysis.risk_score >= 0.7:
                    print(f"HIGH RISK: r/{post.subreddit}/{post.id} - Score: {analysis.risk_score:.2f}")
                    
            except Exception as e:
                print(f"Error analyzing post {post.id}: {str(e)}")
                continue
        
        return analyzed_posts
    
    def save_posts(
        self, 
        posts: List[RedditPost], 
        filename: str,
        include_csv: bool = True
    ) -> List[str]:
        """
        Save posts to files
        
        Args:
            posts: List of posts to save
            filename: Base filename (without extension)
            include_csv: Whether to also save as CSV
            
        Returns:
            List of saved file paths
        """
        saved_files = []
        
        posts_data = [asdict(post) for post in posts]
        
        # Save JSON
        json_data = {
            "collection_info": {
                "collected_at": datetime.now().isoformat(),
                "total_posts": len(posts),
                "disclaimer": self.disclaimer.strip()
            },
            "posts": posts_data
        }
        
        json_path = self.file_manager.save_json(json_data, filename, "raw")
        saved_files.append(json_path)
        
        # Save CSV
        if include_csv:
            csv_path = self.file_manager.save_csv(posts_data, filename, "raw")
            saved_files.append(csv_path)
        
        return saved_files
    
    def save_analyzed_posts(
        self, 
        posts: List[RedditPost], 
        filename: str
    ) -> Dict[str, Any]:
        """
        Save analyzed posts grouped by risk level
        
        Args:
            posts: List of analyzed posts
            filename: Base filename
            
        Returns:
            Summary dictionary
        """
        # Categorize by risk level
        high_risk = [p for p in posts if p.risk_analysis and p.risk_analysis.get('risk_score', 0) >= 0.7]
        medium_risk = [p for p in posts if p.risk_analysis and 0.4 <= p.risk_analysis.get('risk_score', 0) < 0.7]
        low_risk = [p for p in posts if p.risk_analysis and p.risk_analysis.get('risk_score', 0) < 0.4]
        
        summary = {
            "analysis_info": {
                "analyzed_at": datetime.now().isoformat(),
                "total_posts": len(posts),
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "disclaimer": self.disclaimer.strip()
            },
            "high_risk_posts": [asdict(p) for p in high_risk],
            "medium_risk_posts": [asdict(p) for p in medium_risk],
            "low_risk_posts": [asdict(p) for p in low_risk]
        }
        
        self.file_manager.save_json(summary, f"{filename}_analyzed", "analyzed")
        
        print(f"Analysis saved: {len(high_risk)} high, {len(medium_risk)} medium, {len(low_risk)} low risk")
        
        return summary

