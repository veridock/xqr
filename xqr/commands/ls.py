"""Ls command for XQR CLI."""
import argparse
from typing import Optional, List

from xqr.core import FileEditor
from .base import BaseCommand


class LsCommand(BaseCommand):
    """List elements matching an XPath expression."""
    
    name = "ls"
    help = "List elements matching an XPath expression"
    requires_editor = True
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'xpath', 
            nargs='?', 
            default='//*',
            help='XPath expression to list elements (default: //*)'
        )
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the ls command."""
        if editor is None:
            return 1
            
        try:
            elements = editor.find_by_xpath(args.xpath)
            if not elements:
                print(f"❌ No elements found matching XPath: {args.xpath}")
                return 0
                
            print(f"Found {len(elements)} element(s) matching '{args.xpath}':\n")
            
            for i, element in enumerate(elements, 1):
                # Get element tag
                tag = getattr(element, 'tag', str(element))
                
                # Get element attributes if any
                attrs = ''
                if hasattr(element, 'attrib') and element.attrib:
                    attrs = ' ' + ' '.join(f'{k}="{v}"' for k, v in element.attrib.items())
                
                # Get element text preview
                text_preview = ''
                if hasattr(element, 'text') and element.text and element.text.strip():
                    text = element.text.strip()
                    preview = text[:50] + '...' if len(text) > 50 else text
                    text_preview = f" - '{preview}'"
                
                print(f"{i}. <{tag}{attrs}>{text_preview}")
                
                # If it's a text node with no children, show the full text
                if hasattr(element, 'tag') and element.tag.endswith('text') and not list(element):
                    print(f"   Text: {element.text}")
                
                # Show children count if any
                if hasattr(element, 'getchildren') and list(element):
                    children = list(element)
                    print(f"   Contains {len(children)} child elements")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error listing elements: {e}")
            return 1
