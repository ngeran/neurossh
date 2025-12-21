# 🧠 NeuroSSH // Portable Neural Link

A high-performance, aesthetically driven SSH terminal manager built with Python and Textual. Designed for systems administrators who prefer a "stealth" cyberpunk aesthetic without sacrificing functional complexity.

## 🚀 Key Functionality

- **Session Archive:** Organize your connections into logical folders.
- **Identity Vault:** Securely store credentials and reuse them across multiple hosts.
- **Multi-Link Tabs:** Run dozens of concurrent SSH sessions with high-contrast tab visibility.
- **Session Protection:** Prompts to save configurations before closing a link.
- **Neural Folders:** Intelligent folder management—pick existing archives or spawn new ones dynamically.

## ⌨️ Command Matrix (Shortcuts)

### Navigation
| Key | Action |
|-----|--------|
| `Ctrl + H` | **Focus Sidebar** - Jump to the Neural Archive tree |
| `Ctrl + L` | **Focus Terminal** - Jump directly into the active session |
| `Tab` | Manual focus cycling between UI components |

### Session Management
| Key | Action |
|-----|--------|
| `Ctrl + N` | **New Session** - Initialize a new link config |
| `Ctrl + I` | **Identity Vault** - Manage usernames and passwords |
| `Ctrl + W` | **Kill Tab** - Terminate link with save-confirmation |
| `E` | **Edit** - Modify the configuration of the selected node |
| `D` | **Delete** - Wipe a session or an entire folder from the archive |
| `Q` | **Quit** - Immediate system shutdown |

## 🛠 Setup & Launch

1. **Environment:** Ensure you have the neural dependencies.
   ```bash
   pip install textual paramiko pyte pyyaml cryptography
