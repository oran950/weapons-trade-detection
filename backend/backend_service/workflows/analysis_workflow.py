"""
Analysis Workflow - Orchestrates analysis pipeline
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

from ..entities.post import RedditPost, TelegramMessage
from ..entities.analysis import AnalysisResult
from ..handlers.analysis_handler import AnalysisHandler
from ..core.detector import WeaponsDetector
from ..utils.file_manager import FileManager
from ..config import config


@dataclass
class AnalysisConfig:
    """Configuration for analysis workflow"""
    use_llm: bool = False
    always_use_llm: bool = False
    extract_entities: bool = False
    generate_explanations: bool = False
    save_results: bool = True
    high_risk_threshold: float = 0.7
    medium_risk_threshold: float = 0.4


class AnalysisWorkflow:
    """
    Orchestrates the analysis pipeline including:
    - Rule-based analysis
    - LLM enhancement (optional)
    - Entity extraction (optional)
    - Report generation
    """
    
    def __init__(self, workflow_config: Optional[AnalysisConfig] = None):
        """
        Initialize analysis workflow
        
        Args:
            workflow_config: Analysis configuration
        """
        self.config = workflow_config or AnalysisConfig()
        self.file_manager = FileManager(config.DATA_DIR)
        
        # Initialize LLM operations if needed
        self.llm_ops = None
        if self.config.use_llm:
            try:
                from .._ai_operations import LLMOperations
                self.llm_ops = LLMOperations()
            except ImportError:
                print("Warning: LLM operations not available")
        
        self.detector = WeaponsDetector(
            use_llm=self.config.use_llm,
            llm_operations=self.llm_ops
        )
        self.handler = AnalysisHandler(
            use_llm=self.config.use_llm,
            llm_operations=self.llm_ops
        )
    
    async def run(
        self, 
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> Dict[str, Any]:
        """
        Run the analysis workflow
        
        Args:
            posts: List of posts to analyze
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            "workflow_id": f"analysis_{int(datetime.now().timestamp())}",
            "started_at": datetime.now().isoformat(),
            "config": {
                "use_llm": self.config.use_llm,
                "extract_entities": self.config.extract_entities,
                "post_count": len(posts)
            },
            "analyzed_posts": [],
            "entities": [],
            "summary": {},
            "errors": []
        }
        
        # Run analysis
        try:
            analyzed = await self._analyze_posts(posts)
            results["analyzed_posts"] = analyzed
        except Exception as e:
            results["errors"].append(f"Analysis failed: {e}")
        
        # Extract entities if configured
        if self.config.extract_entities and self.llm_ops:
            try:
                entities = await self._extract_entities(analyzed)
                results["entities"] = entities
            except Exception as e:
                results["errors"].append(f"Entity extraction failed: {e}")
        
        # Generate summary
        results["summary"] = self._generate_summary(analyzed)
        results["completed_at"] = datetime.now().isoformat()
        
        # Save if configured
        if self.config.save_results:
            results["saved_files"] = self.save_results(results)
        
        return results
    
    async def _analyze_posts(
        self, 
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> List[Union[RedditPost, TelegramMessage]]:
        """Analyze all posts"""
        # Run in thread pool for CPU-bound operations
        loop = asyncio.get_event_loop()
        analyzed = await loop.run_in_executor(
            None,
            lambda: self.handler.analyze_posts_batch(posts, self.config.use_llm)
        )
        return analyzed
    
    async def _extract_entities(
        self, 
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> List[Dict[str, Any]]:
        """Extract entities from high-risk posts"""
        entities = []
        
        for post in posts:
            if not post.risk_analysis:
                continue
            
            score = post.risk_analysis.get('risk_score', 0)
            if score < self.config.high_risk_threshold:
                continue
            
            # Get content
            if isinstance(post, RedditPost):
                content = f"{post.title}. {post.content}"
            else:
                content = post.content
            
            try:
                extracted = self.llm_ops.extract_entities(content)
                entities.append({
                    "post_id": post.id,
                    "platform": post.platform,
                    "risk_score": score,
                    "entities": extracted.to_dict()
                })
            except Exception as e:
                print(f"Entity extraction failed for {post.id}: {e}")
        
        return entities
    
    def _generate_summary(
        self, 
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> Dict[str, Any]:
        """Generate analysis summary"""
        total = len(posts)
        
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        platforms = {}
        all_keywords = []
        
        for post in posts:
            # Count by platform
            platform = post.platform
            platforms[platform] = platforms.get(platform, 0) + 1
            
            if not post.risk_analysis:
                continue
            
            score = post.risk_analysis.get('risk_score', 0)
            
            if score >= self.config.high_risk_threshold:
                high_risk += 1
                all_keywords.extend(post.risk_analysis.get('detected_keywords', []))
            elif score >= self.config.medium_risk_threshold:
                medium_risk += 1
            else:
                low_risk += 1
        
        return {
            "total_analyzed": total,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "high_risk_percentage": round(high_risk / total * 100, 2) if total > 0 else 0,
            "platforms": platforms,
            "common_keywords": list(set(all_keywords))[:20],
            "llm_used": self.config.use_llm
        }
    
    def save_results(self, results: Dict[str, Any]) -> List[str]:
        """Save analysis results"""
        saved_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full results
        from dataclasses import asdict
        
        output_data = {
            "workflow_id": results["workflow_id"],
            "started_at": results["started_at"],
            "completed_at": results["completed_at"],
            "summary": results["summary"],
            "high_risk_posts": [],
            "medium_risk_posts": [],
            "low_risk_posts": []
        }
        
        for post in results["analyzed_posts"]:
            post_data = asdict(post)
            score = post.risk_analysis.get('risk_score', 0) if post.risk_analysis else 0
            
            if score >= self.config.high_risk_threshold:
                output_data["high_risk_posts"].append(post_data)
            elif score >= self.config.medium_risk_threshold:
                output_data["medium_risk_posts"].append(post_data)
            else:
                output_data["low_risk_posts"].append(post_data)
        
        path = self.file_manager.save_json(
            output_data, 
            f"analysis_{timestamp}", 
            "analyzed"
        )
        saved_files.append(path)
        
        # Save entities if extracted
        if results.get("entities"):
            entities_data = {
                "workflow_id": results["workflow_id"],
                "extracted_at": results["completed_at"],
                "entities": results["entities"]
            }
            path = self.file_manager.save_json(
                entities_data,
                f"entities_{timestamp}",
                "analyzed"
            )
            saved_files.append(path)
        
        return saved_files
    
    def run_sync(
        self, 
        posts: List[Union[RedditPost, TelegramMessage]]
    ) -> Dict[str, Any]:
        """Synchronous version of run"""
        return asyncio.run(self.run(posts))

