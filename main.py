import os
import yaml
import uuid
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, Tabs, Tab, ContentSwitcher, Button, Static, Input, Select
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual import on, events

# Importing your project-specific modules
from models import SessionConfig, LOCAL_VAULT, IDENTITY_FILE, get_all_profiles
from terminal import CyberTerminal
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Tabs, Tab, Button
from textual import on

# --- CUSTOM TAB WITH CLOSE BUTTON ---

class ClosableTab(Tab):
    """A Tab widget with close button (using Ctrl+W or middle-click to close)"""
    pass

# --- MODALS ---

class ConfirmModal(ModalScreen):
    """A reusable modal for alerts, help text, and delete confirmations."""
    def __init__(self, message: str, confirm_text="CONFIRM", cancel_text="ABORT"):
        super().__init__()
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-dialog"):
            yield Static("NEURAL LINK COMMAND", id="modal-title")
            yield Static(self.message, id="modal-msg")
            with Horizontal(classes="button-row"):
                yield Button(self.confirm_text, id="confirm", classes="btn-neuro-confirm")
                yield Button(self.cancel_text, id="cancel", classes="btn-neuro-cancel")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id == "confirm")

class SessionModal(ModalScreen):
    """Handles creating and editing sessions with smart folder selection."""
    def __init__(self, config=None, existing_folders=None):
        super().__init__()
        self.config = config
        folders = [("Create New...", "NEW")]
        if existing_folders:
            folders.extend([(f, f) for f in existing_folders if f != "Default"])
        self.folder_options = folders

    def compose(self) -> ComposeResult:
        profiles = get_all_profiles()
        is_edit = self.config is not None
        
        with Vertical(id="modal-dialog"):
            yield Static("NEURAL LINK CONFIG", id="modal-title")
            yield Static("Device Name", classes="field-label")
            yield Input(value=self.config.name if is_edit else "", id="name")
            yield Static("IP / Host", classes="field-label")
            yield Input(value=self.config.host if is_edit else "", id="host")
            
            yield Static("Target Folder", classes="field-label")
            yield Select(self.folder_options, id="folder_select", value=self.config.folder if is_edit else "NEW")
            yield Input(placeholder="Enter New Folder Name...", id="new_folder_input", 
                        value=self.config.folder if is_edit else "")
            
            yield Static("Identity Profile", classes="field-label")
            yield Select(profiles, id="profile", value=self.config.profile if is_edit else (profiles[0][0] if profiles else None))
            
            with Horizontal(classes="button-row"):
                yield Button("SAVE", id="save", classes="btn-neuro-confirm")
                yield Button("CANCEL", id="cancel", classes="btn-neuro-cancel")

    def on_mount(self):
        if self.query_one("#folder_select").value != "NEW":
            self.query_one("#new_folder_input").display = False

    @on(Select.Changed, "#folder_select")
    def toggle_folder_input(self, event):
        self.query_one("#new_folder_input").display = (event.value == "NEW")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save":
            folder_choice = self.query_one("#folder_select").value
            final_folder = self.query_one("#new_folder_input").value if folder_choice == "NEW" else folder_choice
            
            self.dismiss({
                "id": self.config.id if self.config else str(uuid.uuid4()),
                "name": self.query_one("#name").value,
                "host": self.query_one("#host").value,
                "folder": final_folder or "Default",
                "profile": self.query_one("#profile").value
            })
        else: self.dismiss(None)

