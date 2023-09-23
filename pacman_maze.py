# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from board import maze_A, maze_B, maze_C, maze_D, maze_E, maze_F, original_board
import pygame
import math
#import pylsl

# LSL COMMUNICATION
#def lsl_mrk_outlet(name):
#    info = pylsl.stream_info(name, 'Markers', 1, 0, pylsl.cf_string, 'ID66666666');
#    outlet = pylsl.stream_outlet(info, 1, 1)
#    print('pacman created result outlet.')
#    return outlet
#mrkstream_allowed_turn_out = lsl_mrk_outlet('Allowed_Turn_Markers') # important this is first

# GAME
pygame.init()
boards = [maze_F, maze_E, maze_D, maze_C, maze_B, maze_A, original_board]
WIDTH = 900 # Don't use complete screen, you'll will have to alt+f4. Plus the whole board expands, doesn't stay the same.
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60 # This decides how fast the game goes. Including pacman and ghosts.
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards.pop(0))
div_width = len(level[0])
div_height = len(level)-1
color = 'blue'
PI = math.pi
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (40, 40)))
arrow = pygame.transform.scale(pygame.image.load(f'assets/extras_images/arrow.png'), (40, 40))
arrow_transparent = pygame.transform.scale(pygame.image.load(f'assets/extras_images/arrow_transparent.png'), (40, 40))
arrow_images = [pygame.transform.rotate(arrow, -90), pygame.transform.rotate(arrow, 90), arrow,
                pygame.transform.rotate(arrow, 180)] # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow_transparent_images = [pygame.transform.rotate(arrow_transparent, -90), pygame.transform.rotate(arrow_transparent, 90), arrow_transparent,
                pygame.transform.rotate(arrow_transparent, 180)] # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow_x = [70, 10, 40, 40] # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
arrow_y = [100, 100, 50, 150] # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
player_x = 450
player_y = 663
direction = 0
counter = 0
flicker = False
# R, L, U, D
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
moving = False
startup_counter = 0
lives = 3
game_over = False
game_won = False

def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (40, 215 + i * 40))
    if game_over:
        pygame.draw.rect(screen, 'red', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over!', True, 'red')
        gameover_text2 = font.render('Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (400, 270))
        screen.blit(gameover_text2, (350, 370))
    if game_won:
        pygame.draw.rect(screen, 'green', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory!', True, 'green')
        gameover_text2 = font.render('Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (400, 270))
        screen.blit(gameover_text2, (350, 370))


def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // div_height
    num2 = WIDTH // div_width
    if 0 < player_x < 870:
        for mod in mods:
            if level[center_y // num1][(center_x+ mod) // num2] in [5, 6, 7, 8]:  # arc numbers
                level[center_y // num1][center_x // num2] = -1
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
    return scor, power, power_count, eaten_ghosts

def draw_board():
    num1 = ((HEIGHT - 50) // div_height)
    num2 = (WIDTH // div_width)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == -1:
                pygame.draw.rect(screen, 'yellow', [j * num2 + (-0.4 * num2), i * num1 + (-0.4 * num1), 55, 55], border_radius=10)


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // div_height
    num2 = (WIDTH // div_width)
    num3 = 15
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
    else:
        turns[0] = True
        turns[1] = True

    return turns


def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y

run = True
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

    screen.fill('black')
    draw_board()
    center_x = player_x + 23
    center_y = player_y + 24

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False
    mods = [20, -20, 40, -40]
    player_circle = pygame.draw.circle(screen, 'pink', (center_x+mods[0], center_y), 20, 10)
    player_circle_2 = pygame.draw.circle(screen, 'pink', (center_x + mods[1], center_y), 20, 10)
    player_circle_3 = pygame.draw.circle(screen, 'pink', (center_x, center_y + mods[2]), 20, 10)
    player_circle_4 = pygame.draw.circle(screen, 'pink', (center_x, center_y + mods[3]), 20, 10)
    draw_player()

    draw_misc()

    turns_allowed = check_position(center_x, center_y)
    #mrkstream_allowed_turn_out.push_sample(pylsl.vectorstr([str(turns_allowed)]))
    if moving:
        player_x, player_y = move_player(player_x, player_y)
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)
    # add to if not powerup to check if eaten ghosts

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
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
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                score = 0
                lives = 3
                level = copy.deepcopy(boards.pop(0))
                game_over = False
                game_won = False

        if event.type == pygame.KEYUP:
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
            screen.blit(arrow_images[direction_index], (arrow_x[direction_index], arrow_y[direction_index]))
            if turns_allowed[direction_index]:
                direction = direction_index
        else:
            screen.blit(arrow_transparent_images[direction_index], (arrow_x[direction_index], arrow_y[direction_index]))

    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    pygame.display.flip()
pygame.quit()


# sound effects, restart and winning messages
