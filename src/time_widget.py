import datetime
from .logger import logger
from textual.widget import Widget
from textual.widgets import Digits, Label
from textual.app import ComposeResult
from datetime import datetime
from textual.reactive import reactive
from pytz import timezone
from itertools import cycle
from textual.containers import HorizontalGroup, VerticalScroll

timezone_cycle = cycle([
    "Europe/Paris",
    "Europe/London"
])


def title(timezone: str) -> str:
    """Generate a title based on the timezone."""
    if timezone == "Europe/Paris":
        return "Time in France 🇫🇷"
    elif timezone == "Europe/London":
        return "Time in UK 🇬🇧"
    else:
        return f"Time in {timezone}"


class TimeWidget(Widget):
    """A widget to display the current time in a specified timezone.
    It allows the user to click and change the timezone displayed.
    The time updates are done reactively in the main app that sets the time."""

    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self, timezone: str) -> None:
        self.timezone = timezone
        self.BORDER_TITLE = title(self.timezone)
        super().__init__()

    def on_click(self) -> None:
        """Handle click events to change the timezone."""
        logger.debug(
            f"Clicked on TimeWidget, changing timezone from {self.timezone}")
        self.timezone = next(timezone_cycle)
        self.query_one(Label).update(title(self.timezone))
        self.watch_time(self.time)

    def compose(self) -> ComposeResult:
        yield Digits("test")

    def watch_time(self, time: datetime) -> None:
        localized_time = time.astimezone(timezone(self.timezone))
        self.query_one(Digits).update(localized_time.strftime("%H:%M:%S"))
