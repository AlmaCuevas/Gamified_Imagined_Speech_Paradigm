# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from board import boards_paradigm_SI, start_positions_paradigm_SI
import pygame
import math
import time
import pyautogui


# import pylsl

# LSL COMMUNICATION
# def lsl_mrk_outlet(name):
#    info = pylsl.stream_info(name, 'Markers', 1, 0, pylsl.cf_string, 'ID66666666');
#    outlet = pylsl.stream_outlet(info, 1, 1)
#    print('pacman created result outlet.')
#    return outlet
# mrkstream_allowed_turn_out = lsl_mrk_outlet('Allowed_Turn_Markers') # important this is first

# GAME
pygame.init()
commands_list_board=[['up','left','left','right','right','up','left', 'left', 'up', 'up'],['up','left','left','right','right','up','left', 'left', 'up']]
## Dimensions
WIDTH = 800  # The whole board expands, but the measures like the initial position changes too.
HEIGHT = 800  # All sizes change when you change this. If you try to make this bigger, usually no prob. But smaller will just led to too big pacman that can't walk
level = copy.deepcopy(boards_paradigm_SI.pop(0))
div_width = len(level[0])  # 33
div_height = len(level)  # 33
num1 = HEIGHT // div_height #23
num2 = WIDTH // div_width #29

commands_list = commands_list_board.pop(0)
 # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN, 4-STOP

screen = pygame.display.set_mode([WIDTH, HEIGHT])
# tiny_screen = pygame.display.set_mode([300,300])
timer = pygame.time.Clock()
fps = 60  # This decides how fast the game goes. Including pacman and ghosts.
font = pygame.font.Font("freesansbold.ttf", 20)
color = "blue"
PI = math.pi


## Images import
player_images = [pygame.transform.scale(pygame.image.load(f'assets/extras_images/right.png'), (40, 40)),
                 pygame.transform.scale(pygame.image.load(f'assets/extras_images/left.png'), (40, 40)),
                 pygame.transform.scale(pygame.image.load(f'assets/extras_images/forward.png'), (40, 40)),
                 pygame.transform.scale(pygame.image.load(f'assets/extras_images/back.png'), (40, 40))] # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

arrow = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/arrow.png"), (30, 30)
)
arrow_transparent = pygame.transform.scale(
    pygame.image.load(f"assets/extras_images/arrow_transparent.png"), (30, 30)
)
arrow_images = [
    pygame.transform.rotate(arrow, -90),
    pygame.transform.rotate(arrow, 90),
    arrow,
    pygame.transform.rotate(arrow, 180),
]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow_transparent_images = [
    pygame.transform.rotate(arrow_transparent, -90),
    pygame.transform.rotate(arrow_transparent, 90),
    arrow_transparent,
    pygame.transform.rotate(arrow_transparent, 180),
]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow_x = [65, 5, 35, 35]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow_y = [80, 80, 50, 110]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN

## Positions
start = start_positions_paradigm_SI.pop(0)
player_x = num2 * start[0] - int(num2 / 2) + 3  # 450
player_y = num1 * start[1] - int(num1 / 2) + 2  # 640
direction = start[2]
last_direction = start[2]

#Other
counter = 0
flicker = False
turns_allowed = [False, False, False, False]  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
direction_command = start[2]
player_speed = 1
score = 0
powerup = False
power_counter = 0
targets = [
    (player_x, player_y),
    (player_x, player_y),
    (player_x, player_y),
    (player_x, player_y),
]
moving = False
startup_counter = 0
lives = 3
game_over = False
game_won = False
last_activate_turn_tile = [1, 1]

