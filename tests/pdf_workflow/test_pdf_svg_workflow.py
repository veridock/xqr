#!/usr/bin/env python3
"""
Tests for the enhanced PDF to SVG workflow.
"""

import os
import sys
import json
import pytest
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union

# Add the parent directory to the path so we can import the example scripts
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'examples'))

# Import the example scripts
import create_sample_pdf
import enhanced_pdf_svg_workflow as epw

# Skip tests if required dependencies are not installed
pytestmark = pytest.mark.skipif(
    not shutil.which('pdftoppm') or not shutil.which('tesseract'),
    reason="Required system dependencies (pdftoppm, tesseract) not installed"
)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / 'data'
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# Sample text for PDF generation
SAMPLE_TEXT = """
This is a test PDF document generated for unit testing.
It contains multiple paragraphs and special characters: 123!@#

The quick brown fox jumps over the lazy dog.
Pack my box with five dozen liquor jugs.
"""

@pytest.fixture(scope="module")
def sample_pdf():
    """Create a sample PDF file for testing."""
    pdf_path = TEST_DATA_DIR / 'test_document.pdf'
    
    # Create a simple PDF using the example script
    create_sample_pdf.create_sample_pdf(str(pdf_path))
    
    # Verify the PDF was created
    assert pdf_path.exists(), "Failed to create sample PDF"
    assert pdf_path.stat().st_size > 0, "Sample PDF is empty"
    
    yield pdf_path
    
    # Cleanup
    if pdf_path.exists():
        pdf_path.unlink()

@pytest.fixture(scope="module")
def password_protected_pdf(sample_pdf):
    """Create a password-protected PDF for testing."""
    from PyPDF2 import PdfReader, PdfWriter
    
    # Create a password-protected version of the sample PDF
    protected_path = TEST_DATA_DIR / 'protected_document.pdf'
    password = 'test123'
    
    # Read the sample PDF
    reader = PdfReader(sample_pdf)
    writer = PdfWriter()
    
    # Copy all pages
    for page in reader.pages:
        writer.add_page(page)
    
    # Encrypt the PDF
    writer.encrypt(password)
    
    # Save the encrypted PDF
    with open(protected_path, 'wb') as f:
        writer.write(f)
    
    assert protected_path.exists(), "Failed to create password-protected PDF"
    
    yield protected_path, password
    
    # Cleanup
    if protected_path.exists():
        protected_path.unlink()

def test_pdf_processor_init(sample_pdf):
    """Test PDFProcessor initialization."""
    # Test with valid PDF
    processor = epw.PDFProcessor(sample_pdf)
    assert processor.pdf_path == str(sample_pdf.resolve())
    assert processor.password is None
    
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        epw.PDFProcessor("nonexistent.pdf")

def test_extract_metadata(sample_pdf):
    """Test metadata extraction from PDF."""
    processor = epw.PDFProcessor(sample_pdf)
    metadata = processor.extract_metadata()
    
    # Check required metadata fields
    assert 'file_info' in metadata
    assert 'pdf_info' in metadata
    assert 'processing' in metadata
    
    # Check file info
    assert metadata['file_info']['filename'] == 'test_document.pdf'
    assert metadata['file_info']['file_size'].endswith(' KB')
    
    # Check PDF info
    assert 'pages' in metadata['pdf_info']
    assert 'page_size' in metadata['pdf_info']
    
    # Check processing info
    assert 'processed_at' in metadata['processing']
    assert metadata['processing']['tool'] == 'Enhanced PDF to SVG Workflow'

def test_extract_text(sample_pdf):
    """Test text extraction from PDF."""
    processor = epw.PDFProcessor(sample_pdf)
    
    # Extract text from first page
    text_dict = processor.extract_text(pages=[1])
    
    # Check that we got some text
    assert len(text_dict) > 0
    assert 1 in text_dict
    assert len(text_dict[1]) > 0
    
    # Check that the sample text is in the extracted text
    assert "Sample Document with Rich Metadata" in text_dict[1]

def test_password_protected_pdf(password_protected_pdf):
    """Test handling of password-protected PDFs."""
    pdf_path, password = password_protected_pdf
    
    # Test without password (should fail with a specific exception)
    with pytest.raises((RuntimeError, subprocess.CalledProcessError, Exception)):
        processor = epw.PDFProcessor(str(pdf_path))
        # This should fail when trying to get PDF info
        processor.extract_metadata()
    
    # Test with correct password (should succeed)
    try:
        processor = epw.PDFProcessor(str(pdf_path), password=password)
        metadata = processor.extract_metadata()
        assert metadata is not None
        assert isinstance(metadata, dict)
        assert len(metadata) > 0  # Should have some metadata
        assert 'file_info' in metadata  # Check for expected metadata key
    except Exception as e:
        pytest.fail(f"Failed to process password-protected PDF with correct password: {e}")
    
    # Test with incorrect password (should fail)
    with pytest.raises((RuntimeError, subprocess.CalledProcessError, Exception)):
        processor = epw.PDFProcessor(str(pdf_path), password='wrong_password')
        processor.extract_metadata()

