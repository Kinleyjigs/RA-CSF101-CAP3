import pygame
import sys
import time
import random

try:
    # Initialize Pygame
    pygame.init()
except pygame.error as e:
    print(f"Pygame initialization failed: {e}")
    sys.exit(-1)

# Difficulty settings
difficulty = 15

# Window size
frame_size_x = 720
frame_size_y = 480

try:
    # Initialize game window
    game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
except pygame.error as e:
    print(f"Failed to create game window: {e}")
    pygame.quit()
    sys.exit(-1)

try:
    # Load sound effects
    apple_sound = pygame.mixer.Sound("apple_engulf.mp3")
    bomb_sound = pygame.mixer.Sound("bomb.mp3")
    game_over_sound = pygame.mixer.Sound("game_over.mp3")
    collide_sound = pygame.mixer.Sound("collide.mp3")
except pygame.error as e:
    print(f"Failed to load sound effects: {e}")
    pygame.quit()
    sys.exit(-1)

# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
yellow = pygame.Color(255, 255, 0)

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

# Game variables
snake_pos = [100, 50]
snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
food_spawn = True

# Initialize bomb positions
bombs = []
for _ in range(10):
    bombs.append([random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10])
bomb_spawn = True

# Initialize enemy snake
enemy_pos = [frame_size_x-100, frame_size_y-50]
enemy_body = [[frame_size_x-100, frame_size_y-50], [frame_size_x-100+10, frame_size_y-50], [frame_size_x-100+(2*10), frame_size_y-50]]
enemy_direction = 'LEFT'

direction = 'RIGHT'
change_to = direction

score = 0
high_score = 0

try:
    # Load high score from file
    with open('high_score.txt', 'r') as file:
        high_score = int(file.read())
except FileNotFoundError:
    print("High score file not found. Creating a new one.")
    with open('high_score.txt', 'w') as file:
        file.write(str(high_score))
except Exception as e:
    print(f"Failed to load high score: {e}")

# Game Over
def game_over():
    global high_score
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('Game Over', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x/2, frame_size_y/4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, red, 'times', 20)

    if score > high_score:
        high_score = score
        try:
            with open('high_score.txt', 'w') as file:
                file.write(str(high_score))
        except Exception as e:
            print(f"Failed to update high score: {e}")

    button_font = pygame.font.SysFont('times new roman', 30)
    continue_text = button_font.render('Continue', True, white)
    exit_text = button_font.render('Exit', True, white)

    continue_rect = continue_text.get_rect()
    exit_rect = exit_text.get_rect()

    continue_rect.center = (frame_size_x/2, frame_size_y/1.75)
    exit_rect.center = (frame_size_x/2, frame_size_y/1.5)

    game_window.blit(continue_text, continue_rect)
    game_window.blit(exit_text, exit_rect)

    pygame.display.flip()

    game_over_sound.play()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if continue_rect.collidepoint(mouse_pos):
                    reset_game()
                    return
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x/10, 15)
    else:
        score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
    game_window.blit(score_surface, score_rect)
    
    high_score_surface = score_font.render('High Score : ' + str(high_score), True, color)
    high_score_rect = high_score_surface.get_rect()
    high_score_rect.midtop = (frame_size_x/2, 15)
    game_window.blit(high_score_surface, high_score_rect)

def reset_game():
    global snake_pos, snake_body, food_pos, food_spawn, bombs, enemy_pos, enemy_body, direction, change_to, score
    snake_pos = [100, 50]
    snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
    food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True
    bombs = []
    for _ in range(10):
        bombs.append([random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10])
    enemy_pos = [frame_size_x-100, frame_size_y-50]
    enemy_body = [[frame_size_x-100, frame_size_y-50], [frame_size_x-100+10, frame_size_y-50], [frame_size_x-100+(2*10), frame_size_y-50]]
    direction = 'RIGHT'
    change_to = direction
    score = 0

