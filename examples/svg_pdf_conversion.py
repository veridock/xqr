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
from typing import Dict, Optional, Any

# For XML/HTML processing
from lxml import etree as ET  # type: ignore

class OutputFormat(Enum):
    """Supported output formats."""
    PDF = "pdf"
    SVG = "svg"
    PNG = "png"
    JPG = "jpg"

    @classmethod
    def from_string(cls, value: str) -> 'OutputFormat':
        """Convert string to OutputFormat enum.
        
        Args:
            value: Format string to convert (case-insensitive)
            
        Returns:
            OutputFormat enum value
            
        Raises:
            ValueError: If the format is not supported
        """
        try:
            return cls(value.lower())
        except ValueError as exc:
            raise ValueError(f"Unsupported format: {value}") from exc

class SVGConverter:
    """Handles SVG to PDF and other format conversions."""

    def __init__(self, input_path: str):
        """Initialize with input file path.
        
        Args:
            input_path: Path to the input SVG file
        """
        self.input_path = os.path.abspath(input_path)
        # Create temp dir in the same directory as the output to avoid cross-device issues
        self.temp_dir = tempfile.mkdtemp(prefix="svg_convert_", dir=os.path.dirname(os.path.abspath(input_path)))
        self.metadata: Dict[str, str] = {}
    
    def extract_embedded_pdf(self, output_path: Optional[str] = None) -> str:
        """
        Extract an embedded PDF from an SVG file.

        Args:
            output_path: Path to save the extracted PDF. If None, uses a temporary file.

        Returns:
            Path to the extracted PDF file.
        """
        # Parse the SVG file
        tree = ET.parse(self.input_path)
        root = tree.getroot()

        # Look for embedded PDF in object tags
        namespaces = {"svg": "http://www.w3.org/2000/svg"}
        objects = root.xpath(
            "//svg:foreignObject//object[@type='application/pdf']",
            namespaces=namespaces
        )

        if not objects:
            # Try alternative XPath for different SVG structures
            objects = root.xpath(
                "//*[local-name()='object' and @type='application/pdf']"
            )

        if not objects:
            raise ValueError("No embedded PDF found in the SVG file.")

        # Get the first PDF object
        pdf_object = objects[0]
        data_uri = pdf_object.get("data", "")

        # Extract base64 data
        match = re.search(r"base64,(.*)", data_uri)
        if not match:
            raise ValueError("Invalid PDF data URI in SVG.")

        pdf_data = base64.b64decode(match.group(1))

        # Determine output path
        if not output_path:
            output_path = os.path.join(self.temp_dir, "extracted.pdf")
        else:
            os.makedirs(os.path.dirname(
                os.path.abspath(output_path)), exist_ok=True)

        # Save the PDF
        with open(output_path, "wb") as f:
            f.write(pdf_data)

        return output_path
    
    def convert_svg_to_pdf(self, output_path: str, **kwargs) -> str:
        """
        Convert an SVG file to PDF using cairosvg or Inkscape.

        
        Args:
            output_path: Path to save the output PDF.
            **kwargs: Additional arguments for the conversion.
            
        Returns:
            Path to the generated PDF file.
        """
        try:
            # Try using cairosvg first (faster if available)
            import cairosvg
            cairosvg.svg2pdf(url=self.input_path, write_to=output_path)
            return output_path
        except ImportError:
            # Fall back to Inkscape
            try:
                subprocess.run([
                    "inkscape",
                    "--export-filename=" + output_path,
                    self.input_path
                ], check=True)
                return output_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError(
                    "Neither cairosvg nor Inkscape is available for SVG to PDF conversion. "
                    "Please install one of them:"
                    "\n  pip install cairosvg"
                    "\nor install Inkscape from https://inkscape.org/"
                )
    
    def convert_pdf_to_svg(self, pdf_path: str, output_path: str, **kwargs) -> str:
        """
        Convert a PDF file to SVG using pdf2svg.
        
        Args:
            pdf_path: Path to the input PDF file.
            output_path: Path to save the output SVG.
            **kwargs: Additional arguments for the conversion.
            
        Returns:
            Path to the generated SVG file.
        """
        try:
            subprocess.run([
                "pdf2svg",
                pdf_path,
                output_path
            ], check=True)
            return output_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "pdf2svg is required for PDF to SVG conversion. "
                "Please install it first:"
                "\n  On Ubuntu/Debian: sudo apt-get install pdf2svg"
                "\n  On macOS (Homebrew): brew install pdf2svg"
            )
    
    def extract_metadata(self) -> Dict[str, str]:
        """Extract metadata from the SVG file."""
        tree = ET.parse(self.input_path)
        root = tree.getroot()
        
        metadata = {}
        
        # Extract basic metadata elements
        for elem in root.xpath("//*[local-name()='metadata']//*"):
            if elem.text and elem.tag and '}' in elem.tag:
                # Handle namespaced elements
                tag = elem.tag.split('}')[-1]
                metadata[tag] = elem.text
        
        # Extract title and description
        title = root.find("{http://www.w3.org/2000/svg}title")
        if title is not None and title.text:
            metadata["title"] = title.text
            
        desc = root.find("{http://www.w3.org/2000/svg}desc")
        if desc is not None and desc.text:
            metadata["description"] = desc.text
        
        self.metadata = metadata
        return metadata
    
    def convert_format(
        self, 
        output_path: str, 
        output_format: str = "pdf",
        **kwargs
    ) -> str:
        """
        Convert the input file to the specified format.
        
        Args:
            output_path: Path to save the output file.
            output_format: Target format (pdf, svg, png, jpg).
            **kwargs: Additional arguments for the conversion.
            
        Returns:
            Path to the generated output file.
        """
        output_format = OutputFormat.from_string(output_format)
        output_path = os.path.abspath(output_path)
        
        if output_format == OutputFormat.PDF:
            return self.convert_svg_to_pdf(output_path, **kwargs)
        elif output_format == OutputFormat.SVG:
            # If input is already SVG, just copy it
            import shutil
            shutil.copy2(self.input_path, output_path)
            return output_path
        else:
            # For image formats, convert to PDF first, then to the target format
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
            
            try:
                # Convert to PDF first
                self.convert_svg_to_pdf(temp_pdf_path, **kwargs)
                
                # Then convert PDF to the target image format
                if output_format == OutputFormat.PNG:
                    self._convert_pdf_to_png(temp_pdf_path, output_path, **kwargs)
                elif output_format == OutputFormat.JPG:
                    self._convert_pdf_to_jpg(temp_pdf_path, output_path, **kwargs)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")
                
                return output_path
            finally:
                # Clean up temporary PDF
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
    
    def _convert_pdf_to_png(self, pdf_path: str, output_path: str, dpi: int = 300) -> str:
        """Convert PDF to PNG using pdftoppm."""
        try:
            # Create a temporary directory for the output
            temp_dir = tempfile.mkdtemp()
            temp_prefix = os.path.join(temp_dir, "page")
            
            # Convert PDF to PNG using pdftoppm
            subprocess.run([
                "pdftoppm",
                "-png",
                "-r", str(dpi),
                pdf_path,
                temp_prefix
            ], check=True)
            
            # Find the generated PNG file
            png_files = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])
            if not png_files:
                "\n  On macOS (Homebrew): brew install poppler"
            )
        finally:
            # Clean up temporary files
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
    
    def _convert_pdf_to_jpg(self, pdf_path: str, output_path: str, dpi: int = 300) -> str:
        """Convert PDF to JPG using pdftoppm."""
        # First convert to PNG, then to JPG
        temp_png = output_path + ".png"
        try:
            self._convert_pdf_to_png(pdf_path, temp_png, dpi)
            
            # Convert PNG to JPG using PIL
            from PIL import Image
            img = Image.open(temp_png)
            
            # Handle transparency by creating a white background
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Save as JPG
            img.convert('RGB').save(output_path, 'JPEG', quality=95)
            return output_path
            
        except ImportError:
            raise RuntimeError(
                "Pillow is required for JPG conversion. "
                "Please install it first:"
                "\n  pip install pillow"
            )
        finally:
            # Clean up temporary PNG
            if os.path.exists(temp_png):
                os.unlink(temp_png)
    
    def __del__(self):
        """Clean up temporary files."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert between SVG, PDF, and other formats"
    )
    
    # Input/output arguments
    parser.add_argument(
        "input_file",
        help="Input SVG or PDF file"
    )
    
    # Action arguments (mutually exclusive group)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--extract-pdf",
        metavar="OUTPUT_PDF",
        help="Extract embedded PDF from SVG and save to the specified file"
    )
    action_group.add_argument(
        "--to-pdf",
        metavar="OUTPUT_PDF",
        help="Convert the input file to PDF"
    )
    action_group.add_argument(
        "--to-svg",
        metavar="OUTPUT_SVG",
        help="Convert the input file to SVG"
    )
    action_group.add_argument(
        "--to-png",
        metavar="OUTPUT_PNG",
        help="Convert the input file to PNG"
    )
    action_group.add_argument(
        "--to-jpg",
        metavar="OUTPUT_JPG",
        help="Convert the input file to JPG"
    )
    action_group.add_argument(
        "--extract-metadata",
        action="store_true",
        help="Extract and display metadata from the input file"
    )
    
    # Additional options
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for image output (default: 300)"
    )
    
    return parser.parse_args()

def main():
    """Main function for command-line usage."""
    args = parse_arguments()
    
    try:
        converter = SVGConverter(args.input_file)
        
        if args.extract_pdf:
            # Extract embedded PDF from SVG
            output_path = converter.extract_embedded_pdf(args.extract_pdf)
            print(f"Extracted PDF saved to: {output_path}")
            
        elif args.extract_metadata:
            # Extract and display metadata
            metadata = converter.extract_metadata()
            print("Metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
                
        else:
            # Handle format conversions
            if args.to_pdf:
                output_path = converter.convert_format(args.to_pdf, "pdf", dpi=args.dpi)
                print(f"PDF saved to: {output_path}")
                
            elif args.to_svg:
                if args.input_file.lower().endswith('.svg'):
                    # Just copy the file if it's already an SVG
                    import shutil
                    shutil.copy2(args.input_file, args.to_svg)
                    print(f"SVG saved to: {args.to_svg}")
                else:
                    # Convert from PDF to SVG
                    converter.convert_pdf_to_svg(args.input_file, args.to_svg)
                    print(f"SVG saved to: {args.to_svg}")
                    
            elif args.to_png:
                output_path = converter.convert_format(args.to_png, "png", dpi=args.dpi)
                print(f"PNG saved to: {output_path}")
                
            elif args.to_jpg:
                output_path = converter.convert_format(args.to_jpg, "jpg", dpi=args.dpi)
                print(f"JPG saved to: {output_path}")
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
