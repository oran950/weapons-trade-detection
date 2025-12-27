"""
Analysis Handler - Orchestrates analysis across platforms
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import asdict

from ..entities.post import Post, RedditPost, TelegramMessage
from ..entities.analysis import AnalysisResult, RiskAssessment
from ..core.detector import WeaponsDetector
from ..utils.file_manager import FileManager


class AnalysisHandler:
    """
    Handles analysis orchestration across different platforms and content types
    """
    
    def __init__(
        self,
        use_llm: bool = False,
        llm_operations=None,
        data_dir: str = "collected_data"
    ):
        """
        Initialize analysis handler
        
        Args:
            use_llm: Whether to use LLM for enhanced analysis
            llm_operations: LLM operations module
            data_dir: Directory for storing results
        """
        self.detector = WeaponsDetector(use_llm=use_llm, llm_operations=llm_operations)
        self.file_manager = FileManager(data_dir)
        self.use_llm = use_llm
        
        print(f"AnalysisHandler initialized (LLM: {'enabled' if use_llm else 'disabled'})")
    
    def analyze_text(self, text: str, use_llm: Optional[bool] = None) -> RiskAssessment:
        """
        Analyze a single piece of text
        
        Args:
            text: Text to analyze
            use_llm: Override LLM setting
            
        Returns:
            RiskAssessment object
        """
        return self.detector.analyze(text, use_llm_override=use_llm)
    
    def analyze_post(
        self, 
        post: Union[RedditPost, TelegramMessage],
        use_llm: Optional[bool] = None
    ) -> Union[RedditPost, TelegramMessage]:
        """
        Analyze a post and attach results
        
        Args:
            post: Post to analyze (Reddit or Telegram)
            use_llm: Override LLM setting
            
        Returns:
            Post with risk_analysis attached
        """
        # Get content based on post type
        if isinstance(post, RedditPost):
            content = f"{post.title}. {post.content}".strip()
        else:
            content = post.content
        
        if not content or content == ".":
            return post
        
        assessment = self.detector.analyze(content, use_llm_override=use_llm)
        post.risk_analysis = assessment.result.to_dict()
        
        return post
    
    def analyze_posts_batch(
        self,
        posts: List[Union[RedditPost, TelegramMessage]],
        use_llm: Optional[bool] = None
    ) -> List[Union[RedditPost, TelegramMessage]]:
        """
        Analyze multiple posts
        
        Args:
            posts: List of posts to analyze
            use_llm: Override LLM setting
            
        Returns:
            List of posts with risk_analysis attached
        """
        print(f"Analyzing batch of {len(posts)} posts...")
        
        analyzed = []
        high_risk_count = 0
        
        for i, post in enumerate(posts):
            result = self.analyze_post(post, use_llm)
            analyzed.append(result)
            
            if result.risk_analysis and result.risk_analysis.get('risk_score', 0) >= 0.7:
                high_risk_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"Analyzed {i + 1}/{len(posts)} posts...")
        
        print(f"Analysis complete. Found {high_risk_count} high-risk posts.")
        return analyzed
    
    def categorize_by_risk(
        self,
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> Dict[str, List[Union[RedditPost, TelegramMessage]]]:
        """
        Categorize posts by risk level
        
        Args:
            posts: List of analyzed posts
            
        Returns:
            Dictionary with 'high', 'medium', 'low' keys
        """
        categories = {
            'high': [],
            'medium': [],
            'low': [],
            'unanalyzed': []
        }
        
        for post in posts:
            if not post.risk_analysis:
                categories['unanalyzed'].append(post)
                continue
            
            score = post.risk_analysis.get('risk_score', 0)
            
            if score >= 0.7:
                categories['high'].append(post)
            elif score >= 0.4:
                categories['medium'].append(post)
            else:
                categories['low'].append(post)
        
        return categories
    
    def generate_summary(
        self,
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> Dict[str, Any]:
        """
        Generate analysis summary
        
        Args:
            posts: List of analyzed posts
            
        Returns:
            Summary dictionary
        """
        categories = self.categorize_by_risk(posts)
        
        # Calculate statistics
        total = len(posts)
        high_count = len(categories['high'])
        medium_count = len(categories['medium'])
        low_count = len(categories['low'])
        
        # Get common keywords across high-risk posts
        all_keywords = []
        all_patterns = []
        
        for post in categories['high']:
            if post.risk_analysis:
                all_keywords.extend(post.risk_analysis.get('detected_keywords', []))
                all_patterns.extend(post.risk_analysis.get('detected_patterns', []))
        
        # Count platforms
        platform_counts = {}
        for post in posts:
            platform = getattr(post, 'platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_posts": total,
            "risk_distribution": {
                "high_risk": high_count,
                "medium_risk": medium_count,
                "low_risk": low_count,
                "high_risk_percentage": round(high_count / total * 100, 2) if total > 0 else 0
            },
            "platform_distribution": platform_counts,
            "common_keywords": list(set(all_keywords))[:20],
            "common_patterns": list(set(all_patterns))[:10],
            "llm_enabled": self.use_llm
        }
        
        return summary
    
    def save_analysis_results(
        self,
        posts: List[Union[RedditPost, TelegramMessage]],
        filename: str
    ) -> Dict[str, Any]:
        """
        Save analysis results to file
        
        Args:
            posts: Analyzed posts
            filename: Base filename
            
        Returns:
            Summary dictionary
        """
        categories = self.categorize_by_risk(posts)
        summary = self.generate_summary(posts)
        
        results = {
            "summary": summary,
            "high_risk_posts": [asdict(p) for p in categories['high']],
            "medium_risk_posts": [asdict(p) for p in categories['medium']],
            "low_risk_posts": [asdict(p) for p in categories['low']]
        }
        
        self.file_manager.save_json(results, f"{filename}_analyzed", "analyzed")
        
        print(f"Results saved: {len(categories['high'])} high, {len(categories['medium'])} medium, {len(categories['low'])} low")
        
        return summary
    
    def quick_triage(
        self,
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> List[Union[RedditPost, TelegramMessage]]:
        """
        Quick triage to identify posts needing further analysis
        Returns only high and medium risk posts
        
        Args:
            posts: List of posts to triage
            
        Returns:
            List of posts with risk >= 0.4
        """
        analyzed = self.analyze_posts_batch(posts, use_llm=False)
        
        return [
            p for p in analyzed 
            if p.risk_analysis and p.risk_analysis.get('risk_score', 0) >= 0.4
        ]

