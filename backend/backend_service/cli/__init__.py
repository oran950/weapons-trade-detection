"""
CLI Module - Command-line interface for batch operations

Usage:
    python -m backend_service.cli.collect reddit -s news worldnews -t day -l 50
    python -m backend_service.cli.analyze text "some text to analyze"
"""

# Lazy imports to avoid circular dependencies
def get_collection_cli():
    from .collect import CollectionCLI
    return CollectionCLI

def get_analysis_cli():
    from .analyze import AnalysisCLI
    return AnalysisCLI

__all__ = ["get_collection_cli", "get_analysis_cli"]

