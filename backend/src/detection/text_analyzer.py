import re
from datetime import datetime
from typing import List, Dict, Any
import string

class WeaponsTextAnalyzer:
    def __init__(self):
        # No heavy AI models - just fast rule-based detection
        print("Initializing lightweight weapons analyzer (no AI models)")
        
        # Comprehensive weapons keywords - any of these should trigger HIGH risk
        self.high_risk_keywords = {
            'firearms': [
                'gun', 'rifle', 'pistol', 'firearm', 'ammunition', 'bullet', 'shotgun', 'handgun',
                'glock', 'ak47', 'ak-47', 'ar15', 'ar-15', 'beretta', 'smith', 'wesson', 'colt',
                'sig', 'sauer', 'ruger', 'remington', 'winchester', 'mossberg', 'revolver',
                'carbine', 'submachine', 'assault rifle', 'sniper', 'scope', 'silencer', 'suppressor',
                # Military weapons
                'm16', 'm4', 'm249', 'm240', 'm14', 'm1911', 'uzi', 'mp5', 'mp7', 'scar', 'fal',
                'hk416', 'g36', 'aug', 'tavor', 'galil', 'aks74', 'rpk', 'pkm', 'mg42', 'm60',
                # Common slang and abbreviations
                'piece', 'heat', 'strap', 'burner', 'nine', 'forty', 'deagle', 'desert eagle',
                'mac10', 'mac11', 'tec9', 'draco', 'choppa', 'stick', 'iron', 'tool', 'biscuit',
                # Ammunition types
                'ammo', 'rounds', 'shells', 'cartridge', 'hollow point', 'fmj', '9mm', '.45',
                '.40', '.380', '.22', '.223', '.308', '.50cal', '7.62', '5.56', '.38', '.357',
                # Weapon parts and accessories
                'barrel', 'trigger', 'stock', 'grip', 'magazine', 'clip', 'chamber', 'laser sight',
                'red dot', 'holster', 'extended mag', 'drum mag', 'bipod', 'muzzle brake'
            ],
            'explosives': [
                'bomb', 'explosive', 'grenade', 'dynamite', 'c4', 'tnt', 'semtex', 'plastique',
                'detonator', 'fuse', 'pipe bomb', 'molotov', 'ied', 'claymore', 'mine', 'rpg',
                'rocket', 'launcher', 'mortar', 'bazooka', 'stinger', 'javelin', 'tow missile',
                'flash bang', 'smoke grenade', 'frag', 'he round', 'incendiary', 'napalm',
                'thermite', 'anfo', 'petn', 'rdx', 'composition', 'blasting cap', 'det cord'
            ],
            'violence': [
                'kill', 'murder', 'assassinate', 'eliminate', 'terminate', 'harm', 'hurt', 'attack',
                'shoot', 'shooting', 'massacre', 'slaughter', 'execute', 'destroy', 'annihilate',
                'neutralize', 'take out', 'waste', 'cap', 'pop', 'smoke', 'ice', 'off', 'whack',
                'hit', 'merc', 'clap', 'drop', 'spray', 'light up', 'swiss cheese', 'headshot',
                'bodycount', 'carnage', 'bloodbath', 'rampage', 'spree', 'hostile', 'target'
            ],
            'illegal_terms': [
                'smuggling', 'black market', 'illegal sale', 'trafficking', 'contraband',
                'untraceable', 'cash only', 'no questions', 'discrete', 'private sale',
                'under the table', 'off the books', 'no paperwork', 'serial numbers filed',
                'ghost gun', 'stolen', 'hot', 'clean', 'throwaway', 'burner phone',
                'meetup', 'drop off', 'pickup', 'stash', 'plug', 'connect', 'hook up',
                'no id', 'anonymous', 'crypto payment', 'bitcoin', 'prepaid card',
                'parking lot', 'back alley', 'warehouse', 'abandoned', 'secure location'
            ]
        }
        
        # Highly suspicious patterns - these should automatically trigger HIGH risk
        self.high_risk_patterns = [
            r'\b(?:buy|sell|trade|purchase|get|want|need|looking for|acquire|seeking)\s+(?:guns?|weapons?|firearms?|pistols?|rifles?|glock|ak47|ar15|m16|m4|uzi|mp5)\b',
            r'\b(?:want|need)\s+to\s+(?:buy|get|purchase|acquire)\s+(?:gun|weapon|firearm|pistol|rifle|glock|m16|ak47|ar15)\b',
            r'\b(?:sell|selling|trade|trading|offering)\s+(?:guns?|weapons?|firearms?|ammunition|ammo|bullets?)\b',
            r'\b(?:cash\s+only|no\s+questions?|untraceable|private\s+sale|ghost\s+gun|stolen\s+gun)\b',
            r'\b(?:buy|get|purchase)\s+(?:to\s+)?(?:kill|murder|harm|shoot|eliminate)\b',
            r'\b(?:illegal|black\s+market|under\s+the\s+table)\s+(?:guns?|weapons?|firearms?)\b',
            r'\b(?:m16|m4|ak47|ar15|uzi|mp5|scar|fal|hk416)\b',
            r'\b(?:9mm|\.45|\.40|\.38|\.357|\.22|\.223|\.308|5\.56|7\.62)\b'
        ]
        
        # Medium risk patterns
        self.medium_risk_patterns = [
            r'\b(?:self\s+defense|protection|security)\s+(?:weapon|gun|firearm)\b',
            r'\b(?:hunting|sport|target\s+practice)\s+(?:rifle|gun|firearm)\b'
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        # Remove extra whitespace and convert to lowercase
        text = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove punctuation but keep spaces
        text = text.translate(str.maketrans('', '', string.punctuation.replace(' ', '')))
        return text
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text with aggressive weapons detection"""
        
        original_text = text
        cleaned_text = self.clean_text(text)
        
        # Initialize results
        results = {
            'risk_score': 0.0,
            'confidence': 0.9,  # High confidence in our detection
            'flags': [],
            'detected_keywords': [],
            'detected_patterns': [],
            'analysis_time': datetime.now().isoformat()
        }
        
        # Check for high-risk keywords (each adds significant risk)
        for category, keywords in self.high_risk_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in cleaned_text:
                    found_keywords.append(keyword)
                    results['risk_score'] += 0.4  # Each keyword adds 40% risk
                    results['flags'].append(f"HIGH RISK: Detected {category} keyword '{keyword}'")
            
            if found_keywords:
                results['detected_keywords'].append(f"{category}: {', '.join(found_keywords)}")
        
        # Check for high-risk patterns (each adds major risk)
        for pattern in self.high_risk_patterns:
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    results['detected_patterns'].append(match)
                    results['risk_score'] += 0.5  # Each pattern adds 50% risk
                    results['flags'].append(f"HIGH RISK: Suspicious intent pattern detected: '{match}'")
        
        # Check for medium-risk patterns
        for pattern in self.medium_risk_patterns:
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    results['detected_patterns'].append(match)
                    results['risk_score'] += 0.3  # Medium risk patterns
                    results['flags'].append(f"MEDIUM RISK: Pattern detected: '{match}'")
        
        # Special combinations that boost risk
        has_weapon_keyword = any(category in ['firearms', 'explosives'] 
                               for category in self.high_risk_keywords.keys() 
                               if any(kw in cleaned_text for kw in self.high_risk_keywords[category]))
        
        has_buy_sell_intent = any(word in cleaned_text for word in ['buy', 'sell', 'trade', 'purchase', 'want', 'need', 'get'])
        has_violence_keyword = any(kw in cleaned_text for kw in self.high_risk_keywords['violence'])
        
        # Boost score for dangerous combinations
        if has_weapon_keyword and has_buy_sell_intent:
            results['risk_score'] += 0.3
            results['flags'].append("CRITICAL: Weapon + transaction intent detected")
        
        if has_weapon_keyword and has_violence_keyword:
            results['risk_score'] += 0.4
            results['flags'].append("CRITICAL: Weapon + violence intent detected")
        
        # Cap risk score at 1.0 and ensure minimum thresholds
        results['risk_score'] = min(results['risk_score'], 1.0)
        
        # Force HIGH risk for any weapon-related content
        if has_weapon_keyword or results['detected_keywords'] or results['detected_patterns']:
            results['risk_score'] = max(results['risk_score'], 0.7)  # Minimum 70% for any weapons content
        
        # Override: Any mention of specific weapons should be HIGH risk
        weapon_mentions = ['gun', 'pistol', 'rifle', 'glock', 'firearm', 'weapon', 'ak47', 'ar15', 
                          'm16', 'm4', 'uzi', 'mp5', 'beretta', 'colt', 'smith', 'wesson', 'sig',
                          'remington', 'winchester', 'mossberg', 'ruger', 'scar', 'fal', 'aug', 'tavor']
        if any(weapon in cleaned_text for weapon in weapon_mentions):
            results['risk_score'] = max(results['risk_score'], 0.8)  # Minimum 80% for direct weapon mentions
            if not any("HIGH RISK" in flag for flag in results['flags']):
                results['flags'].append("HIGH RISK: Direct weapon reference detected")
        
        return results