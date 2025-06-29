import base64
import subprocess
import tempfile
from pathlib import Path
from lxml import etree

def create_svg_with_pdf(pdf_path: str, output_svg: str):
    """
    Create an SVG with an embedded PDF
    """
    # Read PDF as base64
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    
    # Create SVG with embedded PDF
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <title>SVG with Embedded PDF</title>
        <desc>This SVG contains an embedded PDF document</desc>
        
        <!-- Add a rectangle as background -->
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        
        <!-- Add title -->
        <text x="20" y="40" font-family="Arial" font-size="24">
            Embedded PDF Document
        </text>
        
        <!-- Embed PDF using data URI -->
        <foreignObject x="20" y="60" width="400" height="500">
            <object data="data:application/pdf;base64,{pdf_base64}" 
                    type="application/pdf" 
                    width="100%" 
                    height="100%">
                <p>Unable to display PDF. <a href="data:application/pdf;base64,{pdf_base64}">Download PDF</a></p>
            </object>
        </foreignObject>
        
        <!-- We'll add extracted text here later -->
        <g id="extracted-text" transform="translate(20, 580)">
            <text x="0" y="20" font-family="Arial" font-size="14" font-weight="bold">
                Extracted Text (from Tesseract):
            </text>
            <!-- Text will be added here -->
        </g>
    </svg>"""
    
    # Save SVG
    with open(output_svg, 'w') as f:
        f.write(svg)
    
    return output_svg

def extract_text_with_tesseract(pdf_path: str) -> str:
    """
    Extract text from PDF using Tesseract OCR
    """
    try:
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Run Tesseract OCR
        cmd = ['pdftotext', '-layout', pdf_path, temp_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"Error running pdftotext: {result.stderr}"
        
        # Read the extracted text
        with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Clean up
        Path(temp_path).unlink()
        
        return text.strip()
    
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def add_metadata_to_svg(svg_path: str, metadata: dict):
    """
    Add metadata to an SVG file
    """
    # Parse the SVG
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()
    
    # Create metadata element if it doesn't exist
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    metadata_elem = root.find('svg:metadata', namespaces=ns)
    
    if metadata_elem is None:
        metadata_elem = etree.SubElement(root, 'metadata')
    
    # Add our custom metadata
    for key, value in metadata.items():
        meta = etree.SubElement(metadata_elem, 'meta')
        meta.set('name', key)
        meta.set('content', str(value))
    
    # Save the modified SVG
    tree.write(svg_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def add_extracted_text_to_svg(svg_path: str, text: str, max_width: int = 100, line_height: int = 20):
    """
    Add extracted text to the SVG in a readable format
    """
    # Parse the SVG
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()
    
    # Find the extracted-text group
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    text_group = root.find('.//svg:g[@id="extracted-text"]', namespaces=ns)
    
    if text_group is None:
        print("Warning: Could not find extracted-text group in SVG")
        return
    
    # Clear any existing text elements (except the title)
    for elem in text_group.findall('svg:text', namespaces=ns):
        if elem.getparent() == text_group and elem != text_group[0]:
            text_group.remove(elem)
    
    # Add the extracted text with word wrapping
    y_pos = 50  # Start below the title
    words = text.split()
    current_line = []
    current_width = 0
    
    for word in words:
        # Simple word wrapping
        if current_line and (current_width + len(word) + 1) > max_width:
            # Add the current line
            line_text = ' '.join(current_line)
            etree.SubElement(
                text_group, 
                '{http://www.w3.org/2000/svg}text',
                x='0',
                y=str(y_pos),
                font_family='monospace',
                font_size='12',
                fill='black'
            ).text = line_text
            
            y_pos += line_height
            current_line = [word]
            current_width = len(word)
        else:
            current_line.append(word)
            current_width += len(word) + 1
    
    # Add the last line
    if current_line:
        line_text = ' '.join(current_line)
        etree.SubElement(
            text_group, 
            '{http://www.w3.org/2000/svg}text',
            x='0',
            y=str(y_pos),
            font_family='monospace',
            font_size='12',
            fill='black'
        ).text = line_text
    
    # Save the modified SVG
    tree.write(svg_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def main():
    # Example usage
    input_pdf = "example.pdf"  # Replace with your PDF file
    output_svg = "output_with_pdf.svg"
    
    if not Path(input_pdf).exists():
        print(f"Error: Input PDF file '{input_pdf}' not found.")
        print("Please provide a valid PDF file path.")
        return
    
    try:
        # Step 1: Create SVG with embedded PDF
        print(f"Creating SVG with embedded PDF: {output_svg}")
        create_svg_with_pdf(input_pdf, output_svg)
        
        # Step 2: Extract text from PDF using Tesseract
        print("Extracting text from PDF...")
        extracted_text = extract_text_with_tesseract(input_pdf)
        
        # Step 3: Add extracted text to SVG
        print("Adding extracted text to SVG...")
        add_extracted_text_to_svg(output_svg, extracted_text)
        
        # Step 4: Add metadata to SVG
        print("Adding metadata to SVG...")
        metadata = {
            'source': input_pdf,
            'processing_date': '2025-06-29',
            'extraction_tool': 'Tesseract OCR',
            'text_length': len(extracted_text)
        }
        add_metadata_to_svg(output_svg, metadata)
        
        print(f"\nDone! Created: {output_svg}")
        print(f"Extracted {len(extracted_text)} characters of text from the PDF.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
