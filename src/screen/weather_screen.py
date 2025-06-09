from src.utils import get_city, get_weather_report
from textual.app import ComposeResult, Screen
from textual.containers import Horizontal
from textual.widgets import Footer, RichLog, Button
from src.logger import logger

from rich.text import Text
from itertools import cycle


class WeatherScreen(Screen):

    def __init__(self) -> None:
        self.city = get_city()
        self.version_cycle = cycle([1, 2, 3])

        self.weather_report = get_weather_report(
            self.city, next(self.version_cycle))

        if self.weather_report:
            first_line = self.weather_report.splitlines(
            )[0] if self.weather_report else ""
            last_line = self.weather_report.splitlines(
            )[-1] if self.weather_report else ""
            # Remove the first line from self.weather_report
            self.weather_report = "\n".join(self.weather_report.splitlines()[
                1:-1]) if self.weather_report else ""

            logger.debug(first_line)
            self.BORDER_TITLE = first_line
            self.BORDER_SUBTITLE = Text.from_ansi(last_line)
        super().__init__()

    def on_button_pressed(self, event) -> None:
        if event.button.id == "version":
            version = next(self.version_cycle)
            self.weather_report = get_weather_report(self.city, version)
            if self.weather_report:
                self.query_one(RichLog).clear().write(
                    Text.from_ansi(self.weather_report), scroll_end=False)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            RichLog().write(Text.from_ansi(self.weather_report),
                            scroll_end=False) if self.weather_report else None,
            Button("Version", id="version")
        )
        yield Footer()
