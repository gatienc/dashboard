import time
import urwid
import multiprocessing


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


class PomodoroWidget(urwid.Button):
    def __init__(self, conn):
        super().__init__('Pomodoro: 25:00 [Ready]')
        self._w = urwid.Text('Pomodoro: 25:00 [Ready]')
        self.conn = conn
        urwid.connect_signal(self, 'click', self.on_click)

    def on_click(self, button):
        self.conn.send('start')

    def refresh(self, loop, user_data=None):
        if self.conn.poll():
            msg = self.conn.recv()
            self._w.set_text(msg)
        loop.set_alarm_in(1, self.refresh)
