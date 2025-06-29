"""
Command Line Interface for the Universal File Editor
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from lxml import etree

from xqr.commands import get_command_class
from xqr.core.editor import FileEditor
from xqr.core.examples import create_example_files
from xqr.jquery_syntax import process_jquery_syntax
from xqr.server.server import start_server
from xqr.state import get_current_file, set_current_file

class CLI:
    """Command Line Interface for XQR"""

    def __init__(self):
        self.editor = None
        self._load_state()
        self.commands: Dict[str, Any] = {}
        self._load_commands()
    
    def _load_commands(self) -> None:
        """Load all available commands."""
        # Import all command modules to register them
        from xqr import commands  # noqa: F401
        
        # Initialize commands
        self.commands = {}
        for cmd_name in [
            'load', 'query', 'get', 'set', 'save', 
            'create', 'ls', 'shell', 'examples', 'server'
        ]:
            try:
                self.commands[cmd_name] = get_command_class(cmd_name)
            except KeyError:
                print(f"⚠️  Failed to load command: {cmd_name}")
        
    def _load_state(self) -> None:
        """Load state and initialize editor if a file was previously loaded."""
        current_file = get_current_file()
        if current_file and Path(current_file).exists():
            try:
                self.editor = FileEditor(current_file)
            except Exception as e:
                print(f"⚠️  Could not load previous file {current_file}: {e}")
                set_current_file(None)
        elif current_file:  # File doesn't exist anymore
            set_current_file(None)

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description='XQR - XPath Query & Replace',
            add_help=False  # We'll handle help manually
        )
        
        # Add global arguments
        parser.add_argument(
            '--help', '-h', 
            action='store_true',
            help='Show this help message and exit'
        )
        
        # Add version
        parser.add_argument(
            '--version', '-v',
            action='store_true',
            help='Show version and exit'
        )
        
        subparsers = parser.add_subparsers(
            dest='command', 
            help='Command to run',
            metavar='command'
        )
        
        # Add commands to the parser
        for cmd_name, cmd_class in self.commands.items():
            # Skip aliases (they'll be handled by the main command)
            if cmd_name in ['get']:  # 'get' is an alias for 'query'
                continue
                
            cmd_parser = subparsers.add_parser(
                cmd_name,
                help=cmd_class.help,
                add_help=False
            )
            cmd_class.add_arguments(cmd_parser)
            cmd_parser.set_defaults(func=cmd_class.execute)
        
        return parser
        get_parser = subparsers.add_parser('get', help='Alias for query')
        get_parser.add_argument('xpath', help='XPath expression')
        get_parser.set_defaults(func=self._handle_query)

        # Set command
        set_parser = subparsers.add_parser('set', help='Set element content or attributes')
        set_parser.add_argument('xpath', help='XPath expression')
        set_parser.add_argument('value', help='Value to set')
        set_parser.add_argument(
            '--type', 
            choices=['text', 'attribute'], 
            default='text',
            help='Type of value to set'
        )
        set_parser.add_argument('--attr', help='Attribute name (required if type=attribute)')
        set_parser.set_defaults(func=self._handle_set)

        # Save command
        save_parser = subparsers.add_parser('save', help='Save changes to file')
        save_parser.add_argument('--output', '-o', help='Output file (default: overwrite input file)')
        save_parser.set_defaults(func=self._handle_save)

        # Create command
        create_parser = subparsers.add_parser('create', help='Create a new file')
        create_parser.add_argument('file', help='File to create')
        create_parser.add_argument('--type', choices=['xml', 'html', 'svg'], 
                                help='File type (default: auto-detect from extension)')
        create_parser.set_defaults(func=self._handle_create)

        # List command
        list_parser = subparsers.add_parser(
            'ls', 
            help='List available XPath expressions'
        )
        list_parser.add_argument(
            'file', 
            nargs='?', 
            help='File to list elements from (default: current file)'
        )
        list_parser.add_argument(
            '--pattern', 
            default='//*', 
            help='XPath pattern to filter elements (default: //*)'
        )
        list_parser.add_argument(
            '--with-ids', 
            action='store_true', 
            help='Only show elements with ID attributes'
        )
        list_parser.set_defaults(func=self._handle_list)

        # Shell command
        subparsers.add_parser('shell', help='Start interactive shell').set_defaults(
            func=self._handle_shell
        )

        # Examples command
        subparsers.add_parser('examples', help='Create example files').set_defaults(
            func=self._handle_examples
        )

        # Server command
        server_parser = subparsers.add_parser('server', help='Start web server')
        server_parser.add_argument('--host', default='0.0.0.0', 
                                 help='Host to bind to (default: 0.0.0.0)')
        server_parser.add_argument('--port', type=int, default=8080, 
                                 help='Port to listen on (default: 8080)')
        server_parser.set_defaults(func=self._handle_server)

        return parser

    def _print_help(self, parser: argparse.ArgumentParser) -> None:
        """Print help message."""
        print("XQR - XPath Query & Replace")
        print("Usage: xqr [OPTIONS] COMMAND [ARGS]...\n")
        print("Options:")
        print("  -h, --help     Show this message and exit")
        print("  -v, --version  Show version and exit\n")
        print("Commands:")
        
        # Get command help text
        for cmd_name, cmd_class in sorted(self.commands.items()):
            # Skip aliases
            if cmd_name in ['get']:  # 'get' is an alias for 'query'
                continue
            print(f"  {cmd_name:<10} {cmd_class.help}")
        
        print("\nRun 'xqr COMMAND --help' for more information on a command.")
        print("\nExamples:")
        print("  xqr load example.html           # Load a file")
        print("  xqr query \"//h1\"               # Query elements")
        print("  xqr example.html//h1           # Query directly from file")
        print("  xqr shell                      # Start interactive shell")

    def run(self) -> int:
        """Run the CLI.
        
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        parser = self._create_parser()
        
        # Parse known args first to handle help/version flags
        args, remaining = parser.parse_known_args()
        
        # Handle help flag
        if getattr(args, 'help', False):
            self._print_help(parser)
            return 0
            
        # Handle version flag
        if getattr(args, 'version', False):
            from xqr import __version__
            print(f"XQR v{__version__}")
            return 0
        
        # Handle direct file/xpath operation
        if remaining and not args.command:
            if handle_direct_operation(remaining):
                return 0
        
        # Handle jQuery syntax
        if remaining and any('$(' in arg for arg in remaining):
            command = ' '.join(remaining)
            if is_jquery_syntax(command):
                process_jquery_syntax(command, self.editor)
                return 0
        
        # If we have a command, execute it
        if hasattr(args, 'func'):
            # For commands that require an editor, pass it along
            if args.command in self.commands and self.commands[args.command].requires_editor:
                if not self.editor:
                    print("❌ No file loaded. Use 'load' command first.")
                    return 1
                return args.func(args, self.editor) or 0
            else:
                return args.func(args, self.editor) or 0
        
        # No command and no direct operation, show help
        self._print_help(parser)
        return 0

    def _handle_load(self, args: argparse.Namespace) -> None:
        """Handle load command.
        
        Args:
            args: Command line arguments
        """
        self.editor = FileEditor(args.file)
        set_current_file(args.file)
        print(f"✅ Loaded {args.file} ({self.editor.file_type})")

    def _handle_query(self, args: argparse.Namespace) -> None:
        """Handle query command.
        
        Args:
            args: Command line arguments
        """
        if not self.editor:
            print("❌ No file loaded. Use 'load' command first.")
            return

        # Default to 'text' if type is not provided
        result_type = getattr(args, 'type', 'text')
        
        try:
            if result_type == 'text':
                result = self.editor.get_element_text(args.xpath)
                if result is not None:
                    print(result)
                else:
                    print(f"❌ No text content found for XPath: {args.xpath}")
            elif result_type == 'html':
                result = self.editor.get_element_html(args.xpath)
                if result:
                    print(result)
                else:
                    print(f"❌ No HTML content found for XPath: {args.xpath}")
            elif result_type == 'xml':
                result = self.editor.get_element_xml(args.xpath)
                if result:
                    print(result)
                else:
                    print(f"❌ No XML content found for XPath: {args.xpath}")
        except Exception as e:
            print(f"❌ Error executing query: {e}")

    def _handle_set(self, args: argparse.Namespace) -> None:
        """Handle set command.
        
        Args:
            args: Command line arguments
        """
        if not self.editor:
            print("❌ No file loaded. Use 'load' command first.")
            return

        success = self.editor.set_element_text(args.xpath, args.value)
        if success:
            print("✅ Element updated")
        else:
            print("❌ Element not found")

    def _handle_save(self, args: argparse.Namespace) -> None:
        """Handle save command.
        
        Args:
            args: Command line arguments
        """
        if not self.editor:
            print("❌ No file loaded. Use 'load' command first.")
            return

        success = self.editor.save(args.output)
        if success:
            save_path = args.output or self.editor.file_path
            print(f"✅ Saved to {save_path}")
        else:
            print("❌ Save failed")

    def _handle_shell(self, _args: argparse.Namespace) -> None:
        """Handle shell command.
        
        Args:
            _args: Command line arguments (unused)
        """
        print("Starting interactive shell. Type 'exit' or 'quit' to exit.")
        print(f"Current file: {self.editor.file_path if self.editor else 'None'}")
        print("Available commands: load, query, set, save, exit")

        while True:
            try:
                command = input("xqr> ").strip()
                if not command:
                    continue
                if command.lower() in ('exit', 'quit'):
                    break
                self._execute_shell_command(command)
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to exit the shell")
            except Exception as e:
                print(f"Error: {e}")

    def _execute_shell_command(self, command: str) -> None:
        """Execute a shell command.
        
        Args:
            command: Command to execute
        """
        parts = command.split()
        if not parts:
            return

        command = parts[0].lower()

        if command == 'load' and len(parts) >= 2:
            file_path = ' '.join(parts[1:])  # Handle filenames with spaces
            try:
                self.editor = FileEditor(file_path)
                print(f"✅ Loaded {file_path} ({self.editor.file_type})")
            except Exception as e:
                print(f"❌ Error loading file: {e}")

        elif command == 'query' and len(parts) >= 2:
            if not self.editor:
                print("❌ No file loaded. Use 'load <file>' first.")
                return

            xpath = ' '.join(parts[1:])
            try:
                result = self.editor.get_element_text(xpath)
                if result:
                    print(f"📄 Text: {result}")
                else:
                    print("📄 No text content found (element may exist but be empty)")
            except Exception as e:
                print(f"❌ Query error: {e}")

        elif command == 'set' and len(parts) >= 3:
            if not self.editor:
                print("❌ No file loaded")
                return

            xpath = parts[1]
            value = ' '.join(parts[2:])
            try:
                success = self.editor.set_element_text(xpath, value)
                if success:
                    print("✅ Text updated")
                else:
                    print("❌ Element not found")
            except Exception as e:
                print(f"❌ Update error: {e}")

        elif command == 'save':
            if not self.editor:
                print("❌ No file loaded")
                return

            output_file = parts[1] if len(parts) > 1 else None
            try:
                success = self.editor.save(output_file)
                if success:
                    save_path = output_file or self.editor.file_path
                    print(f"✅ Saved to {save_path}")
                else:
                    print("❌ Save failed")
            except Exception as e:
                print(f"❌ Save error: {e}")

        elif command == 'info':
            if not self.editor:
                print("❌ No file loaded")
                return

            print(f"📁 File: {self.editor.file_path}")
            print(f"📄 Type: {self.editor.file_type}")

        else:
            print("❌ Unknown command or missing arguments")
            print("💡 Type 'help' for available commands")

    def _handle_server(self, args: argparse.Namespace) -> None:
        """Handle server command.
        
        Args:
            args: Command line arguments
        """
        start_server(args.host, args.port)

    def _handle_examples(self, _args: argparse.Namespace) -> None:
        """Handle examples command.
        
        Args:
            _args: Command line arguments (unused)
        """
        try:
            create_example_files()
            print("✅ Created example files: example.svg, example.xml, example.html")
        except Exception as e:
            print(f"❌ Could not create example files: {e}")

    def _handle_create(self, args) -> int:
        """Handle the create command.
        
        Args:
            args: Command line arguments
            
        Returns:
            int: 0 on success, 1 on error
        """
        try:
            # Create an empty file with the specified type
            file_path = Path(args.file)
            file_type = args.type or file_path.suffix[1:].lower()
            
            if not file_type:
                print("❌ Could not determine file type. Please specify with --type")
                return 1
                
            if file_path.exists():
                print(f"❌ File already exists: {file_path}")
                return 1
                
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create basic content based on file type
            if file_type == 'svg':
                content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#f0f0f0"/>
  <text x="50" y="50" text-anchor="middle" fill="black">New SVG</text>
