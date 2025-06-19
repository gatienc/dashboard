import datetime
from src.logger import logger
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
from src.utils import get_city, get_weather, to_camel_case


class WeatherWidget(Widget):
    """A widget to display the current weather"""
    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self) -> None:
        self.city = get_city()
        self.BORDER_TITLE = f"Weather in {self.city}"

        super().__init__()

    def update_weather(self) -> None:
        """Update the weather information displayed in the widget."""
        weather_info = get_weather(self.city)
        if weather_info:
            self.query_one(Static).update(Text.from_ansi(weather_info))

    def compose(self) -> ComposeResult:
        logger.debug("Composing WeatherWidget")
        weather_info = get_weather(self.city)

        if weather_info:
            yield Static(Text.from_ansi(weather_info), classes="center")

    def watch_time(self, time: datetime) -> None:
        # update only once an hour
        if time.minute == 0 and time.second == 0:
            logger.debug(
                f"Updating weather at {time}")
            self.update_weather()