class ManageIdentitiesModal(ModalScreen):
    """The Vault UI for managing usernames and passwords."""
    def compose(self) -> ComposeResult:
        with Vertical(id="modal-dialog"):
            yield Static("--- IDENTITY VAULT ---", id="modal-title")
            yield Static("Profile Name", classes="field-label")
            yield Input(placeholder="e.g. PRODUCTION", id="p_name")
            yield Static("Username", classes="field-label")
            yield Input(placeholder="admin", id="p_user")
            yield Static("Password", classes="field-label")
            yield Input(placeholder="••••••••", password=True, id="p_pass")
            with Horizontal(classes="button-row"):
                yield Button("SECURE", id="save_id", classes="btn-neuro-confirm")
                yield Button("CLOSE", id="cancel", classes="btn-neuro-cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save_id":
            name, user, pw = self.query_one("#p_name").value, self.query_one("#p_user").value, self.query_one("#p_pass").value
            if name and user and pw:
                data = {}
                if os.path.exists(IDENTITY_FILE):
                    with open(IDENTITY_FILE, "r") as f: data = yaml.safe_load(f) or {}
                data[name] = {"user": user, "pass": pw}
                with open(IDENTITY_FILE, "w") as f: yaml.dump(data, f)
                self.app.notify(f"Identity '{name}' Secured.")
                self.dismiss(True)
        else: self.dismiss(False)

# --- MAIN APP ---

class NeuroSSH(App):
    TITLE = "N Ξ U R O - S S H"
    CSS_PATH = "neuro.tcss"
    BINDINGS = [
        ("ctrl+n", "new_session", "New"),
        ("ctrl+i", "manage_ids", "Identity"),
        ("ctrl+w", "confirm_close_tab", "Kill Tab"),
        ("ctrl+s", "save_session", "Save"),
        ("q", "quit", "Quit"),
        ("ctrl+h", "focus_sidebar", "Sidebar"),
        ("ctrl+l", "focus_terminal", "Terminal"),
        ("e", "edit_node", "Edit"),
        ("d", "delete_node", "Delete"),
        ("f1", "help", "Help")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("NEURAL ARCHIVE", id="sidebar-title")
                yield Tree("DEVICES", id="session-tree")
            with Vertical(id="main-area"):
                yield Tabs(id="session-tabs")
                with ContentSwitcher(initial="splash", id="view-stack"):
                    yield Static(">> SYSTEM IDLE. SELECT A NODE TO INITIALIZE LINK.", id="splash")
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        """Global interceptor ensures navigation shortcuts always work."""
        if event.key == "ctrl+h":
            self.action_focus_sidebar()
            event.stop()
        elif event.key == "ctrl+l":
            self.action_focus_terminal()
            event.stop()

    def on_mount(self):
        self.load_sessions()
        self.query_one("#session-tree").focus()

    def get_existing_folders(self):
        folders = set()
        if os.path.exists(LOCAL_VAULT):
            with open(LOCAL_VAULT, "r") as f:
                data = yaml.safe_load(f) or []
                for s in data: folders.add(s.get('folder', 'Default'))
        return sorted(list(folders))

    def load_sessions(self):
        tree = self.query_one("#session-tree")
        tree.clear()
        tree.root.expand()
        if os.path.exists(LOCAL_VAULT):
            with open(LOCAL_VAULT, "r") as f:
                sessions = yaml.safe_load(f) or []
                for s in sessions:
                    conf = SessionConfig(**s)
                    folder_node = next((n for n in tree.root.children if str(n.label) == conf.folder), None)
                    if not folder_node:
                        folder_node = tree.root.add(conf.folder, expand=True)
                    folder_node.add_leaf(conf.name or conf.host, data=conf)

    @on(Tree.NodeSelected)
    def handle_selection(self, event):
        if event.node.data:
            self.open_session(event.node.data)

    def open_session(self, config):
        tabs, stack = self.query_one("#session-tabs"), self.query_one("#view-stack")
        tid = f"id_{config.id}"
        label = str(config.name or config.host)

        if tid not in [t.id for t in tabs.query("Tab")]:
            # Use ClosableTab instead of regular Tab
            tabs.add_tab(ClosableTab(label, id=tid))
            # Wrap terminal in scrollable container
            term = CyberTerminal(config)
            scroll_container = VerticalScroll(term, id=tid)
            stack.mount(scroll_container)

        tabs.active = tid
        stack.current = tid
        self.action_focus_terminal()

    @on(Tabs.TabActivated)
    def sync_tabs(self, event: Tabs.TabActivated):
        if event.tab and event.tab.id:
            self.query_one("#view-stack").current = event.tab.id
            self.action_focus_terminal()

    def action_focus_sidebar(self):
        self.query_one("#session-tree").focus()

    def action_focus_terminal(self):
        stack = self.query_one("#view-stack")
        if stack.current and stack.current != "splash":
            try:
                # Focus the terminal inside the scroll container
                scroll_container = self.query_one(f"#{stack.current}")
                terminal = scroll_container.query_one(CyberTerminal)
                terminal.focus()
            except:
                pass

    def action_new_session(self): 
        self.push_screen(SessionModal(existing_folders=self.get_existing_folders()), self.save_session_callback)

    def action_edit_node(self):
        node = self.query_one("#session-tree").cursor_node
        if node and node.data:
            self.push_screen(SessionModal(node.data, existing_folders=self.get_existing_folders()), self.save_session_callback)

    def action_confirm_close_tab(self):
        tabs = self.query_one("#session-tabs")
        if not tabs.active: return
        self.push_screen(ConfirmModal("Terminate this neural link?"), self.process_tab_closure)

    def close_tab(self, tab_id):
        """Close a tab and its SSH session (called by ClosableTab close button)"""
        try:
            tabs = self.query_one("#session-tabs")
            stack = self.query_one("#view-stack")

            # Get the scroll container (which holds the terminal)
            scroll_container = self.query_one(f"#{tab_id}")

            # Close the SSH connection
            terminal = scroll_container.query_one(CyberTerminal)
            if terminal:
                terminal.close_ssh()

            # Remove tab and container
            tabs.remove_tab(tab_id)
            scroll_container.remove()

            # Show splash if no tabs left
            if not tabs.active:
                stack.current = "splash"
        except:
            pass

    def process_tab_closure(self, confirmed):
        if not confirmed: return
        tabs = self.query_one("#session-tabs")
        tid = tabs.active
        if tid:
            self.close_tab(tid)

    def action_delete_node(self):
        node = self.query_one("#session-tree").cursor_node
        if not node or node == self.query_one("#session-tree").root: return
        self.push_screen(ConfirmModal(f"Purge '{node.label}'?"), lambda c: self.process_delete_confirmed(c, node))

    def process_delete_confirmed(self, confirmed, node):
        if not confirmed: return
        if not os.path.exists(LOCAL_VAULT): return
        with open(LOCAL_VAULT, "r") as f: sessions = yaml.safe_load(f) or []
        if node.data: sessions = [s for s in sessions if s.get('id') != node.data.id]
        else: sessions = [s for s in sessions if s.get('folder') != str(node.label)]
        with open(LOCAL_VAULT, "w") as f: yaml.dump(sessions, f)
        self.load_sessions()

    def save_session_callback(self, data):
        if not data: return
        sessions = []
        if os.path.exists(LOCAL_VAULT):
            with open(LOCAL_VAULT, "r") as f: sessions = yaml.safe_load(f) or []
        
        found = False
        for i, s in enumerate(sessions):
            if s.get('id') == data['id']:
                sessions[i] = data
                found = True
                break
        if not found: sessions.append(data)
            
        with open(LOCAL_VAULT, "w") as f: yaml.dump(sessions, f)
        self.load_sessions()

    def action_manage_ids(self):
        self.push_screen(ManageIdentitiesModal())

    def action_help(self):
        help_text = (
            "[b]NEURAL CONTROL INTERFACE[/b]\n\n"
            "[cyan]Navigation:[/cyan]\n"
            "CTRL+H: Focus Archive  |  CTRL+L: Focus Terminal\n\n"
            "[cyan]Management:[/cyan]\n"
            "CTRL+N: New Link  |  E: Edit  |  D: Delete\n"
            "CTRL+I: Identity Vault\n\n"
            "CTRL+W: Kill Tab  |  CTRL+S: Save Session\n"
            "Q: Shutdown"
        )
        self.push_screen(ConfirmModal(help_text, confirm_text="GOT IT", cancel_text="CLOSE"))

    def action_save_session(self):
        """Save the current terminal session to a text file"""
        try:
            stack = self.query_one("#view-stack")
            if not stack.current or stack.current == "splash":
                self.notify("[bold yellow]No active session to save[/bold yellow]")
                return

            scroll_container = self.query_one(f"#{stack.current}")
            terminal = scroll_container.query_one(CyberTerminal)

            filename = terminal.save_session()
            if filename:
                self.notify(f"[bold green]Session saved to:[/bold green] {filename}")
            else:
                self.notify("[bold red]Failed to save session[/bold red]")
        except Exception as e:
            self.notify(f"[bold red]Error saving session:[/bold red] {str(e)}")

if __name__ == "__main__":
    NeuroSSH().run()
