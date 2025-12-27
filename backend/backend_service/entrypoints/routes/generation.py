"""
Generation API Routes
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException
from datetime import datetime

from ...models.requests import (
    ContentGenerationRequest,
    BatchGenerationRequest,
    BigDataGenerationRequest
)
from ...models.responses import GenerationResponse, BatchGenerationResponse, BigDataGenerationResponse

# Import the existing content generator
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from generation.content_generator import SyntheticContentGenerator, ContentParameters
except ImportError:
    # Fallback if import fails
    SyntheticContentGenerator = None
    ContentParameters = None

router = APIRouter(prefix="/api/generation", tags=["generation"])

# Initialize content generator
if SyntheticContentGenerator:
    content_generator = SyntheticContentGenerator()
else:
    content_generator = None


@router.post("/content", response_model=GenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    Generate synthetic content for academic research
    """
    if not content_generator:
        raise HTTPException(
            status_code=500,
            detail="Content generator not available"
        )
    
    try:
        params = ContentParameters(
            content_type=request.content_type,
            intensity_level=request.intensity_level,
            quantity=request.quantity,
            language=request.language,
            include_contact=request.include_contact,
            include_pricing=request.include_pricing
        )
        
        generated_content = content_generator.generate_content(params)
        
        return GenerationResponse(
            status="success",
            generated_count=len(generated_content),
            content=generated_content,
            parameters=request.dict(),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/batch", response_model=BatchGenerationResponse)
async def generate_batch_content(request: BatchGenerationRequest):
    """
    Generate a batch of content across all types and intensities
    """
    if not content_generator:
        raise HTTPException(status_code=500, detail="Content generator not available")
    
    try:
        batch_config = {
            "quantity_per_type": request.quantity_per_type,
            "include_contact": request.include_contact,
            "include_pricing": request.include_pricing
        }
        
        batch_results = content_generator.generate_batch(batch_config)
        
        return BatchGenerationResponse(
            status="success",
            batch_results=batch_results,
            configuration=batch_config,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")


@router.post("/big-data", response_model=BigDataGenerationResponse)
async def generate_big_data(request: BigDataGenerationRequest):
    """
    Generate a large batch of content for big data analysis
    """
    if not content_generator:
        raise HTTPException(status_code=500, detail="Content generator not available")
    
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            big_data_results = await loop.run_in_executor(
                executor,
                content_generator.generate_big_data_batch,
                request.total_quantity,
                request.platforms,
                request.content_lengths
            )
        
        return BigDataGenerationResponse(
            status="success",
            message=f"Generated {big_data_results['statistics']['total_generated']} posts",
            content=big_data_results['content'],
            statistics=big_data_results['statistics'],
            configuration={
                "total_quantity": request.total_quantity,
                "platforms": request.platforms,
                "content_lengths": request.content_lengths
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Big data generation failed: {str(e)}")


@router.get("/templates")
async def get_generation_templates():
    """
    Get available templates and vocabulary for content generation
    """
    if not content_generator:
        raise HTTPException(status_code=500, detail="Content generator not available")
    
    return {
        "content_types": ["post", "message", "ad", "forum"],
        "intensity_levels": ["low", "medium", "high"],
        "vocabulary_sample": {
            "low": content_generator.vocabulary["low"],
            "medium": content_generator.vocabulary["medium"],
            "high": content_generator.vocabulary["high"]
        },
        "platform_styles": content_generator.platform_styles,
        "supported_languages": ["en"],
        "max_quantity": 50
    }

