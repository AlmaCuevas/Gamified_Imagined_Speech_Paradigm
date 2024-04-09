### Gamified Paradigm for Imagined Speech Acquisiton ###

import copy
import pygame
import math
import time
import pylsl
from board import (
    prompts_paradigm_SI,
    boards_paradigm_SI,
    start_positions_paradigm_SI,
    commands_list_board,
)


## LSL COMMUNICATION
def lsl_mrk_outlet(name):
    """
    Open an Lab Streaming Layer (LSL) outlet

    Args:
        name: Name of the outlet

    Returns:
        outlet: The opened LSL outlet
    """
    info = pylsl.stream_info(name, "Markers", 1, 0, pylsl.cf_string, "ID66666666")
    outlet = pylsl.stream_outlet(info, 1, 1)
    print("Experimental paradigm created result outlet.")
    return outlet

# Important this is first
mrkstream_allowed_turn_out = lsl_mrk_outlet("PyGame - Experimental Paradigm")  

## GAME
pygame.init()

## Board, prompt list, commands list
current_level = 0
level = copy.deepcopy(boards_paradigm_SI[current_level]) # The board
prompts = copy.deepcopy(prompts_paradigm_SI[current_level]) # Correct prompt order("AVANZAR","RETROCEDER","IZQUIERDA","DERECHA")
commands_list = commands_list_board.pop(0) # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN


## Screen Dimensions
display_info = pygame.display.Info()  # Get the monitor's display info
WIDTH = int(display_info.current_h)
HEIGHT = int(display_info.current_h)
screen = pygame.display.set_mode([WIDTH, HEIGHT])

## Scales
div_width = len(level[0])
div_height = len(level)
yscale = HEIGHT // div_height
xscale = WIDTH // div_width


## General Variables
font = pygame.font.Font("freesansbold.ttf", 30)
PI = math.pi


## Import Images
image_xscale = xscale
image_yscale = yscale

# Player
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
]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

# Arrow
arrow = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/arrow.png"), (image_xscale, image_yscale)
)
arrow_images = [
    pygame.transform.rotate(arrow, -90),
    pygame.transform.rotate(arrow, 90),
    arrow,
    pygame.transform.rotate(arrow, 180),
]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

#Cookie
cookie = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/cookie.png"), (image_xscale, image_yscale)
)

