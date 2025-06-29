"""
XQR (XPath Query & Replace) - CLI tool for editing SVG, HTML, and XML files
using XPath and CSS selectors.
"""

from .core.editor import FileEditor
from .core.examples import create_example_files
from .server.server import FileEditorServer, start_server
from .cli import CLI

__version__ = "0.1.2"  # Updated version for server refactoring
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"

# Define public API
__all__ = [
    "FileEditor",
    "FileEditorServer",
    "CLI",
    "create_example_files",
    "start_server"
]
