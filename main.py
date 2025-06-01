import urwid
import multiprocessing
from time_widget import TimeWidget, time_worker
from weather_widget import WeatherWidget, weather_worker
from pomodoro_widget import PomodoroWidget, pomodoro_worker

if __name__ == '__main__':
    # Set up pipes and processes
    time_parent, time_child = multiprocessing.Pipe()
    weather_parent, weather_child = multiprocessing.Pipe()
    pomo_parent, pomo_child = multiprocessing.Pipe()

    time_proc = multiprocessing.Process(
        target=time_worker, args=(time_child,), daemon=True)
    weather_proc = multiprocessing.Process(
        target=weather_worker, args=(weather_child,), daemon=True)
    pomo_proc = multiprocessing.Process(
        target=pomodoro_worker, args=(pomo_child,), daemon=True)

    time_proc.start()
    weather_proc.start()
    pomo_proc.start()

    # Widgets
    time_widget = TimeWidget(time_parent)
    weather_widget = WeatherWidget(weather_parent)
    pomodoro_widget = PomodoroWidget(pomo_parent)

    # Layout
    body = urwid.Padding(
        urwid.Columns([
            ('weight', 2, urwid.Filler(weather_widget, valign='top')),
            ('weight', 1, urwid.Filler(time_widget, valign='top')),
            ('weight', 1, urwid.Filler(pomodoro_widget, valign='top')),
        ]), left=2, right=2
    )

    main_loop = urwid.MainLoop(body, palette=[('reversed', 'standout', '')])
    main_loop.set_alarm_in(0.5, time_widget.refresh)
    main_loop.set_alarm_in(1, weather_widget.refresh)
    main_loop.set_alarm_in(1, pomodoro_widget.refresh)
    main_loop.run()