## Game Functions
def draw_misc():
    """
    Draws win screen between levels
    """
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
        text_rect = gameover_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        gameover_text2 = font.render("¡Prepárate para el siguiente nivel!", True, "red")
        text_rect2 = gameover_text2.get_rect(center=(WIDTH//2, HEIGHT//2))

        screen.blit(gameover_text, text_rect)
        screen.blit(gameover_text2, text_rect2)


def command_leader(current_command, player_y, player_x):
    """
    Sets the next goal for the character

    Args:
        current_command: A string indicating the next movement
        player_y: The player's "y" coordinate
        player_x: The player's "x" coordinate

    Returns:
        goal_x: The next x coordinate
        goal_y: The next y coordinate
    """
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


def check_collisions(center_x, center_y):
    """
    Checks if a progress dot has been collected
    """
    if 0 < player_x < 870:
        if level[center_y // yscale][center_x // xscale] == 1:
            level[center_y // yscale][center_x // xscale] = 0
        if level[center_y // yscale][center_x // xscale] == 2:
            level[center_y // yscale][center_x // xscale] = 0


def draw_board(color):
    """
    Draws the board
    
    Args:
        color: The color of the board's walls
    """
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


def draw_player(direction, player_x, player_y):
    """
    Draws the player according to the direction its facing
    
    Args:
        direction: The direction between 0-3 the player should be facing
        player_x: The player's x coordinate
        player_y: The player's y coordinate
    """
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    screen.blit(player_images[direction], (player_x, player_y))


def move_player(direction,play_x, play_y):
    """
    Moves the player
    
    Args: 
        direction: The direction between 0-3 the player should move
        play_x: The player's x coordinate
        play_y: The player's y coordinate
    """
    if direction == 0: # Right
        play_x += player_speed
    elif direction == 1: # Left
        play_x -= player_speed
    if direction == 2: # Up
        play_y -= player_speed
    elif direction == 3: # Down
        play_y += player_speed
    return play_x, play_y


def change_colors():
    """"
    Change board colors
    """
    # Draw Arrow
    if len(commands_list) > 0:
        if first_movement == True:
            if current_command == "right":  # Right
                screen.blit(arrow_images[0], (player_x + xscale, player_y))
            elif current_command == "left":  # Left
                screen.blit(arrow_images[1], (player_x - xscale, player_y))
            elif current_command == "up":  # Up
                screen.blit(arrow_images[2], (player_x, player_y - yscale))
            elif current_command == "down":  # Down
                screen.blit(arrow_images[3], (player_x, player_y + yscale))
        else:
            if commands_list[0] == "right":  # Right
                screen.blit(arrow_images[0], (player_x + xscale, player_y))
            elif commands_list[0] == "left":  # Left
                screen.blit(arrow_images[1], (player_x - xscale, player_y))
            elif commands_list[0] == "up":  # Up
                screen.blit(arrow_images[2], (player_x, player_y - yscale))
            elif commands_list[0] == "down":  # Down
                screen.blit(arrow_images[3], (player_x, player_y + yscale))

    
        pygame.display.flip()
        said_command = prompts.pop(0)

        # Decision Making
        time.sleep(1.4)

        # Imagined Speech (Green)
        draw_board("green")
        pygame.display.flip()
        mrkstream_allowed_turn_out.push_sample(pylsl.vectorstr([str(said_command)]))
        time.sleep(1.4)

        # Auditory Speech (Blue)
        draw_board("blue")
        pygame.display.flip()
        mrkstream_allowed_turn_out.push_sample(pylsl.vectorstr([str("Spoken " + said_command)]))
        time.sleep(1.4)

        # Preparing for movement
        draw_board("white")


## Run Game
# Game Variables
timer = pygame.time.Clock()
fps = 60  # This decides how fast the game goes
player_speed = 1 # Moves 1 pixel
startup_counter = 0
moving = False
game_won = False
run = True

# Player position and direction
start = start_positions_paradigm_SI.pop(0)
player_x = int(start[0] * xscale)
player_y = int(start[1] * yscale)
direction = start[2]
last_direction = start[2]

# Draw board
screen.fill("black")
draw_board("white")

# Draw the player
draw_player(direction, player_x, player_y)

# Commands for first movement
first_movement = True
current_command = commands_list.pop(0)
goal_x, goal_y = command_leader(current_command, player_y, player_x)

# Run cycle
while run:
    timer.tick(fps)

    # Inital 20s pause
    if startup_counter < fps * 20 and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    # Change board colors without moving (only first movment)
    if moving and first_movement:
        color = change_colors()
        first_movement = False

    # Draw board
    screen.fill("black")
    draw_board("white")

    # Move the player
    if moving:
        player_x, player_y = move_player(direction, player_x, player_y)

    # Draw the player
    draw_player(direction, player_x, player_y)

    # Calculate player's center
    center_x = int(player_x + image_xscale // 2)
    center_y = int(player_y + image_yscale // 2)

    # Collect Progress Dots
    check_collisions(center_x, center_y)

    # Stop the player
    if math.isclose(goal_x, player_x, abs_tol=0) and math.isclose(
        goal_y, player_y, abs_tol=0):

        # Change board colors
        change_colors()
        
        # Update Command
        if len(commands_list) > 0:
            current_command = commands_list.pop(0)
        else:
            current_command = "None"
            game_won = True

        # Update player's direction
        if current_command == "right":
            direction = 0
        if current_command == "left":
            direction = 1
        if current_command == "up":
            direction = 2
        if current_command == "down":
            direction = 3

        # Update goal
        goal_x, goal_y = command_leader(current_command, player_y, player_x)

    if game_won:
        first_movement = True
        draw_misc()
        pygame.display.flip()
        time.sleep(10)
        startup_counter = 0
        start = start_positions_paradigm_SI.pop(0)
        player_x = int(start[0] * xscale)
        player_y = int(start[1] * yscale)
        direction = start[2]
        current_level += 1
        if current_level < len(boards_paradigm_SI):
            level = copy.deepcopy(boards_paradigm_SI[current_level])
            prompts = copy.deepcopy(prompts_paradigm_SI[current_level])
        game_won = False
        commands_list = commands_list_board.pop(0)
        current_command = commands_list.pop(0)
        goal_x, goal_y = command_leader(current_command, player_y, player_x)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()
pygame.quit()