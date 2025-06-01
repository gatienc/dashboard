import requests
import time
import urwid
import multiprocessing


def weather_worker(conn, update_freq=600):
    def get_weather(fmt):
        try:
            response = requests.get(f'https://wttr.in/Roubaix?format={fmt}')
            if response.status_code == 200:
                return response.text.strip()
            else:
                return 'Error fetching data'
        except requests.RequestException:
            return 'Error fetching data'

    fmt_index = 0
    fmts = ['1', '2', '3', '4']
    time_counter = 0
    fmt = fmts[fmt_index]
    weather_info = get_weather(fmt)
    conn.send(f'Weather: {weather_info}')
    while True:
        if conn.poll():
            msg = conn.recv()
            if msg == 'cycle':
                fmt_index = (fmt_index + 1) % len(fmts)
                fmt = fmts[fmt_index]
                weather_info = get_weather(fmt)
                conn.send(f'Weather: {weather_info}')
        elif time_counter % update_freq == 0:
            fmt = fmts[fmt_index]
            weather_info = get_weather(fmt)
            conn.send(f'Weather: {weather_info}')
        time.sleep(1)
        time_counter += 1


class WeatherWidget(urwid.Button):
    def __init__(self, conn):
        super().__init__('Weather: --')
        self._w = urwid.Text('Weather: --')
        self.conn = conn
        urwid.connect_signal(self, 'click', self.cycle_weather_format)

    def cycle_weather_format(self, button):
        self.conn.send('cycle')

    def refresh(self, loop, user_data=None):
        if self.conn.poll():
            msg = self.conn.recv()
            self._w.set_text(msg)
        loop.set_alarm_in(1, self.refresh)
