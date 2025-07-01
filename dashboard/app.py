from dashboard.screen import WeatherScreen, DashboardScreen
from textual.app import App
from pathlib import Path


class DashboardApp(App):
    CSS_PATH = Path(__file__).parent / "app.tcss"

    BINDINGS = [
        ("🏠️", "switch_mode('dashboard')", "Dashboard"),
        ("☁️", "switch_mode('weather')", "Weather"),
        # ("✨", "switch_mode('fun')", "Fun")

    ]
    MODES = {
        "dashboard": DashboardScreen,
        "weather": WeatherScreen,
        # "fun": FunTermScreen
    }

    def on_mount(self) -> None:
        self.theme = "dracula"
        self.switch_mode("dashboard")


def main():
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()
