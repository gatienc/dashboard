import datetime
from dashboard.logger import logger
from textual.widget import Widget
from textual.widgets import Label, Log, Static, Markdown, TextArea
from textual.app import ComposeResult
from datetime import datetime
from textual.reactive import reactive
from itertools import cycle
import requests
from textual.events import MouseEvent
import json
from rich.text import Text
from dashboard.utils import get_city, get_weather, get_minimal_weather


class WeatherWidget(Widget):
    """A widget to display the current weather"""
    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self, small_screen: bool = False):
        self.city = get_city()
        self.small_screen = small_screen
        if not small_screen:
            self.BORDER_TITLE = f"Weather in {self.city}"

        super().__init__()

    def update_weather(self) -> None:
        """Update the weather information displayed in the widget."""
        if self.small_screen:
            # Use minimal weather data for small screens
            weather_info = get_minimal_weather(self.city)
            if weather_info:
                # Ensure no trailing whitespace in the display
                clean_weather_info = weather_info.strip()
                self.query_one(Static).update(
                    Text.from_ansi(clean_weather_info))
            else:
                self.query_one(Static).update("Weather data unavailable")
        else:
            # Use full weather data for regular screens
            weather_info = get_weather(self.city)
            if weather_info:
                # Ensure no trailing whitespace in the display
                clean_weather_info = weather_info.strip()
                self.query_one(Static).update(
                    Text.from_ansi(clean_weather_info))
            else:
                self.query_one(Static).update("Weather data unavailable")

    def compose(self) -> ComposeResult:

        yield Static("Loading weather info", classes="center")

    def on_mount(self) -> None:
        self.update_weather()

    def watch_time(self, time: datetime) -> None:
        # update only once an hour
        if time.minute == 0 and time.second == 0:
            logger.debug(
                f"Updating weather at {time}")
            self.update_weather()
