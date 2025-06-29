"""
Command Line Interface for the Universal File Editor
"""

from typing import List, Optional, Type, Dict, Any
from pathlib import Path
import sys
import re
import argparse
import importlib
from xqr.core.editor import FileEditor
from xqr.state import get_current_file, set_current_file
from xqr.jquery_syntax import process_jquery_syntax
from xqr.commands import get_command_class


class CLI:
    """Command Line Interface for XQR"""

    def __init__(self):
        self.editor = None
        self._load_state()
        self.commands: Dict[str, Type[Any]] = {}
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

    Args:
        arg: Input string in format 'file.svg//xpath' or 'file.svg'

    Returns:
        Tuple of (file_path, xpath)
    """
    if '//' in arg:
        file_part, xpath = arg.split('//', 1)
        return Path(file_part), f'//{xpath}'
    return Path(arg), '//*'

def is_jquery_syntax(arg: str) -> bool:
    """Check if the argument is a jQuery-style command.
    
    Args:
        arg: Command argument to check
        
    Returns:
        bool: True if the argument is a jQuery-style command
    """
    return bool(re.match(r'^[^$]*\$\s*\(', arg))

def handle_direct_operation(args: List[str]) -> bool:
    """Handle direct file/xpath operations.

    Returns:
        bool: True if the operation was handled, False otherwise
    """
    if not args or args[0].startswith('-'):
        return False
        
    # Skip if the argument is a valid subcommand (except 'get' which we want to handle specially)
    valid_commands = ['load', 'query', 'set', 'save', 'create', 'ls', 'shell', 'examples', 'server']
    if args[0] in valid_commands:
        return False
        
    # Handle jQuery syntax
    if is_jquery_syntax(' '.join(args)):
        return False
        
    # Special handling for 'get' command
    if args[0] == 'get' and len(args) > 1:
        # Treat as direct operation with XPath
        xpath = args[1]
        file_path = get_current_file()
        if not file_path:
            print("❌ No file loaded. Use 'load' command first.")
            return True
            
        try:
            editor = FileEditor(file_path)
            result = editor.get_element_text(xpath)
            if result is not None:
                print(result)
            else:
                print(f"❌ Element not found: {xpath}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return True

    try:
        file_path, xpath = parse_file_xpath(args[0])
        value = args[1] if len(args) > 1 else None

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return True

        editor = FileEditor(file_path)

        # Handle delete operation (empty string as value)
        if value == '':
            success = editor.set_element_text(xpath, '')
            if success:
                editor.save()
                print(f"✅ Deleted content of {xpath} in {file_path}")
            else:
                print(f"❌ Element not found: {xpath}")
            return True

        # Handle update/create operation
        if value is not None:
            success = editor.set_element_text(xpath, value)
            if success:
                editor.save()
                print(f"✅ Updated {xpath} in {file_path}")
            else:
                print(f"❌ Could not update {xpath} (element not found)")
            return True

        # Handle read operation (no value provided)
        elements = editor.find_by_xpath(xpath)
        if not elements:
            print(f"❌ No elements found matching XPath: {xpath}")
        else:
            for i, element in enumerate(elements, 1):
                if hasattr(element, 'text') and element.text and element.text.strip():
                    print(f"{i}. {element.text.strip()}")
                elif hasattr(element, 'tag'):
                    print(f"{i}. <{element.tag}> (no text content)")
                else:
                    print(f"{i}. {str(element).strip()}")
        return True

    except Exception as e:
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