from itertools import cycle
from pytz import timezone
from textual.reactive import reactive
from datetime import datetime
from textual.app import ComposeResult
from textual.widgets import Digits, Label, Static
from textual.containers import Center
from datetime import datetime
from dashboard.logger import logger
from textual.widget import Widget

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


def get_flag(timezone: str) -> str:
    """Get the flag emoji for a timezone."""
    if timezone == "Europe/Paris":
        return "🇫🇷"
    elif timezone == "Europe/London":
        return "🇬🇧"
    else:
        return "🌍"


class TimeWidget(Widget):
    """A widget to display the current time in a specified timezone.
    It allows the user to click and change the timezone displayed.
    The time updates are done reactively in the main app that sets the time."""

    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self, timezone: str, small_screen: bool = False):
        self.timezone = timezone
        self.small_screen = small_screen
        if not small_screen:
            self.BORDER_TITLE = title(self.timezone)
        super().__init__()

    def on_click(self) -> None:
        """Handle click events to change the timezone."""
        logger.debug(
            f"Clicked on TimeWidget, changing timezone from {self.timezone}")
        self.timezone = next(timezone_cycle)
        if not self.small_screen:
            self.border_title = title(self.timezone)
        self.watch_time(self.time)

    def compose(self) -> ComposeResult:
        if self.small_screen:
            # Minimal format for small screens
            yield Static("Loading...", classes="center")
        else:
            # Regular format
            with Center():
                yield Label("Date", classes="center")
                yield Digits("test", classes="center")

    def watch_time(self, time: datetime) -> None:
        localized_time = time.astimezone(timezone(self.timezone))

        if self.small_screen:
            # Minimal format: "HH:MM DD/MM" with flag
            flag = get_flag(self.timezone)
            minimal_time = localized_time.strftime("%H:%M %d/%m")
            self.query_one(Static).update(f"{flag} {minimal_time}")
        else:
            # Regular format
            self.query_one(Digits).update(localized_time.strftime("%H:%M:%S"))
            self.query_one(Label).update(
                localized_time.strftime("%A, %d %B %Y"))
