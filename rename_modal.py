class RenameModal(ModalScreen):
    def __init__(self, current_name):
        super().__init__()
        self.current_name = current_name

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-dialog"):
            yield Static(f"[bold #5f5faf]RENAME TARGET:[/bold #5f5faf] {self.current_name}", id="modal-title")
            yield Input(value=self.current_name, id="new-name-input")
            with Horizontal():
                yield Button("APPLY", variant="success", id="confirm")
                yield Button("CANCEL", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.dismiss(self.query_one("#new-name-input").value)
        else:
            self.dismiss(None)
