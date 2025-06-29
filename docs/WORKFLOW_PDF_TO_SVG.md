# PDF to SVG Workflow

This guide explains how to convert PDF files to SVG format with embedded metadata and text extraction.

## Prerequisites

- Install required system dependencies (see [Installation Guide](INSTALLATION.md))
- Python packages: `pdf2image`, `pytesseract`, `Pillow`, `lxml`

## Basic Usage

### Convert PDF to SVG

```bash
python examples/enhanced_pdf_svg_workflow.py input.pdf -o output.svg
```

### Extract Specific Pages

Extract pages 1, 3, and 5-7:

```bash
python examples/enhanced_pdf_svg_workflow.py input.pdf --pages "1,3,5-7"
```

### Export Metadata

Export metadata to JSON:

```bash
python examples/enhanced_pdf_svg_workflow.py input.pdf --format json --output metadata.json
```

Export metadata to HTML:

```bash
python examples/enhanced_pdf_svg_workflow.py input.pdf --format html --output metadata.html
```

## Advanced Features

### Password-Protected PDFs

```bash
python examples/enhanced_pdf_svg_workflow.py encrypted.pdf --password "your-password"
```

### Custom DPI for Text Extraction

Increase DPI for better OCR accuracy (default: 300):

```bash
python examples/enhanced_pdf_svg_workflow.py input.pdf --dpi 600
```

### Output Formats

XQR supports multiple output formats:

1. **SVG with Embedded PDF**:
   - Interactive PDF viewer (browser-dependent)
   - Extracted text with formatting
   - Comprehensive metadata section

2. **HTML**:
   - Formatted metadata display
   - Navigation links
   - Responsive design

3. **JSON**:
   - Raw metadata in machine-readable format
   - Compatible with other tools and scripts

## Troubleshooting

### Common Issues

- **Missing Dependencies**: Ensure all system dependencies are installed
- **Font Issues**: Install system fonts or specify font paths
- **Memory Errors**: Process large files in chunks using `--chunk-size`

For more information, see the [Troubleshooting Guide](TROUBLESHOOTING.md).
