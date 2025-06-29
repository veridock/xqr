"""
Command modules for the XQR CLI.

This package contains command implementations for the XQR command-line interface.
Each command is implemented as a separate module that defines a Command class.
"""

from typing import Dict, Type
from .base import BaseCommand

# Import all command classes here
from .load import LoadCommand
from .query import QueryCommand
from .set import SetCommand
from .save import SaveCommand
from .create import CreateCommand
from .ls import LsCommand
from .shell import ShellCommand
from .examples import ExamplesCommand
from .server import ServerCommand

# Map of command names to their corresponding command classes
COMMANDS: Dict[str, Type[BaseCommand]] = {
    'load': LoadCommand,
    'query': QueryCommand,
    'get': QueryCommand,  # Alias for query
    'set': SetCommand,
    'save': SaveCommand,
    'create': CreateCommand,
    'ls': LsCommand,
    'shell': ShellCommand,
    'examples': ExamplesCommand,
    'server': ServerCommand,
}

def get_command_class(command_name: str) -> Type[BaseCommand]:
    """Get the command class for the given command name.
    
    Args:
        command_name: Name of the command
        
    Returns:
        The command class
        
    Raises:
        KeyError: If the command is not found
    """
    return COMMANDS[command_name]
