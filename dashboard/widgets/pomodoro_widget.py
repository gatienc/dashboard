"""
Todo implement dynamic time assignment for work and break
"""

from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal, Center, Middle, Vertical
from textual.widget import Widget
from textual.color import Gradient
from textual.widgets import Button, Digits, Footer, Header, ProgressBar, Static, Tooltip
from textual.timer import Timer
from textual.reactive import reactive
from datetime import datetime
from dashboard.logger import logger
from dashboard.utils import play_sound
from pathlib import Path
import threading
from textual import on
from textual.events import Click
from textual.message import Message

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


def count_to_minimal_time(count) -> str:
    """
    From count return remaining time in minimal format for small screens
    return time format MM:SS
    """
    minutes, seconds = divmod(count, 60)
    return f"{minutes:02}:{seconds:02}"


class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class PomodoroConfigPopup(Screen):
    """Modal screen for configuring Pomodoro timer."""

    def __init__(self, work_duration: int, break_duration: int, small_screen: bool = False):
        super().__init__()
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.small_screen = small_screen
        self.BORDER_TITLE = "Configure Pomodoro Timer"

    def compose(self) -> ComposeResult:
        with Vertical(classes="popup-container"):
            yield Static("Configure your Pomodoro timer", classes="popup-title")

            yield Static("")  # Small spacer

            yield Static("Work time:", classes="config-label")
            with Horizontal(classes="config-row"):
                yield Button("⬆️", id="work-up", classes="config-btn")
                yield Static(f"{self.work_duration // 60} min", id="work-time", classes="config-time")
                yield Button("⬇️", id="work-down", classes="config-btn")

            yield Static("")  # Small spacer

            yield Static("Break time:", classes="config-label")
            with Horizontal(classes="config-row"):
                yield Button("⬆️", id="break-up", classes="config-btn")
                yield Static(f"{self.break_duration // 60} min", id="break-time", classes="config-time")
                yield Button("⬇️", id="break-down", classes="config-btn")

            yield Static("")  # Small spacer

            with Horizontal(classes="button-row"):
                yield Button("Cancel", id="cancel-config", variant="error")
                yield Button("Apply", id="apply-config", variant="primary")

    @on(Button.Pressed, "#work-up")
    def increase_work_time(self) -> None:
        """Increase work time by 5 minutes."""
        self.work_duration += 5 * 60
        self.query_one(
            "#work-time", Static).update(f"{self.work_duration // 60} min")

    @on(Button.Pressed, "#work-down")
    def decrease_work_time(self) -> None:
        """Decrease work time by 5 minutes."""
        if self.work_duration > 5 * 60:  # Minimum 5 minutes
            self.work_duration -= 5 * 60
            self.query_one(
                "#work-time", Static).update(f"{self.work_duration // 60} min")

    @on(Button.Pressed, "#break-up")
    def increase_break_time(self) -> None:
        """Increase break time by 1 minute."""
        self.break_duration += 1 * 60
        self.query_one(
            "#break-time", Static).update(f"{self.break_duration // 60} min")

    @on(Button.Pressed, "#break-down")
    def decrease_break_time(self) -> None:
        """Decrease break time by 1 minute."""
        if self.break_duration > 1 * 60:  # Minimum 1 minute
            self.break_duration -= 1 * 60
            self.query_one(
                "#break-time", Static).update(f"{self.break_duration // 60} min")

    @on(Button.Pressed, "#cancel-config")
    def cancel_config(self) -> None:
        """Cancel configuration and close modal screen."""
        logger.debug("Cancel button pressed, closing modal screen")
        self.app.pop_screen()

    @on(Button.Pressed, "#apply-config")
    def apply_config(self) -> None:
        """Apply configuration and close modal screen."""
        logger.debug(
            f"Apply button pressed in modal screen: work={self.work_duration}s, break={self.break_duration}s")

        # Try both message posting and direct method call for reliability
        try:
            # Emit message with new durations
            self.post_message(ConfigApplied(
                self.work_duration, self.break_duration))
            logger.debug("ConfigApplied message posted")
        except Exception as e:
            logger.error(f"Failed to post message: {e}")

        # Also try direct method call if parent widget reference exists
        if hasattr(self, 'parent_widget'):
            try:
                logger.debug("Calling parent widget method directly")
                self.parent_widget.work_duration = self.work_duration
                self.parent_widget.break_duration = self.break_duration

                # Always reset the timer state
                self.parent_widget.started = False
                self.parent_widget.count = 0
                self.parent_widget.work_mode = True
                self.parent_widget.target_count = self.work_duration
                self.parent_widget.pause = True

                # Stop the timer if it's running
                if hasattr(self.parent_widget, 'progress_timer'):
                    self.parent_widget.progress_timer.pause()

                # Reset the display
                self.parent_widget.reset_display(self.work_duration)
                logger.debug("Direct method call successful")
            except Exception as e:
                logger.error(f"Failed direct method call: {e}")

        # Close the modal screen
        self.app.pop_screen()