</svg>'''
            elif file_type == 'html':
                content = '''<!DOCTYPE html>
<html>
<head>
  <title>New Document</title>
</head>
<body>
  <h1>New HTML Document</h1>
</body>
</html>'''
            elif file_type == 'xml':
                content = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
  <element>New XML Document</element>
</root>'''
            else:
                content = ''
                
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Created new {file_type.upper()} file: {file_path}")
            return 0
            
        except Exception as e:
            print(f"❌ Error creating file: {e}")
            return 1

    def _handle_list(self, args) -> int:
        """Handle the list command.
        
        Args:
            args: Command line arguments
            
        Returns:
            int: 0 on success, 1 on error
        """
        file_path = args.file or get_current_file()
        if not file_path:
            print("❌ No file specified and no file is currently loaded")
            print("Usage: xqr ls [FILE] [--pattern XPATH] [--with-ids]")
            return 1

        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return 1

        try:
            # Create a temporary editor instance for listing
            editor = FileEditor(file_path)
            elements = editor.list_elements(args.pattern)

            if not elements:
                print(f"No elements found matching pattern: {args.pattern}")
                return 0

            print(f"\nAvailable elements in {file_path}:")
            print("-" * 80)

            for elem in elements:
                tag = elem['tag']
                attrs = elem['attributes']

                # Skip elements without IDs if --with-ids is specified
                if args.with_ids and 'id' not in attrs:
                    continue

                # Create a more readable XPath expression
                if 'id' in attrs:
                    xpath = f"//{tag}[@id='{attrs['id']}']"
                # For SVG elements with xlink:href, create a specific XPath
                elif '{http://www.w3.org/1999/xlink}href' in attrs:
                    href = attrs['{http://www.w3.org/1999/xlink}href']
                    xpath = f"//{tag}[@xlink:href='{href}']"
                else:
                    xpath = elem['path']

                # Print the XPath with element info
                print(f"xqr {file_path}//{xpath}")

                # Print attributes if available
                if attrs:
                    attr_str = ', '.join(
                        f"{k}={v}" for k, v in attrs.items() 
                        if not k.startswith('{')
                    )
                    print(f"  Attributes: {attr_str}")

                # Print text content if available
                if elem['text']:
                    text = elem['text']
                    text_preview = text[:50] + ('...' if len(text) > 50 else '')
                    print(f"  Text: {text_preview}")
                print()

            print(f"\nFound {len(elements)} elements")
            print("Tip: Use 'xqr ls --pattern' to filter elements by XPath")
            print("     Use 'xqr ls --with-ids' to only show elements with ID attributes")

            # If no elements were shown due to --with-ids filter
            if args.with_ids and not any('id' in e['attributes'] for e in elements):
                print("\nNo elements with ID attributes found. "
                      "Try without --with-ids to see all elements.")

            return 0

        except Exception as e:
            print(f"❌ Error listing elements: {e}")
            return 1

    def execute_command(self, args):
        """Execute a CLI command"""
        try:
            if args.command == 'load':
                self.editor = FileEditor(args.file)
                set_current_file(args.file)
                print(f"✅ Loaded {args.file} ({self.editor.file_type})")
                return
                
            if not self.editor:
                current_file = get_current_file()
                if current_file and Path(current_file).exists():
                    try:
                        self.editor = FileEditor(current_file)
                        print(f"ℹ️  Using previously loaded file: {current_file}")
                    except Exception as e:
                        print(f"❌ Could not load previous file {current_file}: {e}")
                        set_current_file(None)
                        return
                else:
                    print("❌ No file loaded. Use 'load' command first.")
                    return

            if args.command == 'query':

                if args.type == 'text':
                    result = self.editor.get_element_text(args.xpath)
                    print(f"Text: {result}")
                elif args.type == 'attribute':
                    if not args.attr:
                        print("❌ --attr required for attribute queries")
                        return
                    result = self.editor.get_element_attribute(args.xpath, args.attr)
                    print(f"Attribute {args.attr}: {result}")

            elif args.command == 'set':
                if not self.editor:
                    print("❌ No file loaded. Use 'load' command first.")
                    return

                if args.type == 'text':
                    success = self.editor.set_element_text(args.xpath, args.value)
                elif args.type == 'attribute':
                    if not args.attr:
                        print("❌ --attr required for attribute updates")
                        return
                    success = self.editor.set_element_attribute(args.xpath, args.attr, args.value)
                else:
                    print("❌ Invalid type. Use 'text' or 'attribute'")
                    return

                if success:
                    print("✅ Element updated")
                else:
                    print("❌ Element not found")

            elif args.command == 'list':
                if not self.editor:
                    print("❌ No file loaded. Use 'load' command first.")
                    return

                try:
                    elements = self.editor.list_elements(args.xpath)
                    if not elements:
                        print("No elements found matching the XPath")
                        return

                    print(f"Found {len(elements)} elements:")
                    for i, elem in enumerate(elements[:20]):  # limit to 20 for readability
                        print(f"\n[{i+1}] Path: {elem.get('path', 'N/A')}")
                        print(f"    Tag: {elem.get('tag', 'N/A')}")
                        text = elem.get('text', '').strip()
                        if text:
                            print(f"    Text: {repr(text[:100])}")  # limit text length
                        attrs = elem.get('attributes', {})
                        if attrs:
                            print(f"    Attributes: {attrs}")

                    if len(elements) > 20:
                        print(f"\n... and {len(elements) - 20} more elements")

                except Exception as e:
                    print(f"❌ Error listing elements: {e}")

            elif args.command == 'save':
                if not self.editor:
                    print("❌ No file loaded. Use 'load' command first.")
                    return

                success = self.editor.save(args.output)
                if success:
                    save_path = args.output or self.editor.file_path
                    print(f"✅ File saved to {save_path}")
                else:
                    print("❌ Save failed")

            else:
                print(f"❌ Unknown command: {args.command}")

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


