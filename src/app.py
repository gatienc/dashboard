from src.screen import WeatherScreen, DashboardScreen
from textual.app import App


class DashboardApp(App):
    CSS_PATH = "app.tcss"

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
