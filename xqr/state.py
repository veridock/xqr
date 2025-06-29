"""
State management for the XQR CLI to maintain state between commands.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

# Default state directory follows XDG Base Directory Specification
STATE_DIR = Path.home() / ".local" / "state" / "xqr"
STATE_FILE = STATE_DIR / "state.json"


def ensure_state_dir() -> None:
    """Ensure the state directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def save_state(data: Dict[str, Any]) -> None:
    """Save state to file.
    
    Args:
        data: Dictionary of state data to save
    """
    ensure_state_dir()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def load_state() -> Dict[str, Any]:
    """Load state from file.

    Returns:
        Dictionary containing the saved state, or empty dict if no state exists
    """
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {}
                return data
    except (json.JSONDecodeError, OSError):
        # If there's any error reading the state file, return empty state
        pass
    return {}


def get_state(key: str, default: Any = None) -> Any:
    """Get a value from the state.

    Args:
        key: Key to retrieve
        default: Default value if key doesn't exist

    Returns:
        The value for the key, or default if not found
    """
    state = load_state()
    return state.get(key, default)


def set_state(key: str, value: Any) -> None:
    """Set a value in the state.

    Args:
        key: Key to set
        value: Value to store
    """
    state = load_state()
    state[key] = value
    save_state(state)


def clear_state() -> None:
    """Clear all state."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def get_current_file() -> Optional[str]:
    """Get the current file path from state.

    Returns:
        Path to the current file, or None if no file is loaded
    """
    result = get_state('current_file')
    return str(result) if result is not None else None


def set_current_file(file_path: Optional[str]) -> None:
    """Set the current file path in state.

    Args:
        file_path: Path to the current file, or None to clear
    """
    if file_path is None:
        set_state('current_file', None)
    else:
        # Store as absolute path for consistency
        set_state('current_file', str(Path(file_path).absolute()))
