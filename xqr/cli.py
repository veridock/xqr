"""
Command Line Interface for the Universal File Editor
"""

import argparse
import sys
from pathlib import Path

from .core import FileEditor
from .server import start_server
from .examples import create_example_files


class CLI:
    """Interfejs CLI"""

    def __init__(self):
        self.editor = None

    def run(self):
        """Uruchom CLI"""
        parser = argparse.ArgumentParser(description='Universal File Editor CLI')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Load command
        load_parser = subparsers.add_parser('load', help='Load file')
        load_parser.add_argument('file', help='File path')

        # Query command
        query_parser = subparsers.add_parser('query', help='Query elements')
        query_parser.add_argument('xpath', help='XPath expression')
        query_parser.add_argument('--type', choices=['text', 'attribute'], default='text')
        query_parser.add_argument('--attr', help='Attribute name')

        # Set command
        set_parser = subparsers.add_parser('set', help='Set element value')
        set_parser.add_argument('xpath', help='XPath expression')
        set_parser.add_argument('value', help='New value')
        set_parser.add_argument('--type', choices=['text', 'attribute'], default='text')
        set_parser.add_argument('--attr', help='Attribute name')

        # List command
        list_parser = subparsers.add_parser('list', help='List elements')
        list_parser.add_argument('--xpath', default='//*', help='XPath filter')

        # Save command
        save_parser = subparsers.add_parser('save', help='Save file')
        save_parser.add_argument('--output', help='Output file path')

        # Server command
        server_parser = subparsers.add_parser('server', help='Start HTTP server')
        server_parser.add_argument('--port', type=int, default=8080, help='Server port')

        # Shell command
        shell_parser = subparsers.add_parser('shell', help='Interactive shell')

        # Examples command
        examples_parser = subparsers.add_parser('examples', help='Create example files')

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        if args.command == 'server':
            start_server(args.port)
        elif args.command == 'shell':
            self.start_shell()
        elif args.command == 'examples':
            create_example_files()
        else:
            self.execute_command(args)

    def execute_command(self, args):
        """Wykonaj komendę CLI"""
        try:
            if args.command == 'load':
                self.editor = FileEditor(args.file)
                print(f"✅ Loaded {args.file} ({self.editor.file_type})")

            elif args.command == 'query':
                if not self.editor:
                    print("❌ No file loaded. Use 'load' command first.")
                    return

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

    def start_shell(self):
        """Uruchom interaktywny shell"""
        print("🚀 Interactive File Editor Shell")
        print("Commands:")
        print("  load <file>           - Load a file")
        print("  query <xpath>         - Query elements with XPath")
        print("  set <xpath> <value>   - Set element text")
        print("  setattr <xpath> <attr> <value> - Set element attribute")
        print("  list [xpath]          - List elements (optional XPath filter)")
        print("  save [file]           - Save changes (optional output file)")
        print("  info                  - Show current file info")
        print("  help                  - Show this help")
        print("  exit                  - Exit shell")
        print()

        while True:
            try:
                command_line = input("📝 > ").strip()
                if not command_line:
                    continue

                if command_line in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break

                if command_line in ['help', '?']:
                    print("\nAvailable commands:")
                    print("  load <file>")
                    print("  query <xpath>")
                    print("  set <xpath> <value>")
                    print("  setattr <xpath> <attr> <value>")
                    print("  list [xpath]")
                    print("  save [file]")
                    print("  info")
                    print("  help")
                    print("  exit")
                    continue

                parts = command_line.split()
                if not parts:
                    continue

                command = parts[0].lower()

                if command == 'load' and len(parts) >= 2:
                    file_path = ' '.join(parts[1:])  # Handle filenames with spaces
                    try:
                        self.editor = FileEditor(file_path)
                        print(f"✅ Loaded {file_path} ({self.editor.file_type})")
                        if hasattr(self.editor, 'find_by_xpath'):
                            try:
                                element_count = len(self.editor.find_by_xpath("//*"))
                                print(f"   📊 Found {element_count} elements")
                            except:
                                pass
                    except Exception as e:
                        print(f"❌ Error loading file: {e}")

                elif command == 'query' and len(parts) >= 2:
                    if not self.editor:
                        print("❌ No file loaded. Use 'load <file>' first.")
                        continue

                    xpath = ' '.join(parts[1:])
                    try:
                        result = self.editor.get_element_text(xpath)
                        if result:
                            print(f"📄 Text: {result}")
                        else:
                            print("📄 No text content found (element may exist but be empty)")
                            # Try to show if element exists
                            elements = self.editor.find_by_xpath(xpath)
                            if elements:
                                elem = elements[0]
                                if hasattr(elem, 'tag'):
                                    print(f"   Element found: <{elem.tag}>")
                                if hasattr(elem, 'attrib'):
                                    attrs = dict(elem.attrib)
                                    if attrs:
                                        print(f"   Attributes: {attrs}")
                            else:
                                print("   No elements found")
                    except Exception as e:
                        print(f"❌ Query error: {e}")

                elif command == 'set' and len(parts) >= 3:
                    if not self.editor:
                        print("❌ No file loaded")
                        continue

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

                elif command == 'setattr' and len(parts) >= 4:
                    if not self.editor:
                        print("❌ No file loaded")
                        continue

                    xpath = parts[1]
                    attr_name = parts[2]
                    attr_value = ' '.join(parts[3:])
                    try:
                        success = self.editor.set_element_attribute(xpath, attr_name, attr_value)
                        if success:
                            print(f"✅ Attribute {attr_name} updated")
                        else:
                            print("❌ Element not found")
                    except Exception as e:
                        print(f"❌ Update error: {e}")

                elif command == 'list':
                    if not self.editor:
                        print("❌ No file loaded")
                        continue

                    xpath = parts[1] if len(parts) > 1 else "//*"
                    try:
                        elements = self.editor.list_elements(xpath)
                        if not elements:
                            print("No elements found")
                            continue

                        print(f"📋 Found {len(elements)} elements:")
                        for i, elem in enumerate(elements[:10]):  # limit to 10 in shell
                            tag = elem.get('tag', 'unknown')
                            text = elem.get('text', '').strip()
                            text_preview = f": {repr(text[:30])}" if text else ""
                            print(f"  {i+1}. <{tag}>{text_preview}")

                        if len(elements) > 10:
                            print(f"  ... and {len(elements) - 10} more")
                    except Exception as e:
                        print(f"❌ List error: {e}")

                elif command == 'save':
                    if not self.editor:
                        print("❌ No file loaded")
                        continue

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
                        continue

                    print(f"📁 File: {self.editor.file_path}")
                    print(f"📄 Type: {self.editor.file_type}")
                    if hasattr(self.editor, 'find_by_xpath'):
                        try:
                            element_count = len(self.editor.find_by_xpath("//*"))
                            print(f"📊 Elements: {element_count}")
                        except:
                            print("📊 Elements: Unable to count")

                else:
                    print("❌ Unknown command or missing arguments")
                    print("💡 Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


def main():
    """Main entry point for CLI"""
    # Sprawdź czy mamy przykładowe pliki
    example_files = ['example.svg', 'example.xml', 'example.html']
    if not any(Path(f).exists() for f in example_files):
        print("📁 No example files found. Creating them...")
        try:
            create_example_files()
        except Exception as e:
            print(f"⚠️  Could not create example files: {e}")

    # Uruchom CLI
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