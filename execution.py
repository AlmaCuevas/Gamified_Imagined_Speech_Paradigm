# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from datetime import datetime
import collections
import random

from board_execution import multiplayer_execution_boards, multiplayer_player_1_start_execution_positions, multiplayer_player_2_start_execution_positions, singleplayer_start_execution_positions, singleplayer_execution_boards, tutorial_player_1_start_execution_positions, tutorial_execution_boards
import pygame
import math
import time
import pylsl
import os

# The report file will only be saved when the game finishes without quitting.
# You don't have to close or open a new game to select a different mode.

# TODO: Redo calibration idea with this version, add the option in menu

# TODO: Once you have that, send the EEG piece to the processing and receive the answer (in execution version)
# TODO: Run the full calibration with training and then testing with executions (both multiplayer and singleplayer)

# LSL COMMUNICATION
def lsl_mrk_outlet(name, number_subject=''):
    info = pylsl.stream_info(name + str(number_subject), 'Markers', 1, 0, pylsl.cf_string, 'ID0123456789')
    outlet = pylsl.stream_outlet(info, 1, 1)
    print(f'Brain Command created result outlet: {name}, for Player {number_subject}.')
    return outlet


def lsl_inlet(name, number_subject=''):
    info = pylsl.resolve_stream('name', name + str(number_subject))
    inlet = pylsl.stream_inlet(info[0], recover=False)
    print(f'Brain Command has received the {info[0].type()} inlet: {name}, for Player {number_subject}.')
    return inlet

