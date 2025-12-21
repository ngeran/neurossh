from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, DataTable
from textual.containers import Vertical

class HelpScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(id="modal-dialog"):
            yield Static("[bold #00ffff]NEURO_SSH // SYSTEM MANUAL[/bold #00ffff]\n")
            yield DataTable(id="help-table")
            yield Button("CLOSE MANUAL [ESC]", id="close-help", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one("#help-table")
        table.add_columns("Hotkey", "Action")
        table.add_rows([
            ("j / k", "Navigate Up/Down Tree"),
            ("Ctrl + H/L", "Focus Sidebar / Focus Term"),
            ("R", "Rename Selected Node/Folder"),
            ("Enter", "Connect to Node / Expand"),
            ("Ctrl + N", "New Neural Link"),
            ("Ctrl + B", "Broadcast Command to All"),
            ("Ctrl + S", "Save Session to Log"),
            ("Q", "Quit Application")
        ])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
