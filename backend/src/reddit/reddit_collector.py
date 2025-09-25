import praw
import json
import time
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import hashlib
from dataclasses import dataclass, asdict

@dataclass
class RedditPost:
    """Data structure for collected Reddit posts"""
    id: str
    title: str
    content: str
    subreddit: str
    author_hash: str  # Hashed for privacy
    score: int
    num_comments: int
    created_utc: float
    url: str
    collected_at: str
    risk_analysis: Optional[Dict] = None

class AcademicRedditCollector:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize Reddit collector with proper authentication
        
        IMPORTANT: You must:
        1. Register your application with Reddit
        2. Get proper academic research approval
        3. Follow Reddit's API terms of service
        4. Implement proper rate limiting
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Create data directory
        self.data_dir = "collected_data"
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/raw_posts", exist_ok=True)
        os.makedirs(f"{self.data_dir}/analyzed_posts", exist_ok=True)
        
        # Academic research disclaimer
        self.disclaimer = """
        ACADEMIC RESEARCH DATA COLLECTION
        This data is collected for legitimate academic research purposes only.
        All data handling follows academic ethics guidelines and privacy laws.
        """
        
        print(self.disclaimer)
    
    def hash_username(self, username: str) -> str:
        """Hash usernames for privacy protection"""
        if not username or username == "[deleted]":
            return "anonymous"
        return hashlib.sha256(username.encode()).hexdigest()[:16]
    
    def collect_subreddit_posts(self, 
                               subreddit_name: str, 
                               time_filter: str = "week",
                               limit: int = 100,
                               sort_method: str = "hot") -> List[RedditPost]:
        """
        Collect posts from a specific subreddit
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            time_filter: "hour", "day", "week", "month", "year", "all"
            limit: Maximum number of posts to collect
            sort_method: "hot", "new", "top", "rising"
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
                # Skip certain content types
                if post.stickied or post.distinguished:
                    continue
                
                # Create post object with privacy protection
                reddit_post = RedditPost(
                    id=post.id,
                    title=post.title,
                    content=post.selftext if hasattr(post, 'selftext') else "",
                    subreddit=subreddit_name,
                    author_hash=self.hash_username(str(post.author) if post.author else "anonymous"),
                    score=post.score,
                    num_comments=post.num_comments,
                    created_utc=post.created_utc,
                    url=f"https://reddit.com{post.permalink}",
                    collected_at=datetime.now().isoformat()
                )
                
                collected_posts.append(reddit_post)
                
                # Rate limiting - be respectful to Reddit's servers
                time.sleep(1)  # 1 second between requests
            
            print(f"Collected {len(collected_posts)} posts from r/{subreddit_name}")
            return collected_posts
            
        except Exception as e:
            print(f"Error collecting from r/{subreddit_name}: {str(e)}")
            return []
    
    def search_posts_by_keywords(self, 
                                subreddit_name: str,
                                keywords: List[str],
                                time_filter: str = "week",
                                limit: int = 50) -> List[RedditPost]:
        """
        Search for posts containing specific keywords
        
        CAUTION: Use responsibly and only for legitimate research
        """
        print(f"Searching r/{subreddit_name} for keywords: {keywords}")
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            collected_posts = []
            
            for keyword in keywords:
                # Search within subreddit
                search_results = subreddit.search(
                    keyword, 
                    time_filter=time_filter, 
                    limit=limit//len(keywords)
                )
                
                for post in search_results:
                    if post.stickied or post.distinguished:
                        continue
                    
                    reddit_post = RedditPost(
                        id=post.id,
                        title=post.title,
                        content=post.selftext if hasattr(post, 'selftext') else "",
                        subreddit=subreddit_name,
                        author_hash=self.hash_username(str(post.author) if post.author else "anonymous"),
                        score=post.score,
                        num_comments=post.num_comments,
                        created_utc=post.created_utc,
                        url=f"https://reddit.com{post.permalink}",
                        collected_at=datetime.now().isoformat()
                    )
                    
                    collected_posts.append(reddit_post)
                    time.sleep(1.5)  # Longer delay for searches
            
            # Remove duplicates based on post ID
            unique_posts = {post.id: post for post in collected_posts}.values()
            return list(unique_posts)
            
        except Exception as e:
            print(f"Error searching r/{subreddit_name}: {str(e)}")
            return []
    
    def save_posts_to_json(self, posts: List[RedditPost], filename: str):
        """Save collected posts to JSON file"""
        filepath = os.path.join(self.data_dir, "raw_posts", f"{filename}.json")
        
        posts_data = [asdict(post) for post in posts]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "collection_info": {
                    "collected_at": datetime.now().isoformat(),
                    "total_posts": len(posts),
                    "academic_disclaimer": self.disclaimer.strip()
                },
                "posts": posts_data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(posts)} posts to {filepath}")
    
    def save_posts_to_csv(self, posts: List[RedditPost], filename: str):
        """Save collected posts to CSV file"""
        filepath = os.path.join(self.data_dir, "raw_posts", f"{filename}.csv")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if posts:
                fieldnames = list(asdict(posts[0]).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for post in posts:
                    writer.writerow(asdict(post))
        
        print(f"Saved {len(posts)} posts to {filepath}")
    
    def analyze_collected_posts(self, posts: List[RedditPost], analyzer) -> List[RedditPost]:
        """
        Analyze collected posts using the existing weapons detection system
        """
        print(f"Analyzing {len(posts)} posts for weapons trade indicators...")
        
        analyzed_posts = []
        
        for post in posts:
            # Combine title and content for analysis
            full_content = f"{post.title}. {post.content}".strip()
            
            if not full_content or full_content == ".":
                continue
            
            try:
                # Use existing analyzer
                analysis_results = analyzer.analyze_text(full_content)
                
                # Create new post with analysis results
                analyzed_post = RedditPost(
                    id=post.id,
                    title=post.title,
                    content=post.content,
                    subreddit=post.subreddit,
                    author_hash=post.author_hash,
                    score=post.score,
                    num_comments=post.num_comments,
                    created_utc=post.created_utc,
                    url=post.url,
                    collected_at=post.collected_at,
                    risk_analysis=analysis_results
                )
                
                analyzed_posts.append(analyzed_post)
                
                # Print high-risk findings
                if analysis_results.get('risk_score', 0) >= 0.7:
                    print(f"HIGH RISK POST FOUND: r/{post.subreddit} - {post.id}")
                    print(f"  Title: {post.title[:100]}...")
                    print(f"  Risk Score: {analysis_results.get('risk_score', 0):.2f}")
                    print(f"  Flags: {len(analysis_results.get('flags', []))}")
                
            except Exception as e:
                print(f"Error analyzing post {post.id}: {str(e)}")
                continue
        
        return analyzed_posts
    
    def save_analyzed_posts(self, posts: List[RedditPost], filename: str):
        """Save analyzed posts with risk assessments"""
        filepath = os.path.join(self.data_dir, "analyzed_posts", f"{filename}_analyzed.json")
        
        # Separate posts by risk level
        high_risk = [p for p in posts if p.risk_analysis and p.risk_analysis.get('risk_score', 0) >= 0.7]
        medium_risk = [p for p in posts if p.risk_analysis and 0.4 <= p.risk_analysis.get('risk_score', 0) < 0.7]
        low_risk = [p for p in posts if p.risk_analysis and p.risk_analysis.get('risk_score', 0) < 0.4]
        
        analysis_summary = {
            "analysis_info": {
                "analyzed_at": datetime.now().isoformat(),
                "total_posts": len(posts),
                "high_risk_posts": len(high_risk),
                "medium_risk_posts": len(medium_risk),
                "low_risk_posts": len(low_risk),
                "academic_disclaimer": self.disclaimer.strip()
            },
            "high_risk_posts": [asdict(post) for post in high_risk],
            "medium_risk_posts": [asdict(post) for post in medium_risk],
            "low_risk_posts": [asdict(post) for post in low_risk]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_summary, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis complete:")
        print(f"  High risk: {len(high_risk)} posts")
        print(f"  Medium risk: {len(medium_risk)} posts") 
        print(f"  Low risk: {len(low_risk)} posts")
        print(f"  Saved to: {filepath}")
        
        return analysis_summary

# Example usage (with proper authentication required)
def example_usage():
    """
    Example of how to use the collector responsibly
    
    REQUIREMENTS:
    1. Reddit API credentials (register at https://www.reddit.com/prefs/apps)
    2. Academic research approval from your institution
    3. Compliance with Reddit's Terms of Service
    4. Proper rate limiting and respectful usage
    """
    
    # Initialize collector with your credentials
    collector = AcademicRedditCollector(
        client_id="your_client_id_here",
        client_secret="your_client_secret_here", 
        user_agent="academic_research:weapons_detection:v1.0 (by /u/your_username)"
    )
    
    # Example: Collect from general discussion subreddits
    # NOTE: Be very careful about which subreddits you target
    subreddits_to_monitor = [
        "news",          # General news discussions
        "worldnews",     # International news
        "politics"       # Political discussions
    ]
    
    all_collected_posts = []
    
    for subreddit in subreddits_to_monitor:
        posts = collector.collect_subreddit_posts(
            subreddit_name=subreddit,
            limit=50,  # Small limit for testing
            time_filter="day"
        )
        all_collected_posts.extend(posts)
        
        # Save raw data
        collector.save_posts_to_json(posts, f"{subreddit}_daily")
        
        time.sleep(10)  # Wait between subreddits
    
    print(f"Total collected: {len(all_collected_posts)} posts")
    
    # Analyze posts (requires your existing analyzer)
    # from detection.text_analyzer import WeaponsTextAnalyzer
    # analyzer = WeaponsTextAnalyzer()
    # analyzed_posts = collector.analyze_collected_posts(all_collected_posts, analyzer)
    # collector.save_analyzed_posts(analyzed_posts, "daily_analysis")

if __name__ == "__main__":
    print("Reddit Academic Research Collector")
    print("Please ensure you have proper authorization before use.")
    # example_usage()  # Uncomment only after getting proper credentials and approval