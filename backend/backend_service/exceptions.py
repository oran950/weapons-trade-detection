"""
Custom exceptions for the backend service
"""


class WeaponsDetectionError(Exception):
    """Base exception for weapons detection system"""
    pass


class ConfigurationError(WeaponsDetectionError):
    """Raised when required configuration is missing"""
    
    def __init__(self, missing_config: list):
        self.missing_config = missing_config
        super().__init__(f"Missing configuration: {', '.join(missing_config)}")


class CollectionError(WeaponsDetectionError):
    """Raised when data collection fails"""
    
    def __init__(self, platform: str, reason: str):
        self.platform = platform
        self.reason = reason
        super().__init__(f"Collection failed for {platform}: {reason}")


class AnalysisError(WeaponsDetectionError):
    """Raised when analysis fails"""
    
    def __init__(self, content_id: str, reason: str):
        self.content_id = content_id
        self.reason = reason
        super().__init__(f"Analysis failed for {content_id}: {reason}")


class LLMError(WeaponsDetectionError):
    """Raised when LLM operations fail"""
    
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"LLM {operation} failed: {reason}")


class RateLimitError(WeaponsDetectionError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, platform: str, retry_after: int = 60):
        self.platform = platform
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {platform}. Retry after {retry_after}s")


class AuthenticationError(WeaponsDetectionError):
    """Raised when authentication fails"""
    
    def __init__(self, platform: str):
        self.platform = platform
        super().__init__(f"Authentication failed for {platform}")


class FileOperationError(WeaponsDetectionError):
    """Raised when file operations fail"""
    
    def __init__(self, operation: str, filepath: str, reason: str):
        self.operation = operation
        self.filepath = filepath
        self.reason = reason
        super().__init__(f"File {operation} failed for {filepath}: {reason}")

