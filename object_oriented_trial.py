# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from datetime import datetime

from board_execution import execution_boards, start_execution_positions
import pygame
import math
import time
import pylsl
import os

ASSETS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

dev_mode = True

# TODO: Add the other player and a second way to check time and turns.
# Instead of making a copy of everything, comparmentalize the things into functions in another file and then call them.
# Otherwise you'll have to repeat everything.

if not dev_mode:
    # LSL COMMUNICATION
    def lsl_mrk_outlet(name):
        info = pylsl.stream_info(name, 'Markers', 1, 0, pylsl.cf_string, 'ID66666666')
        outlet = pylsl.stream_outlet(info, 1, 1)
        print('pacman created result outlet.')
        return outlet


    mrkstream_allowed_turn_out = lsl_mrk_outlet('Allowed_Turn_Markers')  # important this is first

# GAME
pygame.init()
current_level = 0  # Inicialmente, el nivel 0 está en juego

# Dimensions
display_info = pygame.display.Info()  # Get the monitor's display info
WIDTH = int(display_info.current_h)
HEIGHT = int(display_info.current_h)

level = copy.deepcopy(execution_boards[current_level])
div_width = len(level[0])
div_height = len(level)
yscale = HEIGHT // div_height
xscale = WIDTH // div_width

# 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60  # This decides how fast the game goes. Including pacman and ghosts.
font = pygame.font.Font("freesansbold.ttf", 30)
color = "white"
PI = math.pi
total_game_time = []
total_game_turns = []
level_turns = []

## Images import
player_images = [pygame.transform.scale(pygame.image.load(f'assets/extras_images/right.png'), (xscale, yscale)),
                 pygame.transform.scale(pygame.image.load(f'assets/extras_images/left.png'), (xscale, yscale)),
                 pygame.transform.scale(pygame.image.load(f'assets/extras_images/forward.png'), (xscale, yscale)),
                 pygame.transform.scale(pygame.image.load(f'assets/extras_images/back.png'),
                                        (xscale, yscale))]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/arrow.png"), (xscale, yscale)
)
arrow_images = [
    pygame.transform.rotate(arrow, -90),
    pygame.transform.rotate(arrow, 90),
    arrow,
    pygame.transform.rotate(arrow, 180),
]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
cookie = pygame.transform.scale(pygame.image.load(f'assets/extras_images/cookie.png'), (xscale, yscale))

## Sounds import
sound_thud = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'sounds', 'thud.mp3'))
sound_go = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'sounds', 'go.mp3'))
sound_win = pygame.mixer.Sound(os.path.join(ASSETS_PATH, 'sounds', 'finish a level.mp3'))
sound_win.set_volume(0.5)

## Positions
start = start_execution_positions[current_level]
player_1_player_x = int(start[0] * xscale)
player_1_player_y = int(start[1] * yscale)
player_2_player_x = int(start[0] * xscale)
player_2_player_y = int(start[1] * yscale)
player_1_direction = start[2]
player_1_last_direction = start[2]
player_2_direction = start[2]
player_2_last_direction = start[2]
# Other
player_1_turns_allowed = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
player_2_turns_allowed = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
player_1_direction_command = start[2]
player_2_direction_command = start[2]
if dev_mode:
    player_1_speed = 5
    player_2_speed = 5
    original_speed = 5
else:
    player_1_speed = 1
    player_2_speed = 1
    original_speed = 1
moving = False
startup_counter = 0
counter = 0
flicker = False
game_over = False
game_won = False
play_won_flag = True
last_activate_turn_tile = [4, 4]  # Check that in all levels this is a 0 pixel
player_1_time_to_corner = 0
player_2_time_to_corner = 0


