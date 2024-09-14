#!/usr/bin/python3

from datetime import datetime, timedelta
from liquidctl.driver import find_liquidctl_devices
import psutil
import sys
from threading import Timer
import time


def hsv_to_rgb(hue, saturation, value):
    c = saturation * value
    xp = ((hue / 60.0) % 2) - 1
    if xp < 0:
        xp = -xp
    x = c * (1 - xp)
    m = value - c
    if hue < 0:
        raise ValueError(f'Valid range for hue angle is [0, 360); {hue} is invalid.')
    if hue < 60:
        rp = c
        gp = x
        bp = 0
    elif hue < 120:
        rp = x
        gp = c
        bp = 0
    elif hue < 180:
        rp = 0
        gp = c
        bp = x
    elif hue < 240:
        rp = 0
        gp = x
        bp = c
    elif hue < 300:
        rp = x
        gp = 0
        bp = c
    elif hue < 360:
        rp = c
        gp = 0
        bp = x
    else:
        raise ValueError(f'Valid range for hue angle is [0, 360); {hue} is invalid.')

    return int(255 * (rp + m)), int(255 * (gp + m)), int(255 * (bp + m))


def set_color_hue_for_cpu_utilization(interval, dev):
    util = psutil.cpu_percent(interval - 2) # seconds
    hue_angle_degrees = 240 - util * 2.4
    red, green, blue = hsv_to_rgb(hue_angle_degrees, 1, 1)
    dev.set_color(channel='led7', mode='fixed', colors=[[red, green, blue]])
    print(f'Utilization: {util}')
    print(f'red: {red}, green: {green}, blue: {blue}')
    print(f'\x1b[48;2;{red};{green};{blue}m\x1b[30m  THIS HUE   \x1b[m')


def on_timer(interval, func, *args, **kwargs):
    print('Performing work.')
    func(*args, **kwargs)

    def next_timer_call():
        return on_timer(interval, func, *args, **kwargs)
    timer = next_minute_timer(next_timer_call, interval)
    timer.start()


def next_minute_timer(func, interval=15):
    start_time = datetime.now()
    next_minute = start_time.replace(second=start_time.second - (start_time.second % interval), microsecond=0) + timedelta(seconds=interval)
    next_interval = (next_minute - start_time).seconds + (next_minute - start_time).microseconds * 0.000001
    print(f'Next timer fires in {next_interval} seconds from {start_time}, reaching {next_minute}')
    return Timer(next_interval, func)


def main(*args, **kwargs):
    if len(args) > 0:
        interval = int(args[0])
        if interval < 4:
            print(f'Warning: {interval} is too low, resetting to default 15 seconds.')
            interval = 15
    else:
        interval = 15

    first_dev = None
    for dev in find_liquidctl_devices(pick=0):
        first_dev = dev

    if not first_dev:
        raise RuntimeError('No liquidctl devices found.')

    with dev.connect():
        init_status = dev.initialize()

        if init_status:
            print(f'Got status from initialize(): {[str([key, value, unit]) for key, value, unit in init_status]}')

        on_timer(interval, set_color_hue_for_cpu_utilization, interval, dev)

        while True:
            time.sleep(86400)


if __name__ == '__main__':
    main(*sys.argv[1:])
