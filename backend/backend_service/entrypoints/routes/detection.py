"""
Detection API Routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from datetime import datetime

from ...core.detector import WeaponsDetector
from ...core.analyzer import TextAnalyzer
from ...models.requests import AnalysisRequest, LLMAnalysisRequest
from ...models.responses import AnalysisResponse

router = APIRouter(prefix="/api/detection", tags=["detection"])

# Initialize components
analyzer = TextAnalyzer()
detector = WeaponsDetector(use_llm=False)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: Dict[str, Any]):
    """
    Analyze text content for weapons trade indicators (rules-only)
    """
    content = request.get("content", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    analysis_results = analyzer.analyze_text(content)
    
    risk_score = analysis_results.risk_score
    risk_level = analysis_results.risk_level
    
    analysis_id = f"analysis_{int(datetime.now().timestamp())}"
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=analysis_results.confidence,
        flags=analysis_results.flags,
        detected_keywords=analysis_results.detected_keywords,
        detected_patterns=analysis_results.detected_patterns,
        summary=f"Analysis completed. Risk level: {risk_level}. Found {len(analysis_results.flags)} potential indicators.",
        timestamp=analysis_results.analysis_time,
        source="rules"
    )


@router.post("/analyze_llm", response_model=AnalysisResponse)
async def analyze_content_llm(
    request: Dict[str, Any],
    use_llm: bool = Query(False, description="Enable LLM verification"),
    always_if_toggled: bool = Query(False, description="Always call LLM when toggled")
):
    """
    Hybrid analysis with optional LLM validation
    """
    content = request.get("content", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    # Get LLM operations if available
    try:
        from ..._ai_operations import LLMOperations
        llm_ops = LLMOperations()
        llm_detector = WeaponsDetector(use_llm=use_llm, llm_operations=llm_ops)
    except ImportError:
        llm_detector = WeaponsDetector(use_llm=False)
    
    assessment = llm_detector.analyze(
        content, 
        use_llm_override=use_llm,
        always_use_llm=always_if_toggled
    )
    
    result = assessment.result
    
    return AnalysisResponse(
        analysis_id=assessment.analysis_id,
        status="completed",
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        confidence=result.confidence,
        flags=result.flags,
        detected_keywords=result.detected_keywords,
        detected_patterns=result.detected_patterns,
        summary=f"{'Hybrid' if result.source == 'hybrid' else 'Rules-only'}: {len(result.flags)} indicators found.",
        timestamp=result.analysis_time,
        source=result.source,
        llm_reasons=result.llm_reasons,
        llm_evidence_spans=result.llm_evidence_spans,
        llm_misclassification_risk=result.llm_misclassification_risk,
        llm_error=result.llm_error
    )


@router.post("/batch")
async def analyze_batch(request: Dict[str, Any]):
    """
    Analyze multiple texts in batch
    """
    contents = request.get("contents", [])
    
    if not contents:
        raise HTTPException(status_code=400, detail="No contents provided")
    
    if len(contents) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 items per batch")
    
    results = []
    for i, content in enumerate(contents):
        analysis = analyzer.analyze_text(content)
        results.append({
            "index": i,
            "risk_score": analysis.risk_score,
            "risk_level": analysis.risk_level,
            "flags_count": len(analysis.flags)
        })
    
    high_risk = sum(1 for r in results if r["risk_score"] >= 0.7)
    medium_risk = sum(1 for r in results if 0.4 <= r["risk_score"] < 0.7)
    low_risk = sum(1 for r in results if r["risk_score"] < 0.4)
    
    return {
        "status": "completed",
        "total_analyzed": len(contents),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/keywords")
async def get_detection_keywords():
    """
    Get list of detection keywords by category
    """
    return {
        "categories": list(analyzer.high_risk_keywords.keys()),
        "high_risk_keywords": analyzer.high_risk_keywords,
        "pattern_count": len(analyzer.high_risk_patterns) + len(analyzer.medium_risk_patterns)
    }

