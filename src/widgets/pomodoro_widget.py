"""
Todo implement dynamic time assignment for work and break
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Center, Middle, Vertical
from textual.widget import Widget
from textual.color import Gradient
from textual.widgets import Button, Digits, Footer, Header, ProgressBar
from textual.timer import Timer
from textual.reactive import reactive
from datetime import datetime
from src.logger import logger
from src.utils import play_sound
from pathlib import Path
import threading

WORK_DURATION = 25 * 60
BREAK_DURATION = 5 * 60


def count_to_time(count) -> str:
    """
    From count return remaining time, 
    return time format MM:SS or H:MM:SS if H != 0
    """
    hours, remainder = divmod(count, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"


class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class PomodoroWidget(Widget):
    time: reactive[datetime] = reactive(datetime.now)

    BORDER_TITLE = "Pomodoro Timer"

    progress_timer: Timer
    """Timer to simulate progress happening."""

    count = 0
    work_mode = True
    started = False
    paused = True
    target_count = WORK_DURATION

    def compose(self) -> ComposeResult:
        gradient = Gradient.from_colors(
            "#99dd55",
            "#44dd88",
            "#eedd00",
            "#ee9944",
            "#cc6666",
            "#0099cc",
        )
        yield Center(
            Digits("    25:00", classes="center"),
            ProgressBar(classes="center", gradient=gradient, show_eta=False)
        )

    def on_click(self) -> None:
        logger.debug("pomodoro clicked")
        if not self.started:
            logger.debug("pomodoro started")
            self.started = True
            self.action_start(WORK_DURATION)
            self.pause = False
        else:
            logger.debug(
                "pomodoro clicked and started. pause = "+str(self.pause))
            self.progress_timer.resume() if self.pause else self.progress_timer.pause()
            self.pause = not self.pause

    def on_mount(self) -> None:
        """Set up a timer to simulate progess happening."""
        self.progress_timer = self.set_interval(
            1, self.make_progress, pause=True)

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        self.count += 1

        if self.count == self.target_count:
            self.query_one(ProgressBar).advance(1)
            self.progress_timer.pause()
            self.count = 0
            sound_dir_path = Path(__file__).parent.parent / "assets"

            sound_to_play = str(sound_dir_path/"sonnerie.mp3") if self.work_mode else str(
                sound_dir_path/"encore_du_travail.mp3")

            def play_notification(): return play_sound(sound_to_play)
            threading.Thread(target=play_notification,
                             daemon=True).start()
            self.work_mode = not self.work_mode
            self.target_count = WORK_DURATION if self.work_mode else BREAK_DURATION
            self.query_one(ProgressBar).update(
                total=self.target_count, progress=0)
            self.query_one(Digits).update("    " + count_to_time(
                self.target_count))

            self.progress_timer.resume()

        else:
            self.query_one(ProgressBar).advance(1)
            self.query_one(Digits).update(
                "    " + count_to_time(self.target_count-self.count))

    def action_start(self, target_time) -> None:
        """Start the progress tracking."""
        self.query_one(ProgressBar).update(total=target_time)
        self.progress_timer.resume()
