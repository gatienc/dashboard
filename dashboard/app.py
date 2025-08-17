from dashboard.screen import WeatherScreen, DashboardScreen
from dashboard.widgets.pomodoro_widget import PomodoroConfigPopup
from textual.app import App
from pathlib import Path
import argparse
import sys
from dashboard.logger import logger


class DashboardApp(App):
    CSS_PATH = Path(__file__).parent / "app.tcss"

    BINDINGS = [
        ("🏠️", "switch_mode('dashboard')", "Dashboard"),
        ("☁️", "switch_mode('weather')", "Weather"),
    ]
    MODES = {
        "dashboard": DashboardScreen,
        "weather": WeatherScreen,
        "pomodoro_config": PomodoroConfigPopup,
    }

    def __init__(self, small_screen: bool = False):
        super().__init__()
        self.small_screen = small_screen
        logger.info(
            f"DashboardApp initialized with small_screen={small_screen}")

    def on_mount(self) -> None:
        self.theme = "nord"
        logger.info("DashboardApp mounted, switching to dashboard mode")
        self.switch_mode("dashboard")


def main():
    parser = argparse.ArgumentParser(description="Dashboard CLI")
    parser.add_argument(
        "--small-screen",
        action="store_true",
        help="Use small screen layout (optimized for Raspberry Pi displays)"
    )

    args = parser.parse_args()
    logger.info(f"Starting dashboard with small_screen={args.small_screen}")

    app = DashboardApp(small_screen=args.small_screen)
    app.run()


if __name__ == "__main__":
    main()
