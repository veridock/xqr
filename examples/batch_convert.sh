#!/bin/bash
# Batch conversion script for SVG files

echo "Starting batch conversion of SVG files..."

for svg_file in sample_*.svg; do
    base_name="${svg_file%.svg}"
    echo -e "\nProcessing $svg_file..."
    
    # Extract PDF if it exists
    echo -n "  Extracting PDF... "
    if python svg_pdf_conversion_fixed.py "$svg_file" --extract-pdf "${base_name}_batch_extracted.pdf" 2>/dev/null; then
        echo "✓"
    else
        echo "✗ (No embedded PDF found)"
    fi
    
    # Convert to PDF
    echo -n "  Converting to PDF... "
    if python svg_pdf_conversion_fixed.py "$svg_file" --to-pdf "${base_name}_batch.pdf" 2>/dev/null; then
        echo "✓"
    else
        echo "✗ (Failed)"
    fi
    
    # Convert to PNG
    echo -n "  Converting to PNG... "
    if python svg_pdf_conversion_fixed.py "$svg_file" --to-png "${base_name}_batch.png" 2>/dev/null; then
        echo "✓"
    else
        echo "✗ (Failed)"
    fi
    
    # Convert to JPG
    echo -n "  Converting to JPG... "
    if python svg_pdf_conversion_fixed.py "$svg_file" --to-jpg "${base_name}_batch.jpg" 2>/dev/null; then
        echo "✓"
    else
        echo "✗ (Failed)"
    fi
    
    # Extract metadata
    echo "  Extracting metadata:"
    python svg_pdf_conversion_fixed.py "$svg_file" --extract-metadata
    
done

echo -e "\nBatch conversion complete!"
