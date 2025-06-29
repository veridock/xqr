#!/usr/bin/env python3
"""
Enhanced PDF to SVG Workflow with Advanced Features

This script demonstrates an enhanced workflow for:
1. Converting PDFs to SVGs with embedded PDF data
2. Extracting and displaying rich metadata
3. Handling password-protected PDFs
4. Extracting specific pages
5. Supporting multiple output formats
"""

import base64
import subprocess
import sys
import os
import re
import json
import tempfile
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from enum import Enum
from datetime import datetime

# XML/HTML escaping
from xml.sax.saxutils import escape as xml_escape

# For SVG generation
from lxml import etree as ET

# For PDF processing
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

class OutputFormat(Enum):
    """Supported output formats."""
    SVG = "svg"
    HTML = "html"
    JSON = "json"
    
    @classmethod
    def from_string(cls, value: str) -> 'OutputFormat':
        """Convert string to OutputFormat enum."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid output format: {value}. Must be one of: {', '.join(f.value for f in cls)}")

class PDFProcessor:
    """Handles PDF processing operations."""
    
    def __init__(self, pdf_path: str, password: str = None):
        """Initialize with PDF path and optional password."""
        self.pdf_path = os.path.abspath(pdf_path)
        self.password = password
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_svg_")
        self.metadata = {}
        
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata from PDF using multiple methods."""
        metadata = {}
        
        # Basic file info
        file_stat = os.stat(self.pdf_path)
        metadata['file_info'] = {
            'filename': os.path.basename(self.pdf_path),
            'file_size': f"{file_stat.st_size / 1024:.2f} KB",
            'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'sha256': self._calculate_file_hash()
        }
        
        # PDF-specific metadata using pdfinfo
        pdf_metadata = self._get_pdf_info()
        if pdf_metadata:
            metadata['pdf_info'] = pdf_metadata
        
        # Extract metadata using PyMuPDF if available
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(self.pdf_path)
                if self.password:
                    doc.authenticate(self.password)
                
                # Get document info
                doc_info = {}
                for key, value in doc.metadata.items():
                    if value:  # Skip empty values
                        doc_info[key.lower()] = value
                
                if doc_info:
                    metadata['document_info'] = doc_info
                
                # Get page count and dimensions
                if doc.page_count > 0:
                    page = doc[0]
                    metadata['page_info'] = {
                        'page_count': doc.page_count,
                        'dimensions': {
                            'width': page.rect.width,
                            'height': page.rect.height,
                            'unit': 'points',
                            'dpi': 72  # Default PDF DPI
                        }
                    }
                
                doc.close()
            except Exception as e:
                metadata['extraction_errors'] = {
                    'pymupdf': str(e)
                }
        
        # Add processing metadata
        metadata['processing'] = {
            'processed_at': datetime.now().isoformat(),
            'tool': 'Enhanced PDF to SVG Workflow',
            'version': '1.0.0',
            'python_version': sys.version.split()[0]
        }
        
        self.metadata = metadata
        return metadata
    
    def extract_text(self, pages: Optional[List[int]] = None, dpi: int = 300) -> Dict[int, str]:
        """Extract text from PDF pages using Tesseract OCR."""
        if not pages:
            # Default to all pages if none specified
            pages = list(range(1, self._get_page_count() + 1))
        
        extracted_text = {}
        
        for page_num in pages:
            try:
                # Convert PDF page to image
                img_path = os.path.join(self.temp_dir, f"page_{page_num:03d}.png")
                self._convert_pdf_page_to_image(page_num, img_path, dpi)
                
                # Extract text using Tesseract
                text = self._extract_text_with_tesseract(img_path)
                if text.strip():
                    extracted_text[page_num] = text
                    
            except Exception as e:
                print(f"Error processing page {page_num}: {e}", file=sys.stderr)
        
        return extracted_text
    
    def generate_svg(self, output_path: str, pages: Optional[List[int]] = None, 
                    include_text: bool = True, dpi: int = 300) -> str:
        """Generate an SVG with embedded PDF and extracted content."""
        if not pages:
            pages = list(range(1, self._get_page_count() + 1))
        
        # Create SVG root element
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': '100%',
            'height': '100%',
            'viewBox': '0 0 800 1100',
            'preserveAspectRatio': 'xMidYMid meet'
        })
        
        # Add metadata section
        self._add_metadata_section(svg)
        
        # Add PDF previews for each page
        y_offset = self._add_pdf_previews(svg, pages)
        
        # Add extracted text if requested
        if include_text:
            extracted_text = self.extract_text(pages, dpi)
            self._add_extracted_text(svg, extracted_text, y_offset + 50)
        
        # Save the SVG
        tree = ET.ElementTree(svg)
        tree.write(output_path, pretty_print=True, encoding='UTF-8', xml_declaration=True)
        return output_path
    
    def export_metadata(self, output_path: str, format: OutputFormat = OutputFormat.JSON) -> str:
        """Export metadata in the specified format."""
        if not self.metadata:
            self.extract_metadata()
        
        if format == OutputFormat.JSON:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        elif format == OutputFormat.HTML:
            self._export_metadata_html(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return output_path
    
    def _get_pdf_info(self) -> Dict[str, str]:
        """Get PDF info using pdfinfo command."""
        try:
            cmd = ['pdfinfo', self.pdf_path]
            if self.password:
                cmd.extend(['-upw', self.password])
                
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse pdfinfo output
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    if key and value:
                        info[key] = value
            return info
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Could not get PDF info: {e}", file=sys.stderr)
            return {}
    
    def _calculate_file_hash(self) -> str:
        """Calculate SHA-256 hash of the PDF file."""
        sha256_hash = hashlib.sha256()
        with open(self.pdf_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_page_count(self) -> int:
        """Get the number of pages in the PDF."""
        try:
            cmd = ['pdfinfo', self.pdf_path]
            if self.password:
                cmd.extend(['-upw', self.password])
                
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Extract page count
            for line in result.stdout.split('\n'):
                if 'Pages:' in line:
                    return int(line.split(':', 1)[1].strip())
                    
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Fallback to PyMuPDF if available
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(self.pdf_path)
                if self.password:
                    doc.authenticate(self.password)
                count = doc.page_count
                doc.close()
                return count
            except Exception:
                pass
                
        return 0  # Default if we can't determine
    
    def _convert_pdf_page_to_image(self, page_num: int, output_path: str, dpi: int = 300):
        """Convert a PDF page to an image."""
        try:
            # Try using pdftoppm first
            cmd = [
                'pdftoppm',
                '-f', str(page_num),
                '-l', str(page_num),
                '-r', str(dpi),
                '-png',
                '-singlefile',
                self.pdf_path,
                os.path.splitext(output_path)[0]  # Remove .png extension
            ]
            
            if self.password:
                cmd.extend(['-upw', self.password])
                
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Check if the file was created
            if not os.path.exists(output_path):
                # Try with .pbm extension (some pdftoppm versions use this)
                alt_path = os.path.splitext(output_path)[0] + '.pbm'
                if os.path.exists(alt_path):
                    os.rename(alt_path, output_path)
                    return
                
                raise FileNotFoundError(f"Output image not found: {output_path}")
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # Fallback to PyMuPDF if available
            if HAS_PYMUPDF:
                try:
                    doc = fitz.open(self.pdf_path)
                    if self.password:
                        doc.authenticate(self.password)
                    
                    page = doc[page_num - 1]  # 0-based index
                    pix = page.get_pixmap(dpi=dpi)
                    pix.save(output_path)
                    doc.close()
                    return
                except Exception as e2:
                    raise RuntimeError(f"Failed to convert page to image: {e2}") from e2
            
            raise RuntimeError(f"Failed to convert page to image: {e}")
    
    def _extract_text_with_tesseract(self, image_path: str) -> str:
        """Extract text from an image using Tesseract OCR."""
        try:
            result = subprocess.run(
                ['tesseract', image_path, 'stdout', '-l', 'eng'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Warning: Tesseract OCR failed: {e}", file=sys.stderr)
            return "[Text extraction failed]"
    
    def _add_metadata_section(self, svg: ET._Element) -> None:
        """Add metadata section to the SVG."""
        if not self.metadata:
            self.extract_metadata()
        
        # Create metadata group
        meta_group = ET.SubElement(svg, 'g', {
            'id': 'metadata',
            'transform': 'translate(20, 20)',
            'font-family': 'Arial, sans-serif',
            'font-size': '12'
        })
        
        # Add title
        title = ET.SubElement(meta_group, 'text', {
            'x': '0', 'y': '0',
            'font-size': '16',
            'font-weight': 'bold',
            'fill': '#2c3e50'
        })
        title.text = 'Document Metadata'
        
        # Add metadata items
        y_offset = 30
        
        # File info section
        y_offset = self._add_metadata_section_group(
            meta_group, 'File Information', self.metadata.get('file_info', {}), y_offset + 20
        )
        
        # PDF info section
        if 'pdf_info' in self.metadata:
            y_offset = self._add_metadata_section_group(
                meta_group, 'PDF Properties', self.metadata['pdf_info'], y_offset + 20
            )
        
        # Document info section
        if 'document_info' in self.metadata:
            y_offset = self._add_metadata_section_group(
                meta_group, 'Document Properties', self.metadata['document_info'], y_offset + 20
            )
        
        # Processing info section
        if 'processing' in self.metadata:
            y_offset = self._add_metadata_section_group(
                meta_group, 'Processing Information', self.metadata['processing'], y_offset + 20
            )
    
    def _add_metadata_section_group(self, parent: ET._Element, title: str, 
                                 data: Dict[str, Any], y_offset: int) -> int:
        """Add a group of metadata items to the SVG."""
        # Add section title
        ET.SubElement(parent, 'text', {
            'x': '0', 'y': str(y_offset),
            'font-size': '14',
            'font-weight': 'bold',
            'fill': '#3498db'
        }).text = title
        
        y_offset += 20
        
        # Add key-value pairs
        for key, value in data.items():
            if value is None:
                continue
                
            # Format key
            key_text = key.replace('_', ' ').title()
            ET.SubElement(parent, 'text', {
                'x': '20', 'y': str(y_offset),
                'font-weight': 'bold',
                'fill': '#2c3e50'
            }).text = f"{key_text}:"
            
            # Format value
            if isinstance(value, dict):
                # Handle nested dictionaries
                y_offset = self._add_metadata_section_group(parent, key_text, value, y_offset + 20)
                continue
            elif isinstance(value, (list, tuple)):
                # Handle lists
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            
            # Add value with word wrapping
            lines = self._wrap_text(value_str, 60)
            for i, line in enumerate(lines):
                ET.SubElement(parent, 'text', {
                    'x': '40', 'y': str(y_offset + (i * 16)),
                    'fill': '#34495e'
                }).text = line
            
            y_offset += len(lines) * 16 + 8
        
        return y_offset
    
    def _add_pdf_previews(self, svg: ET._Element, pages: List[int]) -> int:
        """Add PDF page previews to the SVG."""
        preview_group = ET.SubElement(svg, 'g', {
            'id': 'pdf_previews',
            'transform': 'translate(20, 300)'
        })
        
        # Add title
        ET.SubElement(preview_group, 'text', {
            'x': '0', 'y': '0',
            'font-family': 'Arial, sans-serif',
            'font-size': '16',
            'font-weight': 'bold',
            'fill': '#2c3e50'
        }).text = 'PDF Previews'
        
        # Add PDF previews for each page
        y_offset = 30
        for i, page_num in enumerate(pages):
            try:
                # Create a preview of the page
                preview_path = os.path.join(self.temp_dir, f"preview_{page_num:03d}.png")
                self._convert_pdf_page_to_image(page_num, preview_path, dpi=150)
                
                # Add page preview
                preview_data = self._image_to_data_uri(preview_path)
                preview_width = 200
                preview_height = 280
                
                # Add preview image
                ET.SubElement(preview_group, 'image', {
                    'x': str((i % 3) * (preview_width + 20)),
                    'y': str(y_offset + (i // 3) * (preview_height + 40)),
                    'width': str(preview_width),
                    'height': str(preview_height),
                    'preserveAspectRatio': 'xMidYMid meet',
                    'href': preview_data
                })
                
                # Add page number
                ET.SubElement(preview_group, 'text', {
                    'x': str((i % 3) * (preview_width + 20) + preview_width / 2),
                    'y': str(y_offset + preview_height + 30 + (i // 3) * (preview_height + 40)),
                    'text-anchor': 'middle',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '12',
                    'fill': '#7f8c8d'
                }).text = f"Page {page_num}"
                
            except Exception as e:
                print(f"Error creating preview for page {page_num}: {e}", file=sys.stderr)
        
        # Calculate total height used by previews
        rows = (len(pages) + 2) // 3  # 3 previews per row
        return 300 + (rows * (preview_height + 40)) + 50
    
    def _add_extracted_text(self, svg: ET._Element, extracted_text: Dict[int, str], y_offset: int) -> None:
        """Add extracted text to the SVG."""
        if not extracted_text:
            return
        
        text_group = ET.SubElement(svg, 'g', {
            'id': 'extracted_text',
            'transform': f'translate(20, {y_offset})',
            'font-family': 'Courier New, monospace',
            'font-size': '10',
            'fill': '#2c3e50'
        })
        
        # Add title
        ET.SubElement(text_group, 'text', {
            'x': '0', 'y': '0',
            'font-family': 'Arial, sans-serif',
            'font-size': '16',
            'font-weight': 'bold',
            'fill': '#2c3e50'
        }).text = 'Extracted Text'
        
        y_offset = 30
        
        for page_num, text in extracted_text.items():
            # Add page header
            ET.SubElement(text_group, 'text', {
                'x': '0', 'y': str(y_offset),
                'font-weight': 'bold',
                'fill': '#e74c3c'
            }).text = f"--- Page {page_num} ---"
            
            y_offset += 20
            
            # Add text with word wrapping
            lines = self._wrap_text(text, 100)
            for i, line in enumerate(lines):
                ET.SubElement(text_group, 'tspan', {
                    'x': '20',
                    'dy': '1.2em',
                    'dominant-baseline': 'hanging'
                }).text = line
                
                # Add line number
                ET.SubElement(text_group, 'text', {
                    'x': '0', 'y': str(y_offset + (i * 14)),
                    'font-size': '8',
                    'fill': '#95a5a6',
                    'text-anchor': 'end',
                    'dominant-baseline': 'hanging'
                }).text = f"{i+1:3d} |"
            
            y_offset += len(lines) * 14 + 20
    
    def _export_metadata_html(self, output_path: str) -> None:
        """Export metadata as an HTML file."""
        if not self.metadata:
            self.extract_metadata()
        
        html = ET.Element('html')
        head = ET.SubElement(html, 'head')
        ET.SubElement(head, 'title').text = f"Metadata: {os.path.basename(self.pdf_path)}"
        
        # Add some basic CSS
        style = ET.SubElement(head, 'style')
        style.text = """
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #3498db; margin-top: 30px; }
            .section { margin-bottom: 30px; }
            .property { margin: 10px 0; }
            .key { font-weight: bold; color: #2c3e50; }
            .value { margin-left: 20px; }
            .nested { margin-left: 30px; border-left: 2px solid #eee; padding-left: 15px; }
        """
        
        body = ET.SubElement(html, 'body')
        ET.SubElement(body, 'h1').text = f"Metadata: {os.path.basename(self.pdf_path)}"
        
        # Add metadata sections
        for section, data in self.metadata.items():
            if not data:
                continue
                
            section_div = ET.SubElement(body, 'div', {'class': 'section'})
            ET.SubElement(section_div, 'h2').text = section.replace('_', ' ').title()
            self._add_html_metadata(section_div, data)
        
        # Save HTML
        tree = ET.ElementTree(html)
        tree.write(output_path, pretty_print=True, encoding='UTF-8', xml_declaration=True)
    
    def _add_html_metadata(self, parent: ET._Element, data: Any, level: int = 0) -> None:
        """Recursively add metadata to HTML."""
        if isinstance(data, dict):
            for key, value in data.items():
                div = ET.SubElement(parent, 'div', {'class': 'property'})
                key_span = ET.SubElement(div, 'span', {'class': 'key'})
                key_span.text = f"{key.replace('_', ' ').title()}: "
                
                if isinstance(value, (dict, list)):
                    value_div = ET.SubElement(div, 'div', {'class': f'nested level-{level}'})
                    self._add_html_metadata(value_div, value, level + 1)
                else:
                    value_span = ET.SubElement(div, 'span', {'class': 'value'})
                    value_span.text = str(value)
        elif isinstance(data, (list, tuple)):
            ul = ET.SubElement(parent, 'ul')
            for item in data:
                li = ET.SubElement(ul, 'li')
                if isinstance(item, (dict, list, tuple)):
                    self._add_html_metadata(li, item, level + 1)
                else:
                    li.text = str(item)
        else:
            parent.text = str(data)
    
    @staticmethod
    def _wrap_text(text: str, max_chars: int = 80) -> List[str]:
        """Wrap text to a maximum number of characters per line."""
        if not text:
            return []
            
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            if not words:
                lines.append('')
                continue
                
            current_line = []
            current_length = 0
            
            for word in words:
                word_length = len(word)
                if current_line and current_length + word_length + 1 > max_chars:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    current_line.append(word)
                    current_length += word_length + (1 if current_line else 0)
            
            if current_line:
                lines.append(' '.join(current_line))
        
        return lines
    
    @staticmethod
    def _image_to_data_uri(image_path: str) -> str:
        """Convert an image file to a data URI."""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Determine MIME type from file extension
        ext = os.path.splitext(image_path)[1].lower()
        if ext == '.png':
            mime_type = 'image/png'
        elif ext in ('.jpg', '.jpeg'):
            mime_type = 'image/jpeg'
        elif ext == '.gif':
            mime_type = 'image/gif'
        else:
            mime_type = 'application/octet-stream'
        
        # Encode as base64
        base64_data = base64.b64encode(image_data).decode('ascii')
        return f"data:{mime_type};base64,{base64_data}"
    
    def __del__(self):
        """Clean up temporary files."""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert PDF to SVG with embedded metadata and text extraction.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('input_pdf', help='Input PDF file')
    parser.add_argument('-o', '--output', help='Output file (default: input filename with appropriate extension)')
    parser.add_argument('--format', type=str, default='svg',
                       choices=[f.value for f in OutputFormat],
                       help='Output format')
    parser.add_argument('--pages', type=str, help='Comma-separated list of page numbers to process (e.g., "1,3,5-7" or "all" for all pages)')
    parser.add_argument('--password', type=str, help='Password for encrypted PDFs')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for text extraction')
    parser.add_argument('--no-text', action='store_true', help='Skip text extraction')
    parser.add_argument('--metadata-only', action='store_true', help='Only extract metadata, not content')
    
    args = parser.parse_args()
    
    # Set default output filename if not provided
    if not args.output:
        base_name = os.path.splitext(args.input_pdf)[0]
        output_format = OutputFormat.from_string(args.format)
        args.output = f"{base_name}.{output_format.value}"
    
    try:
        # Parse page range
        pages = None
        if args.pages and args.pages.lower() != 'all':
            pages = []
            for part in args.pages.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages.extend(range(start, end + 1))
                else:
                    pages.append(int(part))
        
        # Process the PDF
        processor = PDFProcessor(args.input_pdf, args.password)
        
        # Extract metadata
        print("Extracting metadata...")
        metadata = processor.extract_metadata()
        
        # Export metadata if requested
        output_format = OutputFormat.from_string(args.format)
        if args.metadata_only:
            print(f"Exporting metadata to {args.output}...")
            processor.export_metadata(args.output, output_format)
            print(f"Metadata exported to {os.path.abspath(args.output)}")
            return
        
        # Generate SVG with embedded content
        if output_format == OutputFormat.SVG:
            print("Generating SVG with embedded content...")
            output_path = processor.generate_svg(
                args.output, 
                pages=pages, 
                include_text=not args.no_text,
                dpi=args.dpi
            )
            print(f"SVG generated: {os.path.abspath(output_path)}")
        else:
            # For non-SVG formats, just export metadata
            print(f"Exporting metadata to {args.output}...")
            processor.export_metadata(args.output, output_format)
        
        print("\nProcessing complete!")
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
