"""
Example file generation for the XQR package.

This module provides functionality to generate example files for demonstration
and testing purposes.
"""

from pathlib import Path
from typing import Optional


def create_example_files(directory: Optional[str] = None) -> None:
    """Create example files for demonstration purposes.

    Creates three example files: example.svg, example.xml, and example.html
    with sample content for testing the editor.

    Args:
        directory: Optional directory path where to create the example files.
                  If not provided, files will be created in the current working directory.
    """
    # Determine the target directory
    target_dir = Path(directory) if directory else Path.cwd()
    target_dir.mkdir(parents=True, exist_ok=True)
    
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
    files = {
        "example.svg": svg_content,
        "example.xml": xml_content,
        "example.html": html_content
    }
    
    for filename, content in files.items():
        filepath = target_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created example file: {filepath}")


if __name__ == "__main__":
    create_example_files()
