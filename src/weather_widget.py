import datetime
from .logger import logger
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

DEFAULT_CITY = "Roubaix"


def get_weather(city: str = DEFAULT_CITY) -> str | None:
    """Fetch the weather data from wttr.in for Roubaix.

    """
    try:
        logger.info(
            f'Fetching weather data with url : https://wttr.in/{city}?0Q&lang=fr&format=j1')
        response = requests.get(
            f'https://wttr.in/{city}?0Q&lang=fr')
        if response.status_code == 200:
            logger.info(response)
            return response.text
        else:
            logger.error(
                f'Error fetching weather data status code: {response.status_code}')
    except requests.RequestException as e:
        logger.error(e)


def get_city(default_city: str = DEFAULT_CITY) -> str:
    """Return the city name for the current position.
    Returns:
        str: The city name or default_city if it cannot be determined.
    """
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            return data.get('city')
        else:
            return default_city
    except Exception as e:
        logger.error(f"Error fetching city name: {e}")
        return default_city


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
