"""
SVG with Embedded PDF and Metadata Extraction Example

This script demonstrates how to:
1. Create an SVG with an embedded PDF
2. Extract text from the PDF using Tesseract OCR
3. Add the extracted text and metadata to the SVG
4. Save the enhanced SVG with all metadata
"""

import os
import sys
import base64
import hashlib
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
from urllib.parse import quote

# Try to import lxml for better XML handling
try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    LXML_AVAILABLE = False

# Constants
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
TEXT_AREA_HEIGHT = 300
MARGIN = 20

class PDFProcessor:
    """Handles PDF processing and text extraction"""
    
    @staticmethod
    def pdf_to_base64(pdf_path: str) -> str:
        """Convert PDF file to base64 encoded string"""
        with open(pdf_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    @staticmethod
    def extract_text_with_tesseract(pdf_path: str) -> Dict[str, str]:
        """
        Extract text from PDF using Tesseract OCR
        
        Returns:
            dict: Dictionary with 'text' and 'metadata' keys
        """
        result = {
            'text': '',
            'metadata': {}
        }
        
        try:
            # Create a temporary directory for output
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert PDF to images (one per page)
                images = []
                for i in range(10):  # Process up to 10 pages
                    output_img = os.path.join(temp_dir, f'page_{i:03d}.tiff')
                    cmd = [
                        'pdftoppm',
                        '-f', str(i+1),
                        '-l', str(i+1),
                        '-tiff',
                        '-r', '300',  # 300 DPI for better OCR
                        pdf_path,
                        os.path.join(temp_dir, 'page')
                    ]
                    
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        if os.path.exists(f"{os.path.join(temp_dir, 'page')}-{i+1:03d}.tiff"):
                            images.append(f"{os.path.join(temp_dir, 'page')}-{i+1:03d}.tiff")
                        else:
                            break  # No more pages
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        break  # No more pages or error
                
                # Process each image with Tesseract
                all_text = []
                for img_path in images:
                    # Extract text
                    cmd = ['tesseract', img_path, 'stdout', '-l', 'eng', '--psm', '6']
                    text = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
                    if text:
                        all_text.append(text)
                    
                    # Clean up
                    try:
                        os.remove(img_path)
                    except:
                        pass
                
                # Extract basic metadata
                pdf_info = {}
                try:
                    cmd = ['pdfinfo', pdf_path]
                    info_output = subprocess.run(cmd, capture_output=True, text=True).stdout
                    for line in info_output.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            pdf_info[key.strip()] = value.strip()
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                result['text'] = '\n\n--- Page Break ---\n\n'.join(all_text)
                result['metadata'] = pdf_info
                
        except Exception as e:
            print(f"Error in text extraction: {e}", file=sys.stderr)
        
        return result


class SVGGenerator:
    """Handles SVG generation and manipulation"""
    
    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        self.width = width
        self.height = height
        self.elements = []
        self.metadata = {}
        
        # Initialize with SVG root
        if LXML_AVAILABLE:
            self.root = etree.Element('svg', {
                'xmlns': 'http://www.w3.org/2000/svg',
                'width': str(width),
                'height': str(height),
                'viewBox': f'0 0 {width} {height}'
            })
        else:
            self.root = ET.Element('svg', {
                'xmlns': 'http://www.w3.org/2000/svg',
                'width': str(width),
                'height': str(height),
                'viewBox': f'0 0 {width} {height}'
            })
    
    def add_embedded_pdf(self, pdf_data: str, x: int, y: int, width: int, height: int) -> None:
        """Add an embedded PDF to the SVG"""
        # Create a container group
        container = self._create_element('g', {
            'id': 'embedded-pdf',
            'transform': f'translate({x}, {y})'
        })
        
        # Add a background rectangle
        bg = self._create_element('rect', {
            'width': str(width),
            'height': str(height),
            'fill': '#f5f5f5',
            'stroke': '#cccccc',
            'stroke-width': '1'
        })
        container.append(bg)
        
        # Add PDF icon
        icon = self._create_element('text', {
            'x': str(width // 2),
            'y': str(height // 2),
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            'font-family': 'Arial',
            'font-size': '24',
            'fill': '#666666'
        })
        icon.text = '📄 PDF'
        container.append(icon)
        
        # Add PDF as an embedded object
        pdf_obj = self._create_element('foreignObject', {
            'x': '0',
            'y': '0',
            'width': str(width),
            'height': str(height)
        })
        
        # Create object element with embedded PDF
        obj = self._create_element('object', {
            'data': f'data:application/pdf;base64,{pdf_data}',
            'type': 'application/pdf',
            'width': '100%',
            'height': '100%'
        })
        
        # Add fallback text
        fallback = self._create_element('p', {})
        fallback.text = 'Your browser does not support embedded PDFs. '
        link = self._create_element('a', {
            'href': f'data:application/pdf;base64,{pdf_data}',
            'download': 'document.pdf'
        })
        link.text = 'Download PDF'
        fallback.append(link)
        
        obj.append(fallback)
        pdf_obj.append(obj)
        container.append(pdf_obj)
        
        self.root.append(container)
    
    def add_extracted_text(self, text: str, x: int, y: int, width: int, max_height: int) -> None:
        """Add extracted text to the SVG with word wrapping"""
        if not text.strip():
            return
            
        # Create a container for the text
        container = self._create_element('g', {
            'id': 'extracted-text',
            'transform': f'translate({x}, {y})',
            'font-family': 'monospace',
            'font-size': '12',
            'fill': 'black'
        })
        
        # Add a title
        title = self._create_element('text', {
            'x': '0',
            'y': '0',
            'font-weight': 'bold',
            'font-size': '14'
        })
        title.text = 'Extracted Text:'
        container.append(title)
        
        # Add the extracted text with word wrapping
        lines = self._wrap_text(text, width, max_height - 30)  # Leave space for title
        
        for i, line in enumerate(lines):
            t = self._create_element('tspan', {
                'x': '0',
                'dy': '1.2em',
                'dominant-baseline': 'hanging'
            })
            t.text = line
            container.append(t)
        
        self.root.append(container)
    
    def add_metadata_section(self, metadata: dict, x: int, y: int, width: int) -> None:
        """Add a metadata section to the SVG"""
        if not metadata:
            return
            
        # Create a container for metadata
        container = self._create_element('g', {
            'id': 'metadata',
            'transform': f'translate({x}, {y})',
            'font-family': 'sans-serif',
            'font-size': '12'
        })
        
        # Add a title
        title = self._create_element('text', {
            'x': '0',
            'y': '0',
            'font-weight': 'bold',
            'font-size': '14'
        })
        title.text = 'Document Metadata:'
        container.append(title)
        
        # Add metadata items
        y_offset = 25
        for key, value in metadata.items():
            if not value:
                continue
                
            # Add key
            key_elem = self._create_element('tspan', {
                'x': '0',
                'y': str(y_offset),
                'font-weight': 'bold'
            })
            key_elem.text = f'{key}:'
            container.append(key_elem)
            
            # Add value (with word wrapping)
            value_lines = self._wrap_text(str(value), width - 100, 1000)  # Large max height
            for i, line in enumerate(value_lines):
                val_elem = self._create_element('tspan', {
                    'x': '150',
                    'y': str(y_offset + (i * 15)),
                    'text-anchor': 'start'
                })
                val_elem.text = line
                container.append(val_elem)
            
            y_offset += max(20, len(value_lines) * 15)
        
        self.root.append(container)
    
    def add_processing_metadata(self, processing_info: dict) -> None:
        """Add processing metadata to the SVG's metadata section"""
        if LXML_AVAILABLE:
            # Find or create metadata element
            ns = {'svg': 'http://www.w3.org/2000/svg'}
            metadata = self.root.find('svg:metadata', namespaces=ns)
            if metadata is None:
                metadata = etree.SubElement(self.root, 'metadata')
            
            # Add processing info
            for key, value in processing_info.items():
                meta = etree.SubElement(metadata, 'meta')
                meta.set('name', key)
                meta.set('content', str(value))
    
    def save(self, output_path: str) -> None:
        """Save the SVG to a file"""
        # Add XML declaration and DOCTYPE
        xml_declaration = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        
        # Serialize the SVG
        if LXML_AVAILABLE:
            # Pretty print with lxml
            xml_str = etree.tostring(
                self.root,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8',
                standalone=True
            ).decode('utf-8')
        else:
            # Fallback to ElementTree with minidom for pretty printing
            rough_string = ET.tostring(self.root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            xml_str = reparsed.toprettyxml(indent="  ")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def _create_element(self, tag: str, attrs: dict):
        """Create an XML/SVG element with the given tag and attributes"""
        if LXML_AVAILABLE:
            elem = etree.Element(tag, **{k: str(v) for k, v in attrs.items()})
        else:
            elem = ET.Element(tag, **{k: str(v) for k, v in attrs.items()})
        return elem
    
    @staticmethod
    def _wrap_text(text: str, max_width: int, max_height: int) -> list:
        """
        Simple text wrapping algorithm that respects words
        
        Args:
            text: The text to wrap
            max_width: Maximum width in characters
            max_height: Maximum height in lines
            
        Returns:
            List of wrapped lines
        """
        if not text:
            return []
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # If adding this word would exceed the width, start a new line
            if current_line and (current_length + len(word) + 1) > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
                
                # Check if we've reached max height
                if len(lines) >= max_height:
                    lines[-1] = lines[-1][:max_width-3] + '...'
                    return lines
            else:
                if current_line:
                    current_length += 1  # for the space
                current_line.append(word)
                current_length += len(word)
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


def process_pdf_to_svg(pdf_path: str, output_svg: str) -> None:
    """
    Process a PDF file and create an SVG with embedded PDF and extracted text
    
    Args:
        pdf_path: Path to the input PDF file
        output_svg: Path to save the output SVG
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Initialize processor and generator
    pdf_processor = PDFProcessor()
    svg_gen = SVGGenerator(
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT + TEXT_AREA_HEIGHT + 200  # Extra space for metadata
    )
    
    # Step 1: Convert PDF to base64
    print(f"Processing PDF: {pdf_path}")
    pdf_base64 = pdf_processor.pdf_to_base64(pdf_path)
    
    # Step 2: Extract text and metadata using Tesseract
    print("Extracting text and metadata...")
    extraction_result = pdf_processor.extract_text_with_tesseract(pdf_path)
    
    # Step 3: Add embedded PDF to SVG
    print("Adding embedded PDF to SVG...")
    svg_gen.add_embedded_pdf(
        pdf_base64,
        x=MARGIN,
        y=MARGIN,
        width=DEFAULT_WIDTH - (2 * MARGIN),
        height=DEFAULT_HEIGHT - (2 * MARGIN) - TEXT_AREA_HEIGHT - 50
    )
    
    # Step 4: Add extracted text
    print("Adding extracted text...")
    text_y = DEFAULT_HEIGHT - TEXT_AREA_HEIGHT - 20
    svg_gen.add_extracted_text(
        extraction_result.get('text', ''),
        x=MARGIN,
        y=text_y,
        width=DEFAULT_WIDTH - (2 * MARGIN),
        max_height=TEXT_AREA_HEIGHT
    )
    
    # Step 5: Add metadata
    print("Adding metadata...")
    metadata = extraction_result.get('metadata', {})
    metadata['Processing Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata['Source File'] = os.path.basename(pdf_path)
    
    svg_gen.add_metadata_section(
        metadata,
        x=MARGIN,
        y=DEFAULT_HEIGHT + 20,
        width=DEFAULT_WIDTH - (2 * MARGIN)
    )
    
    # Add processing metadata to SVG's metadata section
    processing_info = {
        'processor': 'xqr-pdf-processor',
        'version': '1.0',
        'extraction_tool': 'Tesseract OCR',
        'extraction_date': datetime.now().isoformat(),
        'source_checksum': hashlib.md5(open(pdf_path, 'rb').read()).hexdigest()
    }
    svg_gen.add_processing_metadata(processing_info)
    
    # Save the SVG
    print(f"Saving SVG to: {output_svg}")
    svg_gen.save(output_svg)
    print("Done!")


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert PDF to SVG with embedded content and extracted text.'
    )
    parser.add_argument(
        'input_pdf',
        help='Path to the input PDF file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to save the output SVG (default: input filename with .svg extension)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(args.input_pdf))[0]
        args.output = f"{base_name}_with_metadata.svg"
    
    try:
        process_pdf_to_svg(args.input_pdf, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