def play_game(game_mode: str):
    ASSETS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))

    if game_mode=='Tutorial':
        player_1_start_execution_positions = tutorial_player_1_start_execution_positions
        player_2_start_execution_positions = multiplayer_player_2_start_execution_positions # It doesn't matter
        execution_boards = tutorial_execution_boards
    elif game_mode == 'Multiplayer':
        player_1_start_execution_positions = multiplayer_player_1_start_execution_positions
        player_2_start_execution_positions = multiplayer_player_2_start_execution_positions
        execution_boards = multiplayer_execution_boards
    elif game_mode == 'Singleplayer':
        player_1_start_execution_positions = singleplayer_start_execution_positions
        player_2_start_execution_positions = multiplayer_player_2_start_execution_positions # It doesn't matter
        execution_boards = singleplayer_execution_boards

    dev_mode = True
    if not dev_mode:
        mrkstream_out = lsl_mrk_outlet('Task_Markers')  # important this is first

        # Wait for a marker, then start recording EEG data
        start_time_1 = 0
        data_1 = collections.deque()
        prediction_movement_1_out = lsl_mrk_outlet('Result', 1)
        eeg_1_in = lsl_inlet('player', 1)  # Don't use special characters or uppercase for the name
        if game_mode == 'Multiplayer':
            start_time_2 = 0
            prediction_movement_2_out = lsl_mrk_outlet('Result', 2)
            eeg_2_in = lsl_inlet('player', 2)  # Don't use special characters or uppercase for the name
            data_2 = collections.deque()


    # GAME
    pygame.init()
    current_level: int = 0  # Inicialmente, el nivel 0 está en juego
    # Dimensions
    display_info = pygame.display.Info()  # Get the monitor's display info
    WIDTH = int(display_info.current_h)
    HEIGHT = int(display_info.current_h)

    level = copy.deepcopy(execution_boards[current_level])
    flat_level_list = [
        x
        for xs in level
        for x in xs
    ]
    cookies_at_the_beginning = flat_level_list.count(2)
    div_width: int = len(level[0])
    div_height: int = len(level)
    yscale: int = HEIGHT // div_height
    xscale: int = WIDTH // div_width

    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    timer = pygame.time.Clock()
    fps = 60  # This decides how fast the game goes. Including pacman and ghosts.
    font = pygame.font.Font("RetroFont.ttf", 30)
    color = "white"
    PI = math.pi
    total_game_time: list = []
    player_1_total_game_turns: list = []
    player_1_level_turns: list[int] = []

    ## All Player 2
    player_2_total_game_turns: list = []
    player_2_level_turns: list[int] = []

    ## Images import
    player_2_images: list = [
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/right_2.png'), (xscale*2, yscale*2)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/left_2.png'), (xscale*2, yscale*2)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/forward_2.png'), (xscale*2, yscale*2)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/back_2.png'), (xscale*2, yscale*2))]

    start_2: list = player_2_start_execution_positions[current_level]
    player_2_player_x: int = int(start_2[0] * xscale)
    player_2_player_y: int = int(start_2[1] * yscale)
    player_2_direction: int = start_2[2]
    player_2_last_direction: int = start_2[2]
    player_2_direction_command: int = start_2[2]
    prediction_movement_2: int = start_2[2]
    player_2_last_activate_turn_tile: list[int] = [4, 4]
    player_2_time_to_corner: int = 0

    ## Images import
    player_1_images: list = [
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/right_1.png'), (xscale*2, yscale*2)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/left_1.png'), (xscale*2, yscale*2)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/forward_1.png'), (xscale*2, yscale*2)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/back_1.png'),
                               (xscale*2, yscale*2))]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

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
    sound_win.set_volume(0.3)

    channel = pygame.mixer.Channel(0)

    ## Positions
    start_1: list = player_1_start_execution_positions[current_level]
    player_1_player_x: int = int(start_1[0] * xscale)
    player_1_player_y: int = int(start_1[1] * yscale)
    player_1_direction: int = start_1[2]
    player_1_last_direction: int = start_1[2]
    prediction_movement_1: int = start_1[2]
    start_time_1 = 0
    start_time_2 = 0

    ## Other
    player_1_direction_command: int = start_1[2]
    if dev_mode:
        player_1_speed: int = 5
        original_speed: int = 5
        player_2_speed: int = 5
    else:
        player_1_speed: int = 5
        original_speed: int = 5
        player_2_speed: int = 5
    moving: bool = False
    startup_counter: int = 0
    counter: int = 0
    flicker: bool = False
    game_over: bool = False
    game_won: bool = False
    play_won_flag: bool = True
    player_1_last_activate_turn_tile: list[int] = [4, 4]  # Check that in all levels this is a 0 pixel
    player_1_time_to_corner: int = 0
    cookie_winner: list = []
    cookie_winner_2_num: int = 0

    def draw_text(text: str):
        font = pygame.font.Font("RetroFont.ttf", 300)
        txt_render = font.render(text, True, "red")
        screen.blit(txt_render,
                    (WIDTH / 2 - txt_render.get_width() / 2, HEIGHT / 2 - txt_render.get_height() / 2))

    def draw_misc(player_num: int, game_mode: str):
        level_done = font.render("¡Nivel Completado!", True, "red")
        if game_mode == 'Multiplayer':
            congrats_winner_str = f"¡Felicidades jugador {player_num}!"
        else:
            congrats_winner_str = "¡Felicidades!"
        congrats_winner = font.render(congrats_winner_str, True, "red")
        if game_over:
            pygame.draw.rect(screen, "gray", [WIDTH * .05, HEIGHT * .1, WIDTH * .9, HEIGHT * .8], 0, 10)
            pygame.draw.rect(screen, "green", [WIDTH * .1, HEIGHT * .2, WIDTH * .8, HEIGHT * .6], 0, 10)
            thanks_for_participating = font.render("¡Gracias por jugar!", True, "red")

            screen.blit(thanks_for_participating,
                        (WIDTH / 2 - thanks_for_participating.get_width() / 2, HEIGHT / 2 - thanks_for_participating.get_height() / 2 + 100))
            screen.blit(congrats_winner,
                            (WIDTH / 2 - congrats_winner.get_width() / 2, HEIGHT / 2 - congrats_winner.get_height() / 2 - 100))
            screen.blit(level_done,
                        (WIDTH / 2 - level_done.get_width() / 2, HEIGHT / 2 - level_done.get_height() / 2))
        elif game_won:
            pygame.draw.rect(screen, "gray", [WIDTH * .05, HEIGHT * .1, WIDTH * .9, HEIGHT * .8], 0, 10)
            pygame.draw.rect(screen, "green", [WIDTH * .1, HEIGHT * .2, WIDTH * .8, HEIGHT * .6], 0, 10)
            prepare_for_next_level = font.render("¡Prepárate para el siguiente nivel!", True, "red")
            screen.blit(prepare_for_next_level,
                        (WIDTH / 2 - prepare_for_next_level.get_width() / 2, HEIGHT / 2 - prepare_for_next_level.get_height() / 2 + 100))
            screen.blit(congrats_winner,
                            (WIDTH / 2 - congrats_winner.get_width() / 2, HEIGHT / 2 - congrats_winner.get_height() / 2 - 100))
            screen.blit(level_done,
                        (WIDTH / 2 - level_done.get_width() / 2, HEIGHT / 2 - level_done.get_height() / 2))


    def check_collisions(last_activate_turn_tile, player_speed, time_to_corner, turns_allowed, direction, center_x,
                         center_y, level, player_num, start_time):
        cookie_winner_num = 0
        if player_num == 2:
            right_volume = 0
            left_volume = 1
        else:
            right_volume = 1
            left_volume = 0
        corner_check = copy.deepcopy(turns_allowed)
        corner_check[direction] = False
        if level[center_y // yscale][center_x // xscale] == 1:
            level[center_y // yscale][center_x // xscale] = 0
        elif level[center_y // yscale][center_x // xscale] == 2:
            cookie_winner_num = player_num
            level[center_y // yscale][center_x // xscale] = 0
        if sum(corner_check) >= 2 or corner_check == turns_allowed:
            if level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] != -1 * player_num and time_to_corner > 10:
                channel.play(sound_thud)
                start_time = time.time()
                channel.set_volume(right_volume, left_volume)
                level[center_y // yscale][center_x // xscale] = -1 * player_num
                last_activate_turn_tile = [center_y // yscale, center_x // xscale]
                player_speed = 0
        elif level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] == -1 * player_num:
            channel.play(sound_go)
            if not dev_mode: mrkstream_out.push_sample(pylsl.vectorstr([f'end_corner_{player_num}']))
            channel.set_volume(right_volume, left_volume)
            level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] = 0
            player_speed = original_speed
            time_to_corner = 0
        return last_activate_turn_tile, player_speed, time_to_corner, level, cookie_winner_num, start_time

    def draw_player(direction, last_direction, player_x, player_y, player_images):
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        for direction_idx in range(0, 4):
            if direction_idx == direction:
                last_direction = direction
                screen.blit(player_images[direction], (player_x - xscale/2, player_y - yscale/2))
        if direction == 4:
            screen.blit(player_images[last_direction], (player_x - xscale/2, player_y - yscale/2))
        return last_direction

    def check_position(direction, centerx, centery, level):
        turns = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        half_scale = xscale // 2 + 5
        if direction == 2 or direction == 3:
            if xscale // 3 <= centerx % xscale <= xscale:
                if level[(centery + half_scale) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx, (centery + half_scale)), 20, 1)
                    turns[3] = True
                if level[(centery - half_scale - 10) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx, (centery - half_scale - 10)), 20, 1)
                    turns[2] = True
            if yscale // 3 <= centery % yscale <= yscale:
                if level[centery // yscale][(centerx - xscale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx - xscale, centery), 20, 1)
                    turns[1] = True
                if level[centery // yscale][(centerx + xscale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx + xscale, centery), 20, 1)
                    turns[0] = True
        elif direction == 0 or direction == 1:
            if xscale // 3 <= centerx % xscale <= xscale:
                if level[(centery + yscale) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'green', (centerx, centery + yscale), 20, 1)
                    turns[3] = True
                if level[(centery - yscale) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'green', (centerx, centery - yscale), 20, 1)
                    turns[2] = True
            if yscale // 3 <= centery % yscale <= yscale:
                if level[centery // yscale][(centerx - half_scale - 8) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'white', ((centerx - half_scale - 8), centery), 20, 1)
                    turns[1] = True
                if level[centery // yscale][(centerx + half_scale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'red', ((centerx + half_scale), centery), 20, 1)
                    turns[0] = True
        return turns

    def move_player(direction, turns_allowed, play_x, play_y, player_speed):
        # r, l, u, d
        # If current direction is right and right is allowed, move right
        if direction == 0 and turns_allowed[0]:
            play_x += player_speed
        elif direction == 1 and turns_allowed[1]:
            play_x -= player_speed
        elif direction == 2 and turns_allowed[2]:
            play_y -= player_speed
        elif direction == 3 and turns_allowed[3]:
            play_y += player_speed
        return play_x, play_y

    def draw_board(level: list, color: str, center_1_x: float, center_1_y: float, center_2_x: float = 0, center_2_y: float = 0):
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
                        "pink",
                        [center_1_x - xscale, center_1_y - yscale, 60, 60],
                        border_radius=10,
                    )
                if level[i][j] == -2:
                    pygame.draw.rect(
                        screen,
                        "pink",
                        [center_2_x - xscale, center_2_y - yscale, 60, 60],
                        border_radius=10,
                    )
        return level

    run = True
    start_time = time.time()
    while run:
        timer.tick(fps)
        screen.fill("black")
        if counter < 19:
            counter += 1
            if counter > 3:
                flicker = False
        else:
            counter = 0
            flicker = True
        if startup_counter < 200 and not game_over and not game_won and not dev_mode:
            moving = False
            startup_counter += 1
            if startup_counter < 60:
                draw_text('3')
            elif startup_counter < 120:
                draw_text('2')
            elif startup_counter < 180:
                draw_text('1')
            else:
                draw_text('GO!')
        else:
            moving = True

        player_1_center_x = player_1_player_x + xscale // 2
        player_1_center_y = player_1_player_y + yscale // 2
        if game_mode == 'Multiplayer':
            player_2_center_x = player_2_player_x + xscale // 2
            player_2_center_y = player_2_player_y + yscale // 2
            level = draw_board(level, color, player_1_center_x, player_1_center_y, player_2_center_x, player_2_center_y)
        else:
            level = draw_board(level, color, player_1_center_x, player_1_center_y)

        draw_misc(cookie_winner[-1:], game_mode)

        if moving and not game_won and not game_over:
            player_1_last_direction = draw_player(player_1_direction, player_1_last_direction, player_1_player_x, player_1_player_y, player_1_images)
            if game_mode == 'Multiplayer': player_2_last_direction = draw_player(player_2_direction, player_2_last_direction, player_2_player_x, player_2_player_y, player_2_images)



            player_1_turns_allowed = check_position(player_1_direction, player_1_center_x, player_1_center_y, level)
            if game_mode == 'Multiplayer': player_2_turns_allowed = check_position(player_2_direction, player_2_center_x, player_2_center_y, level)

            ## Section to process direction prediction with the EEG.
            # TODO: Put it in a Function and call it instead
            if not dev_mode:
                movement_option = [0, 1, 2, 3]
                eeg_1, t_eeg_1 = eeg_1_in.pull_sample(timeout=0)

                if time.time() - start_time_1 > 1.4 and player_1_speed == 0: # Duration is 1.4s
                    start_time_1 = 0
                    ## HERE IS WHERE THE PROCESSING CALL GO! Replace the two lines below
                    allowed_1_movement_random = [x for x, flag in zip(movement_option, player_1_turns_allowed) if flag]
                    prediction_movement_1 = allowed_1_movement_random[random.randint(0, len(allowed_1_movement_random)-1)] # exclusive range
                    print(f'Player 1. Classifier returned: {prediction_movement_1}')
                    prediction_movement_1_out.push_sample(pylsl.vectorstr([str(prediction_movement_1)]))

                    player_1_level_turns.append(player_1_direction_command)
                    player_1_direction_command = prediction_movement_1
                    player_1_speed = original_speed
                    data_1 = collections.deque()
                else:
                    if eeg_1 is not None:
                        data_1.append([t_eeg_1, *eeg_1])
                if game_mode == 'Multiplayer':
                    eeg_2, t_eeg_2 = eeg_2_in.pull_sample(timeout=0)
                    if time.time() - start_time_2 > 1.4 and player_2_speed == 0:
                        start_time_2 = 0
                        ## HERE IS WHERE THE PROCESSING CALL GO! Replace the two lines below
                        allowed_2_movement_random = [x for x, flag in zip(movement_option, player_2_turns_allowed) if flag]
                        prediction_movement_2 = allowed_2_movement_random[
                            random.randint(0, len(allowed_2_movement_random) - 1)]  # exclusive range
                        print(f'Player 2. Classifier returned: {prediction_movement_2}')
                        prediction_movement_2_out.push_sample(pylsl.vectorstr([str(prediction_movement_2)]))
                        data_2 = collections.deque()
                        player_2_speed = original_speed

                        player_2_level_turns.append(player_2_direction_command)
                        player_2_direction_command = prediction_movement_2

                    else:
                        if eeg_2 is not None:
                            data_2.append([t_eeg_2, *eeg_2])



            player_1_player_x, player_1_player_y = move_player(player_1_direction, player_1_turns_allowed, player_1_player_x, player_1_player_y, player_1_speed)
            if game_mode == 'Multiplayer': player_2_player_x, player_2_player_y = move_player(player_2_direction, player_2_turns_allowed, player_2_player_x, player_2_player_y, player_2_speed)

            player_1_last_activate_turn_tile, player_1_speed, player_1_time_to_corner, level, cookie_winner_1_num, start_time_1 = check_collisions(player_1_last_activate_turn_tile, player_1_speed, player_1_time_to_corner, player_1_turns_allowed, player_1_direction, player_1_center_x, player_1_center_y, level, 1, start_time_1)
            if game_mode == 'Multiplayer': player_2_last_activate_turn_tile, player_2_speed, player_2_time_to_corner, level, cookie_winner_2_num, start_time_2 = check_collisions(player_2_last_activate_turn_tile, player_2_speed, player_2_time_to_corner, player_2_turns_allowed, player_2_direction, player_2_center_x, player_2_center_y, level, 2, start_time_2)


            ## Section to decide if the game is finished.
            # TODO: Put it in a Function and call it instead
            game_won = False
            flat_level_list = [
                x
                for xs in level
                for x in xs
            ]
            if cookies_at_the_beginning != flat_level_list.count(2):
                if play_won_flag:
                    if cookie_winner_1_num:
                        cookie_winner.append(cookie_winner_1_num)
                    elif cookie_winner_2_num and game_mode == 'Multiplayer':
                        cookie_winner.append(cookie_winner_2_num)
                    sound_win.play()
                    total_game_time.append('{:.2f}'.format(time.time() - start_time))
                    player_1_total_game_turns.append(player_1_level_turns[1:])
                    if game_mode == 'Multiplayer': player_2_total_game_turns.append(player_2_level_turns[1:])
                    play_won_flag = False
                if len(player_1_start_execution_positions) == current_level+1:
                    game_over = True
                game_won = True

            player_1_time_to_corner += 1
            if game_mode == 'Multiplayer': player_2_time_to_corner += 1

            for direction_index in range(0, 4):
                if player_1_direction_command == direction_index and player_1_turns_allowed[direction_index]:
                    player_1_direction = direction_index
                if game_mode == 'Multiplayer':
                    if player_2_direction_command == direction_index and player_2_turns_allowed[direction_index]:
                        player_2_direction = direction_index

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if (player_1_speed == 0 or player_2_speed == 0) and dev_mode:
                    if event.key == pygame.K_RIGHT and player_1_turns_allowed[0]:
                        player_1_level_turns.append(player_1_direction)
                        player_1_direction_command = 0
                        player_1_speed = original_speed
                    elif event.key == pygame.K_LEFT and player_1_turns_allowed[1]:
                        player_1_level_turns.append(player_1_direction)
                        player_1_direction_command = 1
                        player_1_speed = original_speed
                    elif event.key == pygame.K_UP and player_1_turns_allowed[2]:
                        player_1_level_turns.append(player_1_direction)
                        player_1_direction_command = 2
                        player_1_speed = original_speed
                    elif event.key == pygame.K_DOWN and player_1_turns_allowed[3]:
                        player_1_level_turns.append(player_1_direction)
                        player_1_direction_command = 3
                        player_1_speed = original_speed

                    if game_mode == 'Multiplayer':
                        if event.key == pygame.K_d and player_2_turns_allowed[0]:
                            player_2_level_turns.append(player_2_direction)
                            player_2_direction_command = 0
                            player_2_speed = original_speed
                        elif event.key == pygame.K_a and player_2_turns_allowed[1]:
                            player_2_level_turns.append(player_2_direction)
                            player_2_direction_command = 1
                            player_2_speed = original_speed
                        elif event.key == pygame.K_w and player_2_turns_allowed[2]:
                            player_2_level_turns.append(player_2_direction)
                            player_2_direction_command = 2
                            player_2_speed = original_speed
                        elif event.key == pygame.K_s and player_2_turns_allowed[3]:
                            player_2_level_turns.append(player_2_direction)
                            player_2_direction_command = 3
                            player_2_speed = original_speed

                if event.key == pygame.K_SPACE and game_over:
                    total_game_time.append('{:.2f}'.format(time.time() - start_time))
                    player_1_total_game_turns.append(player_1_level_turns[1:])
                    if game_mode == 'Multiplayer': player_2_total_game_turns.append(player_2_level_turns[1:])
                    run = False
                elif event.key == pygame.K_SPACE and game_won:
                    play_won_flag = True
                    startup_counter = 0
                    current_level += 1
                    if dev_mode:
                        player_1_speed = original_speed
                        if game_mode == 'Multiplayer': player_2_speed = original_speed
                    else:
                        player_1_speed = original_speed
                        if game_mode == 'Multiplayer': player_2_speed = original_speed
                    if current_level < len(execution_boards):
                        level = copy.deepcopy(execution_boards[current_level])
                        flat_level_list = [
                            x
                            for xs in level
                            for x in xs
                        ]
                        cookies_at_the_beginning = flat_level_list.count(2)
                        start_1 = player_1_start_execution_positions[current_level]
                        if game_mode == 'Multiplayer':
                            start_2 = player_2_start_execution_positions[current_level]
                            player_2_direction = start_2[2]
                            player_2_player_x = int(start_2[0] * xscale)
                            player_2_player_y = int(start_2[1] * yscale)
                            player_2_direction_command = start_2[2]
                        player_1_direction = start_1[2]
                        player_1_player_x = int(start_1[0] * xscale)
                        player_1_player_y = int(start_1[1] * yscale)
                        player_1_direction_command = start_1[2]
                    game_won = False
                    start_time = time.time()
                    player_1_level_turns = []
                    if game_mode == 'Multiplayer': player_2_level_turns = []
            if dev_mode:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT and player_1_direction_command == 0:
                        player_1_direction_command = player_1_direction
                    elif event.key == pygame.K_LEFT and player_1_direction_command == 1:
                        player_1_direction_command = player_1_direction
                    elif event.key == pygame.K_UP and player_1_direction_command == 2:
                        player_1_direction_command = player_1_direction
                    elif event.key == pygame.K_DOWN and player_1_direction_command == 3:
                        player_1_direction_command = player_1_direction

                    if game_mode == 'Multiplayer':
                        if event.key == pygame.K_d and player_2_direction_command == 0:
                            player_2_direction_command = player_2_direction
                        elif event.key == pygame.K_a and player_2_direction_command == 1:
                            player_2_direction_command = player_2_direction
                        elif event.key == pygame.K_w and player_2_direction_command == 2:
                            player_2_direction_command = player_2_direction
                        elif event.key == pygame.K_s and player_2_direction_command == 3:
                            player_2_direction_command = player_2_direction

        pygame.display.flip()
    #pygame.quit()
    mrkstream_out.push_sample(pylsl.vectorstr(['die']))

    filename = datetime.now().strftime('game_variables_%H%M_%m%d%Y.txt')

    file = open(os.path.join(ASSETS_PATH, 'game_saved_files', filename), 'w')
    file.write(f'game_mode, {game_mode}\n')
    file.write(f'total_game_time, {total_game_time}\n')
    file.write(f'cookie_winner, {cookie_winner}\n')
    file.write(f'player_1_turns, {player_1_total_game_turns}\n')
    file.write(f'player_2_turns, {player_2_total_game_turns}\n')
    file.close()
