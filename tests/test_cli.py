"""Tests for the XQR CLI functionality."""
import os
import sys
from pathlib import Path
from unittest import TestCase, mock
from io import StringIO

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from xqr.cli import CLI, handle_direct_operation, parse_file_xpath
from xqr.core import FileEditor


class TestCLI(TestCase):
    """Test cases for the CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = CLI()
        self.test_file = Path(__file__).parent / "test_data" / "example.svg"
        self.test_file.parent.mkdir(exist_ok=True)
        
        # Create a test SVG file
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
            <text id="text1">Hello SVG</text>
            <text id="text2">New Text</text>
            <g id="group1">
                <rect id="rect1" width="50" height="50"/>
            </g>
        </svg>"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)

    def tearDown(self):
        """Clean up test files."""
        if self.test_file.exists():
            self.test_file.unlink()

    def test_parse_file_xpath(self):
        """Test parsing file and XPath from argument."""
        # Test with XPath
        file_path, xpath = parse_file_xpath("file.svg//path/to/element")
        self.assertEqual(str(file_path), "file.svg")
        self.assertEqual(xpath, "//path/to/element")
        
        # Test with just file
        file_path, xpath = parse_file_xpath("file.svg")
        self.assertEqual(str(file_path), "file.svg")
        self.assertEqual(xpath, "//*")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_handle_direct_operation_read(self, mock_stdout):
        """Test direct operation with read (no value)."""
        # Test with valid XPath
        args = [f"{self.test_file}//text[@id='text1']"]
        handle_direct_operation(args)
        self.assertIn("Hello SVG", mock_stdout.getvalue())
        
        # Test with invalid XPath
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        args = [f"{self.test_file}//invalid/xpath"]
        handle_direct_operation(args)
        self.assertIn("No elements found", mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_handle_direct_operation_write(self, mock_stdout):
        """Test direct operation with write (value provided)."""
        # Test update operation
        args = [f"{self.test_file}//text[@id='text1']", "Updated Text"]
        handle_direct_operation(args)
        self.assertIn("✅ Updated", mock_stdout.getvalue())
        
        # Verify the update
        editor = FileEditor(self.test_file)
        result = editor.get_element_text("//text[@id='text1']")
        self.assertEqual(result, "Updated Text")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_handle_direct_operation_delete(self, mock_stdout):
        """Test direct operation with delete (empty string as value)."""
        # Test delete operation
        args = [f"{self.test_file}//text[@id='text1']", ""]
        handle_direct_operation(args)
        self.assertIn("✅ Deleted content", mock_stdout.getvalue())
        
        # Verify the delete
        editor = FileEditor(self.test_file)
        result = editor.get_element_text("//text[@id='text1']")
        self.assertEqual(result, "")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_handle_direct_operation_get_command(self, mock_stdout):
        """Test direct operation with 'get' command."""
        # Test get command with XPath
        args = ["get", "//text[@id='text1']", str(self.test_file)]
        handle_direct_operation(args)
        self.assertIn("Hello SVG", mock_stdout.getvalue())

    def test_cli_load_command(self):
        """Test the load command."""
        with mock.patch('sys.argv', ['xqr', 'load', str(self.test_file)]):
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.cli.run()
                self.assertIn(f"✅ Loaded {self.test_file}", mock_stdout.getvalue())
                self.assertIsNotNone(self.cli.editor)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_cli_get_command(self, mock_stdout):
        """Test the get command."""
        # First load the file
        self.cli.editor = FileEditor(self.test_file)
        
        # Test get command
        with mock.patch('sys.argv', ['xqr', 'get', "//text[@id='text1']"]):
            self.cli.run()
            self.assertIn("Hello SVG", mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_cli_query_command(self, mock_stdout):
        """Test the query command."""
        # First load the file
        self.cli.editor = FileEditor(self.test_file)
        
        # Test query command
        with mock.patch('sys.argv', ['xqr', 'query', "//text[@id='text1']"]):
            self.cli.run()
            self.assertIn("Hello SVG", mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_cli_set_command(self, mock_stdout):
        """Test the set command."""
        # First load the file
        self.cli.editor = FileEditor(self.test_file)
        
        # Test set command
        with mock.patch('sys.argv', ['xqr', 'set', "//text[@id='text1']", "New Value"]):
            self.cli.run()
            self.assertIn("✅ Updated", mock_stdout.getvalue())
            
            # Verify the update
            self.assertEqual(self.cli.editor.get_element_text("//text[@id='text1']"), "New Value")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_cli_ls_command(self, mock_stdout):
        """Test the ls command."""
        # First load the file
        self.cli.editor = FileEditor(self.test_file)
        
        # Test ls command
        with mock.patch('sys.argv', ['xqr', 'ls', "//text"]):
            self.cli.run()
            output = mock_stdout.getvalue()
            self.assertIn("text", output)
            self.assertIn("text1", output)
            self.assertIn("text2", output)
