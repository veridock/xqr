"""
HTTP Server for the XQR package.

This package provides an HTTP server for remote file editing functionality.
"""

from .server import start_server
from .handlers import FileEditorServer

__all__ = ['start_server', 'FileEditorServer']
