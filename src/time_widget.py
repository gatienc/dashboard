# src/time_widget.py
import datetime
import time
import urwid
from .logger import logger


def time_worker(conn):
    is_uk = False
    while True:
        if conn.poll():
            msg = conn.recv()
            if msg == 'toggle':
                is_uk = not is_uk
        if is_uk:
            now = datetime.datetime.now(datetime.timezone.utc).astimezone(
                datetime.timezone(datetime.timedelta(hours=1))
            ).strftime('%H:%M:%S')
            conn.send(f'Time (UK): {now}')
        else:
            now = datetime.datetime.now().strftime('%H:%M:%S')
            conn.send(f'Time: {now}')
        time.sleep(1)


class TimeWidget(urwid.Button):
    def __init__(self, conn):
        super().__init__('Time: --:--:--')
        self._w = urwid.Text('Time: --:--:--')
        self.conn = conn
        urwid.connect_signal(self, 'click', self.toggle_time_zone)
        logger.info('TimeWidget initialized')

    def toggle_time_zone(self, button):
        self.conn.send('toggle')
        logger.info('TimeWidget: Time zone toggled')

    def refresh(self, loop, user_data=None):
        if self.conn.poll():
            msg = self.conn.recv()
            self._w.set_text(msg)
            # logger.info(f'TimeWidget: Updated display to "{msg}"')
        loop.set_alarm_in(0.5, self.refresh)
