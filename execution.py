# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from datetime import datetime

from board_execution import execution_boards, player_1_start_execution_positions, player_2_start_execution_positions
import pygame
import math
import time
import pylsl
import os

def play_game():
    ASSETS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
    dev_mode = True

    # TODO: Add the tutorial (3 levels), multi or single player to menu
    # TODO: Do this option available for single to multiplayer, a simple bool should be ok


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
    current_level: int = 0  # Inicialmente, el nivel 0 está en juego
    game_state = "start_menu"
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
    font = pygame.font.Font("freesansbold.ttf", 30)
    color = "white"
    PI = math.pi
    total_game_time: list = []
    player_1_total_game_turns: list = []
    player_1_level_turns: list[int] = []

    player_2_total_game_turns: list = []
    player_2_level_turns: list[int] = []

    ## Images import
    player_1_images: list = [
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/right_1.png'), (xscale, yscale)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/left_1.png'), (xscale, yscale)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/forward_1.png'), (xscale, yscale)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/back_1.png'),
                               (xscale, yscale))]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    player_2_images: list = [
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/right_2.png'), (xscale, yscale)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/left_2.png'), (xscale, yscale)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/forward_2.png'), (xscale, yscale)),
        pygame.transform.scale(pygame.image.load(f'assets/extras_images/back_2.png'), (xscale, yscale))]
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

    channel = pygame.mixer.Channel(0)

    ## Positions
    start_1: list = player_1_start_execution_positions[current_level]
    start_2: list = player_2_start_execution_positions[current_level]
    player_1_player_x: int = int(start_1[0] * xscale)
    player_1_player_y: int = int(start_1[1] * yscale)
    player_2_player_x: int = int(start_2[0] * xscale)
    player_2_player_y: int = int(start_2[1] * yscale)
    player_1_direction: int = start_1[2]
    player_2_direction: int = start_2[2]
    player_1_last_direction: int = start_1[2]
    player_2_last_direction: int = start_2[2]

    ## Other
    player_1_turns_allowed: list[bool] = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    player_2_turns_allowed: list[bool] = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    player_1_direction_command: int = start_1[2]
    player_2_direction_command: int = start_2[2]
    if dev_mode:
        player_1_speed: int = 5
        player_2_speed: int = 5
        original_speed: int = 5
    else:
        player_1_speed: int = 1
        player_2_speed: int = 1
        original_speed: int = 1
    moving: bool = False
    startup_counter: int = 0
    counter: int = 0
    flicker: bool = False
    game_over: bool = False
    game_won: bool = False
    play_won_flag: bool = True
    player_1_last_activate_turn_tile: list[int] = [4, 4]  # Check that in all levels this is a 0 pixel
    player_2_last_activate_turn_tile: list[int] = [4, 4]
    player_1_time_to_corner: int = 0
    player_2_time_to_corner: int = 0
    cookie_winner: list = []

    def draw_misc():
        gameover_text = font.render("¡Nivel Completado!", True, "red")
        if game_over:
            pygame.draw.rect(screen, "gray", [WIDTH * .05, HEIGHT * .1, WIDTH * .9, HEIGHT * .8], 0, 10)
            pygame.draw.rect(screen, "green", [WIDTH * .1, HEIGHT * .2, WIDTH * .8, HEIGHT * .6], 0, 10)
            gameover_text2 = font.render("¡Gracias por participar!", True, "red")
            gameover_text3 = font.render("Ya puedes cerrar la ventana.", True, "red")
            screen.blit(gameover_text,
                        (WIDTH / 2 - gameover_text.get_width() / 2, HEIGHT / 2 - gameover_text.get_height() / 2 - 100))
            screen.blit(gameover_text2,
                        (WIDTH / 2 - gameover_text2.get_width() / 2, HEIGHT / 2 - gameover_text2.get_height() / 2))
            screen.blit(gameover_text3,
                        (WIDTH / 2 - gameover_text3.get_width() / 2, HEIGHT / 2 - gameover_text3.get_height() / 2 + 100))
        elif game_won:
            pygame.draw.rect(screen, "gray", [WIDTH * .05, HEIGHT * .1, WIDTH * .9, HEIGHT * .8], 0, 10)
            pygame.draw.rect(screen, "green", [WIDTH * .1, HEIGHT * .2, WIDTH * .8, HEIGHT * .6], 0, 10)
            gameover_text2 = font.render("¡Prepárate para el siguiente nivel!", True, "red")
            screen.blit(gameover_text,
                        (WIDTH / 2 - gameover_text.get_width() / 2, HEIGHT / 2 - gameover_text.get_height() / 2 - 50))
            screen.blit(gameover_text2,
                        (WIDTH / 2 - gameover_text2.get_width() / 2, HEIGHT / 2 - gameover_text2.get_height() / 2 + 50))

    def check_collisions(last_activate_turn_tile, player_speed, time_to_corner, turns_allowed, direction, center_x,
                         center_y, level, player_num):
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
                channel.set_volume(right_volume, left_volume)
                level[center_y // yscale][center_x // xscale] = -1 * player_num
                last_activate_turn_tile = [center_y // yscale, center_x // xscale]
                player_speed = 0
        elif level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] == -1 * player_num:
            channel.play(sound_go)
            channel.set_volume(right_volume, left_volume)
            level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] = 0
            player_speed = original_speed
            time_to_corner = 0
        return last_activate_turn_tile, player_speed, time_to_corner, level, cookie_winner_num

    def draw_board(level: list, color: str, center_1_x: float, center_1_y: float, center_2_x: float, center_2_y: float):
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
                        [center_1_x - xscale, center_1_y - yscale, 60, 60],
                        border_radius=10,
                    )
                if level[i][j] == -2:
                    pygame.draw.rect(
                        screen,
                        "yellow",
                        [center_2_x - xscale, center_2_y - yscale, 60, 60],
                        border_radius=10,
                    )
        return level

    def draw_player(direction, last_direction, player_x, player_y, player_images):
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        for direction_idx in range(0, 4):
            if direction_idx == direction:
                last_direction = direction
                screen.blit(player_images[direction], (player_x, player_y))
        if direction == 4:
            screen.blit(player_images[last_direction], (player_x, player_y))
        return last_direction

    def check_position(direction, centerx, centery, level):
        turns = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        half_scale = xscale // 2 + 5
        if direction == 2 or direction == 3:
            if xscale // 3 <= centerx % xscale <= xscale:
                if level[(centery + half_scale) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx, (centery + half_scale)), 20, 10)
                    turns[3] = True
                if level[(centery - half_scale - 10) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx, (centery - half_scale - 10)), 20, 10)
                    turns[2] = True
            if yscale // 3 <= centery % yscale <= yscale:
                if level[centery // yscale][(centerx - xscale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx - xscale, centery), 20, 10)
                    turns[1] = True
                if level[centery // yscale][(centerx + xscale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'pink', (centerx + xscale, centery), 20, 10)
                    turns[0] = True
        elif direction == 0 or direction == 1:
            if xscale // 3 <= centerx % xscale <= xscale:
                if level[(centery + yscale) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'green', (centerx, centery + yscale), 20, 10)
                    turns[3] = True
                if level[(centery - yscale) // yscale][centerx // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'green', (centerx, centery - yscale), 20, 10)
                    turns[2] = True
            if yscale // 3 <= centery % yscale <= yscale:
                if level[centery // yscale][(centerx - half_scale - 8) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'white', ((centerx - half_scale - 8), centery), 20, 10)
                    turns[1] = True
                if level[centery // yscale][(centerx + half_scale) // xscale] < 3:
                    if dev_mode: pygame.draw.circle(screen, 'red', ((centerx + half_scale), centery), 20, 10)
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
        elif startup_counter < fps*20 and not game_won and not dev_mode:
            moving = False
            startup_counter += 1
        else:
            moving = True

        screen.fill("black")
        player_1_center_x = player_1_player_x + xscale // 2
        player_1_center_y = player_1_player_y + yscale // 2
        player_2_center_x = player_2_player_x + xscale // 2
        player_2_center_y = player_2_player_y + yscale // 2
        level = draw_board(level, color, player_1_center_x, player_1_center_y, player_2_center_x, player_2_center_y)

        player_1_last_direction = draw_player(player_1_direction, player_1_last_direction, player_1_player_x, player_1_player_y, player_1_images)
        player_2_last_direction = draw_player(player_2_direction, player_2_last_direction, player_2_player_x, player_2_player_y, player_2_images)

        draw_misc()

        player_1_turns_allowed = check_position(player_1_direction, player_1_center_x, player_1_center_y, level)
        player_2_turns_allowed = check_position(player_2_direction, player_2_center_x, player_2_center_y, level)

        # mrkstream_allowed_turn_out.push_sample(pylsl.vectorstr([str(player_1_turns_allowed)]))
        if moving:
            player_1_player_x, player_1_player_y = move_player(player_1_direction, player_1_turns_allowed, player_1_player_x, player_1_player_y, player_1_speed)
            player_2_player_x, player_2_player_y = move_player(player_2_direction, player_2_turns_allowed, player_2_player_x, player_2_player_y, player_2_speed)

        player_1_last_activate_turn_tile, player_1_speed, player_1_time_to_corner, level, cookie_winner_1_num = check_collisions(player_1_last_activate_turn_tile, player_1_speed, player_1_time_to_corner, player_1_turns_allowed, player_1_direction, player_1_center_x, player_1_center_y, level, 1)
        player_2_last_activate_turn_tile, player_2_speed, player_2_time_to_corner, level, cookie_winner_2_num = check_collisions(player_2_last_activate_turn_tile, player_2_speed, player_2_time_to_corner, player_2_turns_allowed, player_2_direction, player_2_center_x, player_2_center_y, level, 2)
        # print(cookie_winner_1_num)
        # print(cookie_winner_2_num)
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
                elif cookie_winner_2_num:
                    cookie_winner.append(cookie_winner_2_num)
                sound_win.play()
                total_game_time.append('{:.2f}'.format(time.time() - start_time))
                player_1_total_game_turns.append(player_1_level_turns[1:])
                player_2_total_game_turns.append(player_2_level_turns[1:])
                play_won_flag = False
            if len(player_1_start_execution_positions) == current_level+1:
                game_over = True
            game_won = True

        player_1_time_to_corner += 1
        player_2_time_to_corner += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and (player_1_speed == 0 or player_2_speed == 0):
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
                    player_2_total_game_turns.append(player_2_level_turns[1:])
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
                        start_1 = player_1_start_execution_positions[current_level]
                        start_2 = player_2_start_execution_positions[current_level]
                        player_1_direction = start_1[2]
                        player_2_direction = start_2[2]
                        player_1_player_x = int(start_1[0] * xscale)
                        player_1_player_y = int(start_1[1] * yscale)
                        player_2_player_x = int(start_2[0] * xscale)
                        player_2_player_y = int(start_2[1] * yscale)
                        player_1_direction_command = start_1[2]
                        player_2_direction_command = start_2[2]
                    game_won = False
                    start_time = time.time()
                    player_1_level_turns = []
                    player_2_level_turns = []

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
    #pygame.quit()

    # Here in case someone decides to finish the game (NOT RECOMMENDED FOR ANALYSIS).
    # If the user doesn't want to continue, at least the progress stays.
    filename = datetime.now().strftime('game_variables_%H%M_%m%d%Y.txt')

    file = open(os.path.join(ASSETS_PATH, 'game_saved_files', filename), 'w')
    file.write('input, multiplayer_1, multiplayer_2\n')
    file.write(f'total_game_time, {total_game_time}\n')
    file.write(f'cookie_winner, {cookie_winner}\n')
    file.write(f'player_1_turns, {player_1_total_game_turns}\n')
    file.write(f'player_2_turns, {player_2_total_game_turns}\n')
    file.close()
