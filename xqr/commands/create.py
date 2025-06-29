"""Create command for XQR CLI."""
import argparse
from pathlib import Path
from typing import Optional

from xqr.core import FileEditor
from .base import BaseCommand


class CreateCommand(BaseCommand):
    """Create a new element using XPath."""
    
    name = "create"
    help = "Create a new element using XPath"
    requires_editor = True
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('xpath', help='XPath expression to identify the parent element')
        parser.add_argument('tag', help='Tag name of the new element')
        parser.add_argument('--content', default='', help='Content for the new element')
        parser.add_argument('--attribute', action='append', nargs=2, metavar=('NAME', 'VALUE'),
                          help='Attribute to set on the new element (can be used multiple times)')
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the create command."""
        if editor is None:
            return 1
            
        try:
            attributes = dict(args.attribute) if hasattr(args, 'attribute') and args.attribute else {}
            
            success = editor.create_element(
                xpath=args.xpath,
                tag=args.tag,
                content=args.content,
                attributes=attributes
            )
            
            if success:
                print(f"✅ Created new {args.tag} element under {args.xpath}")
                return 0
            else:
                print(f"❌ Failed to create element at {args.xpath}")
                return 1
                
        except Exception as e:
            print(f"❌ Error creating element: {e}")
            return 1
