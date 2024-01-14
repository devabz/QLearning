import pygame.event

from ql import *

pygame.init()
SCREEN = pygame.display.set_mode((scr[2], scr[1]))
CLOCK = pygame.time.Clock()


class FrameWork:
    CLOCK = CLOCK
    SCREEN = SCREEN
    BG_COLOR_IDX = 0

    def __init__(self):
        self.env = Environment()
        self.AI = QL(self.env)
        self.menu = Menu(self)

        self._RUN: bool = True
        self._PREP: bool = False
        self._PREPPED: bool = False
        self._CLEARED: bool = False
        self._GOAL_SET: bool = False
        self._OBSTACLES_SET: bool = False

        self.enable_C_KEYS: bool = True

    def RUN_SIMULATION(self):

        while self._RUN:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self._RUN = False

                if event.type == pygame.KEYDOWN:
                    pass

                    if event.key == pygame.K_RETURN:
                        if not self._PREPPED:
                            self._PREP = True
                            if self._PREP:
                                self._prep_simulation()
                                self._PREP = False
                                self._PREPPED = True
                                self.AI.flow = True
                                self.AI.PREPPED = True
                        else:
                            self.AI.flow = not self.AI.flow

                    elif event.key == pygame.K_n:
                        # print(self.AI.q_Table)
                        if not self._PREPPED:
                            self._PREP = True
                            if self._PREP:
                                self._prep_simulation()
                                self._PREP = False
                                self._PREPPED = True
                        else:
                            self.AI.next_step = not self.AI.next_step

                    elif event.key == pygame.K_SPACE:
                        colors['ally'] += 1
                        print(f"COLOR: {colors['ally']}")

                    elif event.key == pygame.K_0:
                        self._GOAL_SET = not self._GOAL_SET

                    elif event.key == pygame.K_1:
                        pass

                    elif event.key == pygame.K_9:

                        self.clear_maze()
                        self._generate_maze()
                        self._update_reward_map()

                    elif event.key == pygame.K_8:
                        self.clear_maze()
                        self._update_reward_map()
                    if self.enable_C_KEYS:
                        self._enable_control_keys(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._get_goal_obs_position()
                    self._update_reward_map()
                    self._read_menu_buttons()

            if self._PREPPED:
                if not self._CLEARED:
                    self.AI.clear_Q_Map()
                    self._CLEARED = True

            self._draw_Environment()
            self._draw_AI()
            self._enable_menu()

            self._update()

    def _prep_simulation(self):
        self.env.prep_reward_map()

        self._PREPPED = True
        self.AI.begin = True

    def _update_reward_map(self):
        self.env.prep_reward_map()

    def _draw_Environment(self):
        self.env.nodes_dict[self.AI.START_POS.x, self.AI.START_POS.x].is_start = True
        self.env.draw_environment(self.SCREEN)
        self.env.nodes_dict[self.AI.START_POS.x, self.AI.START_POS.x].color = colors['start']

    def _draw_AI(self):
        self.AI.draw_AI(self.SCREEN)

    def _get_goal_obs_position(self):
        pos_ = vector(pygame.mouse.get_pos()) // sqr_size
        if 0 <= pos_.x < x_sqr and 0 <= pos_.y < y_sqr:
            if not self._GOAL_SET:
                if not self.env.nodes_dict[pos_.x, pos_.y].is_obstacle:
                    if not self.env.nodes_dict[pos_.x, pos_.y].is_goal:
                        self.env.nodes_dict[pos_.x, pos_.y].is_goal = True
                        if pos_ not in self.env.goal_nodes:
                            self.env.goal_nodes.append(pos_)

                    else:
                        self.env.nodes_dict[pos_.x, pos_.y].is_goal = False
                        for old_pos in self.env.goal_nodes:
                            if old_pos == pos_:
                                self.env.goal_nodes.remove(old_pos)

            if self._GOAL_SET:
                if not self.env.nodes_dict[pos_.x, pos_.y].is_goal:
                    if not self.env.nodes_dict[pos_.x, pos_.y].is_obstacle:
                        self.env.nodes_dict[pos_.x, pos_.y].is_obstacle = True
                        if pos_ not in self.env.obs_nodes:
                            self.env.obs_nodes.append(pos_)

                    else:
                        self.env.nodes_dict[pos_.x, pos_.y].is_obstacle = False
                        for old_pos in self.env.obs_nodes:
                            if old_pos == pos_:
                                self.env.obs_nodes.remove(old_pos)

    def _update(self):
        static_DRAW_GRID(self.SCREEN)
        self._update_reward_map()
        pygame.display.update()
        self.CLOCK.tick(framerate)

    def _generate_maze(self):

        for node in self.env.obs_nodes:
            self.env.nodes_dict[node.x, node.y].is_obstacle = False

        blocks = random.randint(5, 8)
        pos_ = []
        for _ in range(blocks):
            x_ = random.randint(0, x_sqr - 1)
            y_ = random.randint(0, y_sqr - 1)
            shift = random.randint(0, x_sqr - 1)

            if random.random() < 0.5:
                pos_.append([vector(x_, (y + shift) % (y_sqr - 1)) for y in range(y_)])

            else:
                pos_.append([vector((x + shift) % (y_sqr - 1), y_) for x in range(x_)])

        for pos in pos_:
            for node in pos:
                if 0 <= node.x < x_sqr and 0 <= node.y < y_sqr:
                    if node != self.AI.START_POS:
                        self.env.nodes_dict[node.x, node.y].is_obstacle = True
                        if node not in self.env.obs_nodes:
                            self.env.obs_nodes.append(node)

    def clear_maze(self):
        for node in self.env.obs_nodes:
            self.env.nodes_dict[node.x, node.y].is_obstacle = False
        for node in self.env.goal_nodes:
            self.env.nodes_dict[node.x, node.y].is_goal = False

        self.env.obs_nodes.clear()
        self.env.goal_nodes.clear()

    def _enable_control_keys(self, event):
        if event.key == pygame.K_LEFT:
            if static_validate_pos(self.AI.pos + self.env.actions['left']()):
                self.AI.prev_move = self.AI.pos, 'left'
                self.AI.pos += self.env.actions['left']()

        elif event.key == pygame.K_RIGHT:
            if static_validate_pos(self.AI.pos + self.env.actions['right']()):
                self.AI.prev_move = self.AI.pos, 'right'
                self.AI.pos += self.env.actions['right']()

        elif event.key == pygame.K_UP:
            if static_validate_pos(self.AI.pos + self.env.actions['up']()):
                self.AI.prev_move = self.AI.pos, 'up'
                self.AI.pos += self.env.actions['up']()

        elif event.key == pygame.K_DOWN:
            if static_validate_pos(self.AI.pos + self.env.actions['down']()):
                self.AI.prev_move = self.AI.pos, 'down'
                self.AI.pos += self.env.actions['down']()

    def _enable_menu(self):
        self.menu.prep_Buttons()
        self.menu.draw_Menu(self.SCREEN)
        self.menu.act_on_button(self.AI, self.env)

    def _read_menu_buttons(self):
        self.menu.read_button()
        self.menu.settings_read_button()
        self.menu.stats_read_button()


class Menu:
    SETTINGS: bool = False
    STATS: bool = False

    class Button:

        def __init__(self, pos_: tuple, text_: str, tag_: str, id_: int = 0):
            menu = Menu(FrameWork())
            self.text = menu.font.render(text_, True, "white")
            self.rect = pygame.Rect(pos_[0] * sqr_size,
                                    pos_[1] * menu.button_size[1] * sqr_size,
                                    (menu.button_size[0]) * sqr_size,
                                    (menu.button_size[1]) * sqr_size)
            self.id = id_
            self.active = False
            self.tag = tag_

    def __init__(self, framework_: FrameWork):
        self.pos = vector(scr[0], 0)

        self.display = pygame.Surface((x_meny * sqr_size, y_sqr * sqr_size))
        self.stats_display = pygame.Surface((x_meny * sqr_size, y_sqr * sqr_size))
        self.settings_display = pygame.Surface((x_meny * sqr_size, y_sqr * sqr_size))

        self.font = pygame.font.SysFont(pygame.font.get_fonts()[2], int(0.6 * sqr_size), True)
        self.font_2 = pygame.font.SysFont(pygame.font.get_fonts()[2], int(0.4 * sqr_size), True)

        self.buttons = []
        self.buttons_dict: dict = {}
        self.text_fields = []
        self.button_size = (x_meny, 2)
        self.button_pad = 7
        self.button_positions = []
        self.COLORS = colors_2
        self.BG_COLOR_IDX = 1
        self.FRAMEWORK = framework_

        self.settings_buttons = []
        self.settings_buttons_dict = {}
        self.settings_button_positions = []

        self.stats_buttons = []
        self.stats_buttons_dict = {}
        self.stats_button_positions = []

    def draw_Menu(self, screen_: pygame.display):
        self.draw_buttons()
        screen_.blit(self.display, self.pos)

    def prep_Buttons(self):
        self.create_button((0, 0), "Change Settings", "settings")
        self.create_button((0, 1), "See Stats", "stats")
        self.create_button((0, 2), "Reset Maze", "reset_maze")
        self.create_button((0, 3), "Reset Q Map", "reset_q_map")
        self.create_button((0, 4), "Change Background", "change_bg")

        self.settings_create_button((0, 0), "Randomness", "randomness")
        self.settings_create_button((0, 1), "Randomness Decay", "randomDecay")
        self.settings_create_button((0, 2), "Learning Rate", "learningRate")
        self.settings_create_button((0, 3), "Discount Rate", "discountRate")
        self.settings_create_button((0, 4), "Back To Main", "B2M")

        self.stats_create_button((0, 0), "Back To Main", "B2M")

    def create_button(self, pos_: tuple, text_: str, tag: str):

        if list(pos_) not in self.button_positions:
            temp = self.Button(pos_, text_, tag, len(self.buttons))
            self.buttons.append(temp)
            self.button_positions.append(list(pos_))
            self.buttons_dict[tag] = temp

    def read_button(self):
        pos_ = vector(pygame.mouse.get_pos())
        if not self.SETTINGS:
            if scr[0] <= pos_.x:
                for idx, button in enumerate(self.buttons):
                    thr_x = self.pos[0], button.rect.width + self.pos[0]
                    thr_y = self.pos[1], button.rect.height + self.pos[1]
                    if thr_x[0] < pos_.x < thr_x[1] and thr_y[0] < pos_.y < button.rect.y + thr_y[1]:

                        button.active = not button.active
                        print(f"{button.tag} : {button.active}")
                        for button_2 in self.buttons:
                            if button != button_2:
                                button_2.active = False
                        break
                    else:
                        button.active = False

    def act_on_button(self, AI: QL, env: Environment):
        if self.buttons_dict["change_bg"].active:
            self.BG_COLOR_IDX += 1
            colors['ally'] = colors_2['ally'][self.BG_COLOR_IDX % len(colors_2['ally'])]
            self.buttons_dict['change_bg'].active = False
            print(f"{self.buttons_dict['change_bg'].tag} : {self.buttons_dict['change_bg'].active}")

        if self.buttons_dict["reset_q_map"].active:
            AI.clear_Q_Map()
            self.buttons_dict['reset_q_map'].active = False
            print(f"{self.buttons_dict['reset_q_map'].tag} : {self.buttons_dict['reset_q_map'].active}")

        if self.buttons_dict["settings"].active:
            self.SETTINGS = True
            self.STATS = False
            self._enable_settings_()
            self.display.blit(self.settings_display, (0, 0))

        if self.buttons_dict["stats"].active:
            self.STATS = True
            self.SETTINGS = False
            self._enable_stats_()
            pygame.draw.rect(self.display, "black", pygame.Rect(20,  20, 44, 80))
            self.display.blit(self.stats_display, (0, 0))

        if self.buttons_dict["reset_maze"].active:
            self.FRAMEWORK.clear_maze()
            self.buttons_dict["reset_maze"].active = False

        if self.settings_buttons_dict["B2M"].active:
            self.SETTINGS = False
            self.STATS = False
            self.settings_buttons_dict["B2M"].active = False
            self.stats_buttons_dict["B2M"].active = False
            self.buttons_dict["settings"].active = False

        if self.stats_buttons_dict["B2M"].active:
            self.SETTINGS = False
            self.STATS = False
            self.settings_buttons_dict["B2M"].active = False
            self.stats_buttons_dict["B2M"].active = False
            self.buttons_dict["settings"].active = False

    def draw_buttons(self):
        if not self.SETTINGS and not self.STATS:
            if len(self.buttons) > 0:
                for button in self.buttons[::-1]:
                    decrease = 0
                    if button.active:
                        pygame.draw.rect(self.display, color_book[555 % len(color_book)], button.rect)
                        decrease = 8
                    pygame.draw.rect(self.display, "black", button.rect, decrease)
                    self.display.blit(button.text,
                                      (button.rect.x + self.button_size[
                                          0] * sqr_size // 2 - button.text.get_width() // 2,
                                       button.rect.y + button.text.get_height() // 2 + self.button_pad))

    def settings_create_button(self, pos_: tuple, text_: str, tag: str):

        if list(pos_) not in self.settings_button_positions:
            temp = self.Button(pos_, text_, tag, len(self.settings_buttons))
            self.settings_buttons.append(temp)
            self.settings_button_positions.append(list(pos_))
            self.settings_buttons_dict[tag] = temp

    def settings_draw_buttons(self):
        if self.SETTINGS and not self.STATS:
            if len(self.settings_buttons) > 0:
                for button in self.settings_buttons[::-1]:
                    decrease = 0
                    if button.active:
                        pygame.draw.rect(self.settings_display, color_book[555 % len(color_book)], button.rect)
                        decrease = 8
                    pygame.draw.rect(self.settings_display, "black", button.rect, decrease)
                    self.settings_display.blit(button.text,
                                               (button.rect.x + self.button_size[
                                                   0] * sqr_size // 2 - button.text.get_width() // 2,
                                                button.rect.y + button.text.get_height() // 2 + self.button_pad))

    def settings_read_button(self):
        pos_ = vector(pygame.mouse.get_pos())
        if self.SETTINGS and not self.STATS:
            if scr[0] <= pos_.x:
                for idx, button in enumerate(self.settings_buttons):
                    thr_x = self.pos[0], button.rect.width + self.pos[0]
                    thr_y = self.pos[1], button.rect.height + self.pos[1]
                    if thr_x[0] < pos_.x < thr_x[1] and thr_y[0] < pos_.y < button.rect.y + thr_y[1]:

                        button.active = not button.active
                        print(f"{button.tag} : {button.active}")
                        for button_2 in self.settings_buttons:
                            if button != button_2:
                                button_2.active = False
                        break
                    else:
                        button.active = False

    def _enable_settings_(self):
        if self.SETTINGS and not self.STATS:
            self.settings_draw_buttons()

    def stats_create_button(self, pos_: tuple, text_: str, tag: str):

        if list(pos_) not in self.stats_button_positions:
            temp = self.Button(pos_, text_, tag, len(self.stats_buttons))
            self.stats_buttons.append(temp)
            self.stats_button_positions.append(list(pos_))
            self.stats_buttons_dict[tag] = temp

    def stats_draw_buttons(self):
        if self.STATS and not self.SETTINGS:
            if len(self.stats_buttons) > 0:
                for button in self.stats_buttons[::-1]:
                    decrease = 0
                    if button.active:
                        pygame.draw.rect(self.stats_display, color_book[555 % len(color_book)], button.rect)
                        decrease = 8
                    pygame.draw.rect(self.stats_display, "black", button.rect, decrease)
                    self.stats_display.blit(button.text,
                                            (button.rect.x + self.button_size[
                                                0] * sqr_size // 2 - button.text.get_width() // 2,
                                             button.rect.y + button.text.get_height() // 2 + self.button_pad))

    def stats_read_button(self):
        pos_ = vector(pygame.mouse.get_pos())
        if self.STATS and not self.SETTINGS:
            if scr[0] <= pos_.x:
                for idx, button in enumerate(self.stats_buttons):
                    thr_x = self.pos[0], button.rect.width + self.pos[0]
                    thr_y = self.pos[1], button.rect.height + self.pos[1]
                    if thr_x[0] < pos_.x < thr_x[1] and thr_y[0] < pos_.y < button.rect.y + thr_y[1]:

                        button.active = not button.active
                        print(f"{button.tag} : {button.active}")
                        for button_2 in self.stats_buttons:
                            if button != button_2:
                                button_2.active = False
                        break
                    else:
                        button.active = False

    def _enable_stats_(self):
        if self.STATS and not self.SETTINGS:
            self.stats_draw_buttons()
            self._log_stats()

    def _log_stats(self):
        AI = self.FRAMEWORK.AI
        traits = {'episodes': AI.episodes,
                  'steps': AI.steps,
                  'current step': AI.c_steps,
                  'min steps': AI.min_steps,
                  'max steps': AI.max_steps,
                  'total steps': AI.t_steps,
                  'total rewards': AI.sum_rewards,
                  'randomness': round(AI.randomness, 2),
                  'learning rate': AI.learning_rate}

        spacing = (y_sqr * (sqr_size*(1 - 0.2))) // (len(traits) + 1)
        pad = 50

        for idx, trait in enumerate(traits):
            txt = self.font_2.render(f"{trait} : {traits[trait]}", True, "white")
            pygame.draw.rect(self.stats_display,
                             "black",
                             pygame.Rect(20, spacing*(idx + 1) + pad, txt.get_width() + 20, txt.get_height()))
            self.stats_display.blit(txt, (20, spacing * (idx + 1) + pad))


