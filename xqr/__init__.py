"""
XQR (XPath Query & Replace) - CLI tool for editing SVG, HTML, and XML files using XPath and CSS selectors
"""

from .core import FileEditor
from .server import FileEditorServer
from .cli import CLI

__version__ = "0.1.0"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"

__all__ = ["FileEditor", "FileEditorServer", "CLI"]