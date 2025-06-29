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
        
    def test_selective_update_single_element(self):
        """Test that updates only affect the first matching element by default."""
        # Create a test file with multiple matching elements
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <item>Original 1</item>
                <item>Original 2</item>
                <item>Original 3</item>
            </root>""")
        
        # Update only the first matching element
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Combine file path and XPath with // separator as expected by handle_direct_operation
            result = handle_direct_operation([f"{self.test_file}//item", "Updated Value"])
            self.assertTrue(result)
            
        # Verify file content - only first element should be updated
        editor = FileEditor(self.test_file)
        elements = editor.find_by_xpath("//item")
        self.assertEqual(len(elements), 3, "Should find 3 item elements")
        self.assertEqual(elements[0].text, "Updated Value", "First element should be updated")
        self.assertEqual(elements[1].text, "Original 2", "Second element should remain unchanged")
        self.assertEqual(elements[2].text, "Original 3", "Third element should remain unchanged")
        
    def test_selective_update_all_elements(self):
        """Test that --all flag updates all matching elements."""
        # Create a test file with multiple matching elements
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <item>Original 1</item>
                <item>Original 2</item>
                <item>Original 3</item>
            </root>""")
        
        # Save original stderr and patch it to capture debug output
        old_stderr = sys.stderr
        debug_output = StringIO()
        sys.stderr = debug_output
        
        try:
            # Mock stdout for the function call
            with mock.patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                # Call the function with --all flag
                result = handle_direct_operation(["--all", f"{self.test_file}//item", "Updated Value"])
                
                # Get the debug output
                debug_output_str = debug_output.getvalue()
                print("\n=== DEBUG OUTPUT ===")
                print(debug_output_str)
                print("===================\n")
                
                # Get the stdout output
                stdout_output = mock_stdout.getvalue()
                print("\n=== STDOUT ===")
                print(stdout_output)
                print("==============\n")
                
                # Verify the function returned True
                self.assertTrue(result, f"handle_direct_operation should return True but returned {result}")
                
                # Verify the file was actually updated
                editor = FileEditor(self.test_file)
                elements = editor.find_by_xpath("//item")
                self.assertEqual(len(elements), 3, "Should find 3 item elements")
                self.assertEqual(elements[0].text, "Updated Value", "First element should be updated")
                self.assertEqual(elements[1].text, "Updated Value", "Second element should be updated")
                self.assertEqual(elements[2].text, "Updated Value", "Third element should be updated")
                
        finally:
            # Restore stderr
            sys.stderr = old_stderr
            
        # Verify file content - all elements should be updated
        editor = FileEditor(self.test_file)
        elements = editor.find_by_xpath("//item")
        self.assertEqual(len(elements), 3, "Should find 3 item elements")
        self.assertEqual(elements[0].text, "Updated Value", "First element should be updated")
        self.assertEqual(elements[1].text, "Updated Value", "Second element should be updated")
        self.assertEqual(elements[2].text, "Updated Value", "Third element should be updated")
        
    def test_selective_update_attribute(self):
        """Test selective update with attributes."""
        # Create a test file with multiple matching elements
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <item id="1" class="test">Item 1</item>
                <item id="2" class="test">Item 2</item>
                <item id="3" class="test">Item 3</item>
            </root>""")
        
        # Update class attribute on first matching element only
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Combine file path and XPath with // separator for attribute update
            result = handle_direct_operation([f"{self.test_file}//item[@class='test']/@class", "updated"])
            self.assertTrue(result)
            
        # Verify file content - only first element's class should be updated
        editor = FileEditor(self.test_file)
        elements = editor.find_by_xpath("//item")
        self.assertEqual(len(elements), 3, "Should find 3 item elements")
        self.assertEqual(elements[0].get("class"), "updated", "First element's class should be updated")
        self.assertEqual(elements[1].get("class"), "test", "Second element's class should remain unchanged")
        self.assertEqual(elements[2].get("class"), "test", "Third element's class should remain unchanged")

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
        output = mock_stdout.getvalue()
        # Check for expected output format
        self.assertIn("No file loaded", output)  # Should fail to load file in this context
        
        # Test with file path in the argument
        args = [f"{self.test_file}//text[@id='text1']"]
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        handle_direct_operation(args)
        output = mock_stdout.getvalue()
        self.assertIn("Hello SVG", output)

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
            # Check for the text content in the output
            self.assertIn("Hello SVG", mock_stdout.getvalue())
            
        # Test get command with type argument
        with mock.patch('sys.argv', ['xqr', 'get', "--type", "text", "//text[@id='text1']"]):
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
            self.cli.run()
            self.assertIn("Hello SVG", mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_cli_query_command(self, mock_stdout):
        """Test the query command."""
        # First load the file
        self.cli.editor = FileEditor(self.test_file)
        
        # Test query command with text type (default)
        with mock.patch('sys.argv', ['xqr', 'query', "//text[@id='text1']"]):
            self.cli.run()
            self.assertIn("Hello SVG", mock_stdout.getvalue())
            
        # Test query command with html type
        with mock.patch('sys.argv', ['xqr', 'query', '--type', 'html', "//text[@id='text1']"]):
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
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
            output = mock_stdout.getvalue()
            self.assertIn("Element updated", output)
            
            # Verify the update
            self.assertEqual(self.cli.editor.get_element_text("//text[@id='text1']"), "New Value")

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_cli_ls_command(self, mock_stdout):
        """Test the ls command."""
        # First load the file
        self.cli.editor = FileEditor(self.test_file)
        
        # Test ls command with XPath
        with mock.patch('sys.argv', ['xqr', 'ls', "//text"]):
            self.cli.run()
            output = mock_stdout.getvalue()
            # Check for expected output format
            self.assertIn("text", output)
            self.assertIn("text1", output)
            self.assertIn("text2", output)
            
        # Test ls command without XPath (should list all elements)
        with mock.patch('sys.argv', ['xqr', 'ls']):
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
            self.cli.run()
            output = mock_stdout.getvalue()
            self.assertIn("svg", output)
