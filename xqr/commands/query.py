"""Query command for XQR CLI."""
import argparse
from typing import Optional

from xqr.core import FileEditor
from .base import BaseCommand


class QueryCommand(BaseCommand):
    """Query elements using XPath."""
    
    name = "query"
    help = "Query elements using XPath (alias: get)"
    requires_editor = True
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('xpath', help='XPath expression')
        parser.add_argument(
            '--type', 
            choices=['text', 'html', 'xml'], 
            default='text',
            help='Output type (default: text)'
        )
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the query command."""
        if editor is None:
            return 1
            
        try:
            if args.type == 'text':
                result = editor.get_element_text(args.xpath)
                if result is not None:
                    print(result)
                else:
                    print(f"❌ No text content found for XPath: {args.xpath}")
            elif args.type == 'html':
                result = editor.get_element_html(args.xpath)
                if result:
                    print(result)
                else:
                    print(f"❌ No HTML content found for XPath: {args.xpath}")
            elif args.type == 'xml':
                result = editor.get_element_xml(args.xpath)
                if result:
                    print(result)
                else:
                    print(f"❌ No XML content found for XPath: {args.xpath}")
            return 0
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return 1
