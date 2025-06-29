"""Examples command for XQR CLI."""
import argparse
from typing import Optional

from xqr.core import FileEditor, create_example_files
from .base import BaseCommand


class ExamplesCommand(BaseCommand):
    """Show usage examples."""
    
    name = "examples"
    help = "Show usage examples"
    requires_editor = False
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the examples command."""
        examples = """
XQR Usage Examples:
==================

1. Basic File Operations:
   ---------------------
   xqr load example.html          # Load an HTML file
   xqr ls                         # List all elements
   xqr query "//h1"               # Get content of all h1 elements
   xqr set "//h1" "New Title"     # Set content of h1 element
   xqr save                      # Save changes

2. XPath Queries:
   --------------
   xqr query "//div[@class='content']"  # Find divs with class 'content'
   xqr query "//a/@href"                # Get all link URLs
   xqr query "//*[contains(@class,'btn')]"  # Find elements with 'btn' in class

3. Modifying Content:
   ------------------
   xqr set "//p[1]" "New paragraph text"  # Update first paragraph
   xqr set "//img/@src" "new-image.jpg"    # Update image source
   xqr create "//div[@id='content']" "p" "New paragraph"  # Add new paragraph

4. Working with Attributes:
   -----------------------
   xqr set "//a[1]" "Click Here" --attribute href "https://example.com"
   xqr set "//button" "Submit" --attribute class "btn btn-primary"

5. Direct File Operations:
   -----------------------
   xqr example.html//h1                     # Get h1 content directly
   xqr example.html//h1 "New Title"         # Set h1 content directly
   xqr example.html//div[@id='main']//p     # Query with complex XPath

6. Interactive Shell:
   ------------------
   xqr shell         # Start interactive shell
   > load example.html
   > ls
   > query "//h1"
   > set "//h1" "New Title"
   > save
   > exit

7. Web Server:
   -----------
   xqr server --port 8000  # Start web server
   # Then open http://localhost:8000 in your browser

8. Creating Example Files:
   ----------------------
   xqr create-example html  # Create example.html
   xqr create-example xml   # Create example.xml
   xqr create-example svg   # Create example.svg

For more information, visit: https://github.com/yourusername/xqr
"""
        print(examples)
        return 0