def draw_misc():
    score_text = font.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, "blue", (140, 930), 15)
    for i in range(lives):
        screen.blit(
            pygame.transform.scale(player_images[0], (30, 30)), (35, 215 + i * 40)
        )
    if game_over:
        pygame.draw.rect(screen, "red", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Game over!", True, "red")
        gameover_text2 = font.render("Space bar to restart!", True, "red")
        screen.blit(gameover_text, (400, 270))
        screen.blit(gameover_text2, (350, 370))
    if game_won:
        pygame.draw.rect(screen, "green", [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, "gray", [70, 220, 760, 260], 0, 10)
        gameover_text = font.render("Victory!", True, "green")
        gameover_text2 = font.render("Space bar to restart!", True, "red")
        screen.blit(gameover_text, (400, 270))
        screen.blit(gameover_text2, (350, 370))

def command_leader(current_command, player_y, player_x):
    goal_x=player_x
    goal_y=player_y
    if current_command == 'right':  # Right
        goal_x = player_x + num2 * 2 + num2/2
    elif current_command == 'left':  # Left
        goal_x = player_x - num2 * 2 - num2/2
    elif current_command == 'up':  # Up
        goal_y = player_y - num1 * 3
    elif current_command == 'down':  # Down
        goal_y = player_y + num1 * 3
    return goal_x, goal_y

def check_collisions(scor, power, power_count, last_activate_turn_tile):
    level[last_activate_turn_tile[0]][last_activate_turn_tile[1]] = 0
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
    return scor, power, power_count, last_activate_turn_tile


def draw_board():
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(
                    screen,
                    "white",
                    (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                    4,
                )
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(
                    screen,
                    "white",
                    (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                    10,
                )
            if level[i][j] == 3:
                pygame.draw.line(
                    screen,
                    color,
                    (j * num2 + (0.5 * num2), i * num1),
                    (j * num2 + (0.5 * num2), i * num1 + num1),
                    3,
                )
            if level[i][j] == 4:
                pygame.draw.line(
                    screen,
                    color,
                    (j * num2, i * num1 + (0.5 * num1)),
                    (j * num2 + num2, i * num1 + (0.5 * num1)),
                    3,
                )
            if level[i][j] == 5:
                pygame.draw.arc(
                    screen,
                    color,
                    [
                        (j * num2 - (num2 * 0.4)) - 2,
                        (i * num1 + (0.5 * num1)),
                        num2,
                        num1,
                    ],
                    0,
                    PI / 2,
                    3,
                )
            if level[i][j] == 6:
                pygame.draw.arc(
                    screen,
                    color,
                    [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                    PI / 2,
                    PI,
                    3,
                )
            if level[i][j] == 7:
                pygame.draw.arc(
                    screen,
                    color,
                    [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                    PI,
                    3 * PI / 2,
                    3,
                )
            if level[i][j] == 8:
                pygame.draw.arc(
                    screen,
                    color,
                    [
                        (j * num2 - (num2 * 0.4)) - 2,
                        (i * num1 - (0.4 * num1)),
                        num2,
                        num1,
                    ],
                    3 * PI / 2,
                    2 * PI,
                    3,
                )
            if level[i][j] == 9:
                pygame.draw.line(
                    screen,
                    "white",
                    (j * num2, i * num1 + (0.5 * num1)),
                    (j * num2 + num2, i * num1 + (0.5 * num1)),
                    3,
                )


def draw_player(last_direction):
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    for direction_idx in range(0,4):
        if direction_idx == direction:
            last_direction=direction
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
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
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

def change_colors():
    time.sleep(1.4)
    # Green (Imagined Speech)
    screen.fill("green")
    draw_board()
    draw_misc()
    draw_player(last_direction)
    pygame.display.flip()
    time.sleep(1.4)

    # Purple (Auditory Speech)
    screen.fill("violet")
    draw_board()
    draw_misc()
    draw_player(last_direction)
    pygame.display.flip()
    time.sleep(1.4)
        
    

# Commands
current_command = commands_list.pop(0)
goal_x, goal_y = command_leader(current_command, player_y, player_x)

run = True
first_movement = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    if moving and first_movement:
       change_colors()
       first_movement = False

    screen.fill("black")
    draw_board()
    center_x = player_x + 23
    center_y = player_y + 24

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False
    last_direction = draw_player(last_direction)

    draw_misc()

    turns_allowed = check_position(center_x, center_y)
    # mrkstream_allowed_turn_out.push_sample(pylsl.vectorstr([str(turns_allowed)]))
    if moving:
        player_x, player_y = move_player(player_x, player_y)
    score, powerup, power_counter, last_activate_turn_tile = check_collisions(
        score, powerup, power_counter, last_activate_turn_tile
    )
    # add to if not powerup to check if eaten ghosts
    print(f"goal_x = {goal_x}")
    print(f"player_x = {player_x}")
    print(f"goal_y = {goal_y}")
    print(f"player_y = {player_y}")

    if math.isclose(goal_x, player_x, abs_tol = 3) and math.isclose(goal_y, player_y, abs_tol = 3):
        change_colors()
        
        # Movement
        pyautogui.keyUp(current_command)
        current_command = commands_list.pop(0)
        pyautogui.keyDown(current_command)
        print(current_command)
        goal_x, goal_y = command_leader(current_command, player_y, player_x) 


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                direction_command = 4
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                powerup = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                start = start_positions_paradigm_SI.pop(0)
                player_x = num2 * start[0] - int(num2 / 2) + 3  # 450
                player_y = num1 * start[1] - int(num1 / 2) + 2  # 640
                direction = start[2]
                direction_command = start[2]
                score = 0
                lives = 3
                level = copy.deepcopy(boards_paradigm_SI.pop(0))
                game_over = False
                game_won = False
                commands_list = commands_list_board.pop(0)
                current_command = commands_list.pop(0)
                goal_x, goal_y, player_y, player_x = command_leader(current_command, player_y, player_x)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and direction_command == 4:
                direction_command = direction
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    for direction_index in range(0, 4):
        if direction_command == direction_index:
            screen.blit(
                arrow_images[direction_index],
                (arrow_x[direction_index], arrow_y[direction_index]),
            )
            if turns_allowed[direction_index]:
                direction = direction_index
        else:
            screen.blit(
                arrow_transparent_images[direction_index],
                (arrow_x[direction_index], arrow_y[direction_index]),
            )
    if direction_command == 4:
        direction = 4
    pygame.display.flip()
pygame.quit()


# sound effects, restart and winning messages
