# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NeuroSSH is a terminal-based SSH session manager built with Python and the Textual TUI framework. It features a cyberpunk aesthetic and provides tabbed multi-session management with profile-based credential storage.

## Running the Application

```bash
# Primary launch method (handles dependencies)
python bootstrap.py

# Direct launch
python main.py
```

## Dependencies

Core dependencies are managed via `bootstrap.py`:
- **textual** - TUI framework for the application interface
- **paramiko** - SSH protocol implementation
- **pyte** - Terminal emulator for rendering SSH sessions
- **PyYAML** - Configuration file parsing
- **cryptography** - Credential encryption (via `vault.py`)

## Architecture

### Entry Point
`main.py` contains the `NeuroSSH` class (Textual App) with the main UI layout.

### Core Components

**main.py** - Main application logic
- `NeuroSSH` class: Root application with sidebar tree and tabbed terminal area
- `SessionModal`: Modal dialog for creating/editing session configurations
- Layout: Three-column design with Header, Sidebar (tree), Main Area (tabs + terminals), Footer

**terminal.py** - SSH terminal implementation
- `CyberTerminal`: Textual Static widget that embeds an SSH session
- Uses `paramiko` for SSH connections and `pyte` for terminal emulation
- Runs SSH connection in a daemon thread, polls for output every 50ms
- Handles keyboard input mapping (arrow keys, special keys) to SSH channel

**models.py** - Data models and persistence
- `SessionConfig`: Dataclass for session configuration (id, name, host, folder, profile)
- `LOCAL_VAULT`: Path to `sessions.yaml` (stores session configurations)
- `IDENTITY_FILE`: Path to `identities.yaml` (stores username/password profiles)
- `get_credentials()`: Retrieves credentials for a given profile name
- `get_all_profiles()`: Returns list of available profiles from identities.yaml

**vault.py** - Cryptographic utilities for credential encryption

**sequences.py** - Command sequence execution utilities

**neuro.tcss** - Textual CSS styling for the cyberpunk theme

### Data Flow

1. Sessions are loaded from `sessions.yaml` on startup and displayed in a Tree widget
2. Selecting a tree node creates a new tab with a `CyberTerminal` instance
3. `CyberTerminal` connects via SSH in a background thread using credentials from the configured profile
4. Terminal output renders via pyte Screen/Stream, updated on a 50ms interval
5. Keyboard input is captured and sent to the SSH channel

### Key Patterns

- **Threading:** SSH connections run in daemon threads to avoid blocking the UI
- **Polling:** Terminal output uses `set_interval(0.05, ...)` for periodic updates
- **YAML Persistence:** Both sessions and identities are stored as YAML files
- **Profile-based Credentials:** Sessions reference a profile name; credentials are looked up from `identities.yaml`
- **Tab Management:** Each session gets a unique tab ID (`id_{session_id}`); tabs and terminals are synced via ContentSwitcher

## File Storage

- `sessions.yaml` - Session configurations (name, host, folder, profile)
- `identities.yaml` - Credential profiles (username/password pairs)
- `vault.key` - Encryption key for the identity vault (gitignored)

## Keyboard Shortcuts

Defined in `NeuroSSH.BINDINGS`:
- `Ctrl+N` - New session modal
- `Ctrl+H` - Focus sidebar tree
- `Ctrl+L` - Focus active terminal
- `E` - Edit selected session
- `D` - Delete selected node
- `Q` - Quit application

## Security Notes

- `identities.yaml` and `vault.key` are in `.gitignore` for security
- Default credentials (admin/admin) are returned if no profile is found
- Consider implementing proper credential encryption when working with authentication
