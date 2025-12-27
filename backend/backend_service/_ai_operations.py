"""
AI Operations Module - All LLM/AI operations
Handles Ollama integration for enhanced analysis
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from .entities.analysis import AnalysisResult, ExtractedEntities
from .entities.risk import RiskClassification
from .llm_globals import (
    LLM_PROVIDER,
    OLLAMA_BASE,
    OLLAMA_MODEL,
    LLM_TIMEOUT,
    CLASSIFICATION_PROMPT,
    ENTITY_EXTRACTION_PROMPT,
    EXPLANATION_PROMPT
)


class LLMOperations:
    """
    Handles all LLM operations for the weapons detection system.
    Currently supports Ollama as the LLM provider.
    """
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize LLM operations
        
        Args:
            base_url: Ollama base URL (defaults to env var)
            model: Model to use (defaults to env var)
        """
        self.base_url = base_url or OLLAMA_BASE
        self.model = model or OLLAMA_MODEL
        self._requests = None
        
        try:
            import requests
            self._requests = requests
        except ImportError:
            print("Warning: requests library not installed. LLM operations unavailable.")
    
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Make a call to Ollama API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON response
        """
        if not self._requests:
            raise RuntimeError("requests library not installed")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self._requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "options": {"temperature": 0},
                "stream": False
            },
            timeout=LLM_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        content = data.get("message", {}).get("content", "{}")
        
        return self._safe_json_parse(content)
    
    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """
        Safely parse JSON from LLM response
        
        Args:
            text: Raw text from LLM
            
        Returns:
            Parsed dictionary
        """
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in text
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Return fallback
        return {
            "final_label": "MEDIUM",
            "risk_adjustment": 0.0,
            "reasons": ["fallback-parser"],
            "evidence_spans": [],
            "misclassification_risk": "MEDIUM"
        }
    
    def classify_risk(
        self, 
        text: str, 
        rule_result: AnalysisResult
    ) -> RiskClassification:
        """
        Classify risk using LLM
        
        Args:
            text: Content to classify
            rule_result: Rule-based analysis result
            
        Returns:
            RiskClassification from LLM
        """
        prompt = CLASSIFICATION_PROMPT.format(
            text=text[:8000],  # Limit text length
            rule_flags=json.dumps(rule_result.flags, ensure_ascii=False),
            keywords=json.dumps(rule_result.detected_keywords, ensure_ascii=False),
            patterns=json.dumps(rule_result.detected_patterns, ensure_ascii=False),
            rule_risk=round(rule_result.risk_score, 3)
        )
        
        result = self._call_ollama(
            prompt,
            system_prompt="You are a precise risk classifier that returns strict JSON only."
        )
        
        return RiskClassification.from_llm_response(result)
    
    def extract_entities(self, text: str) -> ExtractedEntities:
        """
        Extract entities from text using LLM
        
        Args:
            text: Content to extract entities from
            
        Returns:
            ExtractedEntities object
        """
        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text[:8000])
        
        result = self._call_ollama(
            prompt,
            system_prompt="You are an entity extractor that returns strict JSON only."
        )
        
        return ExtractedEntities(
            weapon_types=result.get('weapon_types', []),
            weapon_models=result.get('weapon_models', []),
            locations=result.get('locations', []),
            contact_methods=result.get('contact_methods', []),
            prices=result.get('prices', []),
            quantities=result.get('quantities', []),
            time_references=result.get('time_references', [])
        )
    
    def explain_flags(self, text: str, flags: List[str]) -> str:
        """
        Generate explanation for detected flags
        
        Args:
            text: Original content
            flags: List of flags to explain
            
        Returns:
            Explanation string
        """
        prompt = EXPLANATION_PROMPT.format(
            text=text[:4000],
            flags=json.dumps(flags, ensure_ascii=False)
        )
        
        result = self._call_ollama(
            prompt,
            system_prompt="You are a clear and concise explainer."
        )
        
        # If result is a dict, try to get explanation
        if isinstance(result, dict):
            return result.get('explanation', str(result))
        
        return str(result)
    
    def detect_evasion(self, text: str) -> Dict[str, Any]:
        """
        Detect evasion patterns in text
        
        Args:
            text: Content to analyze
            
        Returns:
            Dictionary with evasion patterns
        """
        prompt = """Analyze the following text for evasion patterns used to disguise illegal weapons trade.

Look for:
- Codewords (e.g., "tool" for gun, "candy" for ammunition)
- Deliberate misspellings
- Leet speak (e.g., "g0n" for "gun")
- Euphemisms
- Obfuscation techniques

Return STRICT JSON:
{
  "patterns_detected": ["pattern1", "pattern2"],
  "confidence": 0.0-1.0,
  "techniques": ["technique1", "technique2"],
  "original_terms": {"detected": "likely_meaning"}
}

TEXT:
\"\"\"""" + text[:4000] + '"""'
        
        result = self._call_ollama(
            prompt,
            system_prompt="You are an expert at detecting obfuscation patterns."
        )
        
        return result
    
    def generate_synthetic_content(
        self,
        content_type: str,
        intensity: str,
        platform: str = "generic"
    ) -> str:
        """
        Generate synthetic content using LLM
        
        Args:
            content_type: Type of content (post, message, ad, forum)
            intensity: Intensity level (low, medium, high)
            platform: Platform style
            
        Returns:
            Generated content string
        """
        prompt = f"""Generate a synthetic {content_type} for academic research on weapons trade detection.

Parameters:
- Content type: {content_type}
- Intensity level: {intensity}
- Platform style: {platform}

Requirements:
- This is for ACADEMIC RESEARCH only
- Generate realistic but fictional content
- Include appropriate indicators for the intensity level
- Make it natural and platform-appropriate

Return only the generated content, no explanation."""
        
        result = self._call_ollama(prompt)
        
        if isinstance(result, dict):
            return result.get('content', str(result))
        return str(result)
    
    def analyze_conversation(
        self, 
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a conversation for deal progression
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Conversation analysis results
        """
        # Format messages for prompt
        formatted = "\n".join([
            f"[{m.get('timestamp', 'unknown')}] {m.get('author', 'User')}: {m.get('content', '')}"
            for m in messages[:50]  # Limit to 50 messages
        ])
        
        prompt = f"""Analyze this conversation for weapons trade indicators.

CONVERSATION:
{formatted}

Return STRICT JSON:
{{
  "deal_progression": "initial_contact"|"negotiation"|"agreement"|"completion"|"none",
  "buyer_indicators": ["indicator1"],
  "seller_indicators": ["indicator1"],
  "negotiation_patterns": ["pattern1"],
  "risk_score": 0.0-1.0,
  "summary": "brief summary"
}}"""
        
        result = self._call_ollama(
            prompt,
            system_prompt="You analyze conversations for illegal trade patterns."
        )
        
        return result
    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        if not self._requests:
            return False
        
        try:
            response = self._requests.get(
                f"{self.base_url}/api/tags",
                timeout=3
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM status"""
        available = self.is_available()
        
        return {
            "provider": LLM_PROVIDER,
            "base_url": self.base_url,
            "model": self.model,
            "available": available,
            "timestamp": datetime.now().isoformat()
        }

