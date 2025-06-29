"""
XPath utilities for the XQR package.

This module provides functionality for working with XPath expressions,
especially for handling SVG namespaces and other XPath-related operations.
"""

from typing import Dict, Tuple, List, Any


def prepare_xpath_for_svg(xpath: str) -> Tuple[str, Dict[str, str]]:
    """Prepare XPath expression and namespaces for SVG files.
    
    Args:
        xpath: Original XPath expression
        
    Returns:
        Tuple of (modified_xpath, namespaces_dict)
    """
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    # If the xpath already has namespace prefixes, use them as-is
    if ':' in xpath and not xpath.lstrip().startswith(('//', '/', './/', './', '(', '@')):
        return xpath, namespaces
        
    # Otherwise, modify the xpath to include svg: prefix for elements
    parts = []
    for part in xpath.split('/'):
        if not part or part == '.':
            parts.append(part)
            continue
            
        # Handle attributes and special cases
        if part.startswith('@') or part in ('text()', '.', '..', 'node()'):
            parts.append(part)
            continue
            
        # Handle predicates
        if '[' in part:
            elem, pred = part.split('[', 1)
            pred = '[' + pred
            if not elem.startswith(('@', '.', 'svg:')) and not any(
                elem.startswith(f) for f in ('contains', 'starts-with', 'ends-with')
            ):
                elem = f'svg:{elem}'
            parts.append(f"{elem}{pred}")
            continue
            
        # Handle element names
        if not any(part.startswith(p) for p in ('@', '.', 'svg:')):
            part = f'svg:{part}'
            
        parts.append(part)
        
    return '/'.join(parts), namespaces


def find_elements_by_xpath(tree: Any, xpath: str, file_type: str = 'xml') -> List[Any]:
    """Find elements using XPath with namespace support.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find elements
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        List of matching elements
        
    Raises:
        ValueError: If the XPath expression is invalid
    """
    try:
        # Handle SVG namespace
        if file_type == 'svg':
            xpath, namespaces = prepare_xpath_for_svg(xpath)
        else:
            namespaces = {}
            
        return tree.xpath(xpath, namespaces=namespaces)
        
    except Exception as e:
        raise ValueError(f"Invalid XPath expression '{xpath}': {e}")


def find_elements_by_css(tree: Any, css_selector: str, content: str) -> List[Any]:
    """Find elements using CSS selectors (HTML only).
    
    Args:
        tree: The root element of the parsed document (unused, kept for API consistency)
        css_selector: CSS selector to find elements
        content: Original HTML content
        
    Returns:
        List of matching elements
        
    Raises:
        ImportError: If beautifulsoup4 is not available
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("CSS selectors require beautifulsoup4 library")
    
    soup = BeautifulSoup(content, 'html.parser')
    return soup.select(css_selector)
