"""
Example of running simple snake game with pygame and pyserial.
"""
from __future__ import annotations

from collections import deque
from threading import Thread
from random import randint


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
    board_size = ((600 // 10) - 10, (600 // 10) - 10)
    display = pg.display.set_mode(size)
    done = False
    food = {(26, 25)}
    snake = deque([(25, 25)])
    snake_segments: set[tuple[int, int]] = {(25, 25)}
    snake_x = 25
    snake_y = 25
    snake_x_change = 1
    snake_y_change = 0
    food_eat_cycle = 0
    required_food = 1
    frames_per_snake_step = 30
    frames_to_snake_step = 0
    clock = pg.time.Clock()
    input_collector = SerialInputCollector()
    input_collector.start()

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
        return
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
        snake.append(snake_head)
        snake_segments.add(snake_head)
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

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
                input_collector.do_listen = False
                input_collector.serial.cancel_read()
            elif event.type == SERIAL_INPUT_EVENT_TYPE:
                print(event.key)

        frames_to_snake_step += 1
        if frames_to_snake_step >= frames_per_snake_step:
            frames_to_snake_step = 0
            move_snake()
            print("step")

        display.fill((0, 0, 0))
        pg.draw.rect(display, (255, 255, 255), (50, 50, 500, 500))

        for thing in food:
            pg.draw.rect(display, (255, 0, 0), ((thing[0] + 5) * 10, (thing[1] + 5) * 10, 10, 10))

        for segment in snake:
            pg.draw.rect(display, (0, 255, 0), ((segment[0] + 5) * 10, (segment[1] + 5) * 10, 10, 10))

        pg.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
