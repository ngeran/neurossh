import threading
import paramiko
import pyte
import socket
from textual.widgets import Static
from textual import events
from models import get_credentials

class CyberTerminal(Static):
    can_focus = True

    def __init__(self, config, **kwargs):
        super().__init__("INITIALIZING NEURAL LINK...", **kwargs)
        self.config = config
        # Virtual terminal emulator screen
        self.terminal_screen = pyte.Screen(120, 40)
        self.stream = pyte.Stream(self.terminal_screen)
        self.channel = None
        self.client = None
        
        # KEY MAP: Translates Textual keys to ANSI escape sequences for SSH
        self.KEY_MAP = {
            "up": "\x1b[A",
            "down": "\x1b[B",
            "right": "\x1b[C",
            "left": "\x1b[D",
            "insert": "\x1b[2~",
            "delete": "\x1b[3~",
            "home": "\x1b[H",
            "end": "\x1b[F",
            "pageup": "\x1b[5~",
            "pagedown": "\x1b[6~",
            "f1": "\x1bOP",
            "f2": "\x1bOQ",
            "f3": "\x1bOR",
            "f4": "\x1bOS",
            "f5": "\x1b[15~",
            "f6": "\x1b[17~",
            "f7": "\x1b[18~",
            "f8": "\x1b[19~",
            "f9": "\x1b[20~",
            "f10": "\x1b[21~",
            "f11": "\x1b[23~",
            "f12": "\x1b[24~",
        }

    def on_mount(self):
        # Refresh the UI every 50ms
        self.set_interval(0.05, self.update_terminal)
        threading.Thread(target=self.connect_ssh, daemon=True).start()

    def connect_ssh(self):
        creds = get_credentials(self.config.profile)
        if not creds:
            self.update("[bold red]ERROR:[/bold red] Identity profile not found.")
            return
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.config.host, 
                username=creds['user'], 
                password=creds['pass'], 
                timeout=10
            )
            # Request xterm to enable colors and proper key handling
            self.channel = self.client.invoke_shell(term='xterm', width=120, height=40)
            self.channel.setblocking(0)
        except Exception as e:
            self.update(f"[bold red]LINK FAILURE:[/bold red] {str(e)}")

    def update_terminal(self):
        if self.channel and self.channel.recv_ready():
            try:
                data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                self.stream.feed(data)
                self.refresh()
            except Exception:
                pass

    def render(self):
        # Join the virtual screen buffer into a single string for display
        return "\n".join(self.terminal_screen.display)

    def on_key(self, event: events.Key) -> None:
        # 1. Focus Escape Hatch (Priority)
        if event.key in ["ctrl+h", "ctrl+l"]:
            return 

        # 2. Check if the connection is alive
        if not self.channel or self.channel.closed:
            return

        try:
            # Handle mapped special keys (Arrows, F-keys, etc.)
            if event.key in self.KEY_MAP:
                self.channel.send(self.KEY_MAP[event.key])
            # Handle Enter
            elif event.key == "enter":
                self.channel.send("\r")
            # Handle Backspace
            elif event.key == "backspace":
                self.channel.send("\x7f")
            # Handle Tab
            elif event.key == "tab":
                self.channel.send("\t")
            # Handle Escape
            elif event.key == "escape":
                self.channel.send("\x1b")
            # Handle standard character input
            elif event.character:
                self.channel.send(event.character)
            
            # Prevent Textual from using the key for UI navigation
            event.stop()
        except (socket.error, EOFError):
            pass

    def on_unmount(self):
        """Clean up connection when the widget is removed."""
        if self.channel:
            self.channel.close()
        if self.client:
            self.client.close()
