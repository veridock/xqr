"""
Main FileEditor class for the XQR package.

This module provides the FileEditor class which serves as the main interface
for working with XML/HTML/SVG files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from . import parsers
from . import operations
from .xpath_utils import find_elements_by_xpath, find_elements_by_css


class FileEditor:
    """Main class for editing XML/HTML/SVG files.
    
    This class provides a high-level interface for parsing, querying, and
    modifying XML, HTML, and SVG files.
    """

    def __init__(self, file_path: Union[str, os.PathLike]) -> None:
        """Initialize FileEditor with a file path.
        
        Args:
            file_path: Path to the file to edit
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed
        """
        self.file_path = Path(file_path)
        self.tree = None
        self.root = None
        self.file_type = None
        self.original_content = None
        self._load_file()

    def _load_file(self) -> None:
        """Load and parse the file.
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed
        """
        self.tree, self.root, self.file_type, self.original_content = \
            parsers.parse_file(self.file_path)

    def reload(self) -> None:
        """Reload the file from disk, discarding any unsaved changes."""
        self._load_file()

    def find_by_xpath(self, xpath: str) -> List[Any]:
        """Find elements using XPath with namespace support.
        
        Args:
            xpath: XPath expression to find elements
            
        Returns:
            List of matching elements
            
        Raises:
            ValueError: If the XPath expression is invalid
        """
        return find_elements_by_xpath(self.tree, xpath, self.file_type)

    def find_by_css(self, css_selector: str) -> List[Any]:
        """Find elements using CSS selectors (HTML only).
        
        Args:
            css_selector: CSS selector to find elements
            
        Returns:
            List of matching elements
            
        Raises:
            ValueError: If the file is not HTML
            ImportError: If beautifulsoup4 is not available
        """
        if self.file_type != 'html':
            raise ValueError("CSS selectors work only with HTML files")
        return find_elements_by_css(self.tree, css_selector, self.original_content)

    def get_element_text(self, xpath: str) -> str:
        """Get the text content of the first element matching the XPath.
        
        Args:
            xpath: XPath expression to find the element
            
        Returns:
            Text content of the element, or empty string if not found
        """
        return operations.get_element_text(self.tree, xpath, self.file_type)

    def get_element_attribute(self, xpath: str, attr_name: str) -> str:
        """Get an attribute value from the first element matching the XPath.
        
        Args:
            xpath: XPath expression to find the element
            attr_name: Name of the attribute to get
            
        Returns:
            Attribute value, or empty string if not found
        """
        return operations.get_element_attribute(self.tree, xpath, attr_name, self.file_type)

    def set_element_text(self, xpath: str, new_text: str) -> bool:
        """Set the text content of the first element matching the XPath.
        
        Args:
            xpath: XPath expression to find the element
            new_text: New text content to set
            
        Returns:
            True if the element was found and updated, False otherwise
        """
        return operations.set_element_text(self.tree, xpath, new_text, self.file_type)

    def set_element_attribute(self, xpath: str, attr_name: str, attr_value: str) -> bool:
        """Set an attribute value on the first element matching the XPath.
        
        Args:
            xpath: XPath expression to find the element
            attr_name: Name of the attribute to set
            attr_value: New value for the attribute
            
        Returns:
            True if the element was found and updated, False otherwise
        """
        return operations.set_element_attribute(
            self.tree, xpath, attr_name, attr_value, self.file_type
        )

    def add_element(
        self,
        parent_xpath: str,
        tag_name: str,
        text: str = "",
        attributes: Optional[Dict[str, str]] = None
    ) -> bool:
        """Add a new element as a child of the first element matching the parent XPath.
        
        Args:
            parent_xpath: XPath expression to find the parent element
            tag_name: Tag name of the new element
            text: Text content for the new element
            attributes: Dictionary of attributes to set on the new element
            
        Returns:
            True if the parent was found and the element was added, False otherwise
        """
        return operations.add_element(
            self.tree, parent_xpath, tag_name, text, attributes, self.file_type
        )

    def remove_element(self, xpath: str) -> bool:
        """Remove the first element matching the XPath.
        
        Args:
            xpath: XPath expression to find the element to remove
            
        Returns:
            True if the element was found and removed, False otherwise
        """
        return operations.remove_element(self.tree, xpath, self.file_type)

    def list_elements(self, xpath: str = "//*") -> List[Dict]:
        """List elements matching the XPath with their properties.
        
        Args:
            xpath: XPath expression to find elements (default: all elements)
            
        Returns:
            List of dictionaries with element properties
        """
        return operations.list_elements(self.tree, xpath, self.file_type)

    def save(self, output_path: Optional[Union[str, os.PathLike]] = None) -> bool:
        """Save changes to a file.
        
        Args:
            output_path: Path to save the file to. If not provided, overwrites the original file.
            
        Returns:
            True if the file was saved successfully, False otherwise
            
        Raises:
            IOError: If there was an error writing the file
        """
        save_path = Path(output_path) if output_path else self.file_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Try lxml first if available
            try:
                from lxml import etree
                
                if self.file_type == 'html':
                    content = etree.tostring(
                        self.tree, 
                        encoding='unicode', 
                        method='html', 
                        pretty_print=True
                    )
                else:
                    content = etree.tostring(
                        self.tree, 
                        encoding='unicode', 
                        pretty_print=True
                    )
                    if not content.startswith('<?xml'):
                        content = '<?xml version="1.0" encoding="UTF-8"?>\n' + content
            except ImportError:
                # Fall back to ElementTree
                from xml.etree import ElementTree as ET
                
                # Ensure we have a string representation
                if hasattr(ET, 'tostring'):
                    content = ET.tostring(self.tree, encoding='unicode')
                else:  # Python 3.8+
                    content = ET.tostring(
                        self.tree, 
                        encoding='unicode',
                        short_empty_elements=False
                    )
                
                # Pretty print with xml.dom.minidom
                from xml.dom import minidom
                dom = minidom.parseString(content)
                content = dom.toprettyxml(indent="  ")
                
                # Remove extra newlines
                content = '\n'.join(
                    line for line in content.split('\n') 
                    if line.strip()
                )
            
            # Write to file
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update original content if saving to the same file
            if save_path.samefile(self.file_path):
                self.original_content = content
                
            return True
            
        except Exception as e:
            raise IOError(f"Error saving file {save_path}: {e}")

    def backup(self, suffix: str = ".bak") -> bool:
        """Create a backup of the original file.
        
        Args:
            suffix: Suffix to append to the backup filename
            
        Returns:
            True if the backup was created successfully, False otherwise
        """
        backup_path = self.file_path.with_suffix(self.file_path.suffix + suffix)
        try:
            import shutil
            shutil.copy2(self.file_path, backup_path)
            return True
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return False
