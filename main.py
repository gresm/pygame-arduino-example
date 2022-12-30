"""
Example of running simple snake game with pygame and pyserial.
"""
from __future__ import annotations

from threading import Thread

import pygame as pg
import serial


SERIAL_INPUT_EVENT_TYPE = pg.event.custom_type()


class SerialInputCollector(Thread):
    def __init__(self):
        super().__init__()
        self.serial = serial.Serial("dev/ttyUSB0")
        self.do_listen = True

        if not self.serial.isOpen():
            self.serial.open()

    def run(self):
        while self.do_listen:
            data = self.serial.read()
            pg.event.post(pg.event.Event(SERIAL_INPUT_EVENT_TYPE, {"key": data}))
