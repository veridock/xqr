"""Base command class for XQR CLI commands."""
from typing import Any, Optional
import argparse
from pathlib import Path

from xqr.core import FileEditor


class BaseCommand:
    """Base class for all XQR commands.
    
    Subclasses should implement the execute() method and set the following
    class attributes:
    - name: str - The command name (used in CLI)
    - help: str - Help text for the command
    - requires_editor: bool - Whether the command requires a loaded file
    """
    
    name: str = ""
    help: str = ""
    requires_editor: bool = False
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments to the parser.
        
        Args:
            parser: Argument parser to add arguments to
        """
        pass
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the command.
        
        Args:
            args: Parsed command line arguments
            editor: Optional FileEditor instance if a file is loaded
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    @classmethod
    def validate_args(cls, args: argparse.Namespace) -> bool:
        """Validate command arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            bool: True if arguments are valid, False otherwise
        """
        return True
    
    @classmethod
    def check_editor_required(cls, editor: Optional[FileEditor]) -> bool:
        """Check if the command can be executed with the current editor state.
        
        Args:
            editor: Current FileEditor instance or None if no file is loaded
            
        Returns:
            bool: True if the command can be executed, False otherwise
        """
        if cls.requires_editor and editor is None:
            print("❌ No file loaded. Use 'load' command first.")
            return False
        return True
