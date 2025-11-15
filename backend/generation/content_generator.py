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
    platform: str = None  # 'reddit', 'twitter', 'facebook', etc.
    content_length: str = 'medium'  # 'short', 'medium', 'long'

class SyntheticContentGenerator:
    def __init__(self):
        # Academic research disclaimer
        self.research_disclaimer = ""
        
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
        
        # Platform-specific styles
        self.platform_specific_styles = {
            'reddit': {
                'prefixes': ['WTS', 'WTB', 'ISO', 'PSA', 'TIL', 'FYI'],
                'hashtags': False,
                'mentions': False,
                'max_length': 1000
            },
            'twitter': {
                'prefixes': [],
                'hashtags': True,
                'mentions': True,
                'max_length': 280
            },
            'facebook': {
                'prefixes': [],
                'hashtags': True,
                'mentions': True,
                'max_length': 5000
            },
            'instagram': {
                'prefixes': [],
                'hashtags': True,
                'mentions': True,
                'max_length': 2200
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
    
    def generate_metadata(self, platform: str = None) -> Dict[str, Any]:
        """Generate synthetic metadata for content"""
        locations = ['NY', 'CA', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        platforms = ['Facebook', 'Craigslist', 'Reddit', 'Telegram', 'Discord', 'Twitter', 'Instagram']
        
        selected_platform = platform if platform else random.choice(platforms)
        
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        return {
            'timestamp': timestamp.isoformat(),
            'platform': selected_platform,
            'location': random.choice(locations),
            'user_id': f"user_{random.randint(10000, 99999)}",
            'post_id': f"post_{random.randint(100000, 999999)}"
        }
    
    def generate_post_content(self, params: ContentParameters) -> str:
        """Generate social media post style content"""
        vocab = self.vocabulary[params.intensity_level]
        
        # Different templates based on content length
        if params.content_length == 'short':
            templates = [
                "{action} {descriptor} {item}",
                "WTS: {descriptor} {item}",
                "ISO {descriptor} {item}",
                "Need {descriptor} {item} ASAP",
                "{item} for sale. {descriptor}",
            ]
        elif params.content_length == 'long':
            templates = [
            "Anyone know where I can find {item}? I'm specifically looking for {descriptor} quality items. {action} and would appreciate any leads or recommendations from the community.",
            "{action} {descriptor} {item}. Serious buyers only. This is a quality piece that I've had for a while and need to move. Feel free to reach out with questions.",
            "Looking for {descriptor} {item}. I've been {action} quickly and haven't had much luck with the usual sources. If anyone has recommendations or knows someone, please let me know.",
            "Have {descriptor} {item} available. {action}. This is a rare find and I'm willing to work with serious buyers. The condition is excellent and I can provide more details upon request.",
            "{item} for sale. {descriptor} condition. {action}. I've had this for a while and it's time to find it a new home. Comes with all original accessories and documentation.",
            "Need {descriptor} {item}. {action} ASAP for a project I'm working on. I'm willing to pay fair market value and can move quickly on the right piece.",
            "Selling {descriptor} {item}. {action}. PM me for details, photos, and pricing. I'm open to reasonable offers and can provide references if needed.",
            "WTS: {descriptor} {item}. {action}. This is a quality piece that I've maintained well. Looking for someone who will appreciate it. Serious inquiries only please.",
            "ISO {descriptor} {item}. {action}. I've been searching for a while and haven't found exactly what I'm looking for. If you have one or know someone who does, please reach out."
        ]
        else:  # medium
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
        
        # Apply platform-specific formatting
        if params.platform:
            content = self.apply_platform_formatting(content, params.platform)
        
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
        
        # Apply platform-specific formatting
        if params.platform:
            content = self.apply_platform_formatting(content, params.platform)
        
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
        
        # Apply platform-specific formatting
        if params.platform:
            content = self.apply_platform_formatting(content, params.platform)
        
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
        
        # Apply platform-specific formatting
        if params.platform:
            content = self.apply_platform_formatting(content, params.platform)
        
        return content
    
    def apply_platform_formatting(self, content: str, platform: str) -> str:
        """Apply platform-specific formatting"""
        if platform.lower() not in self.platform_specific_styles:
            return content
        
        style = self.platform_specific_styles[platform.lower()]
        
        # Add hashtags for platforms that support them
        if style['hashtags'] and random.random() > 0.5:
            hashtags = ['#trading', '#collectibles', '#gear', '#equipment', '#vintage']
            content += ' ' + ' '.join(random.sample(hashtags, random.randint(1, 3)))
        
        # Add mentions for platforms that support them
        if style['mentions'] and random.random() > 0.7:
            mentions = ['@user123', '@collector', '@trader']
            content = random.choice(mentions) + ' ' + content
        
        # Add platform-specific prefixes
        if style['prefixes'] and random.random() > 0.6:
            prefix = random.choice(style['prefixes'])
            content = f"{prefix}: {content}"
        
        # Truncate if exceeds platform max length
        if len(content) > style['max_length']:
            content = content[:style['max_length']-3] + '...'
        
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
            metadata = self.generate_metadata(params.platform)
            
            # Compile final content object
            content_object = {
                'id': f"synthetic_{random.randint(100000, 999999)}",
                'content': f"{self.research_disclaimer} {content}",
                'parameters': {
                    'type': params.content_type,
                    'intensity': params.intensity_level,
                    'language': params.language,
                    'platform': params.platform or metadata['platform'],
                    'content_length': params.content_length
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
    
    def generate_big_data_batch(self, total_quantity: int = 2000, platforms: List[str] = None, 
                                  content_lengths: List[str] = None) -> Dict[str, Any]:
        """Generate a large batch of content for big data analysis"""
        if platforms is None:
            platforms = ['reddit', 'twitter', 'facebook', 'instagram']
        if content_lengths is None:
            content_lengths = ['short', 'medium', 'long']
        
        all_content = []
        content_types = ['post', 'message', 'ad', 'forum']
        intensity_levels = ['low', 'medium', 'high']
        
        # Calculate distribution
        items_per_combination = max(1, total_quantity // (len(platforms) * len(content_lengths) * len(content_types) * len(intensity_levels)))
        
        print(f"Generating {total_quantity} posts across {len(platforms)} platforms, {len(content_lengths)} lengths...")
        
        generated_count = 0
        for platform in platforms:
            for content_length in content_lengths:
                for content_type in content_types:
                    for intensity in intensity_levels:
                        if generated_count >= total_quantity:
                            break
                        
                        # Calculate how many to generate for this combination
                        remaining = total_quantity - generated_count
                        quantity = min(items_per_combination, remaining)
                        
                        if quantity > 0:
                            params = ContentParameters(
                                content_type=content_type,
                                intensity_level=intensity,
                                quantity=quantity,
                                platform=platform,
                                content_length=content_length,
                                include_contact=random.random() > 0.7,  # 30% include contact
                                include_pricing=random.random() > 0.6   # 40% include pricing
                            )
                            
                            content = self.generate_content(params)
                            all_content.extend(content)
                            generated_count += len(content)
                            
                            if generated_count % 100 == 0:
                                print(f"Generated {generated_count}/{total_quantity} posts...")
        
        # Generate final batch with remaining items if needed
        if generated_count < total_quantity:
            remaining = total_quantity - generated_count
            params = ContentParameters(
                content_type=random.choice(content_types),
                intensity_level=random.choice(intensity_levels),
                quantity=remaining,
                platform=random.choice(platforms),
                content_length=random.choice(content_lengths),
                include_contact=random.random() > 0.7,
                include_pricing=random.random() > 0.6
            )
            content = self.generate_content(params)
            all_content.extend(content)
            generated_count += len(content)
        
        # Shuffle for randomness
        random.shuffle(all_content)
        
        # Generate statistics
        platform_distribution = {}
        length_distribution = {}
        intensity_distribution = {}
        
        for item in all_content:
            platform = item['parameters'].get('platform', 'unknown')
            platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            
            length = item['parameters'].get('content_length', 'unknown')
            length_distribution[length] = length_distribution.get(length, 0) + 1
            
            intensity = item['parameters'].get('intensity', 'unknown')
            intensity_distribution[intensity] = intensity_distribution.get(intensity, 0) + 1
        
        return {
            'content': all_content,
            'statistics': {
                'total_generated': len(all_content),
                'platform_distribution': platform_distribution,
                'length_distribution': length_distribution,
                'intensity_distribution': intensity_distribution,
                'generation_time': datetime.now().isoformat(),
                'configuration': {
                    'total_quantity': total_quantity,
                    'platforms': platforms,
                    'content_lengths': content_lengths
                }
            }
        }