def parse_file_xpath(arg: str) -> Tuple[Path, str]:
    """Parse file path and XPath from argument in format 'file.svg//xpath'.

    Supports various formats:
    - file.svg//xpath
    - file.xml//xpath
    - file.json//xpath
    - file.svg (returns //* for the entire document)
    - file.svg//*[contains(@class, 'example')] (handles attribute predicates)
    - file.svg//tag[@id='value'] (handles attribute predicates with values)

    Args:
        arg: Input string containing file path and optional XPath

    Returns:
        Tuple of (file_path, xpath)
    """
    # Handle empty or invalid input
    if not arg or not isinstance(arg, str):
        raise ValueError("Invalid input: argument must be a non-empty string")

    # Default to matching all elements if no XPath is provided
    default_xpath = '//*'
    
    # Check if the argument contains a double slash (//) which indicates an XPath
    if '//' in arg:
        # Split on the first occurrence of // to separate file path from XPath
        file_part, xpath = arg.split('//', 1)
        
        # Handle attribute selection (e.g., @class)
        if xpath.startswith('@'):
            # For attributes, we need to modify the XPath to select the parent element
            # and append the attribute selection
            xpath = f'//*[@{xpath[1:]}]'
        # Clean up the XPath - ensure it starts with // if it's a path (not a function call)
        elif not xpath.startswith(('//', 'contains(', 'starts-with(', 'text()')):
            xpath = f'//{xpath}'
            
        # Handle special cases for SVG files
        file_path = Path(file_part)
        if file_path.suffix.lower() in ('.svg', '.svgx'):
            # Don't modify the XPath here - let prepare_xpath_for_svg handle it
            # Just ensure it's a valid XPath
            if not xpath.startswith(('.', '//', '@', '(', 'contains', 'starts-with', 'text()', 'name()')):
                xpath = f'//{xpath}'
        
        return file_path, xpath
    
    # If no XPath provided, return the default XPath
    return Path(arg), default_xpath

