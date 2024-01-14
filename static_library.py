import pygame
from config import *


def static_validate_pos(pos_: pygame.math.Vector2):
    if 0 <= pos_.x < x_sqr and 0 <= pos_.y < y_sqr:
        return True
    else:
        return False


def static_DRAW_GRID(screen_: pygame.Surface):
    S = pygame.Surface((scr[0], scr[1]))
    S.fill("white")
    S.set_alpha(20)
    for y in range(y_sqr):
        pygame.draw.line(screen_, "black", (0, y * sqr_size), (scr[0], y * sqr_size), 3)

    for x in range(x_sqr):
        pygame.draw.line(screen_, "black", (x * sqr_size, 0), (x * sqr_size, scr[1]), 3)

    screen_.blit(S, (0, 0))


def env_1_move_right():
    return [1, 0]


def env_1_move_left():
    return [-1, 0]


def env_1_move_up():
    return [0, -1]


def env_1_move_down():
    return [0, 1]
