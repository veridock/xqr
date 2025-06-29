"""Shell command for XQR CLI."""
import argparse
import cmd
import sys
from typing import Optional, List, Dict, Any

from xqr.core import FileEditor
from xqr.state import get_current_file, set_current_file
from .base import BaseCommand


class XQRShell(cmd.Cmd):
    """Interactive shell for XQR."""
    
    prompt = 'xqr> '
    editor: Optional[FileEditor] = None
    
    def __init__(self, editor: Optional[FileEditor] = None, **kwargs):
        super().__init__(**kwargs)
        self.editor = editor
        self._load_commands()
    
    def _load_commands(self) -> None:
        """Load available commands dynamically."""
        from xqr.commands import get_command_class
        self.commands: Dict[str, Any] = {}
        
        # Import commands to register them
        import xqr.commands  # This will register commands via __init__.py
        
        # Get all registered commands
        for cmd_name in ['load', 'query', 'get', 'set', 'save', 'create', 'ls', 'examples', 'server']:
            try:
                self.commands[cmd_name] = get_command_class(cmd_name)
            except KeyError:
                pass
    
    def emptyline(self) -> bool:
        """Do nothing on empty input."""
        return False
    
    def default(self, line: str) -> None:
        """Handle unknown commands."""
        print(f"❌ Unknown command: {line}")
        print("Type 'help' for a list of commands.")
    
    def do_help(self, arg: str) -> None:
        """Show help for commands."""
        if arg:
            # Show help for specific command
            if arg in self.commands:
                cmd_class = self.commands[arg]
                print(f"\n{cmd_class.help}")
                print("\nUsage:")
                print(f"  {arg} [options]")
                return
            print(f"\nNo help available for '{arg}'")
            return
        
        # Show general help
        print("\nAvailable commands:")
        for name, cmd_class in sorted(self.commands.items()):
            print(f"  {name:<10} {cmd_class.help}")
        print("\nType 'help <command>' for help on a specific command.")
    
    def do_exit(self, _: str) -> bool:
        """Exit the shell."""
        print("Goodbye!")
        return True
    
    def do_clear(self, _: str) -> None:
        """Clear the screen."""
        print("\033c", end="")  # ANSI escape code to clear screen
    
    def do_load(self, arg: str) -> None:
        """Load a file."""
        self._execute_command('load', arg)
    
    def do_query(self, arg: str) -> None:
        """Query elements using XPath."""
        self._execute_command('query', arg)
    
    def do_get(self, arg: str) -> None:
        """Alias for query."""
        self._execute_command('query', arg)
    
    def do_set(self, arg: str) -> None:
        """Set element content or attributes."""
        self._execute_command('set', arg)
    
    def do_save(self, arg: str) -> None:
        """Save the current file."""
        self._execute_command('save', arg)
    
    def do_create(self, arg: str) -> None:
        """Create a new element."""
        self._execute_command('create', arg)
    
    def do_ls(self, arg: str) -> None:
        """List elements."""
        self._execute_command('ls', arg)
    
    def do_examples(self, arg: str) -> None:
        """Show usage examples."""
        self._execute_command('examples', arg)
    
    def do_server(self, arg: str) -> None:
        """Start the web server."""
        self._execute_command('server', arg)
    
    def _execute_command(self, cmd_name: str, args_str: str) -> None:
        """Execute a command with the given arguments."""
        try:
            cmd_class = self.commands[cmd_name]
            
            # Parse arguments
            parser = argparse.ArgumentParser(prog=cmd_name, add_help=False)
            cmd_class.add_arguments(parser)
            
            try:
                # Split args string into a list, handling quoted strings
                import shlex
                args_list = shlex.split(args_str) if args_str else []
                args = parser.parse_args(args_list)
            except SystemExit:
                # Don't exit on parse error
                return
            
            # Execute the command
            if cmd_class.requires_editor and not self.editor:
                print("❌ No file loaded. Use 'load' command first.")
                return
                
            cmd_class.execute(args, self.editor)
            
            # Update editor reference if we just loaded a file
            if cmd_name == 'load' and hasattr(args, 'file'):
                self.editor = FileEditor(args.file)
                
        except KeyError:
            print(f"❌ Unknown command: {cmd_name}")
        except Exception as e:
            print(f"❌ Error executing command: {e}")


class ShellCommand(BaseCommand):
    """Start an interactive shell."""
    
    name = "shell"
    help = "Start an interactive shell"
    requires_editor = False
    
    @classmethod
    def execute(cls, args: argparse.Namespace, editor: Optional[FileEditor] = None) -> int:
        """Execute the shell command."""
        print("XQR Interactive Shell")
        print("Type 'help' for a list of commands, 'exit' to quit\n")
        
        if editor:
            print(f"Currently loaded: {editor.file_path} ({editor.file_type})\n")
        
        try:
            shell = XQRShell(editor=editor)
            shell.cmdloop()
            return 0
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
            return 0
        except Exception as e:
            print(f"❌ Error in shell: {e}")
            return 1
