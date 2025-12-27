"""
LLM API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import os

from ...models.responses import LLMStatusResponse

router = APIRouter(prefix="/api/llm", tags=["llm"])

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


@router.get("/status", response_model=LLMStatusResponse)
async def llm_status():
    """
    Check LLM service status
    """
    ok = True
    problems = []
    reachable = False
    requests_installed = False
    
    # Check if requests is installed
    try:
        import requests
        requests_installed = True
    except ImportError:
        problems.append("python-requests not installed")
        ok = False
    
    # Check provider
    if LLM_PROVIDER != "ollama":
        problems.append(f"LLM_PROVIDER={LLM_PROVIDER} (expected 'ollama')")
        ok = False
    
    # Try to reach Ollama
    if requests_installed and LLM_PROVIDER == "ollama":
        try:
            import requests
            r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
            reachable = r.status_code == 200
            
            if reachable:
                # Check if model is available
                models = r.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                if not any(OLLAMA_MODEL in name for name in model_names):
                    problems.append(f"Model '{OLLAMA_MODEL}' not found in Ollama")
        except Exception as e:
            problems.append(f"Ollama not reachable at {OLLAMA_BASE}: {e}")
            ok = False
    
    return LLMStatusResponse(
        provider=LLM_PROVIDER,
        ollama_base=OLLAMA_BASE,
        model=OLLAMA_MODEL,
        requests_installed=requests_installed,
        ollama_reachable=reachable,
        ok=ok and reachable,
        problems=problems
    )


@router.get("/models")
async def list_models():
    """
    List available Ollama models
    """
    try:
        import requests
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        
        if r.status_code != 200:
            return {"models": [], "error": "Failed to fetch models"}
        
        models = r.json().get('models', [])
        
        return {
            "models": [
                {
                    "name": m.get('name'),
                    "size": m.get('size'),
                    "modified_at": m.get('modified_at')
                }
                for m in models
            ],
            "current_model": OLLAMA_MODEL,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="requests library not installed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify")
async def classify_content(request: Dict[str, Any]):
    """
    Classify content using LLM
    """
    content = request.get("content", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    try:
        from ..._ai_operations import LLMOperations
        
        llm_ops = LLMOperations()
        
        # First run rule-based analysis
        from ...core.analyzer import TextAnalyzer
        analyzer = TextAnalyzer()
        rule_result = analyzer.analyze_text(content)
        
        # Then get LLM classification
        classification = llm_ops.classify_risk(content, rule_result)
        
        return {
            "status": "success",
            "rule_based": {
                "risk_score": rule_result.risk_score,
                "risk_level": rule_result.risk_level,
                "flags": rule_result.flags
            },
            "llm_classification": classification.to_dict() if classification else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"LLM operations not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-entities")
async def extract_entities(request: Dict[str, Any]):
    """
    Extract entities from content using LLM
    """
    content = request.get("content", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    try:
        from ..._ai_operations import LLMOperations
        
        llm_ops = LLMOperations()
        entities = llm_ops.extract_entities(content)
        
        return {
            "status": "success",
            "entities": entities.to_dict() if entities else {},
            "has_transaction_indicators": entities.has_transaction_indicators if entities else False,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="LLM operations not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_flags(request: Dict[str, Any]):
    """
    Generate explanation for detected flags
    """
    content = request.get("content", "")
    flags = request.get("flags", [])
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    try:
        from ..._ai_operations import LLMOperations
        
        llm_ops = LLMOperations()
        explanation = llm_ops.explain_flags(content, flags)
        
        return {
            "status": "success",
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="LLM operations not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

