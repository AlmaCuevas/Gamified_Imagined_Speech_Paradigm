# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from board import boards_tutorial, start_positions_tutorial, commands_list_tutorial
import pygame
import math
import time


# GAME
pygame.init()
current_level = 0  # Inicialmente, el nivel 0 está en juego

# Dimensions
display_info = pygame.display.Info()  # Get the monitor's display info
WIDTH = int(display_info.current_h)
HEIGHT = int(display_info.current_h)

level = copy.deepcopy(boards_tutorial[current_level])
div_width = len(level[0])
div_height = len(level)
yscale = HEIGHT // div_height
xscale = WIDTH // div_width


commands_list = commands_list_tutorial.pop(0)
# 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN, 4-STOP

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60  # This decides how fast the game goes. Including pacman and ghosts.
font = pygame.font.Font("freesansbold.ttf", 30)
color = "white"
PI = math.pi


## Images import
image_xscale = xscale
image_yscale = yscale
player_images = []
player_images = [
    pygame.transform.scale(
        pygame.image.load(f"assets/extras_images/right.png"),
        (image_xscale, image_yscale),
    ),
    pygame.transform.scale(
        pygame.image.load(f"assets/extras_images/left.png"),
        (image_xscale, image_yscale),
    ),
    pygame.transform.scale(
        pygame.image.load(f"assets/extras_images/forward.png"),
        (image_xscale, image_yscale),
    ),
    pygame.transform.scale(
        pygame.image.load(f"assets/extras_images/back.png"),
        (image_xscale, image_yscale),
    ),
    pygame.transform.scale(
        pygame.image.load(f"assets/extras_images/back.png"),
        (image_xscale * 10, image_yscale * 10),
    ),
]
# 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN, 4-Bigger Image
arrow = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/arrow.png"), (image_xscale, image_yscale)
)
arrow_images = [
    pygame.transform.rotate(arrow, -90),
    pygame.transform.rotate(arrow, 90),
    arrow,
    pygame.transform.rotate(arrow, 180),
]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
cookie = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/cookie.png"), (image_xscale, image_yscale)
)
cookie_big = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/cookie.png"),
    (image_xscale * 10, image_yscale * 10),
)


## Positions
start = start_positions_tutorial.pop(0)
player_x = int(start[0] * xscale)
player_y = int(start[1] * yscale)
direction = start[2]
last_direction = start[2]

# Other
turns_allowed = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
direction_command = start[2]
player_speed = 1
moving = False
startup_counter = 0
game_won = False
last_activate_turn_tile = [1, 1]