class ConfigApplied(Message):
    """Message emitted when configuration is applied."""

    def __init__(self, work_duration: int, break_duration: int):
        super().__init__()
        self.work_duration = work_duration
        self.break_duration = break_duration


class PomodoroWidget(Widget):
    """Pomodoro widget that adapts its display based on screen size."""

    time: reactive[datetime] = reactive(datetime.now)

    BORDER_TITLE = "Pomodoro Timer"

    progress_timer: Timer
    """Timer to simulate progress happening."""

    count = 0
    work_mode = True
    started = False
    paused = True
    target_count = WORK_DURATION
    work_duration = WORK_DURATION
    break_duration = BREAK_DURATION

    def __init__(self, small_screen: bool = False):
        super().__init__()
        self.small_screen = small_screen
        if not small_screen:
            self.BORDER_TITLE = "Pomodoro Timer"
        # Ensure proper initial state
        self.started = False
        self.count = 0
        self.work_mode = True
        self.pause = True
        self.target_count = self.work_duration

    def compose(self) -> ComposeResult:
        # Only compose the timer mode
        if self.small_screen:
            yield Static("25:00", classes="center", id="timer-display")
        else:
            gradient = Gradient.from_colors(
                "#99dd55",
                "#44dd88",
                "#eedd00",
                "#ee9944",
                "#cc6666",
                "#0099cc",
            )
            yield Center(
                Digits("    25:00", classes="center", id="timer-digits"),
                ProgressBar(classes="center", gradient=gradient,
                            show_eta=False, id="timer-progress")
            )

    def on_click(self) -> None:
        logger.debug("pomodoro clicked - event received")
        if not self.started:
            logger.debug("pomodoro started")
            self.started = True
            self.action_start(self.work_duration)
            self.pause = False
        else:
            logger.debug(
                "pomodoro clicked and started. pause = "+str(self.pause))
            self.progress_timer.resume() if self.pause else self.progress_timer.pause()
            self.pause = not self.pause

    def on_mouse_down(self, event: Click) -> None:
        """Handle right click to open configuration popup."""
        logger.debug(
            f"Mouse down event received: button={event.button}, x={event.x}, y={event.y}")
        if event.button == 3:  # Right click
            logger.debug("Right click detected, opening config popup")
            self.show_config_popup()
        else:
            logger.debug(
                f"Non-right click detected: button={event.button}, treating as left click")
            # Handle as left click for timer control
            self.on_click()

    def show_config_popup(self) -> None:
        """Show configuration popup as a modal screen."""
        logger.debug("Opening Pomodoro config as modal screen")

        # Create the modal screen
        config_screen = PomodoroConfigPopup(
            self.work_duration, self.break_duration, self.small_screen)

        # Store reference to this widget in the screen for direct method calls
        config_screen.parent_widget = self

        # Push the modal screen
        self.app.push_screen(config_screen)

    @on(ConfigApplied)
    def on_config_applied(self, event: ConfigApplied) -> None:
        """Apply new configuration from popup."""
        logger.debug(
            f"ConfigApplied message received: work={event.work_duration}s, break={event.break_duration}s")

        # Update the durations
        old_work = self.work_duration
        old_break = self.break_duration
        self.work_duration = event.work_duration
        self.break_duration = event.break_duration

        logger.debug(
            f"Updated durations: work {old_work}s -> {self.work_duration}s, break {old_break}s -> {self.break_duration}s")

        # Always reset the timer state when configuration changes
        logger.debug("Resetting timer state due to configuration change")
        self.started = False
        self.count = 0
        self.work_mode = True
        self.target_count = self.work_duration
        self.pause = True

        # Stop the timer if it's running
        if hasattr(self, 'progress_timer'):
            self.progress_timer.pause()

        # Reset the display to show the new work duration
        self.reset_display(self.work_duration)
        logger.debug(f"Timer reset to {self.work_duration}s work duration")

    def on_mount(self) -> None:
        """Set up a timer to simulate progress happening."""
        self.progress_timer = self.set_interval(
            1, self.make_progress, pause=True)
        # Ensure the display is properly initialized
        self.reset_display(self.work_duration)

    def make_progress(self) -> None:
        """Called automatically to advance the progress bar."""
        self.count += 1

        if self.count == self.target_count:
            if not self.small_screen:
                self.query_one("#timer-progress", ProgressBar).advance(1)
            self.progress_timer.pause()
            self.count = 0
            sound_dir_path = Path(__file__).parent.parent / "assets"

            sound_to_play = str(sound_dir_path/"sonnerie.mp3") if self.work_mode else str(
                sound_dir_path/"encore_du_travail.mp3")

            def play_notification(): return play_sound(sound_to_play)
            threading.Thread(target=play_notification,
                             daemon=True).start()
            self.work_mode = not self.work_mode
            self.target_count = self.work_duration if self.work_mode else self.break_duration

            self.reset_display(self.target_count)
            self.progress_timer.resume()

        else:
            remaining_time = self.target_count - self.count
            self.update_display(remaining_time, self.pause)

    def update_display(self, remaining_time: int, is_paused: bool = False):
        """Update the display based on screen size."""
        if self.small_screen:
            # Minimal display
            mode_text = "WORK" if self.work_mode else "BREAK"
            time_text = count_to_minimal_time(remaining_time)
            status = "⏸️" if is_paused else "▶️"
            self.query_one("#timer-display",
                           Static).update(f"{mode_text} {time_text} {status}")
        else:
            # Full display
            self.query_one("#timer-progress", ProgressBar).advance(1)
            self.query_one("#timer-digits", Digits).update("    " +
                                                           count_to_time(remaining_time))

    def reset_display(self, target_time: int):
        """Reset the display for a new timer."""
        logger.debug(
            f"Resetting display: target_time={target_time}s, work_mode={self.work_mode}, small_screen={self.small_screen}")
        if self.small_screen:
            # Minimal display
            mode_text = "WORK" if self.work_mode else "BREAK"
            time_text = count_to_minimal_time(target_time)
            self.query_one("#timer-display",
                           Static).update(f"{mode_text} {time_text} ▶️")
        else:
            # Full display
            self.query_one("#timer-progress",
                           ProgressBar).update(total=target_time, progress=0)
            self.query_one("#timer-digits",
                           Digits).update("    " + count_to_time(target_time))
        logger.debug(f"Display reset complete: {count_to_time(target_time)}")

    def action_start(self, target_time) -> None:
        """Start the progress tracking."""
        logger.debug(f"Starting timer with target time: {target_time}s")
        self.started = True
        self.pause = False
        self.target_count = target_time
        self.count = 0
        self.reset_display(target_time)
        self.progress_timer.resume()
        logger.debug("Timer started successfully")
