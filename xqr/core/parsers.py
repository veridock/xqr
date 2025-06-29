"""
Parsing utilities for the XQR package.

This module provides functionality for parsing XML/HTML/SVG files and detecting file types.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, Optional, Any, Union

try:
    from lxml import etree, html
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def detect_file_type(file_path: Union[str, Path], content: str) -> str:
    """Detect the type of file based on its extension and content.
    
    Args:
        file_path: Path to the file
        content: File content as string
        
    Returns:
        str: File type ('svg', 'html', or 'xml')
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    content_lower = content.lower()

    if extension == '.svg' or '<svg' in content_lower:
        return 'svg'
    if extension in ['.html', '.htm'] or '!doctype html' in content_lower or '<html' in content_lower:
        return 'html'
    if extension == '.xml' or '<?xml' in content_lower:
        return 'xml'
    return 'xml'  # Default to XML


def parse_with_lxml(content: str, file_type: str) -> Tuple[Any, Any]:
    """Parse content using lxml library.
    
    Args:
        content: File content as string
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        Tuple of (tree, root) elements
        
    Raises:
        ValueError: If parsing fails
    """
    if not LXML_AVAILABLE:
        raise ImportError("lxml is required for this operation")
        
    try:
        if file_type == 'html':
            tree = html.fromstring(content)
        else:
            tree = etree.fromstring(content.encode('utf-8'))
        return tree, tree
    except Exception as e:
        raise ValueError(f"Failed to parse with lxml: {e}")


def parse_with_elementtree(content: str) -> Tuple[Any, Any]:
    """Parse content using standard library's ElementTree.
    
    Args:
        content: File content as string
        
    Returns:
        Tuple of (tree, root) elements
        
    Raises:
        ValueError: If parsing fails
    """
    try:
        tree = ET.fromstring(content)
        return tree, tree
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse with ElementTree: {e}")


def parse_file(file_path: Union[str, Path]) -> Tuple[Any, Any, str, str]:
    """Parse a file and return its contents as a parse tree.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        Tuple of (tree, root, file_type, original_content)
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file cannot be parsed
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    file_type = detect_file_type(file_path, original_content)
    
    # Try lxml first if available
    if LXML_AVAILABLE:
        try:
            tree, root = parse_with_lxml(original_content, file_type)
            return tree, root, file_type, original_content
        except Exception as e:
            print(f"lxml parsing failed: {e}, trying ElementTree...")
    
    # Fall back to ElementTree
    try:
        tree, root = parse_with_elementtree(original_content)
        return tree, root, file_type, original_content
    except Exception as e:
        raise ValueError(f"Failed to parse file {file_path}: {e}")