def draw_misc():
    text_x = WIDTH // 20
    text_y = HEIGHT // 10
    if current_level == 0 or current_level == 1:
        tutorial_text = font.render("AVANZAR", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 3, text_y))
        tutorial_text = font.render(
            "Moverá al personaje hacia su parte delantera", True, "white"
        )
        screen.blit(tutorial_text, (text_x, text_y + HEIGHT // 10))
    elif current_level == 2 or current_level == 3:
        tutorial_text = font.render("RETROCEDER", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 3, text_y))
        tutorial_text = font.render(
            "Moverá al personaje hacia su parte trasera", True, "white"
        )
        screen.blit(tutorial_text, (text_x, text_y + HEIGHT // 10))
    elif current_level == 4 or current_level == 5:
        tutorial_text = font.render("DERECHA", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 3, text_y))
        tutorial_text = font.render(
            "Moverá al personaje hacia su derecha", True, "white"
        )
        screen.blit(tutorial_text, (text_x, text_y + HEIGHT // 10))
    elif current_level == 6 or current_level == 7:
        tutorial_text = font.render("IZQUIERDA", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 3, text_y))
        tutorial_text = font.render(
            "Moverá al personaje hacia su izquierda", True, "white"
        )
        screen.blit(tutorial_text, (text_x, text_y + HEIGHT // 10))
    if game_won:
        pygame.draw.rect(
            screen,
            "gray",
            [WIDTH * 0.05, HEIGHT * 0.1, WIDTH * 0.9, HEIGHT * 0.8],
            0,
            10,
        )
        pygame.draw.rect(
            screen,
            "green",
            [WIDTH * 0.1, HEIGHT * 0.2, WIDTH * 0.8, HEIGHT * 0.6],
            0,
            10,
        )
        gameover_text = font.render("¡Nivel Completado!", True, "red")
        gameover_text2 = font.render("¡Prepárate para el siguiente nivel!", True, "red")
        screen.blit(gameover_text, (WIDTH // 4, HEIGHT // 3))
        screen.blit(gameover_text2, (WIDTH // 10, HEIGHT // 2))


def command_leader(current_command, player_y, player_x):
    goal_x = player_x
    goal_y = player_y
    if current_command == "right":  # Right
        goal_x = player_x + xscale * 3
    elif current_command == "left":  # Left
        goal_x = player_x - xscale * 3
    elif current_command == "up":  # Up
        goal_y = player_y - yscale * 3
    elif current_command == "down":  # Down
        goal_y = player_y + yscale * 3
    return goal_x, goal_y


def check_collisions(last_activate_turn_tile):
    level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] = 0
    if 0 < player_x < 870:
        if level[center_y // yscale][center_x // xscale] == 1:
            level[center_y // yscale][center_x // xscale] = 0
        if level[center_y // yscale][center_x // xscale] == 2:
            level[center_y // yscale][center_x // xscale] = 0
    return last_activate_turn_tile


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
            if level[i][j] == 2:
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
                        (j * xscale - (xscale * 0.4)) - 2,
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
                    [
                        (j * xscale + (xscale * 0.5)),
                        (i * yscale + (0.5 * yscale)),
                        xscale,
                        yscale,
                    ],
                    PI / 2,
                    PI,
                    3,
                )
            if level[i][j] == 7:
                pygame.draw.arc(
                    screen,
                    color,
                    [
                        (j * xscale + (xscale * 0.5)),
                        (i * yscale - (0.4 * yscale)),
                        xscale,
                        yscale,
                    ],
                    PI,
                    3 * PI / 2,
                    3,
                )
            if level[i][j] == 8:
                pygame.draw.arc(
                    screen,
                    color,
                    [
                        (j * xscale - (xscale * 0.4)) - 2,
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
            if level[i][j] < 0:
                number_text = font.render(str(abs(level[i][j])), True, "white")
                cell_x = j * xscale + (0.5 * xscale) - 10
                cell_y = i * yscale + (0.5 * yscale) - 10
                screen.blit(number_text, (cell_x, cell_y))


def draw_player(last_direction):
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    for direction_idx in range(0, 4):
        if direction_idx == direction:
            last_direction = direction
            screen.blit(player_images[direction], (player_x, player_y))
    if direction == 4:
        screen.blit(player_images[last_direction], (player_x, player_y))
    return last_direction


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num3 = 5
    # check collisions based on center x and center y of player +/- fudge number
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // yscale][(centerx - num3) // xscale] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // yscale][(centerx + num3) // xscale] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // yscale][centerx // xscale] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // yscale][centerx // xscale] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % xscale <= 18:
                if level[(centery + num3) // yscale][centerx // xscale] < 3:
                    turns[3] = True
                if level[(centery - num3) // yscale][centerx // xscale] < 3:
                    turns[2] = True
            if 12 <= centery % yscale <= 18:
                if level[centery // yscale][(centerx - xscale) // xscale] < 3:
                    turns[1] = True
                if level[centery // yscale][(centerx + xscale) // xscale] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % xscale <= 18:
                if level[(centery + yscale) // yscale][centerx // xscale] < 3:
                    turns[3] = True
                if level[(centery - yscale) // yscale][centerx // xscale] < 3:
                    turns[2] = True
            if 12 <= centery % yscale <= 18:
                if level[centery // yscale][(centerx - num3) // xscale] < 3:
                    turns[1] = True
                if level[centery // yscale][(centerx + num3) // xscale] < 3:
                    turns[0] = True
        if direction == 4:
            turns = [True, True, True, True]
    else:
        turns = [True, True, True, True]

    return turns


def move_player(play_x, play_y):
    # r, l, u, d
    # If current direction is right and right is allowed, move right
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y


def change_colors(color):

    if len(commands_list) >= 0:
        if first_movement == True:
            movement_command = current_command
            if current_command == "right":  # Right
                screen.blit(arrow_images[0], (player_x + xscale, player_y))
            elif current_command == "left":  # Left
                screen.blit(arrow_images[1], (player_x - xscale, player_y))
            elif current_command == "up":  # Up
                screen.blit(arrow_images[2], (player_x, player_y - yscale))
            elif current_command == "down":  # Down
                screen.blit(arrow_images[3], (player_x, player_y + yscale))
        else:
            movement_command = commands_list[0]
            if commands_list[0] == "right":  # Right
                screen.blit(arrow_images[0], (player_x + xscale, player_y))
            elif commands_list[0] == "left":  # Left
                screen.blit(arrow_images[1], (player_x - xscale, player_y))
            elif commands_list[0] == "up":  # Up
                screen.blit(arrow_images[2], (player_x, player_y - yscale))
            elif commands_list[0] == "down":  # Down
                screen.blit(arrow_images[3], (player_x, player_y + yscale))

        pygame.display.flip()

        time.sleep(1.4)
        # Green (Imagined Speech)
        color = "green"
        draw_board(color)
        draw_misc()
        draw_player(last_direction)
        pygame.display.flip()
        time.sleep(1.4)

        # Blue (Auditory Speech)
        color = "blue"
        draw_board(color)
        draw_misc()
        draw_player(last_direction)
        pygame.display.flip()
        time.sleep(1.4)
        color = "white"
        draw_board(color)

        return color


# Commands
current_command = commands_list.pop(0)
goal_x, goal_y = command_leader(current_command, player_y, player_x)

run = True
first_movement = True
move_counter = 0
while run:
    timer.tick(fps)
    if startup_counter < fps * 3 and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    if moving and first_movement:
        change_colors(color)
        first_movement = False

    if move_counter == 0:
        # Bienvenida
        screen.fill("black")
        tutorial_text = font.render("¡Bienvenido al tutorial!", True, "white")
        screen.blit(tutorial_text, (WIDTH // 4, HEIGHT // 2))
        pygame.display.flip()
        time.sleep(5)
        # Objetivo
        screen.fill("black")
        tutorial_text = font.render("Come todas las galletas para ganar", True, "white")
        screen.blit(tutorial_text, (WIDTH // 10, HEIGHT // 5))
        screen.blit(player_images[4], (WIDTH // 10, HEIGHT // 3))
        screen.blit(cookie_big, (WIDTH - WIDTH // 2, HEIGHT // 3))
        pygame.display.flip()
        time.sleep(7)
        # Prompts
        screen.fill("black")
        text_x = WIDTH // 4
        text_y = HEIGHT // 3
        tutorial_text = font.render("Puedes utilizar 4 palabras", True, "white")
        screen.blit(tutorial_text, (text_x, text_y))
        tutorial_text = font.render("Avanzar", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 10, text_y + HEIGHT // 10))
        tutorial_text = font.render("Retroceder", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 10, text_y + 2 * HEIGHT // 10))
        tutorial_text = font.render("Izquierda", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 10, text_y + 3 * HEIGHT // 10))
        tutorial_text = font.render("Derecha", True, "white")
        screen.blit(tutorial_text, (text_x + WIDTH // 10, text_y + 4 * HEIGHT // 10))
        pygame.display.flip()
        time.sleep(7)
        # Colores
        text_x = WIDTH // 5
        text_y = HEIGHT // 10
        screen.fill("black")
        tutorial_text = font.render("En VERDE", True, "green")
        screen.blit(tutorial_text, (text_x * 2, text_y))
        tutorial_text = font.render("Realiza el HABLA IMAGINADA", True, "green")
        screen.blit(tutorial_text, (text_x, text_y + HEIGHT // 10))
        draw_board("green")
        pygame.display.flip()
        time.sleep(7)
        screen.fill("black")
        tutorial_text = font.render("En AZUL", True, "blue")
        screen.blit(tutorial_text, (text_x * 2, text_y))
        tutorial_text = font.render("Realiza el HABLA VOCALIZADA", True, "blue")
        screen.blit(tutorial_text, (text_x, text_y + HEIGHT // 10))
        draw_board("blue")
        pygame.display.flip()
        time.sleep(7)
        move_counter += 1

    screen.fill("black")
    draw_board("white")
    center_x = int(player_x + image_xscale // 2)
    center_y = int(player_y + image_yscale // 2)

    # FIX POSITIONS
    # Tutorial
    if current_level == 2 and moving:
        direction = 3
        last_direction = draw_player(last_direction)
    elif current_level == 3 and moving:
        direction = 1
        last_direction = draw_player(last_direction)
    elif current_level == 4 and moving:
        direction = 2
        last_direction = draw_player(last_direction)
    elif current_level == 5 and moving:
        direction = 0
        last_direction = draw_player(last_direction)
    elif current_level == 6 and moving:
        direction = 3
        last_direction = draw_player(last_direction)
    elif current_level == 7 and moving:
        direction = 1
        last_direction = draw_player(last_direction)
    # Examples
    if current_level == 8 and moving and move_counter == 1:
        direction = 0
        last_direction = draw_player(last_direction)
        move_counter += 1
    elif current_level == 9 and moving and move_counter == 2:
        direction = 2
        last_direction = draw_player(last_direction)
        move_counter += 1
    elif current_level == 10 and moving and move_counter == 3:
        direction = 1
        last_direction = draw_player(last_direction)
        move_counter += 1
    elif current_level == 11 and moving and move_counter == 4:
        direction = 0
        last_direction = draw_player(last_direction)
        move_counter += 1

    last_direction = draw_player(last_direction)
    draw_misc()
    turns_allowed = [True, True, True, True]

    if moving:
        player_x, player_y = move_player(player_x, player_y)
    last_activate_turn_tile = check_collisions(last_activate_turn_tile)

    if math.isclose(goal_x, player_x, abs_tol=0) and math.isclose(
        goal_y, player_y, abs_tol=0
    ):
        if len(commands_list) != 0:
            change_colors(color)
        # Change Command
        if len(commands_list) > 0:
            current_command = commands_list.pop(0)
        else:
            current_command = "None"
            game_won = True
        # Change Direction
        if current_command == "right":
            direction = 0
        if current_command == "left":
            direction = 1
        if current_command == "up":
            direction = 2
        if current_command == "down":
            direction = 3
        goal_x, goal_y = command_leader(current_command, player_y, player_x)

    if game_won:
        draw_misc()
        pygame.display.flip()
        time.sleep(3)
        startup_counter = 0
        start = start_positions_tutorial.pop(0)
        player_x = int(start[0] * xscale)
        player_y = int(start[1] * yscale)
        direction = start[2]
        direction_command = start[2]
        current_level += 1
        if current_level < len(boards_tutorial):
            level = copy.deepcopy(boards_tutorial[current_level])
        game_won = False
        commands_list = commands_list_tutorial.pop(0)
        current_command = commands_list.pop(0)
        goal_x, goal_y = command_leader(current_command, player_y, player_x)
        first_movement = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()
pygame.quit()