def draw_misc():
    gameover_text = font.render("¡Nivel Completado!", True, "red")
    if game_over:
        pygame.draw.rect(screen, "gray", [WIDTH * .05, HEIGHT * .1, WIDTH * .9, HEIGHT * .8], 0, 10)
        pygame.draw.rect(screen, "green", [WIDTH * .1, HEIGHT * .2, WIDTH * .8, HEIGHT * .6], 0, 10)
        gameover_text2 = font.render("¡Gracias por participar!", True, "red")
        gameover_text3 = font.render("Ya puedes cerrar la ventana.", True, "red")
        screen.blit(gameover_text, (xscale * 13, HEIGHT // 3))
        screen.blit(gameover_text2, (xscale * 12, HEIGHT // 2))
        screen.blit(gameover_text3, (xscale * 11, xscale * 20))
    elif game_won:
        pygame.draw.rect(screen, "gray", [WIDTH * .05, HEIGHT * .1, WIDTH * .9, HEIGHT * .8], 0, 10)
        pygame.draw.rect(screen, "green", [WIDTH * .1, HEIGHT * .2, WIDTH * .8, HEIGHT * .6], 0, 10)
        gameover_text2 = font.render("¡Prepárate para el siguiente nivel!", True, "red")
        screen.blit(gameover_text, (xscale * 13, HEIGHT // 3))
        screen.blit(gameover_text2, (xscale * 9, HEIGHT // 2))


class Player:
    def __init__(self, last_direction, last_activate_turn_tile, original_speed, time_to_corner, direction, player_x,
                 player_y, turns_allowed):
        self.direction: int = direction
        self.player_x: float = player_x
        self.player_y: float = player_y
        self.center_x: float = self.player_x + xscale // 2
        self.center_y: float = self.player_y + yscale // 2
        self.turns_allowed: list[bool] = turns_allowed
        self.last_direction: int = last_direction
        self.last_activate_turn_tile: list = last_activate_turn_tile
        self.player_speed: int = original_speed
        self.time_to_corner: float = time_to_corner

    def draw_player(self, direction: int, last_direction: int, player_x: float, player_y: float):
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        self.direction = direction
        self.last_direction = last_direction
        self.player_x, self.player_y = player_x, player_y
        for direction_idx in range(0, 4):
            if direction_idx == self.direction:
                self.last_direction = self.direction
                screen.blit(player_images[self.direction], (self.player_x, self.player_y))
        if self.direction == 4:
            screen.blit(player_images[self.last_direction], (self.player_x, self.player_y))
        return self.last_direction

    def move_player(self, direction: int, turns_allowed: list[bool], player_x: float, player_y: float,
                    player_speed: int):
        self.direction = direction
        self.turns_allowed = turns_allowed
        self.player_x, self.player_y = player_x, player_y
        self.player_speed = player_speed
        if self.direction == 0 and self.turns_allowed[0]:
            self.player_x += self.player_speed
        elif self.direction == 1 and self.turns_allowed[1]:
            self.player_x -= self.player_speed
        elif self.direction == 2 and self.turns_allowed[2]:
            self.player_y -= self.player_speed
        elif self.direction == 3 and self.turns_allowed[3]:
            self.player_y += self.player_speed
        return self.player_x, self.player_y

    def check_collisions(self, player_speed: int, time_to_corner: float):
        self.player_speed = player_speed
        self.time_to_corner = time_to_corner
        corner_check = copy.deepcopy(self.turns_allowed)
        corner_check[self.direction] = False
        if 1 <= level[self.center_y // yscale][self.center_x // xscale] <= 2:
            level[self.center_y // yscale][self.center_x // xscale] = 0
        if sum(corner_check) >= 2 or corner_check == self.turns_allowed:
            if level[self.last_activate_turn_tile[0]][
                self.last_activate_turn_tile[1]] != -1 and self.time_to_corner > 10:
                sound_thud.play()
                level[self.center_y // yscale][self.center_x // xscale] = -1
                self.last_activate_turn_tile = [self.center_y // yscale, self.center_x // xscale]
                self.player_speed = 0
        elif level[self.last_activate_turn_tile[0]][self.last_activate_turn_tile[1]] == -1:
            sound_go.play()
            level[self.last_activate_turn_tile[0]][self.last_activate_turn_tile[1]] = 0
            self.player_speed = original_speed
            self.time_to_corner = 0
        return self.player_speed, self.time_to_corner

    def check_position(self, direction: int, center_x: float, center_y: float):
        self.direction = direction
        self.center_x = center_x
        self.center_y = center_y
        self.turns_allowed = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        half_scale = xscale // 2 + 5
        if self.direction == 2 or self.direction == 3:
            if xscale // 3 <= self.center_x % xscale <= xscale:
                if level[(self.center_y + half_scale) // yscale][self.center_x // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (self.center_x, (self.center_y + half_scale)), 20,
                                                    10)
                    self.turns_allowed[3] = True
                if level[(self.center_y - half_scale - 10) // yscale][self.center_x // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (self.center_x, (self.center_y - half_scale - 10)),
                                                    20, 10)
                    self.turns_allowed[2] = True
            if yscale // 3 <= self.center_y % yscale <= yscale:
                if level[self.center_y // yscale][(self.center_x - xscale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (self.center_x - xscale, self.center_y), 20, 10)
                    self.turns_allowed[1] = True
                if level[self.center_y // yscale][(self.center_x + xscale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (self.center_x + xscale, self.center_y), 20, 10)
                    self.turns_allowed[0] = True
        elif self.direction == 0 or self.direction == 1:
            if xscale // 3 <= self.center_x % xscale <= xscale:
                if level[(self.center_y + yscale) // yscale][self.center_x // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'green', (self.center_x, self.center_y + yscale), 20, 10)
                    self.turns_allowed[3] = True
                if level[(self.center_y - yscale) // yscale][self.center_x // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'green', (self.center_x, self.center_y - yscale), 20, 10)
                    self.turns_allowed[2] = True
            if yscale // 3 <= self.center_y % yscale <= yscale:
                if level[self.center_y // yscale][(self.center_x - half_scale - 8) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'white', ((self.center_x - half_scale - 8), self.center_y),
                                                    20, 10)
                    self.turns_allowed[1] = True
                if level[self.center_y // yscale][(self.center_x + half_scale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'red', ((self.center_x + half_scale), self.center_y), 20,
                                                    10)
                    self.turns_allowed[0] = True
        return self.turns_allowed


def draw_board(color):
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(
                    screen,
                    "white",
                    (j * xscale + (0.5 * xscale), i * yscale + (0.5 * yscale)),
                    4,
                )
            if level[i][j] == 2:  # and not flicker: # The flicker could affect the brain frequency
                screen.blit(cookie, (j * xscale, i * yscale))
            if level[i][j] == 3:
                pygame.draw.line(
                    screen,
                    color,
                    (j * xscale + (0.5 * xscale), i * yscale),
                    (j * xscale + (0.5 * xscale), i * yscale + yscale),
                    3,
                )
            if level[i][j] == 4:
                pygame.draw.line(
                    screen,
                    color,
                    (j * xscale, i * yscale + (0.5 * yscale)),
                    (j * xscale + xscale, i * yscale + (0.5 * yscale)),
                    3,
                )
            if level[i][j] == 5:
                pygame.draw.arc(
                    screen,
                    color,
                    [
                        (j * xscale - (xscale * 0.4)),
                        (i * yscale + (0.5 * yscale)),
                        xscale,
                        yscale,
                    ],
                    0,
                    PI / 2,
                    3,
                )
            if level[i][j] == 6:
                pygame.draw.arc(
                    screen,
                    color,
                    [(j * xscale + (xscale * 0.5)), (i * yscale + (0.5 * yscale)), xscale, yscale],
                    PI / 2,
                    PI,
                    3,
                )
            if level[i][j] == 7:
                pygame.draw.arc(
                    screen,
                    color,
                    [(j * xscale + (xscale * 0.5)), (i * yscale - (0.4 * yscale)), xscale, yscale],
                    PI,
                    3 * PI / 2,
                    3,
                )
            if level[i][j] == 8:
                pygame.draw.arc(
                    screen,
                    color,
                    [
                        (j * xscale - (xscale * 0.4)),
                        (i * yscale - (0.4 * yscale)),
                        xscale,
                        yscale,
                    ],
                    3 * PI / 2,
                    2 * PI,
                    3,
                )
            if level[i][j] == 9:
                pygame.draw.line(
                    screen,
                    "white",
                    (j * xscale, i * yscale + (0.5 * yscale)),
                    (j * xscale + xscale, i * yscale + (0.5 * yscale)),
                    3,
                )
            if level[i][j] == -1:
                pygame.draw.rect(
                    screen,
                    "yellow",
                    [j * xscale + (-0.5 * xscale), i * yscale + (-0.5 * yscale), 60, 60],
                    border_radius=10,
                )


player_1 = Player(player_1_last_direction, last_activate_turn_tile, original_speed, player_1_time_to_corner,
                  player_1_direction, int(start[0] * xscale),
                  int(start[1] * yscale), player_1_turns_allowed)
player_2 = Player(player_1_last_direction, last_activate_turn_tile, original_speed, player_2_time_to_corner,
                  player_2_direction, int(start[0] * xscale),
                  int(start[1] * yscale), player_2_turns_allowed)

run = True
first_movement = True
start_time = time.time()
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    if startup_counter < 180 and not game_over and not game_won and not dev_mode:
        moving = False
        startup_counter += 1
    elif startup_counter < fps * 20 and not game_won and not dev_mode:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill("black")
    draw_board(color)

    game_won = False
    flat_level_list = [
        x
        for xs in level
        for x in xs
    ]
    if 2 not in flat_level_list:
        if play_won_flag:
            sound_win.play()
            total_game_time.append('{:.2f}'.format(time.time() - start_time))
            total_game_turns.append(level_turns[1:])
            play_won_flag = False
        if len(start_execution_positions) == current_level + 1:
            game_over = True
        game_won = True

    player_1_last_direction = draw_player(player_1_direction, player_1_last_direction, player_1_player_x,
                                          player_1_player_y)
    player_2_last_direction = draw_player(player_2_direction, player_2_last_direction, player_2_player_x,
                                          player_2_player_y)

    draw_misc()

    player_1_time_to_corner += 1
    player_2_time_to_corner += 1

    player_1_turns_allowed = check_position(player_1_direction, player_1_player_x, player_1_player_y)
    player_2_turns_allowed = check_position(player_2_direction, player_2_player_x, player_2_player_y)

    if moving:
        player_1_player_x, player_1_player_y = move_player(player_1_direction, player_1_turns_allowed,
                                                           player_1_player_x, player_1_player_y, player_1_speed)
        player_2_player_x, player_2_player_y = move_player(player_2_direction, player_2_turns_allowed,
                                                           player_2_player_x, player_2_player_y, player_2_speed)

    player_1_speed, player_1_time_to_corner = check_collisions(player_1_speed, player_1_time_to_corner)
    player_2_speed, player_2_time_to_corner = check_collisions(player_2_speed, player_2_time_to_corner)

    # mrkstream_allowed_turn_out.push_sample(pylsl.vectorstr([str(player_1_turns_allowed)]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and player_1_speed == 0:
            if event.key == pygame.K_RIGHT and player_1_turns_allowed[0]:
                level_turns.append(player_1_direction)
                player_1_direction_command = 0
                player_1_speed = original_speed
            elif event.key == pygame.K_LEFT and player_1_turns_allowed[1]:
                level_turns.append(player_1_direction)
                player_1_direction_command = 1
                player_1_speed = original_speed
            elif event.key == pygame.K_UP and player_1_turns_allowed[2]:
                level_turns.append(player_1_direction)
                player_1_direction_command = 2
                player_1_speed = original_speed
            elif event.key == pygame.K_DOWN and player_1_turns_allowed[3]:
                level_turns.append(player_1_direction)
                player_1_direction_command = 3
                player_1_speed = original_speed

            if event.key == pygame.K_d and player_2_turns_allowed[0]:
                level_turns.append(player_2_direction)
                player_2_direction_command = 0
                player_2_speed = original_speed
            elif event.key == pygame.K_a and player_2_turns_allowed[1]:
                level_turns.append(player_2_direction)
                player_2_direction_command = 1
                player_2_speed = original_speed
            elif event.key == pygame.K_w and player_2_turns_allowed[2]:
                level_turns.append(player_2_direction)
                player_2_direction_command = 2
                player_2_speed = original_speed
            elif event.key == pygame.K_s and player_2_turns_allowed[3]:
                level_turns.append(player_2_direction)
                player_2_direction_command = 3
                player_2_speed = original_speed

            if event.key == pygame.K_SPACE and game_over:
                total_game_time.append('{:.2f}'.format(time.time() - start_time))
                total_game_turns.append(level_turns[1:])
                run = False
            elif event.key == pygame.K_SPACE and game_won:
                play_won_flag = True
                first_movement = True
                draw_misc()
                pygame.display.flip()
                startup_counter = 0
                current_level += 1
                if dev_mode:
                    player_1_speed = 5
                    player_2_speed = 5
                    original_speed = 5
                else:
                    player_1_speed = 1
                    player_2_speed = 1
                    original_speed = 1
                if current_level < len(execution_boards):
                    level = copy.deepcopy(execution_boards[current_level])
                    start = start_execution_positions[current_level]
                    player_1_direction = start[2]
                    player_2_direction = start[2]
                    player_1 = Player(last_activate_turn_tile, original_speed, player_1_time_to_corner,
                                      player_1_direction, int(start[0] * xscale), int(start[1] * yscale),
                                      player_1_turns_allowed)
                    player_2 = Player(last_activate_turn_tile, original_speed, player_2_time_to_corner,
                                      player_2_direction, int(start[0] * xscale), int(start[1] * yscale),
                                      player_2_turns_allowed)
                    direction_command = start[2]
                game_won = False
                start_time = time.time()
                level_turns = []

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and player_1_direction_command == 0:
                player_1_direction_command = player_1_direction
            elif event.key == pygame.K_LEFT and player_1_direction_command == 1:
                player_1_direction_command = player_1_direction
            elif event.key == pygame.K_UP and player_1_direction_command == 2:
                player_1_direction_command = player_1_direction
            elif event.key == pygame.K_DOWN and player_1_direction_command == 3:
                player_1_direction_command = player_1_direction

            if event.key == pygame.K_d and player_2_direction_command == 0:
                player_2_direction_command = player_2_direction
            elif event.key == pygame.K_a and player_2_direction_command == 1:
                player_2_direction_command = player_2_direction
            elif event.key == pygame.K_w and player_2_direction_command == 2:
                player_2_direction_command = player_2_direction
            elif event.key == pygame.K_s and player_2_direction_command == 3:
                player_2_direction_command = player_2_direction

    for direction_index in range(0, 4):
        if player_1_direction_command == direction_index and player_1_turns_allowed[direction_index]:
            player_1_direction = direction_index
        if player_2_direction_command == direction_index and player_2_turns_allowed[direction_index]:
            player_2_direction = direction_index
    pygame.display.flip()
pygame.quit()

# Here in case someone decides to finish the game (NOT RECOMMENDED FOR ANALYSIS).
# If the user doesn't want to continue, at least the progress stays.
filename = datetime.now().strftime('game_variables_%H%M_%m%d%Y.txt')

file = open(os.path.join(ASSETS_PATH, 'game_saved_files', filename), 'w')
file.write('tutorial_1, tutorial_2, tutorial_3, singleplayer_1, singleplayer_2\n')
file.write(f'{total_game_time}\n')
file.write(f'{total_game_turns}\n')
file.close()