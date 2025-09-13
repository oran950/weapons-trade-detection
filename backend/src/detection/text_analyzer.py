import re
from typing import Dict, List
from datetime import datetime

class WeaponsTextAnalyzer:
    def __init__(self):
        # Academic research patterns for weapons detection
        self.weapons_keywords = {
            'firearms': ['gun', 'rifle', 'pistol', 'firearm', 'ammunition', 'bullet'],
            'explosives': ['bomb', 'explosive', 'grenade', 'dynamite'],
            'illegal_trade': ['smuggling', 'black market', 'illegal sale', 'trafficking'],
            'suspicious_terms': ['untraceable', 'cash only', 'no questions']
        }
        
        # Suspicious communication patterns
        self.suspicious_patterns = [
            r'\b(buy|sell|trade)\s+(guns?|weapons?|firearms?)\b',
            r'\b(cash\s+only|no\s+paperwork|untraceable)\b',
            r'\b(meet\s+in\s+person|private\s+sale)\b'
        ]
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text content for weapons trade indicators"""
        text_lower = text.lower()
        
        results = {
            'risk_score': 0.0,
            'confidence': 0.0,
            'flags': [],
            'detected_keywords': [],
            'detected_patterns': []
        }
        
        # Keyword detection
        keyword_score = self._detect_keywords(text_lower, results)
        
        # Pattern detection  
        pattern_score = self._detect_patterns(text_lower, results)
        
        # Calculate overall scores
        results['risk_score'] = min(1.0, (keyword_score + pattern_score) / 2)
        results['confidence'] = 0.85 if results['flags'] else 0.1
        
        return results
    
    def _detect_keywords(self, text: str, results: Dict) -> float:
        """Detect weapons-related keywords"""
        total_score = 0.0
        
        for category, keywords in self.weapons_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    results['detected_keywords'].append(f"{category}: {keyword}")
                    results['flags'].append(f"Detected {category} keyword: {keyword}")
                    total_score += 0.3
        
        return min(1.0, total_score)
    
    def _detect_patterns(self, text: str, results: Dict) -> float:
        """Detect suspicious communication patterns"""
        pattern_score = 0.0
        
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                results['detected_patterns'].extend(matches)
                results['flags'].append(f"Suspicious pattern detected")
                pattern_score += 0.4
        
        return min(1.0, pattern_score)