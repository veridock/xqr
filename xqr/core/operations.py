"""
Core operations for the XQR package.

This module provides the core functionality for manipulating XML/HTML/SVG documents,
including getting, setting, adding, and removing elements.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .xpath_utils import find_elements_by_xpath


def get_element_text(tree: Any, xpath: str, file_type: str = 'xml') -> str:
    """Get the text content of the first element matching the XPath.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find the element
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        Text content of the element, or empty string if not found
    """
    elements = find_elements_by_xpath(tree, xpath, file_type)
    if elements:
        element = elements[0]
        if hasattr(element, 'text'):
            return element.text or ""
        return str(element)
    return ""


def get_element_attribute(tree: Any, xpath: str, attr_name: str, file_type: str = 'xml') -> str:
    """Get an attribute value from the first element matching the XPath.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find the element
        attr_name: Name of the attribute to get
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        Attribute value, or empty string if not found
    """
    elements = find_elements_by_xpath(tree, xpath, file_type)
    if elements:
        element = elements[0]
        if hasattr(element, 'get'):
            return element.get(attr_name, "")
        elif hasattr(element, 'attrib'):
            return element.attrib.get(attr_name, "")
    return ""


def set_element_text(tree: Any, xpath: str, new_text: str, file_type: str = 'xml') -> bool:
    """Set the text content of the first element matching the XPath.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find the element
        new_text: New text content to set
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        True if the element was found and updated, False otherwise
    """
    elements = find_elements_by_xpath(tree, xpath, file_type)
    if elements and hasattr(elements[0], 'text'):
        elements[0].text = new_text
        return True
    return False


def set_element_attribute(
    tree: Any, 
    xpath: str, 
    attr_name: str, 
    attr_value: str, 
    file_type: str = 'xml'
) -> bool:
    """Set an attribute value on the first element matching the XPath.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find the element
        attr_name: Name of the attribute to set
        attr_value: New value for the attribute
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        True if the element was found and updated, False otherwise
    """
    elements = find_elements_by_xpath(tree, xpath, file_type)
    if not elements:
        return False
        
    element = elements[0]
    if hasattr(element, 'set'):
        element.set(attr_name, attr_value)
    elif hasattr(element, 'attrib'):
        element.attrib[attr_name] = attr_value
    return True


def add_element(
    tree: Any, 
    parent_xpath: str, 
    tag_name: str, 
    text: str = "", 
    attributes: Optional[Dict[str, str]] = None,
    file_type: str = 'xml'
) -> bool:
    """Add a new element as a child of the first element matching the parent XPath.
    
    Args:
        tree: The root element of the parsed document
        parent_xpath: XPath expression to find the parent element
        tag_name: Tag name of the new element
        text: Text content for the new element
        attributes: Dictionary of attributes to set on the new element
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        True if the parent was found and the element was added, False otherwise
    """
    parents = find_elements_by_xpath(tree, parent_xpath, file_type)
    if not parents:
        return False
        
    parent = parents[0]
    try:
        # Try lxml.etree first
        from lxml import etree
        new_element = etree.SubElement(parent, tag_name)
    except (ImportError, AttributeError):
        # Fall back to ElementTree
        from xml.etree import ElementTree as ET
        new_element = ET.SubElement(parent, tag_name)
    
    if text:
        new_element.text = text
    
    if attributes:
        for key, value in attributes.items():
            new_element.set(key, value)
    
    return True


def remove_element(tree: Any, xpath: str, file_type: str = 'xml') -> bool:
    """Remove the first element matching the XPath.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find the element to remove
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        True if the element was found and removed, False otherwise
    """
    elements = find_elements_by_xpath(tree, xpath, file_type)
    if not elements:
        return False
        
    element = elements[0]
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)
        return True
    return False


def list_elements(tree: Any, xpath: str = "//*", file_type: str = 'xml') -> List[Dict]:
    """List elements matching the XPath with their properties.
    
    Args:
        tree: The root element of the parsed document
        xpath: XPath expression to find elements
        file_type: Type of the file ('svg', 'html', or 'xml')
        
    Returns:
        List of dictionaries with element properties
    """
    elements = find_elements_by_xpath(tree, xpath, file_type)
    result = []

    for i, element in enumerate(elements):
        try:
            # Try to get the element path (lxml only)
            element_path = tree.getpath(element) if hasattr(tree, 'getpath') else f"element[{i}]"
        except Exception:
            element_path = f"element[{i}]"
            
        element_info = {
            'path': element_path,
            'tag': getattr(element, 'tag', str(type(element))),
            'text': (getattr(element, 'text', '') or "").strip(),
            'attributes': dict(getattr(element, 'attrib', {}))
        }
        result.append(element_info)

    return result
