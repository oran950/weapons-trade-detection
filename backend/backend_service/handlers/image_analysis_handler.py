"""
Image Analysis Handler - Weapon detection in images using LLaVA vision model
"""
import os
import base64
import json
import httpx
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from io import BytesIO

# Configure logger
logger = logging.getLogger("ImageAnalysisHandler")
logger.setLevel(logging.DEBUG)

# Image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class WeaponDetection:
    """Represents a detected weapon in an image"""
    weapon_type: str  # e.g., "handgun", "rifle", "knife"
    confidence: float  # 0.0 to 1.0
    description: str  # Detailed description
    location_hint: str  # e.g., "center", "left side", "top right"
    risk_level: str  # HIGH, MEDIUM, LOW
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImageAnalysisResult:
    """Result of analyzing an image for weapons"""
    image_url: str
    analyzed_at: str
    contains_weapons: bool
    weapon_count: int
    detections: List[WeaponDetection]
    overall_risk: str  # HIGH, MEDIUM, LOW
    risk_score: float  # 0.0 to 1.0
    analysis_notes: str
    processing_time_ms: int
    model_used: str
    annotated_image_base64: Optional[str] = None  # Base64 encoded annotated image
    analysis_completed: bool = True  # False if timeout/error occurred
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'detections': [d.to_dict() for d in self.detections]
        }