introduction_font = pygame.font.SysFont('times new roman', 30)
introduction_texts = [
    ("SNAKE GAME", 3),
    "Use Arrow Keys to Move",
    "Press 'Space' to Pause",
    "Press 'Enter' to Start",   
]

game_window.fill(black)

for i, text in enumerate(introduction_texts):
    if isinstance(text, tuple):
        text, font_size = text
        text_surface = introduction_font.render(text, True, red)
        text_surface = pygame.transform.scale(text_surface, (text_surface.get_width() * font_size, text_surface.get_height() * font_size))
    else:
        text_surface = introduction_font.render(text, True, white)
    
    if text != "SNAKE GAME":
        text_rect = text_surface.get_rect(midtop=(frame_size_x/2, frame_size_y/2 + i*30))
        game_window.blit(text_surface, text_rect)
    else:
        text_rect = text_surface.get_rect(midtop=(frame_size_x/2, frame_size_y/6))
        game_window.blit(text_surface, text_rect)

pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                break
    else:
        continue
    break

paused = False
chase_time = time.time() + 0.1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = 'UP'
            elif event.key == pygame.K_DOWN:
                change_to = 'DOWN'
            elif event.key == pygame.K_LEFT:
                change_to = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                change_to = 'RIGHT'
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        current_time = time.time()
        if current_time >= chase_time:
            if snake_pos[0] < enemy_pos[0]:
                enemy_pos[0] -= 10
            elif snake_pos[0] > enemy_pos[0]:
                enemy_pos[0] += 10
            elif snake_pos[1] < enemy_pos[1]:
                enemy_pos[1] -= 10
            elif snake_pos[1] > enemy_pos[1]:
                enemy_pos[1] += 10
            chase_time = current_time + 0.05

            if enemy_pos[0] == food_pos[0] and enemy_pos[1] == food_pos[1]:
                score += 1
                enemy_body.append(enemy_body[-1])
                food_spawn = False

        if enemy_pos[0] == snake_pos[0] and enemy_pos[1] == snake_pos[1]:
            if len(snake_body) >= len(enemy_body):
                enemy_pos = [frame_size_x - 100, frame_size_y - 50]
                enemy_body = [[frame_size_x - 100, frame_size_y - 50], [frame_size_x - 100 + 10, frame_size_y - 50],
                              [frame_size_x - 100 + (2 * 10), frame_size_y - 50]]
            else:
                collide_sound.play()
                game_over()

        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            apple_sound.play()
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
        food_spawn = True

        game_window.fill(black)
        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

        pygame.draw.rect(game_window, red, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        for bomb in bombs:
            pygame.draw.rect(game_window, blue, pygame.Rect(bomb[0], bomb[1], 10, 10))
        pygame.draw.rect(game_window, yellow, pygame.Rect(enemy_pos[0], enemy_pos[1], 10, 10))

        if snake_pos[0] < 0 or snake_pos[0] > frame_size_x-10:
            game_over()
        if snake_pos[1] < 0 or snake_pos[1] > frame_size_y-10:
            game_over()
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over()

        for bomb in bombs:
            if snake_pos[0] == bomb[0] and snake_pos[1] == bomb[1]:
                bomb_sound.play()
                if len(snake_body) > 1:
                    snake_body.pop()
                    score -= 1
                    if score == -2:
                        game_over()
                bombs.remove(bomb)

        for bomb in bombs:
            if enemy_pos[0] == bomb[0] and enemy_pos[1] == bomb[1]:
                bombs.remove(bomb)

        show_score(1, white, 'consolas', 20)
    else:
        pause_font = pygame.font.SysFont('times new roman', 50)
        pause_text = pause_font.render('Paused', True, red)
        pause_rect = pause_text.get_rect(center=(frame_size_x/2, frame_size_y/2))
        game_window.blit(pause_text, pause_rect)

    pygame.display.update()
    fps_controller.tick(difficulty)
