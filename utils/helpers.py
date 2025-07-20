"""
Helper utility functions for the Research Agent.
"""

import re
import html
from urllib.parse import urlparse
from typing import Optional, List
from bs4 import BeautifulSoup

def format_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Format and clean text content.
    
    Args:
        text: Text to format
        max_length: Optional maximum length to truncate
        
    Returns:
        Formatted text
    """
    
    if not text:
        return ""
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length - 3] + '...'
    
    return text

def clean_html(html_content: str) -> str:
    """
    Clean HTML content and extract plain text.
    
    Args:
        html_content: HTML content to clean
        
    Returns:
        Plain text content
    """
    
    if not html_content:
        return ""
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script.decompose()
    
    # Get text content
    text = soup.get_text()
    
    # Clean up text
    text = format_text(text)
    
    return text

def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return "unknown"

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'his', 'her', 'its', 'their', 'our', 'your', 'are', 'was',
        'were', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'said', 'say', 'says', 'get', 'got',
        'make', 'made', 'take', 'took', 'come', 'came', 'go', 'went', 'see',
        'saw', 'know', 'knew', 'think', 'thought', 'look', 'looked', 'use',
        'used', 'find', 'found', 'give', 'gave', 'tell', 'told', 'ask', 'asked',
        'work', 'worked', 'seem', 'seemed', 'feel', 'felt', 'try', 'tried',
        'leave', 'left', 'call', 'called'
    }
    
    # Filter out stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_words[:max_keywords]]

def truncate_content(content: str, max_chars: int = 5000) -> str:
    """
    Truncate content to a maximum number of characters.
    
    Args:
        content: Content to truncate
        max_chars: Maximum number of characters
        
    Returns:
        Truncated content
    """
    
    if not content or len(content) <= max_chars:
        return content
    
    # Try to truncate at sentence boundary
    truncated = content[:max_chars]
    last_sentence = truncated.rfind('.')
    
    if last_sentence > max_chars * 0.8:  # If we can keep at least 80% of content
        return truncated[:last_sentence + 1]
    else:
        return truncated + '...'

def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove excessive dots and spaces
    filename = re.sub(r'\.{2,}', '.', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip('._')

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time for text in minutes.
    
    Args:
        text: Text to estimate reading time for
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    
    return reading_time