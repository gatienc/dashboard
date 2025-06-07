# from .pomodoro_widget import PomodoroWidget, pomodoro_worker
# from .weather_widget import WeatherWidget, weather_worker
from .time_widget import TimeWidget
from .weather_widget import WeatherWidget, get_weather, get_city
from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal
from textual.widgets import Footer, Markdown, Placeholder, Header, Digits, RichLog, Static, Log
from rich_pixels import Pixels
from .logger import logger
from textual.reactive import reactive
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO


class DashboardScreen(Screen):
    CSS_PATH = "app.tcss"
    time: reactive[datetime] = reactive(datetime.now)

    def compose(self) -> ComposeResult:
        logger.debug("Composing DashboardApp")
        yield Header()
        yield Horizontal(
            TimeWidget("Europe/Paris").data_bind(
                time=DashboardScreen.time
            ),
            WeatherWidget().data_bind(
                time=DashboardScreen.time),
            Placeholder()
        )
        yield Placeholder()
        yield Footer()

    def update_time(self) -> None:
        self.time = datetime.now()

    def on_mount(self) -> None:
        logger.debug("DashboardApp mounted")
        self.update_time()
        self.set_interval(1, self.update_time)


class WeatherScreen(Screen):
    CSS_PATH = "app.tcss"

    def __init__(self) -> None:
        super().__init__()
        self.city = get_city()
        try:
            response = requests.get(
                f'https://v1.wttr.in/{self.city}?F&lang=fr')
            if response.status_code == 200:
                self.weather_info = response.text
            else:
                self.weather_info = "Error fetching weather data"
                logger.error(
                    f"Failed to fetch weather data for {self.city}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            self.weather_info = "Error fetching weather data"

    def compose(self) -> ComposeResult:
        yield Log().write(self.weather_info)
        yield Footer()


class DashboardApp(App):
    BINDINGS = [
        ("🏠️", "switch_mode('dashboard')", "Dashboard"),
        ("☁️", "switch_mode('weather')", "Weather"),
    ]
    MODES = {
        "dashboard": DashboardScreen,
        "weather": WeatherScreen,
    }

    def on_mount(self) -> None:
        self.theme = "dracula"
        self.switch_mode("dashboard")


def main():
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
