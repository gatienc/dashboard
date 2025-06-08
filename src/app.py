# from .pomodoro_widget import PomodoroWidget, pomodoro_worker
# from .weather_widget import WeatherWidget, weather_worker
from .time_widget import TimeWidget
from .weather_widget import WeatherWidget, get_weather, get_city
from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal
from textual.widgets import Footer, Markdown, Placeholder, Header, Digits, RichLog, Static, Log, Button
from rich_pixels import Pixels
from .logger import logger
from textual.reactive import reactive
from datetime import datetime
import requests
from rich.text import Text
from itertools import cycle


class DashboardScreen(Screen):
    CSS_PATH = "app.tcss"
    time: reactive[datetime] = reactive(datetime.now)

    def compose(self) -> ComposeResult:
        logger.debug("Composing DashboardApp")
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


def get_weather_report(city: str, version: int = 1) -> str:
    """
    Fetch the weather report for a given city and wttr.in API version (1, 2, or 3).
    """
    if version not in (1, 2, 3):
        logger.error(f"Invalid version: {version}. Must be 1, 2, or 3.")
        return "Invalid weather API version"
    try:
        response = requests.get(
            f'https://v{version}.wttr.in/{city}?F&lang=fr')
        if response.status_code == 200:
            return response.text
        else:
            logger.error(
                f"Failed to fetch weather data for {city}: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")


class WeatherScreen(Screen):
    CSS_PATH = "app.tcss"

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
