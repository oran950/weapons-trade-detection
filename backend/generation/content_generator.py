import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class ContentParameters:
    content_type: str  # 'post', 'message', 'ad', 'forum'
    intensity_level: str  # 'low', 'medium', 'high'
    language: str = 'en'
    include_contact: bool = False
    include_pricing: bool = False
    quantity: int = 1

class SyntheticContentGenerator:
    def __init__(self):
        # Academic research disclaimer
        self.research_disclaimer = "[SYNTHETIC DATA FOR ACADEMIC RESEARCH ONLY]"
        
        # Vocabulary organized by intensity levels
        self.vocabulary = {
            'low': {
                'items': ['sporting goods', 'collectibles', 'antiques', 'equipment', 'gear', 'tools', 'accessories'],
                'descriptors': ['vintage', 'classic', 'rare', 'authentic', 'quality', 'professional', 'premium'],
                'actions': ['selling', 'trading', 'looking for', 'interested in', 'collecting', 'seeking', 'wanting']
            },
            'medium': {
                'items': ['tactical gear', 'survival equipment', 'protection items', 'security tools', 'defense gear', 'tactical accessories'],
                'descriptors': ['military-style', 'professional-grade', 'heavy-duty', 'specialized', 'tactical', 'combat-ready'],
                'actions': ['need', 'seeking', 'want to acquire', 'looking to purchase', 'require', 'must have']
            },
            'high': {
                'items': ['firearms', 'weapons', 'guns', 'pistols', 'rifles', 'tactical equipment', 'defense items', 'ammunition'],
                'descriptors': ['untraceable', 'no questions asked', 'cash only', 'discrete', 'private', 'clean', 'reliable'],
                'actions': ['need asap', 'urgent', 'cash deal', 'private transaction', 'quick sale', 'immediate need']
            }
        }
        
        # Communication patterns by platform type
        self.platform_styles = {
            'post': {
                'format': 'social_media',
                'length': 'short',
                'tone': 'casual'
            },
            'message': {
                'format': 'direct_message', 
                'length': 'medium',
                'tone': 'personal'
            },
            'ad': {
                'format': 'classified',
                'length': 'structured',
                'tone': 'business'
            },
            'forum': {
                'format': 'discussion',
                'length': 'long',
                'tone': 'community'
            }
        }
        
        # Contact generation templates
        self.contact_templates = [
            "Text {phone}",
            "Email {email}",
            "Contact via {app}",
            "DM for details",
            "Signal: {phone}",
            "Telegram: @{username}",
            "WhatsApp {phone}",
            "Discord: {username}",
            "Call {phone}"
        ]
        
        # Pricing patterns
        self.pricing_patterns = [
            "${amount}",
            "${amount} firm",
            "${amount} OBO",
            "Best offer",
            "Price negotiable",
            "Cash only ${amount}",
            "${amount} no trades",
            "Starting at ${amount}",
            "${amount} each"
        ]
    
    def generate_contact_info(self) -> Dict[str, str]:
        """Generate synthetic contact information"""
        fake_phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        fake_email = f"user{random.randint(100, 999)}@tempmail.com"
        fake_username = f"user_{random.randint(1000, 9999)}"
        apps = ['WhatsApp', 'Telegram', 'Signal', 'Discord', 'Wire']
        
        return {
            'phone': fake_phone,
            'email': fake_email,
            'username': fake_username,
            'app': random.choice(apps)
        }
    
    def generate_pricing(self, intensity: str) -> str:
        """Generate synthetic pricing based on intensity"""
        if intensity == 'low':
            amount = random.randint(50, 500)
        elif intensity == 'medium':
            amount = random.randint(200, 1500)
        else:  # high
            amount = random.randint(500, 5000)
        
        template = random.choice(self.pricing_patterns)
        return template.format(amount=amount)
    
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate synthetic metadata for content"""
        locations = ['NY', 'CA', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        platforms = ['Facebook', 'Craigslist', 'Reddit', 'Telegram', 'Discord', 'Twitter', 'Instagram']
        
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        return {
            'timestamp': timestamp.isoformat(),
            'platform': random.choice(platforms),
            'location': random.choice(locations),
            'user_id': f"user_{random.randint(10000, 99999)}",
            'post_id': f"post_{random.randint(100000, 999999)}"
        }
    
    def generate_post_content(self, params: ContentParameters) -> str:
        """Generate social media post style content"""
        vocab = self.vocabulary[params.intensity_level]
        
        templates = [
            "Anyone know where I can find {item}? {descriptor} preferred. {action}",
            "{action} {descriptor} {item}. Serious buyers only.",
            "Looking for {descriptor} {item}. {action} quickly.",
            "Have {descriptor} {item} available. {action}.",
            "{item} for sale. {descriptor} condition. {action}.",
            "Need {descriptor} {item}. {action} ASAP.",
            "Selling {descriptor} {item}. {action}. PM me.",
            "WTS: {descriptor} {item}. {action}.",
            "ISO {descriptor} {item}. {action}."
        ]
        
        template = random.choice(templates)
        content = template.format(
            item=random.choice(vocab['items']),
            descriptor=random.choice(vocab['descriptors']),
            action=random.choice(vocab['actions'])
        )
        
        return content
    
    def generate_message_content(self, params: ContentParameters) -> str:
        """Generate direct message style content"""
        vocab = self.vocabulary[params.intensity_level]
        
        templates = [
            "Hey, heard you might have {item}. I'm {action} {descriptor} ones.",
            "Still have that {descriptor} {item}? I'm interested.",
            "Can you help me find {descriptor} {item}? {action} discretely.",
            "Friend referred me to you for {item}. {action} {descriptor} quality.",
            "Need {descriptor} {item} for collection. {action} authentic pieces.",
            "You still dealing with {descriptor} {item}? {action} something reliable.",
            "Got any {descriptor} {item} available? {action} soon.",
            "Looking for {descriptor} {item}. Heard you're the person to talk to.",
            "Need to discuss {item}. {action} {descriptor} ones only."
        ]
        
        template = random.choice(templates)
        content = template.format(
            item=random.choice(vocab['items']),
            descriptor=random.choice(vocab['descriptors']),
            action=random.choice(vocab['actions'])
        )
        
        return content
    
    def generate_ad_content(self, params: ContentParameters) -> str:
        """Generate classified ad style content"""
        vocab = self.vocabulary[params.intensity_level]
        
        templates = [
            "{descriptor} {item} - {action}. Excellent condition.",
            "FOR SALE: {descriptor} {item}. {action} serious inquiries only.",
            "{item} available. {descriptor} quality. {action}.",
            "WANTED: {descriptor} {item}. {action} immediately.",
            "{descriptor} {item} collection. {action} individual pieces.",
            "SELLING: {descriptor} {item}. {action}. No lowballers.",
            "RARE {descriptor} {item}. {action}. Must see to appreciate.",
            "{item} - {descriptor}. {action}. Cash preferred.",
            "Moving sale: {descriptor} {item}. {action}."
        ]
        
        template = random.choice(templates)
        content = template.format(
            item=random.choice(vocab['items']),
            descriptor=random.choice(vocab['descriptors']),
            action=random.choice(vocab['actions'])
        )
        
        return content
    
    def generate_forum_content(self, params: ContentParameters) -> str:
        """Generate forum discussion style content"""
        vocab = self.vocabulary[params.intensity_level]
        
        templates = [
            "Has anyone had experience with {descriptor} {item}? I'm {action} and would appreciate advice on where to find quality pieces.",
            "New to collecting {item}. Looking for {descriptor} examples. Any recommendations on {action}?",
            "Community question: What's the best way to find {descriptor} {item}? I've been {action} but having trouble.",
            "Discussion: {descriptor} {item} availability. Where is everyone {action} these days?",
            "Advice needed: {action} {descriptor} {item} for research purposes. Any suggestions?",
            "Forum members: Anyone know reliable sources for {descriptor} {item}? {action} for project.",
            "Help needed: {action} {descriptor} {item}. What should I look for?",
            "Question for the community: Best places for {descriptor} {item}? {action} soon.",
            "Seeking guidance: {action} {descriptor} {item}. New to this area."
        ]
        
        template = random.choice(templates)
        content = template.format(
            item=random.choice(vocab['items']),
            descriptor=random.choice(vocab['descriptors']),
            action=random.choice(vocab['actions'])
        )
        
        return content
    
    def add_variations(self, content: str, intensity: str) -> str:
        """Add realistic variations like typos, abbreviations, etc."""
        if intensity == 'high':
            # Add more secretive language
            variations = {
                'selling': 'moving',
                'buying': 'looking',
                'gun': 'piece',
                'weapon': 'tool',
                'deal': 'transaction',
                'meet': 'connect'
            }
            for old, new in variations.items():
                if old in content.lower():
                    content = content.replace(old, new)
        
        return content
    
    def generate_content(self, params: ContentParameters) -> List[Dict[str, Any]]:
        """Main content generation function"""
        generated_content = []
        
        for _ in range(params.quantity):
            # Generate base content based on type
            if params.content_type == 'post':
                content = self.generate_post_content(params)
            elif params.content_type == 'message':
                content = self.generate_message_content(params)
            elif params.content_type == 'ad':
                content = self.generate_ad_content(params)
            elif params.content_type == 'forum':
                content = self.generate_forum_content(params)
            else:
                content = self.generate_post_content(params)  # default
            
            # Add variations
            content = self.add_variations(content, params.intensity_level)
            
            # Add contact info if requested
            contact_info = None
            if params.include_contact:
                contact_info = self.generate_contact_info()
                contact_template = random.choice(self.contact_templates)
                contact_text = contact_template.format(**contact_info)
                content += f" {contact_text}"
            
            # Add pricing if requested
            pricing = None
            if params.include_pricing:
                pricing = self.generate_pricing(params.intensity_level)
                content += f" {pricing}"
            
            # Generate metadata
            metadata = self.generate_metadata()
            
            # Compile final content object
            content_object = {
                'id': f"synthetic_{random.randint(100000, 999999)}",
                'content': f"{self.research_disclaimer} {content}",
                'parameters': {
                    'type': params.content_type,
                    'intensity': params.intensity_level,
                    'language': params.language
                },
                'metadata': metadata,
                'contact_info': contact_info,
                'pricing': pricing,
                'generated_at': datetime.now().isoformat()
            }
            
            generated_content.append(content_object)
        
        return generated_content
    
    def generate_batch(self, batch_config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate multiple content types in a batch"""
        results = {
            'low_intensity': [],
            'medium_intensity': [],
            'high_intensity': [],
            'statistics': {}
        }
        
        # Generate content for each intensity level
        for intensity in ['low', 'medium', 'high']:
            for content_type in ['post', 'message', 'ad', 'forum']:
                params = ContentParameters(
                    content_type=content_type,
                    intensity_level=intensity,
                    quantity=batch_config.get('quantity_per_type', 3),
                    include_contact=batch_config.get('include_contact', False),
                    include_pricing=batch_config.get('include_pricing', False)
                )
                
                content = self.generate_content(params)
                results[f'{intensity}_intensity'].extend(content)
        
        # Generate statistics
        total_generated = sum(len(results[key]) for key in results if key != 'statistics')
        results['statistics'] = {
            'total_generated': total_generated,
            'generation_time': datetime.now().isoformat(),
            'configuration': batch_config
        }
        
        return results