def test_generate_svg(sample_pdf, tmp_path):
    """Test SVG generation from PDF."""
    output_path = tmp_path / 'output.svg'
    
    # Create processor and generate SVG
    processor = epw.PDFProcessor(sample_pdf)
    result_path = processor.generate_svg(
        str(output_path),
        pages=[1],
        include_text=True,
        dpi=150
    )
    
    # Check output file
    assert result_path == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Check SVG content
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert '<svg' in content
        assert 'PDF Previews' in content
        assert 'Document Metadata' in content

def test_export_metadata_json(sample_pdf, tmp_path):
    """Test metadata export to JSON."""
    output_path = tmp_path / 'metadata.json'
    
    # Create processor and export metadata
    processor = epw.PDFProcessor(sample_pdf)
    result_path = processor.export_metadata(
        str(output_path),
        epw.OutputFormat.JSON
    )
    
    # Check output file
    assert result_path == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Check JSON content
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert 'file_info' in data
        assert 'pdf_info' in data

def test_export_metadata_html(sample_pdf, tmp_path):
    """Test metadata export to HTML."""
    output_path = tmp_path / 'metadata.html'
    
    # Create processor and export metadata
    processor = epw.PDFProcessor(sample_pdf)
    result_path = processor.export_metadata(
        str(output_path),
        epw.OutputFormat.HTML
    )
    
    # Check output file
    assert result_path == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Check HTML content
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        # Check for basic HTML structure
        assert '<!doctype html>' in content or '<html' in content
        
        # Check for metadata sections (case insensitive)
        metadata_terms = ['metadata', 'information', 'document', 'pdf', 'file']
        assert any(term in content for term in metadata_terms)

def test_main_cli(sample_pdf, tmp_path, monkeypatch):
    """Test the main CLI interface."""
    output_path = tmp_path / 'cli_output.svg'
    
    # Mock command line arguments
    args = [
        'enhanced_pdf_svg_workflow.py',
        str(sample_pdf),
        '--output', str(output_path),
        '--pages', '1',
        '--dpi', '150'
    ]
    
    with monkeypatch.context() as m:
        m.setattr(sys, 'argv', args)
        epw.main()
    
    # Check output file
    assert output_path.exists()
    assert output_path.stat().st_size > 0

def test_invalid_pdf(tmp_path):
    """Test handling of invalid PDF files."""
    # Create a non-PDF file
    invalid_pdf = tmp_path / 'invalid.pdf'
    with open(invalid_pdf, 'w', encoding='utf-8') as f:
        f.write('This is not a PDF file')
    
    # The PDFProcessor might not raise an exception immediately on init
    # but should fail when trying to extract metadata
    processor = epw.PDFProcessor(str(invalid_pdf))
    
    # Should raise an exception when trying to extract metadata
    with pytest.raises((RuntimeError, subprocess.CalledProcessError, Exception)):
        processor.extract_metadata()

@pytest.mark.parametrize("pages_arg,expected_pages", [
    (None, list(range(1, 6))),  # All 5 pages (1-5)
    ("1,3", [1, 3]),
    ("2-4", [2, 3, 4]),
    ("1,3-5,7", [1, 3, 4, 5]),  # Note: Page 7 doesn't exist, should be capped at 5
])
def test_page_parsing(pages_arg, expected_pages, sample_pdf, monkeypatch):
    """Test page range parsing and processing."""
    # Create a PDF with multiple pages
    from PyPDF2 import PdfWriter, PdfReader
    
    # Create a multi-page PDF with 5 pages
    writer = PdfWriter()
    reader = PdfReader(sample_pdf)
    
    # Add multiple pages with unique content
    for i in range(5):
        writer.add_page(reader.pages[0])
    
    multi_page_pdf = TEST_DATA_DIR / 'multi_page.pdf'
    with open(multi_page_pdf, 'wb') as f:
        writer.write(f)
    
    output_path = None
    try:
        processor = epw.PDFProcessor(str(multi_page_pdf))
        
        # If pages_arg is None, test the default behavior (all pages)
        if pages_arg is None:
            text_dict = processor.extract_text(pages=None)
            expected_page_count = 5  # Default is all pages
            assert len(text_dict) == expected_page_count
            return  # Skip the rest of the test for None case
            
        # For specific page ranges, test both CLI and direct API
        output_path = TEST_DATA_DIR / 'page_test_output.svg'
        
        # Test CLI interface with monkeypatching
        args = [
            'enhanced_pdf_svg_workflow.py',
            str(multi_page_pdf),
            '--output', str(output_path),
            '--pages', str(pages_arg)
        ]
        
        with monkeypatch.context() as m:
            m.setattr(sys, 'argv', args)
            epw.main()
        
        # Verify output file was created and has content
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Test direct API with the same page ranges
        # Adjust expected_pages to not exceed actual page count
        adjusted_expected_pages = [p for p in expected_pages if p <= 5]
        text_dict = processor.extract_text(pages=pages_arg)
        
        # Verify we got the expected number of pages
        assert len(text_dict) == len(adjusted_expected_pages)
        
        # Verify page numbers in the output match expected pages
        assert sorted(int(k) for k in text_dict.keys()) == sorted(adjusted_expected_pages)
        
    finally:
        # Clean up test files
        if output_path and output_path.exists():
            output_path.unlink()
        if multi_page_pdf.exists():
            multi_page_pdf.unlink()

if __name__ == "__main__":
    pytest.main([__file__])
