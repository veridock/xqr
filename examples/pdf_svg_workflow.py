#!/usr/bin/env python3
"""
PDF to SVG Workflow Example

This script demonstrates a complete workflow for:
1. Converting a PDF to an SVG with embedded PDF data
2. Extracting text and metadata from the PDF
3. Including the extracted information in the SVG
"""

import base64
import subprocess
import sys
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# XML/HTML escaping
from xml.sax.saxutils import escape as xml_escape

# For SVG generation
from lxml import etree as ET

# For command-line arguments
import argparse

def create_svg_with_embedded_pdf(pdf_path: str, output_svg: str) -> str:
    """
    Step 1: Create an SVG with an embedded PDF
    
    Args:
        pdf_path: Path to the input PDF file
        output_svg: Path where the output SVG will be saved
        
    Returns:
        Path to the created SVG file
    """
    print(f"\n{'='*80}")
    print("STEP 1: Creating SVG with embedded PDF")
    print(f"Input PDF: {pdf_path}")
    print(f"Output SVG: {output_svg}")
    
    # Read the PDF file as binary
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    # Encode PDF as base64
    pdf_base64 = base64.b64encode(pdf_data).decode('ascii')
    
    # Create SVG root element
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': '800',
        'height': '1100',
        'viewBox': '0 0 800 1100'
    })
    
    # Add title
    title = ET.SubElement(svg, 'title')
    title.text = f'PDF Document: {os.path.basename(pdf_path)}'
    
    # Add a background
    ET.SubElement(svg, 'rect', {
        'x': '0', 'y': '0',
        'width': '800', 'height': '1100',
        'fill': '#f5f5f5'
    })
    
    # Add a title section
    title_group = ET.SubElement(svg, 'g', {'transform': 'translate(20, 30)'})
    ET.SubElement(title_group, 'text', {
        'x': '0', 'y': '0',
        'font-family': 'Arial', 'font-size': '24', 'font-weight': 'bold'
    }).text = 'PDF to SVG Workflow Example'
    
    # Add PDF preview section
    pdf_group = ET.SubElement(svg, 'g', {'transform': 'translate(20, 80)'})
    ET.SubElement(pdf_group, 'text', {
        'x': '0', 'y': '0',
        'font-family': 'Arial', 'font-size': '16', 'font-weight': 'bold'
    }).text = '1. PDF Preview:'
    
    # Add PDF as an embedded object
    pdf_embed = ET.SubElement(pdf_group, 'g', {'transform': 'translate(0, 30)'})
    pdf_rect = ET.SubElement(pdf_embed, 'rect', {
        'x': '0', 'y': '0',
        'width': '760', 'height': '500',
        'fill': 'white',
        'stroke': '#ccc',
        'rx': '5', 'ry': '5'
    })
    
    # Add PDF as an embedded object using data URI
    pdf_object = ET.SubElement(pdf_embed, 'foreignObject', {
        'x': '30', 'y': '30',
        'width': '700', 'height': '440'
    })
    
    # Create HTML content for the PDF embed
    html = ET.Element('div', {
        'xmlns': 'http://www.w3.org/1999/xhtml',
        'style': 'width:100%; height:100%; overflow:hidden;'
    })
    
    # Create object tag with PDF data URI
    object_tag = f"""
    <object data="data:application/pdf;base64,{pdf_base64}" 
            type="application/pdf" 
            style="width:100%; height:100%; border: none;">
        <p>Your browser does not support embedded PDFs. Please download the PDF to view it.</p>
    </object>
    """
    html.append(ET.fromstring(object_tag))
    pdf_object.append(html)
    
    # Add a note about the embedded PDF
    ET.SubElement(pdf_embed, 'text', {
        'x': '0', 'y': '490',
        'font-family': 'Arial', 'font-size': '10', 'fill': '#666'
    }).text = 'Note: The PDF is embedded above. You can interact with it if your browser supports embedded PDFs.'
    
    # Create the SVG file
    tree = ET.ElementTree(svg)
    tree.write(output_svg, pretty_print=True, encoding='UTF-8', xml_declaration=True)
    
    print(f"Created SVG with embedded PDF: {output_svg}")
    return output_svg

