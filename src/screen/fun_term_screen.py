
from textual.app import ComposeResult, Screen
from textual.widgets import Footer
from src.logger import logger
from textual.reactive import reactive
from datetime import datetime
from textual_terminal import Terminal


class FunTermScreen(Screen):
    time: reactive[datetime] = reactive(datetime.now)

    def compose(self) -> ComposeResult:
        yield Terminal(command="htop", id="terminal_htop")
        yield Footer()

    def on_ready(self) -> None:
        terminal_htop: Terminal = self.query_one(
            "#terminal_htop")
        terminal_htop.start()

    def update_time(self) -> None:
        self.time = datetime.now()

    def on_mount(self) -> None:
        self.update_time()
        self.set_interval(1, self.update_time)
