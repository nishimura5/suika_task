import math
from itertools import combinations

import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256
GRAVITY = 0.4
AIR_RESISTANCE = 0.96


ball_types = {
    "red": {"radius": 10, "color": 8},
    "orange": {"radius": 12, "color": 9},
    "blue": {"radius": 20, "color": 12},
    "purple": {"radius": 30, "color": 2},
    "yellow": {"radius": 36, "color": 10},
    "green": {"radius": 42, "color": 3},
    "white": {"radius": 50, "color": 7},
    "black": {"radius": 60, "color": 6},
}
level_table = [k for k in ball_types.keys()]


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Ball:
    def __init__(self, ball_id, x, y, name):
        self.id = ball_id
        self.pos = Vector(x, y)
        self.level = level_table.index(name)
        self.radius = ball_types[name]["radius"]
        self.color = ball_types[name]["color"]

        self.vel = Vector(0, 0)

    def update(self):
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0
        if abs(self.vel.y) < 0.2:
            self.vel.y = 0

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.pos.y + self.radius > SCREEN_HEIGHT:
            self.pos.y = SCREEN_HEIGHT - self.radius
            self.vel.y = -self.vel.y * 0.5
            self.vel.x *= 0.5
        if self.pos.x + self.radius > SCREEN_WIDTH:
            self.pos.x = SCREEN_WIDTH - self.radius
        elif self.pos.x - self.radius < 0:
            self.pos.x = self.radius


class Gauge:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = 5
        self.color = 7
        self.value = 0

    def reset(self):
        self.value = 0

    def count_up(self):
        self.value += 0.5
        if self.value > 10:
            self.value = 10

    def draw(self):
        pyxel.rect(self.x, self.y, self.value, self.height, self.color)


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Suika Task", capture_scale=1)

        self.last_ball_id = 0
        self.balls = []
        self.cursor_x = SCREEN_WIDTH // 2

        self.gauge = Gauge(10, 10)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.move_cursor()
        self.drop_ball()

        for ball in self.balls:
            ball.vel.y += GRAVITY
            ball.vel.x *= AIR_RESISTANCE
            ball.vel.y *= AIR_RESISTANCE

        combi_list = list(combinations(self.balls, 2))
        for a, b in combi_list:
            theta = colliding(a, b)
            if theta is None:
                continue
            if theta == "levelup":
                # Remove balls a and b from the list
                self.balls = [
                    ball for ball in self.balls if ball.id not in [a.id, b.id]
                ]
                if a.level == len(level_table) - 1:
                    continue
                # Create a new ball with the average position of a and b
                new_ball = level_table[a.level + 1]
                self.create_ball(
                    (a.pos.x + b.pos.x) / 2, (a.pos.y + b.pos.y) / 2, new_ball
                )
                # Prevent the new ball from colliding with a and b
                a.level = -1
                b.level = -1
        for ball in self.balls:
            ball.update()

    def draw(self):
        pyxel.cls(0)
        pyxel.line(0, 20, SCREEN_WIDTH, 20, 7)
        pyxel.rect(self.cursor_x - 5, 0, 10, 10, 7)
        for ball in self.balls:
            pyxel.circ(ball.pos.x, ball.pos.y, ball.radius - 1, ball.color)
        self.gauge.draw()

    def create_ball(self, x, y, name):
        self.balls.append(Ball(self.last_ball_id, x, y, name))
        self.last_ball_id += 1

    def move_cursor(self):
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.cursor_x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.cursor_x += 2
        self.cursor_x = max(0, min(SCREEN_WIDTH, self.cursor_x))

    def drop_ball(self):
        gauge_val = self.gauge.value
        if gauge_val < 10:
            self.gauge.count_up()
            return

        if pyxel.btnr(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.create_ball(self.cursor_x, 10, "red")
            self.gauge.reset()


def colliding(ball_a, ball_b):
    dx = ball_a.pos.x - ball_b.pos.x
    if abs(dx) < 1:
        dx = pyxel.rndf(-2, 2)
    dy = ball_a.pos.y - ball_b.pos.y
    distance = (dx**2 + dy**2) ** 0.5
    normal_x = dx / distance
    normal_y = dy / distance
    penetration_depth = (ball_a.radius + ball_b.radius) - distance
    if penetration_depth <= 0:
        return None
    if penetration_depth > 0 and ball_a.level == ball_b.level:
        return "levelup"

    penet_x = penetration_depth * normal_x
    penet_y = penetration_depth * normal_y

    ball_a.vel.x += penet_x
    ball_a.vel.y += penet_y
    ball_b.vel.x -= penet_x
    ball_b.vel.y -= penet_y

    return None


App()
