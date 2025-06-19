
from textual.app import ComposeResult, Screen
from textual.containers import Horizontal
from textual.widgets import Footer, Placeholder
from src.logger import logger
from textual.reactive import reactive
from datetime import datetime
from src.widgets import TimeWidget, WeatherWidget, PomodoroWidget, ObsidianWidget


class DashboardScreen(Screen):
    time: reactive[datetime] = reactive(datetime.now)

    def compose(self) -> ComposeResult:
        logger.debug("Composing DashboardApp")
        yield TimeWidget("Europe/Paris").data_bind(
            time=DashboardScreen.time
        )
        yield WeatherWidget().data_bind(
            time=DashboardScreen.time)
        yield PomodoroWidget().data_bind(
            time=DashboardScreen.time)
        yield ObsidianWidget().data_bind(time=DashboardScreen.time)

        yield Footer()

    def update_time(self) -> None:
        self.time = datetime.now()

    def on_mount(self) -> None:
        logger.debug("DashboardApp mounted")
        self.update_time()
        self.set_interval(1, self.update_time)