class ImageAnalysisHandler:
    """
    Handles weapon detection in images using LLaVA vision model through Ollama.
    """
    
    # Weapon detection prompt for LLaVA - optimized for accurate detection
    WEAPON_DETECTION_PROMPT = """You are a weapons detection expert. Analyze this image carefully and identify ANY weapons present.

WEAPONS TO DETECT:
- Handguns/Pistols (Glock, Sig Sauer, Beretta, 1911, revolvers, etc.)
- Rifles (AR-15, AK-47, hunting rifles, sniper rifles)
- Shotguns
- Knives, machetes, swords
- Explosives, grenades
- Any other weapon or dangerous object

IMPORTANT: If you see a gun, pistol, or firearm of ANY kind, set "contains_weapons" to TRUE.

Respond ONLY in JSON format:
{
    "contains_weapons": true/false,
    "weapons_detected": [
        {
            "type": "handgun/rifle/shotgun/knife/explosive/other",
            "description": "detailed description including brand if visible (e.g., 'Black Glock pistol')",
            "location": "center/left/right/top/bottom",
            "confidence": 0.0-1.0,
            "model_or_brand": "Glock/Sig Sauer/AR-15/AK-47/unknown etc."
        }
    ],
    "context": "describe what's shown in the image",
    "risk_assessment": "HIGH/MEDIUM/LOW",
    "notes": "additional observations"
}

Be thorough but avoid false positives. Common false positives to avoid:
- Toy guns (usually brightly colored)
- Camera equipment or tools
- Umbrellas or walking sticks
- Gaming controllers or electronics"""

    def __init__(
        self,
        ollama_base: str = None,
        vision_model: str = None,
        timeout: int = 120
    ):
        """
        Initialize the image analysis handler.
        
        Args:
            ollama_base: Ollama API base URL
            vision_model: Vision model to use (e.g., llava:7b)
            timeout: Request timeout in seconds
        """
        self.ollama_base = ollama_base or os.getenv("OLLAMA_BASE", "http://localhost:11434")
        self.vision_model = vision_model or os.getenv("OLLAMA_VISION_MODEL", "llava:7b")
        self.timeout = timeout
        
        if not PIL_AVAILABLE:
            print("⚠️ PIL/Pillow not installed. Image annotation disabled.", flush=True)
    
    async def check_model_available(self) -> bool:
        """Check if the vision model is available in Ollama."""
        print(f"🔍 Checking vision model: {self.vision_model} at {self.ollama_base}", flush=True)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.ollama_base}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m['name'] for m in data.get('models', [])]
                    print(f"   Available models: {models}", flush=True)
                    is_available = any(self.vision_model in m for m in models)
                    if is_available:
                        print(f"✅ Vision model '{self.vision_model}' is available", flush=True)
                    else:
                        print(f"⚠️ Vision model '{self.vision_model}' not found", flush=True)
                    return is_available
        except httpx.ConnectError as e:
            print(f"❌ Cannot connect to Ollama at {self.ollama_base}: {e}", flush=True)
        except Exception as e:
            print(f"❌ Error checking vision model: {type(e).__name__}: {e}", flush=True)
        return False
    
    async def download_image(self, image_url: str) -> Optional[bytes]:
        """Download an image from URL."""
        print(f"   📥 Downloading image: {image_url[:60]}...", flush=True)
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                # Handle Reddit's HTML-encoded URLs
                clean_url = image_url.replace('&amp;', '&')
                response = await client.get(clean_url)
                if response.status_code == 200:
                    print(f"   ✅ Image: {len(response.content)} bytes", flush=True)
                    return response.content
                print(f"   ⚠️ Image download failed: HTTP {response.status_code}", flush=True)
        except Exception as e:
            print(f"   ❌ Error downloading image: {type(e).__name__}: {e}", flush=True)
        return None
    
    async def analyze_image(self, image_url: str) -> ImageAnalysisResult:
        """
        Analyze an image for weapons using LLaVA.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            ImageAnalysisResult with detection details
        """
        start_time = datetime.now()
        print(f"🔫 Vision analyzing image: {image_url[:60]}...", flush=True)
        
        # Download the image
        image_data = await self.download_image(image_url)
        if not image_data:
            print(f"   ⚠️ Image download failed, skipping analysis", flush=True)
            return ImageAnalysisResult(
                image_url=image_url,
                analyzed_at=datetime.now().isoformat(),
                contains_weapons=False,
                weapon_count=0,
                detections=[],
                overall_risk="LOW",
                risk_score=0.0,
                analysis_notes="Failed to download image",
                processing_time_ms=0,
                model_used=self.vision_model
            )
        
        # Resize image if too large (speeds up LLaVA significantly)
        if PIL_AVAILABLE and len(image_data) > 500000:  # If > 500KB
            try:
                img = Image.open(BytesIO(image_data))
                # Resize to max 800x800 while keeping aspect ratio
                max_size = 800
                if img.width > max_size or img.height > max_size:
                    ratio = min(max_size / img.width, max_size / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"   📐 Resized image: {new_size[0]}x{new_size[1]}", flush=True)
                
                # Convert to RGB if needed and compress
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Save as JPEG with quality 85
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                image_data = buffer.getvalue()
                print(f"   📦 Compressed: {len(image_data)//1000}KB", flush=True)
            except Exception as e:
                print(f"   ⚠️ Image resize failed, using original: {e}", flush=True)
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"   📤 Sending to LLaVA: {len(image_base64)//1000}KB, model={self.vision_model}", flush=True)
        
        # Call LLaVA for analysis
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                print(f"   ⏳ Calling Ollama vision API (timeout={self.timeout}s)...", flush=True)
                response = await client.post(
                    f"{self.ollama_base}/api/generate",
                    json={
                        "model": self.vision_model,
                        "prompt": self.WEAPON_DETECTION_PROMPT,
                        "images": [image_base64],
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent detection
                            "num_predict": 1024
                        }
                    }
                )
                
                if response.status_code != 200:
                    print(f"   ❌ Ollama vision API error: HTTP {response.status_code}", flush=True)
                    raise Exception(f"Ollama returned status {response.status_code}")
                
                result = response.json()
                llm_response = result.get('response', '')
                print(f"   📥 LLaVA response: {len(llm_response)} chars", flush=True)
                
        except httpx.TimeoutException as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"⏱️ VISION TIMEOUT after {processing_time}ms: {e}", flush=True)
            return ImageAnalysisResult(
                image_url=image_url,
                analyzed_at=datetime.now().isoformat(),
                contains_weapons=False,
                weapon_count=0,
                detections=[],
                overall_risk="LOW",
                risk_score=0.0,
                analysis_notes=f"Vision analysis timed out after {self.timeout}s",
                processing_time_ms=processing_time,
                model_used=self.vision_model,
                analysis_completed=False  # Timeout - don't mark as verified
            )
        except httpx.ConnectError as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"❌ VISION CONNECTION ERROR - Cannot reach Ollama: {e}", flush=True)
            return ImageAnalysisResult(
                image_url=image_url,
                analyzed_at=datetime.now().isoformat(),
                contains_weapons=False,
                weapon_count=0,
                detections=[],
                overall_risk="LOW",
                risk_score=0.0,
                analysis_notes=f"Connection error: Ollama unreachable",
                processing_time_ms=processing_time,
                model_used=self.vision_model,
                analysis_completed=False  # Error - don't mark as verified
            )
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"❌ VISION ANALYSIS ERROR: {type(e).__name__}: {e}", flush=True)
            return ImageAnalysisResult(
                image_url=image_url,
                analyzed_at=datetime.now().isoformat(),
                contains_weapons=False,
                weapon_count=0,
                detections=[],
                overall_risk="LOW",
                risk_score=0.0,
                analysis_notes=f"Analysis failed: {str(e)}",
                processing_time_ms=processing_time,
                model_used=self.vision_model,
                analysis_completed=False  # Error - don't mark as verified
            )
        
        # Parse LLM response
        detections, risk_assessment, notes = self._parse_llm_response(llm_response)
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Calculate overall risk score
        if detections:
            risk_score = max(d.confidence for d in detections)
            if risk_assessment == "HIGH":
                risk_score = max(risk_score, 0.8)
            elif risk_assessment == "MEDIUM":
                risk_score = max(risk_score, 0.5)
            weapon_types = [d.weapon_type for d in detections]
            print(f"🔫 WEAPONS DETECTED! {processing_time}ms | Count: {len(detections)} | Types: {weapon_types}", flush=True)
        else:
            risk_score = 0.0
            print(f"✅ No weapons in {processing_time}ms", flush=True)
        
        # Create annotated image if weapons detected
        annotated_base64 = None
        if detections and PIL_AVAILABLE:
            print(f"   🖼️ Creating annotated image with {len(detections)} markers", flush=True)
            annotated_base64 = self._create_annotated_image(image_data, detections)
        
        return ImageAnalysisResult(
            image_url=image_url,
            analyzed_at=datetime.now().isoformat(),
            contains_weapons=len(detections) > 0,
            weapon_count=len(detections),
            detections=detections,
            overall_risk=risk_assessment,
            risk_score=risk_score,
            analysis_notes=notes,
            processing_time_ms=processing_time,
            model_used=self.vision_model,
            annotated_image_base64=annotated_base64
        )
    
    def _parse_llm_response(self, response: str) -> Tuple[List[WeaponDetection], str, str]:
        """Parse the LLM response into structured detections."""
        detections = []
        risk_assessment = "LOW"
        notes = ""
        
        print(f"   🔍 Parsing LLaVA response ({len(response)} chars)...", flush=True)
        
        try:
            # Try to extract JSON from response
            json_match = response.strip()
            
            # Handle cases where response might have extra text
            if '{' in json_match:
                start = json_match.index('{')
                end = json_match.rindex('}') + 1
                json_str = json_match[start:end]
                data = json.loads(json_str)
                
                # Log parsed JSON summary
                contains = data.get('contains_weapons', False)
                weapons_list = data.get('weapons_detected', [])
                print(f"   📋 Parsed: contains_weapons={contains}, weapons_count={len(weapons_list)}", flush=True)
                
                risk_assessment = data.get('risk_assessment', 'LOW')
                notes = data.get('notes', '')
                context = data.get('context', '')
                
                if context:
                    notes = f"{context}. {notes}"
                
                # If contains_weapons is true but list is empty, create generic detection
                if contains and len(weapons_list) == 0:
                    print(f"   ⚠️ Model says contains_weapons=true but no list - creating generic detection", flush=True)
                    detections.append(WeaponDetection(
                        weapon_type='weapon',
                        confidence=0.7,
                        description=context or 'Weapon detected in image',
                        location_hint='unknown',
                        risk_level='MEDIUM'
                    ))
                    risk_assessment = 'MEDIUM'
                
                # Parse weapons from list
                for weapon in weapons_list:
                    confidence = float(weapon.get('confidence', 0.5))
                    weapon_type = weapon.get('type', 'unknown').lower()
                    
                    # Determine risk level based on weapon type and confidence
                    if weapon_type in ['rifle', 'shotgun', 'explosive', 'assault', 'ar-15', 'ak-47']:
                        weapon_risk = 'HIGH'
                    elif weapon_type in ['handgun', 'pistol', 'gun', 'firearm', 'revolver']:
                        weapon_risk = 'HIGH' if confidence > 0.7 else 'MEDIUM'
                    elif weapon_type in ['knife', 'blade', 'machete', 'sword']:
                        weapon_risk = 'MEDIUM'
                    else:
                        weapon_risk = 'MEDIUM' if confidence > 0.5 else 'LOW'
                    
                    detections.append(WeaponDetection(
                        weapon_type=weapon_type,
                        confidence=confidence,
                        description=weapon.get('description', ''),
                        location_hint=weapon.get('location', 'unknown'),
                        risk_level=weapon_risk
                    ))
                    print(f"   ✅ Detected: {weapon_type} ({confidence:.0%} confidence)", flush=True)
            else:
                # No JSON found - try to detect weapons from plain text
                print(f"   ⚠️ No JSON in response, checking text...", flush=True)
                response_lower = response.lower()
                if any(w in response_lower for w in ['gun', 'pistol', 'rifle', 'firearm', 'weapon', 'handgun', 'glock', 'revolver']):
                    print(f"   🔫 Weapon keywords found in non-JSON response", flush=True)
                    detections.append(WeaponDetection(
                        weapon_type='firearm',
                        confidence=0.6,
                        description='Weapon mentioned in analysis',
                        location_hint='unknown',
                        risk_level='MEDIUM'
                    ))
                    risk_assessment = 'MEDIUM'
                    notes = response[:200]
                    
        except json.JSONDecodeError as e:
            notes = f"Could not parse response: {response[:200]}"
            print(f"   ❌ JSON parse error: {e}", flush=True)
        except Exception as e:
            notes = f"Parse error: {str(e)}"
            print(f"   ❌ Parse error: {e}", flush=True)
        
        return detections, risk_assessment, notes
    
    def _create_annotated_image(
        self,
        image_data: bytes,
        detections: List[WeaponDetection]
    ) -> Optional[str]:
        """
        Create an annotated version of the image with weapon markers.
        
        Since LLaVA doesn't provide bounding boxes, we add text overlays
        indicating detected weapons.
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            # Open image
            img = Image.open(BytesIO(image_data))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create overlay for annotations
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
                small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            except:
                font = ImageFont.load_default()
                small_font = font
            
            # Add warning banner at top
            banner_height = 40
            draw.rectangle([(0, 0), (img.width, banner_height)], fill=(255, 0, 0, 200))
            
            warning_text = f"⚠️ {len(detections)} WEAPON(S) DETECTED"
            # Get text size for centering
            bbox = draw.textbbox((0, 0), warning_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            draw.text((x, 8), warning_text, fill=(255, 255, 255, 255), font=font)
            
            # Add detection labels at bottom
            y_offset = img.height - (len(detections) * 30) - 10
            for i, detection in enumerate(detections):
                label = f"• {detection.weapon_type.upper()}: {detection.description} ({int(detection.confidence * 100)}%)"
                
                # Draw semi-transparent background for text
                bbox = draw.textbbox((10, y_offset), label, font=small_font)
                padding = 5
                draw.rectangle(
                    [(bbox[0] - padding, bbox[1] - padding), 
                     (bbox[2] + padding, bbox[3] + padding)],
                    fill=(0, 0, 0, 180)
                )
                
                # Color based on risk level
                if detection.risk_level == 'HIGH':
                    color = (255, 50, 50, 255)
                elif detection.risk_level == 'MEDIUM':
                    color = (255, 200, 50, 255)
                else:
                    color = (100, 255, 100, 255)
                
                draw.text((10, y_offset), label, fill=color, font=small_font)
                y_offset += 30
            
            # Composite the overlay onto the original image
            result = Image.alpha_composite(img, overlay)
            
            # Convert back to RGB for JPEG encoding
            result = result.convert('RGB')
            
            # Encode to base64
            buffer = BytesIO()
            result.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Error creating annotated image: {e}")
            return None
    
    async def analyze_batch(
        self,
        image_urls: List[str],
        max_concurrent: int = 3
    ) -> List[ImageAnalysisResult]:
        """
        Analyze multiple images concurrently.
        
        Args:
            image_urls: List of image URLs to analyze
            max_concurrent: Maximum concurrent analyses
            
        Returns:
            List of ImageAnalysisResult objects
        """
        import asyncio
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_limit(url: str) -> ImageAnalysisResult:
            async with semaphore:
                return await self.analyze_image(url)
        
        tasks = [analyze_with_limit(url) for url in image_urls]
        results = await asyncio.gather(*tasks)
        return results

