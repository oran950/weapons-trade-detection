"""
Hashing utilities for privacy protection
"""
import hashlib
from typing import Optional


def hash_username(username: str, salt: str = "") -> str:
    """
    Hash usernames for privacy protection
    
    Args:
        username: The username to hash
        salt: Optional salt for additional security
        
    Returns:
        First 16 characters of SHA-256 hash
    """
    if not username or username in ("[deleted]", "anonymous", ""):
        return "anonymous"
    
    to_hash = f"{salt}{username}" if salt else username
    return hashlib.sha256(to_hash.encode()).hexdigest()[:16]


def hash_content(content: str, full_hash: bool = False) -> str:
    """
    Hash content for deduplication and privacy
    
    Args:
        content: The content to hash
        full_hash: Whether to return full hash or truncated
        
    Returns:
        SHA-256 hash of content
    """
    if not content:
        return ""
    
    hash_result = hashlib.sha256(content.encode()).hexdigest()
    return hash_result if full_hash else hash_result[:32]


def hash_email(email: str) -> str:
    """
    Hash email addresses for privacy
    
    Args:
        email: The email to hash
        
    Returns:
        Hashed email with domain preserved for analysis
    """
    if not email or "@" not in email:
        return "anonymous_email"
    
    local, domain = email.split("@", 1)
    hashed_local = hashlib.sha256(local.encode()).hexdigest()[:8]
    return f"{hashed_local}@{domain}"


def hash_phone(phone: str) -> str:
    """
    Hash phone numbers, preserving country code for analysis
    
    Args:
        phone: The phone number to hash
        
    Returns:
        Partially hashed phone number
    """
    if not phone:
        return "anonymous_phone"
    
    # Remove non-digits
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) < 4:
        return "anonymous_phone"
    
    # Keep last 4 digits visible for pattern analysis
    hidden_part = hashlib.sha256(digits[:-4].encode()).hexdigest()[:4]
    return f"***{hidden_part}{digits[-4:]}"

