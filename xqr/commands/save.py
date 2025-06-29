"""Save command for XQR CLI."""
import argparse
from typing import Optional

from xqr.core import FileEditor
from .base import BaseCommand


class SaveCommand(BaseCommand):
    """Save the current file."""
    
    name = "save"
    help = "Save the current file"
    requires_editor = True
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--output', 
            '-o',
            help='Output file path (default: overwrite current file)'
        )
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the save command."""
        if editor is None:
            return 1
            
        try:
            output_path = getattr(args, 'output', None)
            if output_path:
                editor.save(output_path)
                print(f"✅ Saved to {output_path}")
            else:
                editor.save()
                print(f"✅ Saved to {editor.file_path}")
            return 0
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return 1
