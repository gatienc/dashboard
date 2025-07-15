from dashboard.utils import get_city, get_weather_report
from textual.app import ComposeResult, Screen
from textual.containers import Horizontal
from textual.widgets import Footer, RichLog, Button
from dashboard.logger import logger

from rich.text import Text
from itertools import cycle


class WeatherScreen(Screen):

    def __init__(self) -> None:
        super().__init__()
        self.city = get_city()
        self.version_cycle = cycle([1, 2, 3])
        self.display_content = ""  # Content to be displayed in RichLog

        initial_report = get_weather_report(self.city, next(self.version_cycle))

        if initial_report:
            lines = initial_report.splitlines()
            if len(lines) >= 2:
                self.BORDER_TITLE = lines[0]
                self.BORDER_SUBTITLE = Text.from_ansi(lines[-1])
                self.display_content = "\n".join(lines[1:-1])
            else:
                # Handle cases where report is too short, e.g., "Invalid weather API version"
                self.BORDER_TITLE = "Weather Report"
                self.BORDER_SUBTITLE = Text.from_ansi("Information available below.")
                self.display_content = initial_report # Display the full short report
        else:
            self.display_content = "Failed to retrieve weather data. Please check your internet connection or try again later."
            self.BORDER_TITLE = "Weather Data Error"
            self.BORDER_SUBTITLE = Text.from_ansi("Could not load weather information.")


    def on_button_pressed(self, event) -> None:
        if event.button.id == "version":
            version = next(self.version_cycle)
            new_report = get_weather_report(self.city, version)
            rich_log = self.query_one(RichLog)
            rich_log.clear()
            if new_report:
                lines = new_report.splitlines()
                if len(lines) >= 2:
                    # Update the content of the RichLog, but not the screen's border title/subtitle
                    rich_log.write(Text.from_ansi("\n".join(lines[1:-1])), scroll_end=False)
                else:
                    rich_log.write(Text.from_ansi(new_report), scroll_end=False)
            else:
                rich_log.write("Failed to retrieve weather data. Please check your internet connection or try again later.", scroll_end=False)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            RichLog().write(Text.from_ansi(self.display_content), scroll_end=False),
            Button("Version", id="version")
        )
        yield Footer()
