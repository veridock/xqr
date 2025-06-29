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
    # Define SVG namespace
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    # If the xpath already uses local-name(), use it as-is
    if 'local-name()' in xpath:
        return xpath, namespaces
    
    # If the xpath already has namespace prefixes, use them as-is
    if ':' in xpath and not xpath.lstrip().startswith(('//', '/', './/', './', '(', '@')):
        return xpath, namespaces
    
    # Special case: empty xpath
    if not xpath:
        return '//*', namespaces
    
    # Handle direct attribute access (e.g., @id)
    if xpath.startswith('@'):
        attr_name = xpath[1:]
        return f'@*[local-name()="{attr_name}"]', namespaces
    
    # Handle simple element names (e.g., 'svg')
    if not any(c in xpath for c in '[]/()@'):
        return f'//*[local-name()="{xpath}"]', namespaces
    
    # For more complex XPath expressions, we'll build it part by part
    parts = []
    for part in xpath.split('/'):
        if not part or part == '.':
            parts.append(part)
            continue
        
        # Handle attributes
        if part.startswith('@'):
            attr_name = part[1:]
            parts.append(f'@*[local-name()="{attr_name}"]')
            continue
        
        # Handle text nodes
        if part == 'text()':
            parts.append('text()')
            continue
        
        # Handle parent and self references
        if part in ('.', '..'):
            parts.append(part)
            continue
        
        # Handle predicates (e.g., [@id='value'] or [1])
        if '[' in part and ']' in part:
            elem_part, pred = part.split('[', 1)
            pred = '[' + pred
            
            # Handle element name if it exists
            if elem_part:
                elem_part = f'*[local-name()="{elem_part}"]'
            
            # Special handling for simple attribute predicates
            if '@' in pred and '=' in pred and ']' in pred:
                try:
                    # Extract the attribute name and value
                    attr_part = pred.split('@', 1)[1].split(']', 1)[0]
                    if '=' in attr_part:
                        attr_name, attr_value = attr_part.split('=', 1)
                        # Clean up quotes if present
                        attr_name = attr_name.strip()
                        attr_value = attr_value.strip().strip("\"'")
                        # Rebuild the predicate with proper namespace handling
                        pred = f"[@*[local-name()='{attr_name}']='{attr_value}']"
                except (IndexError, ValueError):
                    # If parsing fails, fall back to the original predicate
                    pass
            
            parts.append(f"{elem_part}{pred}" if elem_part else pred)
            continue
        
        # Handle simple element names
        parts.append(f'*[local-name()="{part}"]')
    
    # Join parts and ensure it starts with // if not already a path
    result = '/'.join(parts)
    if not any(result.startswith(p) for p in ('//', './/', '/', './', '(', '@')):
        result = f'//{result}'
    
    return result, namespaces


def find_elements_by_xpath(tree: Any, xpath: str, file_type: str = 'xml') -> List[Any]:
    """Find elements using XPath with namespace support.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find elements
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        List of matching elements
        
    Raises:
        ValueError: If the XPath expression is invalid or empty
    """
    if not xpath or not xpath.strip():
        raise ValueError("XPath expression cannot be empty")
        
    # Basic XPath syntax validation - check for common syntax errors
    stack = []
    in_quotes = False
    quote_char = None
    
    for i, char in enumerate(xpath):
        if char in ("'", '"') and (i == 0 or xpath[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        elif not in_quotes:
            if char in ('[', '(', '{'):
                stack.append(char)
            elif char in (']', ')', '}'):
                if not stack:
                    raise ValueError(f"Unmatched '{char}' at position {i} in XPath expression")
                last = stack.pop()
                if (char == ']' and last != '[') or \
                   (char == ')' and last != '(') or \
                   (char == '}' and last != '{'):
                    raise ValueError(f"Mismatched '{last}' and '{char}' in XPath expression")
    
    if in_quotes:
        raise ValueError("Unclosed string literal in XPath expression")
    if stack:
        raise ValueError(f"Unmatched '{stack[-1]}' in XPath expression")
    
    # Check for common XPath syntax errors
    if '//' in xpath and '//.' in xpath:
        raise ValueError("Invalid XPath expression: '//.' is not a valid XPath step")
    if ']]' in xpath and ']]>' not in xpath:  # Allow ]]> as it's valid in XPath 2.0+
        raise ValueError("Invalid XPath expression: ']]' is not valid outside of CDATA")
    
    try:
        # Handle SVG namespace
        if file_type == 'svg':
            xpath, namespaces = prepare_xpath_for_svg(xpath)
        else:
            namespaces = {}
            
        # Test the XPath expression with a simple evaluation first
        # This helps catch syntax errors that our validation might miss
        test_result = tree.xpath('count(//*)')  # Simple XPath that should work on any XML/HTML
        if test_result is None:
            raise ValueError("Failed to evaluate simple XPath expression")
            
        # Now try the actual XPath
        result = tree.xpath(xpath, namespaces=namespaces)
        return result
        
    except Exception as e:
        # Try to provide a more specific error message for common issues
        error_msg = str(e).lower()
        if 'xpath' in error_msg and ('invalid' in error_msg or 'syntax' in error_msg):
            raise ValueError(f"Invalid XPath expression: {xpath}") from e
        raise ValueError(f"Error evaluating XPath expression '{xpath}': {e}")


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
