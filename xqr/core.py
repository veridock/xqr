"""
Core FileEditor class for parsing and manipulating XML/HTML/SVG files
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

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


def create_example_files() -> None:
    """Create example files for demonstration purposes.

    Creates three example files: example.svg, example.xml, and example.html
    with sample content for testing the editor.
    """
    # Example SVG file
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="100" fill="#f0f0f0"/>
  <text x="100" y="50" font-family="Arial" font-size="16"
        text-anchor="middle" id="text1">Hello SVG</text>
  <text x="100" y="80" font-family="Arial" font-size="12"
        text-anchor="middle" id="text2">Edit me!</text>
</svg>"""
    
    # Example XML file
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
  <greeting>Hello World</greeting>
  <items>
    <item id="1">First item</item>
    <item id="2">Second item</item>
  </items>
</root>"""
    
    # Example HTML file
    html_content = """<!DOCTYPE html>
<html>
<head>
  <title>Example</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .highlight { color: blue; }
  </style>
</head>
<body>
  <h1>Example HTML</h1>
  <p class="highlight">This is a sample HTML file.</p>
  <ul id="items">
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</body>
</html>"""
    
    # Write files
    with open("example.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    with open("example.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
    with open("example.html", "w", encoding="utf-8") as f:
        f.write(html_content)



class FileEditor:
    """Main class for editing XML/HTML/SVG files"""

    def __init__(self, file_path: str) -> None:
        """Initialize FileEditor with a file path
        
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
        """Load file and determine its type
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.original_content = f.read()

        # Określ typ pliku
        extension = self.file_path.suffix.lower()
        content_lower = self.original_content.lower()

        if extension == '.svg' or '<svg' in content_lower:
            self.file_type = 'svg'
        elif extension in ['.html', '.htm'] or '<!doctype html' in content_lower or '<html' in content_lower:
            self.file_type = 'html'
        elif extension == '.xml' or '<?xml' in content_lower:
            self.file_type = 'xml'
        else:
            self.file_type = 'xml'  # domyślnie XML

        # Parsuj plik
        if LXML_AVAILABLE:
            try:
                if self.file_type == 'html':
                    self.tree = html.fromstring(self.original_content)
                else:
                    self.tree = etree.fromstring(self.original_content.encode('utf-8'))
                self.root = self.tree
            except Exception as e:
                print(f"lxml parsing failed: {e}, trying ElementTree...")
                self._fallback_parse()
        else:
            self._fallback_parse()

    def _fallback_parse(self) -> None:
        """Fallback parsing using ElementTree
        
        Raises:
            ValueError: If the file cannot be parsed
        """
        try:
            self.tree = ET.fromstring(self.original_content)
            self.root = self.tree
        except ET.ParseError as e:
            raise ValueError(f"Cannot parse file: {e}")

    def _prepare_xpath_for_svg(self, xpath: str) -> tuple[str, dict]:
        """Prepare XPath expression and namespaces for SVG files
        
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

    def find_by_xpath(self, xpath: str) -> List:
        """Find elements using XPath with namespace support
        
        Args:
            xpath: XPath expression to find elements
            
        Returns:
            List of matching elements
            
        Raises:
            NotImplementedError: If lxml is not available
            ValueError: If the XPath expression is invalid
        """
        if not LXML_AVAILABLE:
            raise NotImplementedError("XPath requires lxml library")

        try:
            if not isinstance(self.tree, etree._Element):
                return []
                
            # Handle SVG namespace
            if self.file_type == 'svg':
                xpath, namespaces = self._prepare_xpath_for_svg(xpath)
            else:
                namespaces = {}
                
            return self.tree.xpath(xpath, namespaces=namespaces)
            
        except Exception as e:
            raise ValueError(f"Invalid XPath expression '{xpath}': {e}")

    def find_by_css(self, css_selector: str) -> List:
        """Find elements using CSS selectors (HTML only)
        
        Args:
            css_selector: CSS selector to find elements
            
        Returns:
            List of matching elements
            
        Raises:
            NotImplementedError: If beautifulsoup4 is not available
            ValueError: If the file is not HTML
        """
        if not BS4_AVAILABLE:
            raise NotImplementedError("CSS selectors require beautifulsoup4 library")

        if self.file_type != 'html':
            raise ValueError("CSS selectors work only with HTML files")

        soup = BeautifulSoup(self.original_content, 'html.parser')
        return soup.select(css_selector)

    def get_element_text(self, xpath: str) -> str:
        """Pobierz tekst elementu"""
        elements = self.find_by_xpath(xpath)
        if elements:
            element = elements[0]
            if hasattr(element, 'text'):
                return element.text or ""
            return str(element)
        return ""

    def get_element_attribute(self, xpath: str, attr_name: str) -> str:
        """Pobierz atrybut elementu"""
        elements = self.find_by_xpath(xpath)
        if elements:
            element = elements[0]
            if hasattr(element, 'get'):
                return element.get(attr_name, "")
            elif hasattr(element, 'attrib'):
                return element.attrib.get(attr_name, "")
        return ""

    def set_element_text(self, xpath: str, new_text: str) -> bool:
        """Ustaw tekst elementu"""
        elements = self.find_by_xpath(xpath)
        if elements:
            element = elements[0]
            if hasattr(element, 'text'):
                element.text = new_text
            return True
        return False

    def set_element_attribute(self, xpath: str, attr_name: str, attr_value: str) -> bool:
        """Ustaw atrybut elementu"""
        elements = self.find_by_xpath(xpath)
        if elements:
            element = elements[0]
            if hasattr(element, 'set'):
                element.set(attr_name, attr_value)
            elif hasattr(element, 'attrib'):
                element.attrib[attr_name] = attr_value
            return True
        return False

    def add_element(self, parent_xpath: str, tag_name: str, text: str = "", attributes: Dict[str, str] = None) -> bool:
        """Dodaj nowy element"""
        parents = self.find_by_xpath(parent_xpath)
        if parents:
            parent = parents[0]
            if LXML_AVAILABLE:
                new_element = etree.SubElement(parent, tag_name)
                if text:
                    new_element.text = text
                if attributes:
                    for key, value in attributes.items():
                        new_element.set(key, value)
            return True
        return False

    def remove_element(self, xpath: str) -> bool:
        """Usuń element"""
        elements = self.find_by_xpath(xpath)
        if elements:
            element = elements[0]
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
                return True
        return False

    def list_elements(self, xpath: str = "//*") -> List[Dict]:
        """Wylistuj elementy z ich ścieżkami"""
        elements = self.find_by_xpath(xpath)
        result = []

        for i, element in enumerate(elements):
            if LXML_AVAILABLE:
                element_path = self.tree.getpath(element) if hasattr(self.tree, 'getpath') else f"element[{i}]"
                element_info = {
                    'path': element_path,
                    'tag': element.tag,
                    'text': (element.text or "").strip(),
                    'attributes': dict(element.attrib) if hasattr(element, 'attrib') else {}
                }
                result.append(element_info)

        return result

    def save(self, output_path: str = None) -> bool:
        """Zapisz zmiany do pliku"""
        save_path = output_path or str(self.file_path)

        try:
            if LXML_AVAILABLE:
                if self.file_type == 'html':
                    content = etree.tostring(self.tree, encoding='unicode', method='html', pretty_print=True)
                else:
                    content = etree.tostring(self.tree, encoding='unicode', pretty_print=True)
                    if not content.startswith('<?xml'):
                        content = '<?xml version="1.0" encoding="UTF-8"?>\n' + content
            else:
                content = ET.tostring(self.tree, encoding='unicode')

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def backup(self) -> str:
        """Utwórz kopię zapasową"""
        backup_path = f"{self.file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(self.original_content)
        return backup_path