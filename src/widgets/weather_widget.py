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
from src.utils import get_city, get_weather


def to_camel_case(text):
    # Split the text into words
    words = text.split()

    # Capitalize each word
    capitalized_words = [word.capitalize() for word in words]

    # Join the words back into a single string
    camel_case_text = ''.join(capitalized_words)

    return camel_case_text


class WeatherWidget(Widget):
    """A widget to display the current weather"""
    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self) -> None:
        self.city = get_city()
        self.BORDER_TITLE = f"Weather in {self.city}"

        super().__init__()

    def update_weather(self, weather_info: str) -> None:
        """Update the weather information displayed in the widget."""
        logger.debug(f"Updating weather info: {weather_info}")
        weather_info = get_weather(self.city)
        if weather_info:
            self.query_one(Static).update(weather_info)

    def compose(self) -> ComposeResult:
        logger.debug("Composing WeatherWidget")
        weather_info = get_weather(self.city)

        if weather_info:
            yield Static(Text.from_ansi(weather_info))

    def watch_time(self, time: datetime) -> None:
        # update only once an hour
        if time.minute == 0 and time.second == 0:
            logger.debug(
                f"Updating weather at {time}")
            weather_info = get_weather(self.city)
            if weather_info:
                self.query_one(Static).update(weather_info)
