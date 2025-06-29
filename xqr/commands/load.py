"""Load command for XQR CLI."""
import argparse
from pathlib import Path
from typing import Optional

from xqr.core import FileEditor
from xqr.state import set_current_file
from .base import BaseCommand


class LoadCommand(BaseCommand):
    """Load a file for editing."""
    
    name = "load"
    help = "Load a file for editing"
    requires_editor = False
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('file', help='File to load')
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the load command."""
        file_path = Path(args.file).expanduser().resolve()
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
            
        try:
            # Create a new editor instance with the file
            new_editor = FileEditor(file_path)
            # Update the current file in state
            set_current_file(str(file_path))
            print(f"✅ Loaded {file_path} ({new_editor.file_type})")
            return 0
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return 1
