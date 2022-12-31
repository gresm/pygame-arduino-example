"""
Example of running simple snake game with pygame and pyserial.
"""
from __future__ import annotations

from collections import deque
from threading import Thread
from random import randint

# Crash handling to prevent not killed processes.
import apport_python_hook
import sys

import pygame as pg
import serial


def catch_errors(trigger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as exc:
                # Call trigger
                trigger()
                # Print traceback
                apport_python_hook.apport_excepthook(exc.__class__, exc, exc.__traceback__)
                # Stop python
                sys.exit(1)
        return wrapper
    return decorator


SERIAL_INPUT_EVENT_TYPE = pg.event.custom_type()


class SerialInputCollector(Thread):
    collector: SerialInputCollector | None = None

    def __init__(self):
        super().__init__()
        self.serial = serial.Serial("/dev/ttyUSB0")
        self.do_listen = False

        if not self.serial.isOpen():
            self.serial.open()

    def __new__(cls, *args, **kwargs):
        """
        Allow only one listener.
        :param args:
        :param kwargs:
        """
        if cls.collector is None or not cls.collector.do_listen:
            ret = super().__new__(cls, *args, **kwargs)
            cls.collector = ret
        return cls.collector

    def start(self):
        self.do_listen = True
        super().start()

    def run(self):
        while self.do_listen:
            data = self.serial.read()
            pg.event.post(pg.event.Event(SERIAL_INPUT_EVENT_TYPE, {"key": data}))

    def stop(self):
        self.do_listen = False
        self.serial.cancel_read()


@catch_errors(lambda: SerialInputCollector.collector.stop() if SerialInputCollector.collector else None)
def main():
    pg.init()
    size = (600, 600)
    display = pg.display.set_mode(size)
    clock = pg.time.Clock()
    input_collector = SerialInputCollector()
    input_collector.start()
    playing = game(display, clock)
    while playing:
        playing = game(display, clock)
    input_collector.stop()


def game(display: pg.Surface, clock: pg.time.Clock):
    size = display.get_size()
    board_size = ((size[0] // 10) - 10, (size[1] // 10) - 10)
    food = {(26, 25)}
    snake = deque([(25, 25)])
    snake_segments: set[tuple[int, int]] = {(25, 25)}
    snake_x = 25
    snake_y = 25
    snake_x_change = 1
    snake_y_change = 0
    food_eat_cycle = 0
    required_food = 2
    frames_per_snake_step = 30
    frames_to_snake_step = 0
    snake_alive = True
    dead_show_red = False
    font = pg.font.SysFont("", 30)
    death_message = "You have died. PRESS OK to play again."
    death_surface = font.render(death_message, False, (127, 127, 127))
    death_rect = death_surface.get_rect()
    death_rect.center = (size[0] // 2, size[1] - 25)

    def check_pos(x: int, y: int, do_food: bool):
        if not (0 <= x < board_size[0]) or not (0 <= y < board_size[1]):
            return False
        xy = (x, y)
        if xy in snake_segments:
            return False
        if do_food and xy in food:
            return False
        return True

    def simple_spawn_thing():
        x = randint(0, board_size[0])
        y = randint(0, board_size[1])
        if check_pos(x, y, True):
            return True, x, y
        x = randint(0, board_size[0])
        y = randint(0, board_size[1])
        if check_pos(x, y, True):
            return True, x, y
        x = randint(0, board_size[0])
        y = randint(0, board_size[1])
        if check_pos(x, y, True):
            return True, x, y
        return False, x, y

    def spawn_thing():
        success, x, y = simple_spawn_thing()
        if success:
            food.add((x, y))
            return True

        tested = set()
        possible = set()

        def possible_add(xy):
            if xy not in tested:
                possible.add(xy)

        def populate_possible():
            if x - 1 >= 0:
                possible_add((x - 1, y))
            if y - 1 >= 0:
                possible_add((x, y - 1))
            if x + 1 >= board_size[0]:
                possible_add((x + 1, y))
            if y + 1 >= board_size[1]:
                possible_add((x, y + 1))

        # TODO: finish flood fill
        return False
        populate_possible()
        while len(possible):
            goto = possible.copy()
            possible.clear()
            for pos in possible:
                pass

    def spawn_food():
        for _ in range(required_food - len(food)):
            spawn_thing()

    def move_snake():
        nonlocal food_eat_cycle, required_food, frames_per_snake_step, snake_x, snake_y
        snake_x += snake_x_change
        snake_y += snake_y_change
        snake_head = (snake_x, snake_y)
        if snake_head in food:
            food.remove(snake_head)
            spawn_food()
            food_eat_cycle += 1
            if food_eat_cycle >= 3:
                food_eat_cycle = 0
                required_food += 1
                frames_per_snake_step -= 2
                if frames_per_snake_step < 4:
                    frames_per_snake_step = 4
        else:
            snake_segments.remove(snake.popleft())

        ret = check_pos(snake_x, snake_y, False)
        snake.append(snake_head)
        snake_segments.add(snake_head)

        return ret

    def snake_movement(x_change: int, y_change: int):
        nonlocal snake_x_change, snake_y_change
        if x_change * -1 == snake_x_change and y_change * -1 == snake_y_change:
            return  # Can't move snake to itself
        snake_x_change = x_change
        snake_y_change = y_change

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            elif event.type == SERIAL_INPUT_EVENT_TYPE:
                if event.key == b"u":
                    snake_movement(0, -1)
                elif event.key == b"r":
                    snake_movement(1, 0)
                elif event.key == b"d":
                    snake_movement(0, 1)
                elif event.key == b"l":
                    snake_movement(-1, 0)
                elif event.key == b"*":
                    snake_alive = False
                elif event.key == b"#":
                    return False
                elif event.key == b"o":
                    if not snake_alive:
                        return True

        frames_to_snake_step += 1
        if frames_to_snake_step >= frames_per_snake_step:
            frames_to_snake_step = 0
            if snake_alive:
                snake_alive = move_snake()
            else:
                dead_show_red = not dead_show_red

        display.fill((0, 0, 0))
        pg.draw.rect(display, (255, 255, 255), (50, 50, 500, 500))

        for thing in food:
            pg.draw.rect(display, (255, 0, 0), ((thing[0] + 5) * 10, (thing[1] + 5) * 10, 10, 10))

        for segment in snake:
            pg.draw.rect(display, (0, 255, 0), ((segment[0] + 5) * 10, (segment[1] + 5) * 10, 10, 10))

        if not snake_alive:
            display.blit(death_surface, death_rect)
            if dead_show_red:
                pg.draw.rect(display, (255, 0, 0), ((snake_x + 5) * 10, (snake_y + 5) * 10, 10, 10))

        pg.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
