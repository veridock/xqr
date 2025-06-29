"""Set command for XQR CLI."""
import argparse
from typing import Optional

from xqr.core import FileEditor
from .base import BaseCommand


class SetCommand(BaseCommand):
    """Set element content or attributes using XPath."""
    
    name = "set"
    help = "Set element content or attributes using XPath"
    requires_editor = True
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('xpath', help='XPath expression to identify the element')
        parser.add_argument('value', help='Value to set (empty string to delete content)')
        parser.add_argument(
            '--attribute', 
            '-a',
            help='Attribute to set instead of element content'
        )
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the set command."""
        if editor is None:
            return 1
            
        try:
            if hasattr(args, 'attribute') and args.attribute:
                # Set attribute
                success = editor.set_element_attribute(args.xpath, args.attribute, args.value)
                action = f"set attribute '{args.attribute}' to '{args.value}'"
            else:
                # Set element content
                success = editor.set_element_text(args.xpath, args.value)
                action = f"set content to '{args.value}'"
                
            if success:
                print(f"✅ Updated {args.xpath} - {action}")
                return 0
            else:
                print(f"❌ Failed to update {args.xpath}")
                return 1
                
        except Exception as e:
            print(f"❌ Error updating element: {e}")
            return 1
