# SVG and PDF Processing Examples

## Example 1: Basic SVG with Embedded PDF (`svg_pdf_example.py`)

This example shows how to:
1. Create an SVG with an embedded PDF
2. Extract text from the PDF using Tesseract OCR
3. Add the extracted text to the SVG

## Example 2: Advanced PDF to SVG with Metadata (`svg_pdf_metadata.py`)

This enhanced example demonstrates:
1. Creating an SVG with an embedded PDF
2. Extracting text and metadata using Tesseract OCR
3. Adding extracted text with word wrapping
4. Including comprehensive document metadata
5. Adding processing information to the SVG metadata section

## Prerequisites

1. Install required system packages:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install poppler-utils tesseract-ocr poppler-utils
   
   # On macOS (using Homebrew)
   brew install poppler tesseract
   ```

2. Install Python dependencies:
   ```bash
   pip install lxml beautifulsoup4 cssselect
   ```

## Basic Example Usage

1. Place your PDF file in the `examples` directory or provide its full path
2. Run the script:
   ```bash
   python svg_pdf_example.py
   ```
3. The script will create an `output_with_pdf.svg` file containing:
   - The original PDF embedded in the SVG
   - Extracted text from the PDF (using Tesseract)
   - Basic metadata about the processing

## Advanced Example Usage

1. Run the enhanced script with a PDF file:
   ```bash
   python svg_pdf_metadata.py input.pdf -o output.svg
   ```
   
   Options:
   - `input.pdf`: Path to the input PDF file
   - `-o, --output`: Output SVG file path (optional, defaults to input filename with .svg extension)

2. The script will create an SVG file containing:
   - Embedded PDF preview
   - Extracted text with word wrapping
   - Document metadata section
   - Processing information in the SVG metadata

## How It Works (Advanced Example)

1. **PDF Processing**:
   - PDF is converted to base64 for embedding
   - Each page is processed with Tesseract OCR for text extraction
   - Document metadata is extracted using `pdfinfo`

2. **SVG Generation**:
   - Creates a responsive SVG layout
   - Embeds the PDF using a data URI
   - Adds visual elements for better presentation

3. **Text Processing**:
   - Extracts text with Tesseract OCR
   - Implements word wrapping for better readability
   - Preserves document structure where possible

4. **Metadata Handling**:
   - Extracts document metadata (author, creation date, etc.)
   - Adds processing information (timestamps, checksums)
   - Includes all metadata in the SVG's metadata section

## Customization

### Basic Example
- Adjust `max_width` and `line_height` in `add_extracted_text_to_svg()` for different text layouts
- Modify the metadata dictionary in `main()` to include custom fields
- Change the SVG styling in `create_svg_with_pdf()` for different visual appearances

### Advanced Example
- Modify `DEFAULT_WIDTH` and `TEXT_AREA_HEIGHT` in the script for different layout dimensions
- Adjust OCR settings in `extract_text_with_tesseract()` for better text extraction
- Customize the SVG styling in the `SVGGenerator` class
- Add custom metadata processing in the `process_pdf_to_svg()` function

## Features

### Basic Example
- Preserves the original PDF's layout in the embedded view
- Extracted text is added below the PDF preview
- Simple and straightforward implementation

### Advanced Example
- Handles multi-page PDFs
- Extracts and displays document metadata
- Includes processing information and checksums
- Better error handling and logging
- More customizable layout and styling
- Word wrapping for better text presentation
- Comprehensive SVG metadata section

## Example Output (Advanced)

```xml
<svg width="800" height="900" viewBox="0 0 800 900" xmlns="http://www.w3.org/2000/svg">
  <title>Processed Document</title>
  <!-- Embedded PDF -->
  <g id="embedded-pdf" transform="translate(20, 20)">
    <!-- PDF preview and object -->
  </g>
  
  <!-- Extracted Text -->
  <g id="extracted-text" transform="translate(20, 500)" font-family="monospace" font-size="12" fill="black">
    <text x="0" y="0" font-weight="bold" font-size="14">Extracted Text:</text>
    <!-- Extracted text content here -->
  </g>
  
  <!-- Document Metadata -->
  <g id="metadata" transform="translate(20, 700)" font-family="sans-serif" font-size="12">
    <text x="0" y="0" font-weight="bold" font-size="14">Document Metadata:</text>
    <!-- Metadata items here -->
  </g>
  
  <!-- Processing Metadata (invisible but embedded) -->
  <metadata>
    <meta name="processor" content="xqr-pdf-processor"/>
    <meta name="version" content="1.0"/>
    <meta name="extraction_tool" content="Tesseract OCR"/>
    <meta name="extraction_date" content="2025-06-29T15:30:00"/>
    <meta name="source_checksum" content="d41d8cd98f00b204e9800998ecf8427e"/>
  </metadata>
</svg>
```

## Notes

- The advanced example provides a more robust solution for document processing
- All text is searchable within the SVG
- The embedded PDF maintains its original formatting
- Processing metadata is included for traceability
- The layout is responsive and can be customized as needed
