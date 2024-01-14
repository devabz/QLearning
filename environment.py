from config import *
from color_book import color_book
from pygame.math import Vector2 as vector
from static_library import *
import pygame
import numpy as np
import pandas as pd
import random


class Node:
    def __init__(self, x, y):
        self.is_goal = False
        self.is_obstacle = False
        self.is_start = False

        self.pos = vector(x, y)
        self.rect: pygame.Rect = pygame.Rect(self.pos.x * sqr_size,
                                             self.pos.y * sqr_size,
                                             sqr_size,
                                             sqr_size)

        self.color = colors['ally']
        self.color_adj = 0

    def draw_node(self, screen_):
        if self.is_goal:
            self.color = colors['goal']

        elif self.is_obstacle:
            self.color = colors['obstacle']

        elif self.is_start:
            self.color = colors['start']

        else:
            self.color = colors['ally']
        pygame.draw.rect(screen_, color_book[(self.color) % len(color_book)], self.rect)
        font = pygame.font.SysFont(pygame.font.get_fonts()[2], 12, True)
        text = font.render(f"{self.color_adj}", True, "white")
        text_pos = self.pos * sqr_size + vector(text.get_width(), text.get_width())//2
        screen_.blit(text, text_pos)


class Environment:

    def __init__(self):
        self.nodes = [Node(x, y) for y in range(y_sqr) for x in range(x_sqr)]
        self.nodes_dict: dict[tuple, Node] = {(node.pos.x, node.pos.y): node for node in self.nodes}
        self.start_pos = vector(x_sqr - 1, y_sqr - 1)

        self.goal_nodes = []
        self.obs_nodes = []

        self.actions = {'up': env_1_move_up,
                        'down': env_1_move_down,
                        'left': env_1_move_left,
                        'right': env_1_move_right}

        self.rewards = {'goal': 500,
                        'obstacle': -100,
                        'ally': -0.5,
                        'delay': -1}

        idx = pd.MultiIndex.from_arrays([[node.pos.x for node in self.nodes],
                                         [node.pos.y for node in self.nodes]],
                                        names=['x', 'y'])
        self.reward_map = pd.DataFrame(np.zeros(idx.shape),
                                       index=idx,
                                       columns=['reward'])

    def draw_environment(self, screen_):
        for node in self.nodes:
            node.draw_node(screen_)

    def prep_reward_map(self):
        for node in self.nodes:
            if node.is_goal:
                self.reward_map.loc[node.pos.x, node.pos.y] = self.rewards['goal']
            elif node.is_obstacle:
                self.reward_map.loc[node.pos.x, node.pos.y] = self.rewards['obstacle']
            else:
                self.reward_map.loc[node.pos.x, node.pos.y] = self.rewards['ally']

