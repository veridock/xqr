#!/usr/bin/env python3
"""
Create a sample PDF with rich metadata for testing.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime

def create_sample_pdf(output_path: str = "sample_document_enhanced.pdf"):
    """Create a sample PDF with rich metadata and sample content."""
    # Create PDF with metadata
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        title="Sample Document with Rich Metadata",
        author="PDF Processing Demo",
        subject="Demonstration of PDF Metadata and Content",
        keywords="pdf, metadata, demo, python",
        creator="PDF Generation Script",
        producer="ReportLab",
    )
    
    # Add more metadata after creation
    doc.setTitle("Sample Document with Rich Metadata")
    doc.setAuthor("PDF Processing Demo")
    doc.setSubject("Demonstration of PDF Metadata and Content")
    doc.setKeywords("pdf, metadata, demo, python")
    doc.setCreator("PDF Generation Script")
    doc.setProducer("ReportLab")
    
    # Create custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db')
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        spaceAfter=12
    )
    
    # Create content
    content = []
    
    # Title
    content.append(Paragraph("Sample Document with Rich Metadata", title_style))
    
    # Document Information
    content.append(Paragraph("Document Information", heading_style))
    content.append(Paragraph(
        "This document contains sample content and rich metadata for testing PDF processing workflows. "
        "It includes multiple sections, formatting, and embedded metadata that can be extracted and displayed "
        "in various output formats.", 
        normal_style
    ))
    
    # Sample Content
    content.append(Paragraph("Sample Content", heading_style))
    content.append(Paragraph(
        "This is a sample paragraph demonstrating text content in the PDF. The quick brown fox jumps over the lazy dog. "
        "Pack my box with five dozen liquor jugs. How vexingly quick daft zebras jump!",
        normal_style
    ))
    
    # Add a table of contents
    content.append(Paragraph("Table of Contents", heading_style))
    content.append(Paragraph("1. Document Information", normal_style))
    content.append(Paragraph("2. Sample Content", normal_style))
    content.append(Paragraph("3. Additional Information", normal_style))
    content.append(Spacer(1, 20))
    
    # Additional sections
    content.append(Paragraph("Additional Information", heading_style))
    content.append(Paragraph(
        "This section contains additional information that might be useful for testing extraction and display. "
        "It includes multiple paragraphs to demonstrate text flow and formatting.",
        normal_style
    ))
    
    # Generate the PDF
    doc.build(content)
    
    print(f"Created sample PDF with rich metadata: {output_path}")
    return output_path

if __name__ == "__main__":
    create_sample_pdf()
