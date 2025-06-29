"""Server command for XQR CLI."""
import argparse
from typing import Optional

from xqr.core import FileEditor
from xqr.server import start_server
from .base import BaseCommand


class ServerCommand(BaseCommand):
    """Start a web server for the current file."""
    
    name = "server"
    help = "Start a web server for the current file"
    requires_editor = True
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--port', 
            type=int, 
            default=8000,
            help='Port to run the server on (default: 8000)'
        )
        parser.add_argument(
            '--host', 
            default='127.0.0.1',
            help='Host to bind to (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--debug', 
            action='store_true',
            help='Enable debug mode'
        )
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the server command."""
        if editor is None:
            return 1
            
        try:
            print(f"Starting server at http://{args.host}:{args.port}")
            print("Press Ctrl+C to stop")
            
            start_server(
                file_path=str(editor.file_path),
                host=args.host,
                port=args.port,
                debug=args.debug
            )
            return 0
            
        except KeyboardInterrupt:
            print("\nServer stopped")
            return 0
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return 1
