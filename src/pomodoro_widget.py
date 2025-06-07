# src/pomodoro_widget.py
import time
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header


def pomodoro_worker(conn):
    WORK_DURATION = 25 * 60
    BREAK_DURATION = 5 * 60
    state = 'ready'
    is_break = False
    time_left = WORK_DURATION
    while True:
        if conn.poll():
            msg = conn.recv()
            if msg == 'start':
                state = 'running'
                is_break = False
                time_left = WORK_DURATION
            elif msg == 'pause':
                state = 'paused'
            elif msg == 'resume':
                state = 'running'
            elif msg == 'reset':
                state = 'ready'
                is_break = False
                time_left = WORK_DURATION
        if state == 'running':
            time_left -= 1
            if time_left <= 0:
                if not is_break:
                    state = 'break'
                    is_break = True
                    time_left = BREAK_DURATION
                else:
                    state = 'ready'
                    is_break = False
                    time_left = WORK_DURATION
        mins, secs = divmod(time_left, 60)
        if state == 'ready':
            text = 'Pomodoro: 25:00 [Ready]'
        elif state == 'running':
            if not is_break:
                text = f'Pomodoro: {mins:02}:{secs:02} [Work]'
            else:
                text = f'Pomodoro: {mins:02}:{secs:02} [Break]'
        elif state == 'paused':
            text = f'Pomodoro: {mins:02}:{secs:02} [Paused]'
        elif state == 'break':
            text = f'Pomodoro: {mins:02}:{secs:02} [Break]'
        else:
            text = 'Pomodoro: --:--'
        conn.send(text)
        time.sleep(1)


class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class PomodoroWidget(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Button('Start', id='start_button', variant='success')
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")
