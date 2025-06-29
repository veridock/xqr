# SVG to PDF and Image Conversion

This guide covers converting SVG files to PDF and other image formats, including handling embedded PDFs and metadata.

## Prerequisites

- Install required system dependencies (see [Installation Guide](INSTALLATION.md))
- Python packages: `cairosvg`, `Pillow`, `lxml`, `python-magic`

## Basic Usage

### Extracting Embedded PDFs

Extract a PDF embedded within an SVG file:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --extract-pdf output.pdf
```

### Converting SVG to PDF

Convert an SVG file to PDF:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-pdf output.pdf
```

### Converting to Image Formats

Convert SVG to PNG:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-png output.png
```

Convert SVG to JPG:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-jpg output.jpg
```

### Extracting Metadata

View metadata contained in an SVG file:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --extract-metadata
```

## Advanced Features

### Custom Page Sizes and Orientation

Convert to A4 size:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-pdf output.pdf --page-size A4
```

Custom page size in points (1/72 inch):

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-pdf output.pdf --page-size "800x600"
```

Landscape orientation:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-pdf output.pdf --landscape
```

### Image Processing

Convert to grayscale:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-png output.png --grayscale
```

Add a white background (useful for transparent SVGs):

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-png output.png --background white
```

Adjust image quality (1-100, higher is better):

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --to-jpg output.jpg --quality 95
```

### Working with Embedded Resources

Extract all embedded images from SVG:

```bash
python examples/svg_pdf_conversion_fixed.py input.svg --extract-images output_dir/
```

Convert SVG with embedded images to PDF (preserves all resources):

```bash
python examples/svg_pdf_conversion_fixed.py complex.svg --to-pdf output.pdf --embed-images
```

### Batch Processing

Process multiple SVGs in parallel (using GNU parallel):

```bash
find . -name "*.svg" | parallel -j 4 "python examples/svg_pdf_conversion_fixed.py {} --to-pdf {.}.pdf"
```

Only process SVGs modified in the last 24 hours:

```bash
find . -name "*.svg" -mtime -1 | while read file; do
    python examples/svg_pdf_conversion_fixed.py "$file" --to-pdf "${file%.svg}.pdf"
done
```

## Integration Examples

### Pipe SVG from stdin

```bash
# Convert SVG from a web request to PDF
curl -s https://example.com/diagram.svg | \
    python examples/svg_pdf_conversion_fixed.py - --to-pdf output.pdf
```

### Use as a Python Module

```python
from svg_pdf_conversion_fixed import SVGConverter

# Convert SVG to PDF
converter = SVGConverter("input.svg")
converter.convert_to_pdf("output.pdf")

# Extract metadata
metadata = converter.extract_metadata()
print(metadata)
```

## Performance Tips

1. **For large SVGs**: Use `--downgrade` to simplify complex paths
2. **For batch processing**: Skip metadata extraction when not needed with `--no-metadata`
3. **Memory optimization**: Process large files with `--chunk-size`
4. **Caching**: Use the `--cache` option to cache intermediate conversions

## Troubleshooting

### Common Issues

- **Missing Dependencies**: Ensure all system dependencies are installed
- **Font Issues**: Install system fonts or specify font paths
- **Memory Errors**: Process large files in chunks using `--chunk-size`

For more information, see the [Troubleshooting Guide](TROUBLESHOOTING.md).
