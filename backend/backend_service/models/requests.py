"""
Request models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    content: str = Field(..., description="Text content to analyze")
    use_llm: bool = Field(default=False, description="Enable LLM validation")
    always_use_llm: bool = Field(default=False, description="Always use LLM regardless of triage")


class ContentGenerationRequest(BaseModel):
    """Request model for synthetic content generation"""
    content_type: str = Field(
        ..., 
        description="Type of content to generate", 
        pattern="^(post|message|ad|forum)$"
    )
    intensity_level: str = Field(
        ..., 
        description="Intensity level", 
        pattern="^(low|medium|high)$"
    )
    quantity: int = Field(default=1, ge=1, le=50, description="Number of items to generate")
    language: str = Field(default="en", description="Language code")
    include_contact: bool = Field(default=False, description="Include contact information")
    include_pricing: bool = Field(default=False, description="Include pricing information")


class BatchGenerationRequest(BaseModel):
    """Request model for batch content generation"""
    quantity_per_type: int = Field(default=5, ge=1, le=20, description="Items per content type")
    include_contact: bool = Field(default=False, description="Include contact information")
    include_pricing: bool = Field(default=False, description="Include pricing information")


class BigDataGenerationRequest(BaseModel):
    """Request model for big data generation"""
    total_quantity: int = Field(default=2000, ge=100, le=10000, description="Total posts to generate")
    platforms: List[str] = Field(
        default=["reddit", "twitter", "facebook", "instagram"], 
        description="Platforms to generate for"
    )
    content_lengths: List[str] = Field(
        default=["short", "medium", "long"], 
        description="Content lengths to include"
    )


class RedditCollectionParams(BaseModel):
    """Parameters for Reddit collection"""
    subreddits: List[str] = Field(default=["news"], description="List of subreddits")
    timeFilter: str = Field(default="day", description="Time filter for posts")
    sortMethod: str = Field(default="hot", description="Sort method for posts")
    limit_per_subreddit: int = Field(default=25, ge=1, le=50, description="Posts per subreddit")
    keywords: str = Field(default="", description="Keywords to search for")
    include_all_defaults: bool = Field(default=False, description="Include default subreddit list")


class RedditCollectionRequest(BaseModel):
    """Request model for Reddit collection"""
    parameters: RedditCollectionParams


class TelegramCollectionParams(BaseModel):
    """Parameters for Telegram collection"""
    channels: List[str] = Field(default=[], description="List of channel usernames")
    groups: List[int] = Field(default=[], description="List of group IDs")
    keywords: List[str] = Field(default=[], description="Keywords to search for")
    limit_per_source: int = Field(default=50, ge=1, le=200, description="Messages per source")
    search_globally: bool = Field(default=False, description="Search across all accessible chats")


class TelegramCollectionRequest(BaseModel):
    """Request model for Telegram collection"""
    parameters: TelegramCollectionParams


class LLMAnalysisRequest(BaseModel):
    """Request model for LLM-enhanced analysis"""
    content: str = Field(..., description="Text content to analyze")
    always_use_llm: bool = Field(default=False, description="Always use LLM")
    extract_entities: bool = Field(default=False, description="Extract entities from content")
    generate_explanation: bool = Field(default=False, description="Generate explanation of flags")


class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    analysis_file: str = Field(..., description="Filename of analysis results")
    report_type: str = Field(default="summary", description="Type of report")
    include_high_risk_only: bool = Field(default=False, description="Include only high-risk posts")

