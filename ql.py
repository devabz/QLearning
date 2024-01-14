import math
import random

import numpy as np
import pandas as pd
import pygame.draw

from environment import *


class QL:
    SARSA: bool = False

    begin: bool = False
    PREPPED: bool = False
    next_step: bool = True
    flow: bool = False

    look_ahead: int = 1
    memory: int = 12
    memory_thr: float = 0.5

    learning_rate: float = 0.7
    discount: float = 0.8
    spread_ratio: float = 0.9
    spread_discount: int = 0

    randomness: float = 1
    randomness_decay: float = randomness / 1800
    randomness_floor: float = 0.000000005
    add_random: bool = True

    current_reward: float = 0
    sum_rewards: float = 0

    steps: float = 0
    steps_xpo: float = 1
    t_steps: float = 0
    max_steps: int = 0
    min_steps: int = 0
    m_steps = []
    c_steps = 0
    episodes: float = 0

    prev_move: list = []
    prev_moves: list = []

    did_good: bool = False
    did_bad: bool = False

    log_CHECK_ACTION_STATEMENTS: bool = False
    log_STATS: bool = False
    log_DIAGNOSIS: bool = True

    CHEAT = True

    ILM_Limit = -1000
    TICK = 0
    TICK_LIMIT = 1

    SCORE_LIMIT = -100_000

    def __init__(self, env_: Environment):
        self.env: Environment = env_
        self.START_POS = self.env.start_pos
        self.pos: vector = self.START_POS
        self.size = int(x_sqr * 1.6)

        self.memory_map = {(x, y): 0 for y in range(y_sqr) for x in range(x_sqr)}
        self.memory_list = []

        self.cheat_rewards: dict[str, float] = {'ILM': -30,
                                                'DLY': -2}

        self.q_Table: pd.DataFrame = self._SET_Q_TABLE()
        # self.cheat_REMOVE_ILLEGAL_MOVES()

    def draw_AI(self, screen_):
        C = (self.pos + vector(0.5, 0.5)) * sqr_size
        pygame.draw.circle(screen_,
                           color_book[colors['ai'] % len(color_book)],
                           C,
                           self.size,
                           self.size)

        self._do_action(screen_)

    def _SET_Q_TABLE(self) -> pd.DataFrame:
        idx = pd.MultiIndex.from_arrays([[node.pos.x for node in self.env.nodes],
                                         [node.pos.y for node in self.env.nodes]],
                                        names=['x', 'y'])

        return pd.DataFrame(np.zeros((idx.shape[0], len(list(self.env.actions)))),
                            index=idx,
                            columns=list(self.env.actions))

    def cheat_REMOVE_ILLEGAL_MOVES(self):
        if self.CHEAT:
            for pos in self.q_Table.index:
                for action in self.env.actions:
                    check_action = vector(pos) + self.env.actions[action]()
                    if check_action.x < 0 or check_action.x > x_sqr - 1 or check_action.y < 0 or check_action.y > y_sqr - 1:
                        if int(self.q_Table.loc[pos[0], pos[1]].loc[action]) > self.ILM_Limit:
                            self.q_Table.loc[pos[0], pos[1]].loc[action] += self.cheat_rewards['ILM']

    def _get_actions(self, screen_: pygame.display, pos_: vector):
        temp = []
        for action in self.env.actions:
            check_action = pos_ + self.env.actions[action]()
            if static_validate_pos(check_action):
                value = self._helper_look_ahead(check_action, screen_, self.look_ahead)
                temp.append([value, list(check_action), action])

        return sorted(temp)[::-1]

    def _do_action(self, screen_):
        if self.PREPPED:
            self._helper_check_terminal()
            if self.next_step or self.flow:
                options = self._get_actions(screen_, self.pos)
                # print(options)
                # print(f"Epsilon: {round(self.randomness, 2)}")
                self.prev_move = [self.pos, options[0][2], options[0][0]]
                if self._add_randomness_():
                    self.do_random_action(options)
                else:
                    self.pos = vector(options[0][1])
                self.next_step = False
                self.cheat_keep_history()
                self.steps += 1
                self.t_steps += 1

    def do_random_action(self, options):
        if self.randomness < self.randomness_floor:
            self.randomness = self.randomness_floor

        action = random.choice(options)
        self.pos = vector(action[1])

    def _add_randomness_(self):
        if self.add_random:
            if random.random() < self.randomness:
                self.randomness -= self.randomness_decay
                return True
            else:
                return False
        else:
            return False

    def _helper_get_future_x_reward(self, pos_: vector):
        return list(self.q_Table.loc[pos_.x, pos_.y])

    def _helper_look_ahead(self, pos_: vector, screen_, depth=look_ahead):
        if depth > 0:
            depth -= 1

            sum_ = 0
            for action in self.env.actions:
                check_action = pos_ + self.env.actions[action]()
                if static_validate_pos(check_action):
                    C = (check_action + vector(0.5, 0.5)) * sqr_size
                    if depth == 1:
                        # pygame.draw.circle(screen_, "blue", C, 8, 8)
                        pass
                    sum_ = self._helper_look_ahead(check_action, screen_, depth)
            return int((self.discount**depth) * (sum(self._helper_get_future_x_reward(pos_)) + sum_))
        else:
            return 0

    def _helper_check_terminal(self):
        if self.pos in self.env.goal_nodes:
            self.did_good = True
            if self.TICK == self.TICK_LIMIT:
                self.q_Table.loc[self.pos.x,
                                 self.pos.y].loc[self.prev_move[1]] += self.env.rewards['goal']

                self.pos = vector(self.env.start_pos)
                self.TICK = 0
                # self._helper_spread_proximity_goal(self.pos, self.env.rewards['goal'], self.look_ahead)
                self._helper_update_node_value()
                self.spread_discount = 0
                self._reset_stats()
                self.sum_rewards += self.env.rewards['goal']

                # print(self.q_Table)

            self.TICK += 1

        elif self.pos in self.env.obs_nodes:
            if self.TICK == self.TICK_LIMIT:
                self.q_Table.loc[self.pos.x,
                                 self.pos.y].loc[self.prev_move[1]] += self.env.rewards['obstacle']
                self.TICK = 0
                self._helper_spread_proximity_obs(self.pos, self.env.rewards['obstacle'], self.look_ahead)
                self.pos = vector(self.env.start_pos)
                self._helper_update_node_value()
                self.spread_discount = 0
                self._reset_stats()
                self.sum_rewards += self.env.rewards['obstacle']

                # print(self.q_Table)

            self.TICK += 1

    def _helper_spread_proximity_obs(self, pos_: vector, value, depth=look_ahead):
        depth_lim = self.look_ahead + 1
        if depth > 0:
            print("OG: ", value)
            depth -= 1
            self.spread_discount += 1
            for action in self.env.actions:
                check_action = pos_ + self.env.actions[action]()
                if static_validate_pos(check_action):

                    bonus = 0

                    dc = self.spread_ratio ** self.spread_discount
                    value_ = int(math.log2(1 + abs(value * (self.spread_ratio ** (depth - depth_lim)))) * dc) // 10

                    if not self.env.nodes_dict[pos_.x, pos_.y].is_goal:
                        if self.env.nodes_dict[pos_.x, pos_.y].is_obstacle:
                            bonus = -20
                        else:
                            bonus = 0
                        if sum(list(self.q_Table.loc[pos_.x, pos_.y])) < -20:
                            self.q_Table.loc[pos_.x,
                                             pos_.y].loc[action] += value_ + bonus
                    else:
                        self.q_Table.loc[pos_.x,
                                         pos_.y].loc[action] += value_
                    print(self.q_Table.loc[self.START_POS.x, self.START_POS.y])
                    self._helper_spread_proximity_obs(check_action, value, depth)
                    self.sum_rewards += value_ + bonus

        else:
            return 0

    def cheat_keep_history(self):
        if self.pos not in self.memory_list:
            self.memory_list.append(self.pos)

        if self.pos in self.memory_list:
            self.q_Table.loc[self.prev_move[0].x,
                             self.prev_move[0].y].loc[self.prev_move[1]] += self.cheat_rewards['DLY']

    def _helper_update_node_value(self):
        for node in self.env.nodes:
            node.color_adj = int(sum(list(self.q_Table.loc[node.pos.x, node.pos.y])))
            if node.color_adj > 2000:
                pass

    def clear_Q_Map(self):
        for idx in self.q_Table.index:
            for action in self.env.actions:
                self.q_Table.loc[idx].loc[action] = 0

    def _reset_stats(self):
        if self.did_good:
            self.m_steps.append(self.steps)
            self.c_steps = self.m_steps[-1]
            self.max_steps = max(self.m_steps)
            self.min_steps = min(self.m_steps)
            self.did_good = False
        self.steps = 0
        self.steps_xpo = 0
        self.episodes += 1
