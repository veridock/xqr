"""
Core functionality for the XQR package.

This package contains the main FileEditor class and related utilities for
parsing and manipulating XML/HTML/SVG files.
"""

from .editor import FileEditor
from .examples import create_example_files

__all__ = ['FileEditor', 'create_example_files']
