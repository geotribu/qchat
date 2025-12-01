import random
from datetime import datetime, timedelta
from typing import Tuple

import numpy as np
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtGui import QTransform
from qgis.utils import iface


def dizzy(
    duration: int = 3,
    d: int = 12,
    r: int = 6,
    interval: int = 50,
    should_start: bool = True,
) -> QTimer:
    """Dizz command, make QGIS shake.

    :param duration: duration in seconds
    :param d: max offset in pixels
    :param r: max rotation in degrees
    :param interval: refresh interval in milliseconds
    :param should_start: whether to start the timer immediately
    :return: QTimer instance
    """

    canvas = iface.mapCanvas()
    stop_time = datetime.now() + timedelta(seconds=duration)

    initial_scene_rect = canvas.sceneRect()
    initial_transform = canvas.transform()

    timer = QTimer()
    timer.setInterval(interval)

    def dizz():
        if datetime.now() >= stop_time:
            timer.stop()
            canvas.setSceneRect(initial_scene_rect)
            canvas.setTransform(initial_transform)
            canvas.refresh()
            return

        rect = initial_scene_rect.translated(
            random.randint(-d, d), random.randint(-d, d)
        )
        canvas.setSceneRect(rect)

        matrix = QTransform()
        matrix.rotate(random.randint(-r, r))
        canvas.setTransform(matrix)

        canvas.refresh()

    timer.timeout.connect(dizz)

    if should_start:
        timer.start()

    return timer


def coords8(size: int, nb_points: int = 100) -> Tuple[int, int]:
    t = np.linspace(0, 2 * np.pi, nb_points)
    x = size * np.sin(t)
    y = size * np.cos(t) / 2
    return (x, y)


def flick_of_the_wrist(
    duration: int = 3,
    size: int = 500,
    nb_points: int = 20,
    interval: int = 50,
    should_start: bool = True,
) -> QTimer:
    canvas = iface.mapCanvas()
    stop_time = datetime.now() + timedelta(seconds=duration)

    center = canvas.center()
    cx, cy = center.x(), center.y()
    coords = coords8(size, nb_points)

    i = 0
    up = True

    timer = QTimer()
    timer.setInterval(interval)

    def flick():
        nonlocal cx, cy, i, up

        if datetime.now() >= stop_time:
            timer.stop()
            return

        nx, ny = coords[0][i], coords[1][i]
        dx, dy = nx - cx, ny - cy

        rect = canvas.sceneRect()
        rect.moveTo(dx, dy)
        canvas.setSceneRect(rect)

        cx = nx
        cy = ny

        if up:
            i += 1
            if i >= nb_points - 1:
                up = False
        else:
            i -= 1
            if i <= 0:
                up = True

    timer.timeout.connect(flick)

    if should_start:
        timer.start()

    return timer
