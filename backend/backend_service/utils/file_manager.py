"""
File management utilities for data storage
"""
import os
import json
import csv
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime
from pathlib import Path


class FileManager:
    """
    Manages file I/O operations for collected and analyzed data
    """
    
    def __init__(self, base_dir: str = "collected_data"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw_posts"
        self.analyzed_dir = self.base_dir / "analyzed_posts"
        self.reports_dir = self.base_dir / "reports"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories"""
        for directory in [self.raw_dir, self.analyzed_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, data: Dict[str, Any], filename: str, directory: str = "raw") -> str:
        """
        Save data to JSON file
        
        Args:
            data: Dictionary to save
            filename: Name of file (without extension)
            directory: 'raw', 'analyzed', or 'reports'
            
        Returns:
            Full path to saved file
        """
        dir_map = {
            "raw": self.raw_dir,
            "analyzed": self.analyzed_dir,
            "reports": self.reports_dir
        }
        
        target_dir = dir_map.get(directory, self.raw_dir)
        filepath = target_dir / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return str(filepath)
    
    def save_csv(self, data: List[Dict[str, Any]], filename: str, directory: str = "raw") -> str:
        """
        Save data to CSV file
        
        Args:
            data: List of dictionaries to save
            filename: Name of file (without extension)
            directory: 'raw', 'analyzed', or 'reports'
            
        Returns:
            Full path to saved file
        """
        dir_map = {
            "raw": self.raw_dir,
            "analyzed": self.analyzed_dir,
            "reports": self.reports_dir
        }
        
        target_dir = dir_map.get(directory, self.raw_dir)
        filepath = target_dir / f"{filename}.csv"
        
        if not data:
            with open(filepath, 'w', encoding='utf-8') as f:
                pass  # Create empty file
            return str(filepath)
        
        # Flatten nested dictionaries for CSV
        flattened_data = [self._flatten_dict(item) for item in data]
        
        fieldnames = list(flattened_data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        return str(filepath)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def load_json(self, filename: str, directory: str = "raw") -> Optional[Dict[str, Any]]:
        """
        Load data from JSON file
        
        Args:
            filename: Name of file (with or without extension)
            directory: 'raw', 'analyzed', or 'reports'
            
        Returns:
            Loaded dictionary or None if file doesn't exist
        """
        dir_map = {
            "raw": self.raw_dir,
            "analyzed": self.analyzed_dir,
            "reports": self.reports_dir
        }
        
        target_dir = dir_map.get(directory, self.raw_dir)
        
        # Add extension if not present
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = target_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_files(self, directory: str = "raw", extension: str = None) -> List[str]:
        """
        List files in a directory
        
        Args:
            directory: 'raw', 'analyzed', or 'reports'
            extension: Filter by extension (e.g., 'json', 'csv')
            
        Returns:
            List of filenames
        """
        dir_map = {
            "raw": self.raw_dir,
            "analyzed": self.analyzed_dir,
            "reports": self.reports_dir
        }
        
        target_dir = dir_map.get(directory, self.raw_dir)
        
        if not target_dir.exists():
            return []
        
        files = list(target_dir.iterdir())
        
        if extension:
            files = [f for f in files if f.suffix == f".{extension}"]
        
        return [f.name for f in files if f.is_file()]
    
    def get_file_info(self, filename: str, directory: str = "raw") -> Optional[Dict[str, Any]]:
        """
        Get information about a file
        
        Args:
            filename: Name of file
            directory: 'raw', 'analyzed', or 'reports'
            
        Returns:
            Dictionary with file info or None
        """
        dir_map = {
            "raw": self.raw_dir,
            "analyzed": self.analyzed_dir,
            "reports": self.reports_dir
        }
        
        target_dir = dir_map.get(directory, self.raw_dir)
        filepath = target_dir / filename
        
        if not filepath.exists():
            return None
        
        stat = filepath.stat()
        return {
            "filename": filename,
            "path": str(filepath),
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
    
    def generate_filename(self, prefix: str, sources: List[str], time_filter: str) -> str:
        """
        Generate a standardized filename
        
        Args:
            prefix: Prefix for the filename
            sources: List of sources (subreddits, channels, etc.)
            time_filter: Time filter used
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if len(sources) <= 3:
            source_str = "_".join(sources[:3])
        else:
            source_str = f"{'_'.join(sources[:3])}_and_{len(sources)-3}_more"
        
        return f"{prefix}_{source_str}_{time_filter}_{timestamp}"