def extract_pdf_metadata(pdf_path: str) -> Dict[str, str]:
    """
    Step 2: Extract metadata from PDF using pdfinfo
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    print(f"\n{'='*80}")
    print("STEP 2: Extracting PDF metadata")
    
    metadata = {}
    
    try:
        # Get basic file info
        file_stat = os.stat(pdf_path)
        metadata['File'] = os.path.basename(pdf_path)
        metadata['File Size'] = f"{file_stat.st_size / 1024:.2f} KB"
        metadata['Created'] = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        metadata['Modified'] = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get PDF-specific metadata using pdfinfo if available
        try:
            result = subprocess.run(
                ['pdfinfo', pdf_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse pdfinfo output
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        metadata[key] = value
                        
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: pdfinfo not available, using basic file metadata only")
            
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    
    # Add processing metadata
    metadata['Processing Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata['Processing Tool'] = 'PDF to SVG Workflow Example'
    
    print("Extracted metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    return metadata

def extract_text_with_tesseract(pdf_path: str) -> str:
    """
    Step 3: Extract text from PDF using Tesseract OCR
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    print(f"\n{'='*80}")
    print("STEP 3: Extracting text with Tesseract OCR")
    
    try:
        # Create a temporary directory for images
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDF to images (one per page)
            img_path = os.path.join(temp_dir, 'page')
            
            # Use pdftoppm to convert PDF to images
            subprocess.run(
                ['pdftoppm', '-png', '-r', '300', pdf_path, img_path],
                check=True,
                capture_output=True
            )
            
            # Process each page image with Tesseract
            extracted_text = []
            page_num = 1
            
            while True:
                img_file = f"{img_path}-{page_num:03d}.png"
                if not os.path.exists(img_file):
                    break
                    
                # Run Tesseract on the image
                result = subprocess.run(
                    ['tesseract', img_file, 'stdout', '-l', 'eng'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if result.stdout.strip():
                    extracted_text.append(f"--- Page {page_num} ---\n{result.stdout}")
                
                page_num += 1
            
            full_text = "\n\n".join(extracted_text)
            print(f"Extracted {len(extracted_text)} pages of text")
            return full_text
            
    except Exception as e:
        print(f"Error extracting text with Tesseract: {e}")
        return "[Error extracting text]"

def add_metadata_to_svg(svg_path: str, metadata: Dict[str, str], extracted_text: str) -> None:
    """
    Step 4: Add metadata and extracted text to the SVG
    
    Args:
        svg_path: Path to the SVG file
        metadata: Dictionary of metadata to add
        extracted_text: Extracted text from the PDF
    """
    print(f"\n{'='*80}")
    print("STEP 4: Adding metadata and extracted text to SVG")
    
    # Parse the existing SVG
    parser = ET.XMLParser(remove_blank_text=True)
    tree = ET.parse(svg_path, parser)
    root = tree.getroot()
    
    # Create a group for metadata at the bottom of the SVG
    metadata_group = ET.Element('g', {
        'transform': 'translate(20, 600)'
    })
    
    # Add metadata section title
    ET.SubElement(metadata_group, 'text', {
        'x': '0', 'y': '0',
        'font-family': 'Arial', 'font-size': '16', 'font-weight': 'bold'
    }).text = '2. Document Metadata:'
    
    # Add metadata items
    y_offset = 30
    for i, (key, value) in enumerate(metadata.items()):
        # Add key
        ET.SubElement(metadata_group, 'text', {
            'x': '20', 'y': str(y_offset),
            'font-family': 'Arial', 'font-size': '12', 'font-weight': 'bold'
        }).text = f'{key}:'
        
        # Add value (with line wrapping)
        lines = []
        words = str(value).split()
        current_line = []
        max_chars = 80
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
            
        for j, line in enumerate(lines):
            ET.SubElement(metadata_group, 'text', {
                'x': '40', 'y': str(y_offset + (j * 16)),
                'font-family': 'Courier New', 'font-size': '10'
            }).text = line
            
        y_offset += (len(lines) * 16) + 8
    
    # Add extracted text section
    y_offset += 20
    ET.SubElement(metadata_group, 'text', {
        'x': '0', 'y': str(y_offset),
        'font-family': 'Arial', 'font-size': '16', 'font-weight': 'bold'
    }).text = '3. Extracted Text:'
    
    y_offset += 30
    
    # Add extracted text with word wrapping
    lines = []
    current_line = []
    max_chars = 100
    
    for word in extracted_text.replace('\n', ' ').split():
        if len(' '.join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    # Limit to first 20 lines to avoid making the SVG too large
    max_lines = 20
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append(f'[... {len(lines) - max_lines} more lines not shown ...]')
    
    for i, line in enumerate(lines):
        ET.SubElement(metadata_group, 'text', {
            'x': '20', 'y': str(y_offset + (i * 16)),
            'font-family': 'Courier New', 'font-size': '10'
        }).text = line
    
    # Add the metadata group to the SVG
    root.append(metadata_group)
    
    # Save the updated SVG
    tree.write(svg_path, pretty_print=True, encoding='UTF-8', xml_declaration=True)
    print(f"Updated SVG with metadata and extracted text: {svg_path}")

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Convert PDF to SVG with embedded metadata')
    parser.add_argument('input_pdf', help='Input PDF file')
    parser.add_argument('-o', '--output', help='Output SVG file (default: input filename with .svg extension)')
    
    args = parser.parse_args()
    
    # Set default output filename if not provided
    if not args.output:
        base_name = os.path.splitext(args.input_pdf)[0]
        args.output = f"{base_name}_with_metadata.svg"
    
    try:
        # Step 1: Create SVG with embedded PDF
        svg_path = create_svg_with_embedded_pdf(args.input_pdf, args.output)
        
        # Step 2: Extract PDF metadata
        metadata = extract_pdf_metadata(args.input_pdf)
        
        # Step 3: Extract text with Tesseract
        extracted_text = extract_text_with_tesseract(args.input_pdf)
        
        # Step 4: Add metadata and text to SVG
        add_metadata_to_svg(svg_path, metadata, extracted_text)
        
        print("\n" + "="*80)
        print("PROCESSING COMPLETE!")
        print(f"Output SVG: {os.path.abspath(svg_path)}")
        print("="*80)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
