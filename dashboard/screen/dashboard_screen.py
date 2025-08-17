
from textual.app import ComposeResult, Screen
from textual.widgets import Footer
from dashboard.logger import logger
from textual.reactive import reactive
from datetime import datetime
from textual.containers import Horizontal, Vertical
from dashboard.widgets import TimeWidget, WeatherWidget, PomodoroWidget, ObsidianWidget


class DashboardScreen(Screen):
    time: reactive[datetime] = reactive(datetime.now)

    def __init__(self):
        super().__init__()
        # Get small_screen from the app
        self.small_screen = getattr(self.app, 'small_screen', False)
        if self.small_screen:
            self.add_class("small-screen")
        logger.info(
            f"DashboardScreen initialized with small_screen={self.small_screen}")

    def compose(self) -> ComposeResult:
        logger.debug("Composing DashboardApp")

        if self.small_screen:
            # Small screen layout
            with Vertical():
                with Horizontal(classes="top-row"):
                    yield TimeWidget("Europe/Paris", small_screen=True).data_bind(time=DashboardScreen.time)
                    yield WeatherWidget(small_screen=True).data_bind(time=DashboardScreen.time)
                    yield PomodoroWidget(small_screen=True).data_bind(time=DashboardScreen.time)

                with Horizontal(classes="bottom-row"):
                    yield ObsidianWidget(small_screen=True).data_bind(time=DashboardScreen.time)
        else:
            # Regular layout
            yield WeatherWidget(small_screen=False).data_bind(time=DashboardScreen.time)
            yield TimeWidget("Europe/Paris", small_screen=False).data_bind(time=DashboardScreen.time)
            yield PomodoroWidget(small_screen=False).data_bind(time=DashboardScreen.time)
            yield ObsidianWidget(small_screen=False).data_bind(time=DashboardScreen.time)

        yield Footer()

    def update_time(self) -> None:
        self.time = datetime.now()

    def on_mount(self) -> None:
        logger.debug("DashboardApp mounted")
        self.update_time()
        self.set_interval(1, self.update_time)
