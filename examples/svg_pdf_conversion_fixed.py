#!/usr/bin/env python3
"""
SVG to PDF and Format Conversion Example

This script demonstrates how to:
1. Extract embedded PDFs from SVG files
2. Convert between SVG, PDF, and other formats
3. Handle metadata during conversion
"""

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from typing import Dict, Optional, cast

# For XML/HTML processing
from lxml import etree as ET  # type: ignore

# Try to import optional dependencies
try:
    import magic  # type: ignore
except ImportError:
    magic = None

try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None

try:
    import PyPDF2  # type: ignore
except ImportError:
    PyPDF2 = None


class OutputFormat(Enum):
    """Supported output formats."""
    PDF = "pdf"
    SVG = "svg"
    PNG = "png"
    JPG = "jpg"

    @classmethod
    def from_string(cls, value: str) -> 'OutputFormat':
        """Convert string to OutputFormat enum."""
        try:
            return cls(value.lower())
        except ValueError as exc:
            raise ValueError(f"Unsupported format: {value}") from exc


class SVGConverter:
    """Handles SVG to PDF and other format conversions with validation."""

    def __init__(self, input_path: str):
        """Initialize with input file path.

        Args:
            input_path: Path to the input SVG file
        """
        self.input_path = os.path.abspath(input_path)
        self.temp_dir = tempfile.mkdtemp(prefix="svg_convert_")
        self.metadata: Dict[str, str] = {}

        # Validate input file
        if not self._validate_file(self.input_path, 'svg'):
            raise ValueError(f"Invalid or corrupted SVG file: {self.input_path}")
    
    def __del__(self) -> None:
        """Clean up temporary directory."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _validate_file(self, file_path: str, file_type: Optional[str] = None) -> bool:
        """Validate if a file exists and is not empty/corrupt.

        Args:
            file_path: Path to the file to validate
            file_type: Optional file type for specific validation ('pdf', 'png', 'jpg', 'svg')

        Returns:
            bool: True if file is valid, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False

        if os.path.getsize(file_path) == 0:
            print(f"Error: File is empty: {file_path}")
            os.remove(file_path)  # Clean up empty file
            return False
        
        # If no specific type checking needed, basic validation is enough
        if not file_type:
            return True
        
        try:
            # Get MIME type if magic is available
            detected_type = None
            if magic:
                mime = magic.Magic(mime=True)
                detected_type = mime.from_file(file_path)
            
            # PDF validation
            if file_type.lower() == 'pdf':
                if detected_type and 'pdf' not in detected_type:
                    msg = f"  ✗ Not a valid PDF (detected as {detected_type}): {file_path}"
                    print(msg)
                    return False
                if PyPDF2:
                    try:
                        with open(file_path, 'rb') as f:
                            PyPDF2.PdfReader(f)
                    except Exception as e:
                        print(f"  ✗ Corrupt PDF: {file_path} - {str(e)}")
                        return False
                return True
            
            # Image validation
            elif file_type.lower() in ['png', 'jpg', 'jpeg']:
                if detected_type:
                    if file_type.lower() == 'png' and 'png' not in detected_type:
                        msg = f"  ✗ Not a valid PNG (detected as {detected_type}): {file_path}"
                        print(msg)
                        return False
                    if file_type.lower() in ['jpg', 'jpeg'] and 'jpeg' not in detected_type:
                        msg = f"  ✗ Not a valid JPG (detected as {detected_type}): {file_path}"
                        print(msg)
                        return False
                
                if Image:
                    try:
                        with Image.open(file_path) as img:
                            img.verify()  # Verify the image data
                    except Exception as e:
                        msg = f"  ✗ Corrupt {file_type.upper()}: {file_path} - {str(e)}"
                        print(msg)
                        return False
                return True
                    
            # SVG validation
            elif file_type.lower() == 'svg':
                if detected_type and 'svg' not in detected_type and 'xml' not in detected_type:
                    msg = f"  ✗ Not a valid SVG (detected as {detected_type}): {file_path}"
                    print(msg)
                    return False
                try:
                    ET.parse(file_path)  # Try to parse as XML
                    return True
                except Exception as e:
                    print(f"  ✗ Corrupt SVG: {file_path} - {str(e)}")
                    return False
                    
        except Exception as e:
            print(f"  ⚠️ Validation error for {file_path}: {str(e)}")
            # Fallback to basic file existence check
            return os.path.exists(file_path) and os.path.getsize(file_path) > 0
        
        return True
    
    def extract_embedded_pdf(self, output_path: Optional[str] = None) -> str:
        """Extract embedded PDF from SVG file.
        
        Args:
            output_path: Path to save the extracted PDF (default: input filename with .pdf)
            
        Returns:
            Path to the extracted PDF file
        """
        if not output_path:
            base_name = os.path.splitext(self.input_path)[0]
            output_path = f"{base_name}_extracted.pdf"
        
        with open(self.input_path, 'rb') as f:
            svg_content = f.read()
        
        # Look for base64-encoded PDF data
        matches = re.findall(r'data:application/pdf;base64,([a-zA-Z0-9+/=]+)', svg_content.decode('utf-8'))
        if not matches:
            raise ValueError("No embedded PDF found in the SVG file")
        
        # Use the last match (most likely the main content)
        pdf_data = base64.b64decode(matches[-1])
        
        # Save the PDF
        with open(output_path, 'wb') as f:
            f.write(pdf_data)
        
        # Validate the extracted PDF
        if not self._validate_file(output_path, 'pdf'):
            os.remove(output_path)  # Clean up invalid file
            raise ValueError(f"Extracted PDF is invalid or corrupted: {output_path}")
        
        print(f"✓ Extracted valid PDF: {output_path} ({os.path.getsize(output_path)} bytes)")
        return output_path
    
    def convert_to_pdf(self, output_path: Optional[str] = None) -> str:
        """Convert SVG to PDF using cairosvg or Inkscape.
        
        Args:
            output_path: Path to save the output PDF (default: input filename with .pdf)
            
        Returns:
            Path to the converted PDF file
        """
        if not output_path:
            base_name = os.path.splitext(self.input_path)[0]
            output_path = f"{base_name}.pdf"
        
        try:
            # Try using cairosvg first (faster)
            import cairosvg  # type: ignore
            cairosvg.svg2pdf(url=self.input_path, write_to=output_path)
            
            # Validate the converted PDF
            if not self._validate_file(output_path, 'pdf'):
                os.remove(output_path)  # Clean up invalid file
                raise ValueError(f"Converted PDF is invalid or corrupted: {output_path}")
                
            print(f"✓ Converted to valid PDF: {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
        except (ImportError, OSError):
            # Fall back to Inkscape if cairosvg fails
            try:
                subprocess.run(
                    ["inkscape", "--export-filename=" + output_path, self.input_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Validate the converted PDF
                if not self._validate_file(output_path, 'pdf'):
                    os.remove(output_path)  # Clean up invalid file
                    raise ValueError(f"Converted PDF is invalid or corrupted: {output_path}")
                    
                print(f"✓ Converted to valid PDF: {output_path} ({os.path.getsize(output_path)} bytes)")
                return output_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError(
                    "Neither cairosvg nor Inkscape is available for SVG to PDF conversion.\n"
                    "Please install one of them:\n"
                    "  pip install cairosvg\n"
                    "or install Inkscape from https://inkscape.org/"
                )
    
    def convert_to_png(self, output_path: Optional[str] = None, dpi: int = 300) -> str:
        """Convert SVG to PNG using cairosvg or Inkscape.
        
        Args:
            output_path: Path to save the output PNG (default: input filename with .png)
            dpi: DPI for the output image (default: 300)
            
        Returns:
            Path to the converted PNG file
        """
        if not output_path:
            base_name = os.path.splitext(self.input_path)[0]
            output_path = f"{base_name}.png"
        
        try:
            # Try using cairosvg first (faster)
            import cairosvg  # type: ignore
            cairosvg.svg2png(url=self.input_path, write_to=output_path, dpi=dpi)
            
            # Validate the converted PNG
            if not self._validate_file(output_path, 'png'):
                os.remove(output_path)  # Clean up invalid file
                raise ValueError(f"Converted PNG is invalid or corrupted: {output_path}")
                
            print(f"✓ Converted to valid PNG: {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
        except (ImportError, OSError):
            # Fall back to Inkscape if cairosvg fails
            try:
                subprocess.run(
                    ["inkscape", f"--export-dpi={dpi}", "--export-filename=" + output_path, self.input_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Validate the converted PNG
                if not self._validate_file(output_path, 'png'):
                    os.remove(output_path)  # Clean up invalid file
                    raise ValueError(f"Converted PNG is invalid or corrupted: {output_path}")
                    
                print(f"✓ Converted to valid PNG: {output_path} ({os.path.getsize(output_path)} bytes)")
                return output_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError(
                    "Neither cairosvg nor Inkscape is available for SVG to PNG conversion.\n"
                    "Please install one of them:\n"
                    "  pip install cairosvg\n"
                    "or install Inkscape from https://inkscape.org/"
                )
    
    def convert_to_jpg(self, output_path: Optional[str] = None, dpi: int = 300, quality: int = 95) -> str:
        """Convert SVG to JPG using cairosvg or Inkscape.
        
        Args:
            output_path: Path to save the output JPG (default: input filename with .jpg)
            dpi: DPI for the output image (default: 300)
            quality: JPG quality (1-100, default: 95)
            
        Returns:
            Path to the converted JPG file
        """
        if not output_path:
            base_name = os.path.splitext(self.input_path)[0]
            output_path = f"{base_name}.jpg"
        
        # First convert to PNG, then to JPG
        temp_png = os.path.join(self.temp_dir, "temp.png")
        self.convert_to_png(temp_png, dpi)
        
        # Convert PNG to JPG using Pillow
        try:
            from PIL import Image  # type: ignore
            img = Image.open(temp_png)
            # Create a white background for transparent SVGs
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            img.convert('RGB').save(output_path, 'JPEG', quality=quality, optimize=True)
            
            # Validate the converted JPG
            if not self._validate_file(output_path, 'jpg'):
                os.remove(output_path)  # Clean up invalid file
                raise ValueError(f"Converted JPG is invalid or corrupted: {output_path}")
                
            print(f"✓ Converted to valid JPG: {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
        except ImportError:
            # If Pillow is not available, try using Inkscape directly
            try:
                subprocess.run(
                    ["inkscape", f"--export-dpi={dpi}", f"--export-jpeg-quality={quality}", 
                     "--export-filename=" + output_path, self.input_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Validate the converted JPG
                if not self._validate_file(output_path, 'jpg'):
                    os.remove(output_path)  # Clean up invalid file
                    raise ValueError(f"Converted JPG is invalid or corrupted: {output_path}")
                    
                print(f"✓ Converted to valid JPG: {output_path} ({os.path.getsize(output_path)} bytes)")
                return output_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError(
                    "Pillow or Inkscape is required for SVG to JPG conversion.\n"
                    "Please install one of them:\n"
                    "  pip install pillow\n"
                    "or install Inkscape from https://inkscape.org/"
                )
    
    def extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from SVG file.
        
        Returns:
            Dictionary containing metadata key-value pairs
        """
        metadata = {}
        try:
            tree = ET.parse(self.input_path)
            root = tree.getroot()
            
            # Extract title
            title = root.find('.//{http://www.w3.org/2000/svg}title')
            if title is not None and title.text:
                metadata['title'] = title.text.strip()
            
            # Extract description
            desc = root.find('.//{http://www.w3.org/2000/svg}desc')
            if desc is not None and desc.text:
                metadata['description'] = desc.text.strip()
            
            # Extract RDF metadata if present
            for desc in root.findall('.//{http://www.w3.org/2000/svg}metadata//{http://purl.org/dc/elements/1.1/}*'):
                tag = desc.tag.split('}')[-1]  # Get tag name without namespace
                if desc.text and desc.text.strip():
                    metadata[tag] = desc.text.strip()
            
            self.metadata = metadata
            return metadata
            
        except Exception as e:
            print(f"Warning: Could not extract metadata: {e}")
            return {}


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Convert between SVG, PDF, and image formats with validation.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_file', help='Input SVG file')
    
    # Output format options
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument('--extract-pdf', metavar='OUTPUT_PDF', help='Extract embedded PDF from SVG')
    output_group.add_argument('--to-pdf', metavar='OUTPUT_PDF', help='Convert SVG to PDF')
    output_group.add_argument('--to-png', metavar='OUTPUT_PNG', help='Convert SVG to PNG')
    output_group.add_argument('--to-jpg', metavar='OUTPUT_JPG', help='Convert SVG to JPG')
    output_group.add_argument('--extract-metadata', action='store_true', help='Extract metadata from SVG')
    output_group.add_argument('--validate', metavar='FILE', help='Validate a file (auto-detects type)')
    
    # Optional arguments
    parser.add_argument('--dpi', type=int, default=300, help='DPI for image output (default: 300)')
    parser.add_argument('--quality', type=int, default=95, help='JPG quality (1-100, default: 95)')
    
    args = parser.parse_args()
    
    # If --validate is used, just validate the file and exit
    if hasattr(args, 'validate') and args.validate:
        if not os.path.exists(args.validate):
            print(f"Error: File to validate does not exist: {args.validate}", file=sys.stderr)
            sys.exit(1)
            
        # Try to detect file type
        file_type = None
        if magic:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(args.validate)
            if 'pdf' in mime_type:
                file_type = 'pdf'
            elif 'png' in mime_type:
                file_type = 'png'
            elif 'jpeg' in mime_type or 'jpg' in mime_type:
                file_type = 'jpg'
            elif 'svg' in mime_type or 'xml' in mime_type:
                file_type = 'svg'
        
        # Create a temporary converter just for validation
        converter = SVGConverter(args.input_file if os.path.exists(args.input_file) else __file__)
        if converter._validate_file(args.validate, file_type):
            print(f"✓ File is valid: {args.validate}")
            sys.exit(0)
        else:
            print(f"✗ File is invalid or corrupted: {args.validate}", file=sys.stderr)
            sys.exit(1)
    
    # For other operations, check input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    try:
        converter = SVGConverter(args.input_file)
        
        if args.extract_pdf:
            converter.extract_embedded_pdf(args.extract_pdf)
        elif args.to_pdf:
            converter.convert_to_pdf(args.to_pdf)
        elif args.to_png:
            converter.convert_to_png(args.to_png, args.dpi)
        elif args.to_jpg:
            converter.convert_to_jpg(args.to_jpg, args.dpi, args.quality)
        elif args.extract_metadata:
            metadata = converter.extract_metadata()
            if metadata:
                print("\nMetadata:")
                for key, value in metadata.items():
                    print(f"{key}: {value}")
            else:
                print("No metadata found in the SVG file.")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