def is_jquery_syntax(arg: str) -> bool:
    """Check if the argument is in jQuery syntax.

    Args:
        arg: Input string to check
        
    Returns:
        bool: True if the input is in jQuery syntax, False otherwise
    """
    return bool(re.match(r'^[^$]*\$\s*\(', arg))

def handle_direct_operation(args: List[str]) -> bool:
    """Handle direct file/xpath operations.
    
    This function processes direct operations in the format:
    - file.xml//xpath [value]  # Read or update element
    - file.xml//@attr [value]  # Read or update attribute
    - file.xml//tag[@attr='value']  # Query with attribute predicate
    - file.xml//*[contains(@class, 'value')]  # Query with function
    
    Returns:
        bool: True if the operation was handled, False otherwise
    """
    print(f"DEBUG: handle_direct_operation initial args: {args}", file=sys.stderr)
    
    if not args:
        print("DEBUG: No arguments provided", file=sys.stderr)
        return False
        
    # Special case for --version and --help
    if '--version' in args:
        print(f"XQR {__version__}")
        return True
        
    if '--help' in args or '-h' in args:
        print_help()
        return True
    
    # Check if we have the --all flag
    update_all = '--all' in args
    if update_all:
        args.remove('--all')
        print(f"DEBUG: Found --all flag, removed from args. New args: {args}", file=sys.stderr)
    else:
        print("DEBUG: No --all flag found", file=sys.stderr)
    
    try:
        # Parse the file path and XPath
        file_path, xpath = parse_file_xpath(args[0])
        value = args[1] if len(args) > 1 else None
        
        print(f"DEBUG: Parsed file_path={file_path}, xpath={xpath}, value={value}", file=sys.stderr)
        print(f"DEBUG: update_all={update_all}", file=sys.stderr)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return True
        
        # Create editor instance
        editor = FileEditor(file_path)
        
        # Check if we're dealing with an SVG file
        is_svg = str(file_path).lower().endswith(('.svg', '.svgz'))
        
        # Check if this is an attribute operation (e.g., //element/@attr or @attr)
        attribute_name = None
        original_xpath = xpath  # Save original XPath for debugging
        
        # Handle attribute selection in XPath (e.g., //item/@class)
        if '@' in xpath and '/@' in xpath and not xpath.endswith(']'):
            # Extract the base XPath and attribute name
            base_xpath, attr_part = xpath.rsplit('/@', 1)
            attribute_name = attr_part.split('/')[0].split(']')[0]  # Get just the attribute name
            xpath = base_xpath or '//*'  # Default to all elements if no specific path given
            print(f"DEBUG: Extracted attribute name: {attribute_name} from XPath", file=sys.stderr)
            print(f"DEBUG: Modified XPath from {original_xpath} to {xpath} for attribute {attribute_name}", file=sys.stderr)
        # Handle simple attribute reference (e.g., @class)
        elif xpath.startswith('@'):
            attribute_name = xpath[1:].split('/')[0].split(']')[0]
            xpath = '//*'  # Default to all elements
            print(f"DEBUG: Using simple attribute reference: {attribute_name}", file=sys.stderr)

        # Handle delete operation (empty string as value)
        if value == '':
            elements = editor.find_by_xpath(xpath)
            if not elements:
                print(f"❌ Element not found: {xpath}")
                return True
                
            # Delete each matching element's content or attribute
            for element in elements:
                if attribute_name:
                    if hasattr(element, 'attrib') and attribute_name in element.attrib:
                        del element.attrib[attribute_name]
                else:
                    if hasattr(element, 'text'):
                        element.text = ''
                    if hasattr(element, 'tail') and element.tail:
                        element.tail = ''
            
            editor.save()
            if attribute_name:
                print(f"✅ Deleted @{attribute_name} from {xpath} in {file_path}")
            else:
                print(f"✅ Deleted content of {xpath} in {file_path}")
            return True

        # Handle update operation
        if value is not None:
            print(f"DEBUG: Handling update operation with value: {value}", file=sys.stderr)
            print(f"DEBUG: Original XPath: {xpath}", file=sys.stderr)
            
            # Handle attribute updates via @attribute syntax
            if xpath.endswith('/@class'):
                # For attribute updates, we want to modify the element, not the attribute directly
                xpath = xpath[:-7]  # Remove '/@class' from the end
                print(f"DEBUG: Modified XPath for attribute update: {xpath}", file=sys.stderr)
                
            elements = editor.find_by_xpath(xpath)
            print(f"DEBUG: Found {len(elements)} elements matching xpath: {xpath}", file=sys.stderr)
            if not elements:
                print(f"❌ Element not found: {xpath}", file=sys.stderr)
                return True
            
            # Check if we should update all matching elements or just the first one
            elements_to_update = elements if update_all else [elements[0]]
            print(f"DEBUG: update_all={update_all}, updating {len(elements_to_update)} of {len(elements)} elements", file=sys.stderr)
            print(f"DEBUG: Elements to update: {[etree.tostring(e) for e in elements_to_update]}", file=sys.stderr)
            
            # Update each matching element
            for element in elements_to_update:
                # Handle attribute updates (attr=value or via @attr in XPath)
                if attribute_name or ('=' in value and not xpath.endswith(']')):
                    attr = attribute_name
                    val = value
                    
                    # If not using @attr syntax, parse from value (e.g., 'class=new-class')
                    if not attr and '=' in value:
                        try:
                            attr, val = value.split('=', 1)
                            attr = attr.strip()
                            val = val.strip('\'"').strip()
                        except ValueError:
                            print(f"❌ Invalid attribute format: {value}. Expected 'attr=value'")
                            return False
                    
                    # If we still don't have an attribute name, we can't proceed
                    if not attr:
                        print(f"❌ No attribute specified for update in XPath: {original_xpath}", file=sys.stderr)
                        return False
                    
                    print(f"DEBUG: Updating attribute - element: {etree.tostring(element)[:100]}..., attr: {attr}, val: {val}", file=sys.stderr)
                    print(f"DEBUG: Element attributes before update: {getattr(element, 'attrib', {})}", file=sys.stderr)
                    
                    # Ensure we have an attribute to update
                    if not attr:
                        print("❌ No attribute specified for update", file=sys.stderr)
                        return False
                    
                    # Handle different element types and update mechanisms
                    updated = False
                    
                    # Method 1: Use set() method if available (lxml.etree)
                    if hasattr(element, 'set'):
                        print("DEBUG: Using element.set() method", file=sys.stderr)
                        element.set(attr, val)
                        updated = True
                    # Method 2: Use attrib dictionary
                    elif hasattr(element, 'attrib') and isinstance(element.attrib, dict):
                        print("DEBUG: Using element.attrib dictionary", file=sys.stderr)
                        element.attrib[attr] = val
                        updated = True
                    # Method 3: Try direct attribute access as last resort
                    elif hasattr(element, attr):
                        print("DEBUG: Using direct attribute access", file=sys.stderr)
                        setattr(element, attr, val)
                        updated = True
                        
                    if not updated:
                        print(f"❌ Could not update attribute {attr}: element doesn't support attribute updates", file=sys.stderr)
                        return False
                        
                    print(f"DEBUG: Element attributes after update: {getattr(element, 'attrib', {})}", file=sys.stderr)
                        
                    print(f"DEBUG: Element attributes after update: {getattr(element, 'attrib', {})}", file=sys.stderr)
                # Handle text content updates
                elif hasattr(element, 'text'):
                    element.text = value
                    
            # If we're in interactive mode, show a hint about --all
            if len(elements) > 1 and not update_all and sys.stdin.isatty():
                print(f"ℹ️  Only updated first of {len(elements)} matches. Use --all to update all.")
            
            print(f"DEBUG: Saving changes to {file_path}", file=sys.stderr)
            editor.save()
            
            if attribute_name:
                msg = f"✅ Updated @{attribute_name} in {xpath} to '{value}' in {file_path}"
            else:
                msg = f"✅ Updated {xpath} in {file_path}"
            print(f"DEBUG: {msg}", file=sys.stderr)
            print(msg)
            return True

        # Handle read operation (no value provided)
        elements = editor.find_by_xpath(xpath)
        if not elements:
            print(f"❌ No elements found matching XPath: {xpath}")
        else:
            for i, element in enumerate(elements, 1):
                # Handle attributes directly if this is an attribute query
                if attribute_name and hasattr(element, 'attrib') and attribute_name in element.attrib:
                    print(f"{i}. {element.attrib[attribute_name]}")
                    continue
                    
                # Handle elements with tags (SVG/XML)
                if hasattr(element, 'tag'):
                    tag = element.tag.split('}')[-1]  # Remove namespace if present
                    attrs = ' '.join(f'{k}="{v}"' for k, v in element.attrib.items())
                    attrs = f' {attrs}' if attrs else ''
                    
                    # Get text content if any
                    text = ''
                    if element.text and element.text.strip():
                        text = f" - {element.text.strip()}"
                    
                    print(f"{i}. <{tag}{attrs}>{text}</{tag}>")
                # Handle text nodes
                elif hasattr(element, 'text'):
                    print(f"{i}. {element.text}")
                # Fallback to string representation
                else:
                    print(f"{i}. {element}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        return False
        print(f"❌ Error: {e}")
        return True

def main() -> None:
    """Main entry point for CLI."""
    # Check for direct file/xpath operation first
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        if handle_direct_operation(sys.argv[1:]):
            return
            
        # Check for jQuery syntax in the command
        command = ' '.join(sys.argv[1:])
        if '$(' in command:
            # Extract file path before $
            parts = command.split('$', 1)
            file_path = parts[0].strip()
            jquery_cmd = '$' + parts[1].strip()
            
            if not file_path:
                print("❌ No file specified")
                sys.exit(1)
                
            try:
                editor = FileEditor(file_path)
                result = process_jquery_syntax(jquery_cmd, editor)
                print(result)
                editor.save()  # Save changes
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error processing jQuery command: {e}")
                sys.exit(1)

    # Check if we have example files
    example_files = ['example.svg', 'example.xml', 'example.html']
    if not any(Path(f).exists() for f in example_files):
        print("📁 No example files found. Creating them...")
        try:
            create_example_files()
            print("✅ Created example files: example.svg, example.xml, example.html")
        except Exception as e:
            print(f"⚠️  Could not create example files: {e}")

    # Run standard CLI
    cli = CLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()