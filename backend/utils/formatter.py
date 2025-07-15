"""
Utility functions for formatting text and responses
"""

import json
import re
from typing import Dict, Any, List
from datetime import datetime

def format_datetime(dt) -> str:
    """Format datetime for JSON serialization"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return str(dt)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    return text

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_response_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format metadata for API responses"""
    formatted = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            formatted[key] = format_datetime(value)
        elif isinstance(value, (dict, list)):
            formatted[key] = json.dumps(value) if value else None
        else:
            formatted[key] = str(value) if value is not None else None
    
    return formatted 