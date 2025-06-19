import datetime
from src.logger import logger
from textual.widget import Widget
from textual.widgets import Digits, Static, MarkdownViewer
from textual.app import ComposeResult
from datetime import datetime
from textual.reactive import reactive
from pytz import timezone
from textual.containers import HorizontalGroup, VerticalScroll

fake_data = """
- [ ] Faire Widget obsidian pour dashboard
- [ ] Relire cours apprentissage de formes

- [ ] [[cours wekeo]]

- [ ] apprendre les différents satellites disponibles et leurs spécificités et utilités

- [ ] ficher hydroponies et ses variantes

- [ ] lire grand papier et ficher

- [ ] lire 100 page ai book
"""


class ObsidianWidget(Widget):
    """A widget to display my obsidian related todo, planning and stats """

    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self) -> None:
        self.BORDER_TITLE = "Obsidian Dashboard"
        super().__init__()

    def on_click(self) -> None:
        """Handle click events to change the timezone."""
        pass

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(fake_data)
