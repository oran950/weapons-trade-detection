"""
LLM-based text analyzer for detecting illegal weapons trade using Ollama.
"""
import httpx
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logger
logger = logging.getLogger("LLMTextAnalyzer")
logger.setLevel(logging.DEBUG)


@dataclass
class LLMAnalysisResult:
    """Result of LLM analysis on a post"""
    is_weapon_related: bool
    is_trade_related: bool
    is_potentially_illegal: bool
    illegality_reason: Optional[str]
    weapon_types_mentioned: list
    trade_indicators: list
    risk_assessment: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE'
    confidence: float
    summary: str
    recommendation: str
    processing_time_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LLMTextAnalyzer:
    """
    Uses Ollama LLM to analyze text for illegal weapons trade indicators.
    """
    
    ANALYSIS_PROMPT = """You are a senior open-source intelligence (OSINT) analyst with a law-enforcement research background.
You specialize in online arms markets, gray-market listings, trafficking lexicon, and disinformation around weapons sales.
You think like a careful investigator: evidence-based, skeptical of hype, attentive to coded language, prices, logistics, and contact handles.
You never fabricate facts; you only infer from the text provided.

Task: assess the item below for (1) weapons/firearms relevance, (2) trade/sale/buy intent, (3) whether it could indicate ILLEGAL arms trade
in a research / monitoring context (not legal advice).

LEGAL vs ILLEGAL (indicators only — jurisdiction varies):
- LEGAL-leaning: licensed retail, reviews, sport/hunting, museum/collecting discourse, clearly regulatory compliance language.
- ILLEGAL-leaning: unlicensed sales, straw purchasing hints, no serial / no paperwork, full-auto conversion offers, stolen goods,
  cross-border smuggling logistics, price + anonymous contact + urgency patterns typical of black-market posts.

POST TO ANALYZE:
Title: {title}
Subreddit/Source: {source}
Content: {content}

Respond ONLY with a JSON object (no markdown fences, no commentary):
{{
    "is_weapon_related": true/false,
    "is_trade_related": true/false,
    "is_potentially_illegal": true/false,
    "illegality_reason": "explanation if illegal, null otherwise",
    "weapon_types_mentioned": ["list", "of", "weapons"],
    "trade_indicators": ["list of phrases suggesting trade/sale"],
    "risk_assessment": "CRITICAL/HIGH/MEDIUM/LOW/NONE",
    "confidence": 0.0-1.0,
    "summary": "Brief 1-2 sentence summary of what this post is about",
    "recommendation": "What action to take: INVESTIGATE/FLAG/MONITOR/IGNORE"
}}"""

    def __init__(
        self,
        ollama_base: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
        timeout: int = 120
    ):
        self.ollama_base = ollama_base
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=ollama_base,
            timeout=httpx.Timeout(timeout)
        )
        
    async def check_model_available(self) -> bool:
        """Check if the LLM model is available"""
        print(f"🔍 Checking LLM model availability: {self.model} at {self.ollama_base}", flush=True)
        try:
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                print(f"   Available models: {models}", flush=True)
                # Check for exact match or version match
                for m in models:
                    if self.model in m or m in self.model:
                        print(f"✅ LLM model '{self.model}' is available", flush=True)
                        return True
                print(f"⚠️ LLM model '{self.model}' not found in available models", flush=True)
                return False
            print(f"❌ Ollama API returned status {response.status_code}", flush=True)
            return False
        except httpx.ConnectError as e:
            print(f"❌ Cannot connect to Ollama at {self.ollama_base}: {e}", flush=True)
            return False
        except Exception as e:
            print(f"❌ Error checking LLM model: {type(e).__name__}: {e}", flush=True)
            return False
    
    async def analyze_post(
        self,
        title: str,
        content: str,
        source: str = "unknown"
    ) -> LLMAnalysisResult:
        """
        Analyze a post using the LLM to detect illegal weapons trade.
        
        Args:
            title: Post title
            content: Post content/body
            source: Subreddit or channel name
            
        Returns:
            LLMAnalysisResult with analysis details
        """
        start_time = datetime.now()
        print(f"🧠 LLM analyzing post: '{title[:50]}...' from {source}", flush=True)
        
        # Build the prompt
        prompt = self.ANALYSIS_PROMPT.format(
            title=title[:500],  # Limit title length
            source=source,
            content=content[:2000]  # Limit content length
        )
        
        try:
            print(f"   📤 Sending to Ollama: model={self.model}, timeout={self.timeout}s", flush=True)
            
            # Call Ollama API
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get("response", "{}")
            print(f"   📥 Response: {len(llm_response)} chars", flush=True)
            
            # Parse JSON response
            try:
                analysis = json.loads(llm_response)
            except json.JSONDecodeError:
                print(f"   ⚠️ JSON parse failed, trying regex extraction", flush=True)
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    print(f"❌ Could not parse LLM response: {llm_response[:200]}", flush=True)
                    raise ValueError("Could not parse LLM response as JSON")
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            is_illegal = analysis.get("is_potentially_illegal", False)
            risk = analysis.get("risk_assessment", "NONE")
            print(f"✅ LLM done: {processing_time}ms | Risk: {risk} | Illegal: {is_illegal}", flush=True)
            
            return LLMAnalysisResult(
                is_weapon_related=analysis.get("is_weapon_related", False),
                is_trade_related=analysis.get("is_trade_related", False),
                is_potentially_illegal=is_illegal,
                illegality_reason=analysis.get("illegality_reason"),
                weapon_types_mentioned=analysis.get("weapon_types_mentioned", []),
                trade_indicators=analysis.get("trade_indicators", []),
                risk_assessment=risk,
                confidence=float(analysis.get("confidence", 0.5)),
                summary=analysis.get("summary", ""),
                recommendation=analysis.get("recommendation", "IGNORE"),
                processing_time_ms=processing_time
            )
            
        except httpx.TimeoutException as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"⏱️ LLM TIMEOUT after {processing_time}ms: {e}", flush=True)
            return LLMAnalysisResult(
                is_weapon_related=False,
                is_trade_related=False,
                is_potentially_illegal=False,
                illegality_reason=None,
                weapon_types_mentioned=[],
                trade_indicators=[],
                risk_assessment="NONE",
                confidence=0.0,
                summary="Analysis timed out",
                recommendation="RETRY",
                processing_time_ms=processing_time
            )
        except httpx.ConnectError as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"❌ LLM CONNECTION ERROR - Cannot reach Ollama: {e}", flush=True)
            return LLMAnalysisResult(
                is_weapon_related=False,
                is_trade_related=False,
                is_potentially_illegal=False,
                illegality_reason=None,
                weapon_types_mentioned=[],
                trade_indicators=[],
                risk_assessment="NONE",
                confidence=0.0,
                summary=f"Connection error: Ollama unreachable",
                recommendation="RETRY",
                processing_time_ms=processing_time
            )
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"❌ LLM ANALYSIS ERROR: {type(e).__name__}: {e}", flush=True)
            return LLMAnalysisResult(
                is_weapon_related=False,
                is_trade_related=False,
                is_potentially_illegal=False,
                illegality_reason=None,
                weapon_types_mentioned=[],
                trade_indicators=[],
                risk_assessment="NONE",
                confidence=0.0,
                summary=f"Analysis error: {str(e)[:100]}",
                recommendation="RETRY",
                processing_time_ms=processing_time
            )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

