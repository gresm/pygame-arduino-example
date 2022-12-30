"""
Example of running simple snake game with pygame and pyserial.
"""
from __future__ import annotations

from collections import deque
from threading import Thread


import pygame as pg
import serial


SERIAL_INPUT_EVENT_TYPE = pg.event.custom_type()


class SerialInputCollector(Thread):
    def __init__(self):
        super().__init__()
        self.serial = serial.Serial("/dev/ttyUSB0")
        self.do_listen = True

        if not self.serial.isOpen():
            self.serial.open()

    def run(self):
        while self.do_listen:
            data = self.serial.read()
            pg.event.post(pg.event.Event(SERIAL_INPUT_EVENT_TYPE, {"key": data}))


def main():
    size = (600, 600)
    display = pg.display.set_mode(size)
    done = False
    food = set()
    snake = deque()
    snake_x = 25
    snake_y = 25
    snake_x_change = 1
    snake_y_change = 0
    clock = pg.time.Clock()
    input_collector = SerialInputCollector()
    input_collector.start()

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
                input_collector.do_listen = False
                input_collector.serial.cancel_read()
            elif event.type == SERIAL_INPUT_EVENT_TYPE:
                print(event.key)

        display.fill((0, 0, 0))
        pg.draw.rect(display, (255, 255, 255), (50, 50, 500, 500))
        clock.tick(60)


if __name__ == '__main__':
    main()
