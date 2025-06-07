import datetime
from .logger import logger
from textual.widget import Widget
from textual.widgets import Label, Log, Static
from textual.app import ComposeResult
from datetime import datetime
from textual.reactive import reactive
from itertools import cycle
import requests
from textual.events import MouseEvent

DEFAULT_CITY = "Roubaix"


def get_weather(city: str = DEFAULT_CITY) -> str:
    """Fetch the weather data from wttr.in for Roubaix.

    """
    try:
        logger.info(
            f'Fetching weather data with url : https://wttr.in/{city}?0Q&lang=fr')
        response = requests.get(f'https://wttr.in/{city}?0Q&lang=fr')
        if response.status_code == 200:
            return response.text.strip()
        else:
            logger.error(
                f'Error fetching weather data status code: {response.status_code}')
            return f'Error fetching data, status code: {response.status_code}'
    except requests.RequestException:
        return 'Error fetching data'


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


class WeatherWidget(Widget):
    """A widget to display the current weather"""
    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self) -> None:
        self.city = get_city()
        super().__init__()

    def update_weather(self, weather_info: str) -> None:
        """Update the weather information displayed in the widget."""
        logger.debug(f"Updating weather info: {weather_info}")
        weather_info = get_weather(self.city)
        if weather_info.startswith('Error'):
            logger.error(f'WeatherWidget: {weather_info}')
        else:
            self.query_one(Label).update(weather_info)

    # def on_click(self, chain: MouseEvent) -> None:
    #     """Handle click events to increase the cycle of weather formats."""
    #     self.format = next(self.format_cycle)
    #     weather_info = get_weather(self.format, self.city)
    #     if weather_info.startswith('Error'):
    #         logger.error(f'WeatherWidget: {weather_info}')
    #     else:
    #         self.query_one("#weather_info", Static).update(weather_info)
    #         logger.info(f'WeatherWidget: {weather_info}')

    def compose(self) -> ComposeResult:
        logger.debug("Composing WeatherWidget")
        weather_info = get_weather(self.city)

        if weather_info.startswith('Error'):
            logger.error(f'WeatherWidget: {weather_info}')
            weather_info = "Error fetching weather data"
        else:
            yield Static(weather_info, id="weather_info", markup=False)

    def watch_time(self, time: datetime) -> None:
        # update only once an hour

        if time.minute == 0 and time.second == 0:
            logger.debug(
                f"Updating weather at {time}")
            weather_info = get_weather(1)
            if weather_info.startswith('Error'):
                logger.error(f'WeatherWidget: {weather_info}')
            else:
                self.query_one("#weather_info", Static).update(weather_info)
