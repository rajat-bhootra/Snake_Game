import pygame
import time
import random
import os

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Updated screen dimensions
width, height = 1600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("🐍 Snake Game")

# Colors
white = (255, 255, 255)
green = (0, 200, 0)
red = (200, 0, 0)
black = (0, 0, 0)
blue = (0, 100, 255)
bg_color = (30, 30, 30)

# Block and speed
block_size = 40
initial_speed = 5

# Fonts
font = pygame.font.SysFont("consolas", 24, bold=True)
game_over_font = pygame.font.SysFont("consolas", 36, bold=True)

#apple image
apple_img = pygame.image.load("assets/image/apple.png")
apple_img = pygame.transform.scale(apple_img, (block_size, block_size))

#special fruit
golden_apple_img = pygame.image.load("assets/image/golden_apple.png")
golden_apple_img = pygame.transform.scale(golden_apple_img, (block_size, block_size))

# Snake head images
head_up = pygame.image.load("assets/image/snake_head_up.png")
head_down = pygame.image.load("assets/image/snake_head_down.png")
head_left = pygame.image.load("assets/image/snake_head_left.png")
head_right = pygame.image.load("assets/image/snake_head_right.png")

# Scale to block size
head_up = pygame.transform.scale(head_up, (60, 60))
head_down = pygame.transform.scale(head_down, (60, 60))
head_left = pygame.transform.scale(head_left, (60, 60))
head_right = pygame.transform.scale(head_right, (60, 60))

# Body
body_img = pygame.image.load("assets/image/snake_body.png")
body_img_horizontal = pygame.image.load("assets/image/snake_body_horizontal.png")

#tail
tail_up = pygame.image.load("assets/image/snake_tail_up.png")
tail_down = pygame.image.load("assets/image/snake_tail_down.png")
tail_left = pygame.image.load("assets/image/snake_tail_left.png")
tail_right = pygame.image.load("assets/image/snake_tail_right.png")

#scale to block size
body_img = pygame.transform.scale(body_img, (block_size, block_size))
body_img_horizontal = pygame.transform.scale(body_img_horizontal, (block_size, block_size))

tail_up = pygame.transform.scale(tail_up, (50, 50))
tail_down = pygame.transform.scale(tail_down, (50, 50))
tail_left = pygame.transform.scale(tail_left, (50, 50))
tail_right = pygame.transform.scale(tail_right, (50, 50))

#bg image
bg_img = pygame.image.load("assets/image/background.jpg")
bg_img = pygame.transform.scale(bg_img, (width, height))

# Load sounds (optional)
try:
    pygame.mixer.music.load("assets/sound/background.mp3")
    pygame.mixer.music.set_volume(0.1)
    eat_sound = pygame.mixer.Sound("assets/sound/eat.mp3")
    eat_sound.set_volume(0.2)
    pygame.mixer.music.play(-1)  # loop forever
    game_over_sound = pygame.mixer.Sound("assets/sound/game_over.mp3")
    game_over_sound.set_volume(0.4)
    golden_eat_sound = pygame.mixer.Sound("assets/sound/golden.mp3")
    golden_eat_sound.set_volume(0.2)
except Exception as e:
    print(f"[sound warning] {e}")

clock = pygame.time.Clock()

def load_highscore():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read().strip())
    except:
        return 0

def save_highscore(score):
    with open("highscore.txt", "w") as file:
        file.write(str(score))


def draw_grid():
    for x in range(0, width, block_size):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, height))
    for y in range(0, height, block_size):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (width, y))

def draw_snake(snake_list, dx ,dy ):
    for i, block in enumerate(snake_list):
        x, y = block

        # Head
        if i == len(snake_list) - 1:
            offset = (block_size - 60) // 2
            if dx > 0:
                screen.blit(head_right, (x + offset, y + offset))
            elif dx < 0:
                screen.blit(head_left, (x + offset, y + offset))
            elif dy > 0:
                screen.blit(head_down, (x + offset, y + offset))
            elif dy < 0:
                screen.blit(head_up, (x + offset, y + offset))

        # Tail
        elif i == 0 and len(snake_list) >= 2:
            offset = (block_size - 50) // 2
            x2, y2 = snake_list[1]
            dx_tail = x2 - x
            dy_tail = y2 - y
            if dx_tail > 0:
                screen.blit(tail_left, (x, y + offset))
            elif dx_tail < 0:
                screen.blit(tail_right, (x + offset, y + offset))
            elif dy_tail > 0:
                screen.blit(tail_up, (x + offset, y + offset))
            elif dy_tail < 0:
                screen.blit(tail_down, (x + offset, y + offset))

        # Body
        else:
            if len(snake_list) == 2:
                continue
            
            prev_x, prev_y = snake_list[i - 1]
            next_x, next_y = snake_list[i + 1]

            # If x stays same, it's vertical
            if prev_x == next_x:
                screen.blit(body_img, (x, y))
            # If y stays same, it's horizontal
            elif prev_y == next_y:
                screen.blit(body_img_horizontal, (x, y))
            else :
                screen.blit(body_img_horizontal,(x, y))
                

def show_score(score, high_score):
    score_text = font.render(f"Score: {score}", True, white)
    high_text = font.render(f"High Score: {high_score}", True, white)

    screen.blit(score_text, [10, 10])
    screen.blit(high_text, [10, 40])

def game_over_screen(score, high_score):
    screen.blit(bg_img,(0,0))

    msg = game_over_font.render("Game Over!", True, red)
    score_msg = font.render(f"Final Score: {score}", True, white)
    highscore_text = font.render(f"High Score: {high_score}", True, white)
    prompt = font.render("Press R to Restart or Q to Quit", True, blue)

    # Position messages nicely centered
    msg_rect = msg.get_rect(center=(width // 2, height // 2 - 100))
    score_rect = score_msg.get_rect(center=(width // 2, height // 2 - 40))
    highscore_rect = highscore_text.get_rect(center=(width // 2, height // 2))
    prompt_rect = prompt.get_rect(center=(width // 2, height // 2 + 60))

    screen.blit(msg, msg_rect)
    screen.blit(score_msg, score_rect)
    screen.blit(highscore_text, highscore_rect)
    screen.blit(prompt, prompt_rect)

    pygame.display.update()

def start_menu():
    waiting = True
    while waiting:
        screen.blit(bg_img,(0,0))
        title = game_over_font.render("Snake Game", True, blue)
        prompt = font.render("Press SPACE to Start or Q to Quit", True, white)

        screen.blit(title, title.get_rect(center=(width//2, height//2 - 150)))
        screen.blit(prompt, prompt.get_rect(center=(width//2, height//2 + 50)))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()


def game_loop():
    game_over = False
    game_close = False
    high_score = load_highscore()

    x, y = width // 2, height // 2
    dx, dy = 0, 0

    snake = [[x - block_size, y], [x, y]]
    length = 2
    score = 0
    special_fruit_active = False
    special_fruit_timer = 0
    special_fruit_duration = 5  # seconds
    special_fruit_interval = 30  # seconds
    last_special_spawn = time.time()
    special_x, special_y = 0, 0
    speed = initial_speed

    food_x = random.randrange(0, width - block_size, block_size)
    food_y = random.randrange(0, height - block_size, block_size)

    start_menu()
    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    speed = initial_speed
    while not game_over:

        while game_close:
            game_over_screen(score, high_score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_r:
                        game_loop()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx = -block_size
                    dy = 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx = block_size
                    dy = 0
                elif event.key == pygame.K_UP and dy == 0:
                    dy = -block_size
                    dx = 0
                elif event.key == pygame.K_DOWN and dy == 0:
                    dy = block_size
                    dx = 0

        x += dx
        y += dy

        # Handle special fruit spawn/despawn
        current_time = time.time()

        # Time to spawn a new special fruit
        if not special_fruit_active and current_time - last_special_spawn > special_fruit_interval:
            special_x = random.randrange(0, width - block_size, block_size)
            special_y = random.randrange(0, height - block_size, block_size)
            special_fruit_active = True
            special_fruit_timer = current_time  # mark the time it appeared

        # Despawn after duration
        if special_fruit_active and current_time - special_fruit_timer > special_fruit_duration:
            special_fruit_active = False
            last_special_spawn = current_time  # reset spawn clock
        
        # Wall collision
        if x < 0 or x >= width or y < 0 or y >= height:
            game_close = True
            try:
                pygame.mixer.music.stop()
                game_over_sound.play()
            except:
                pass

        screen.fill(bg_color)
        draw_grid() 
        screen.blit(apple_img, (food_x, food_y))

        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        # Self collision
        if length >= 3:
            for segment in snake[:-1]:
                if segment == [x, y]:   
                    game_close = True
                    try:
                        pygame.mixer.music.stop()
                        game_over_sound.play()
                    except:
                        pass

        draw_snake(snake, dx, dy)
        show_score(score, high_score)
        if dx == 0 and dy == 0:
            press_text = font.render("Press Arrow Key to Start", True, white)
            screen.blit(press_text, (width//2 - 150, height//2 + 100))
        if special_fruit_active:
            screen.blit(golden_apple_img, (special_x, special_y))

        pygame.display.update()
        clock.tick(speed)

        # Eat food
        if x == food_x and y == food_y:
            food_x = random.randrange(0, width - block_size, block_size)
            food_y = random.randrange(0, height - block_size, block_size)
            length += 1
            score += 10
            speed = min(speed + 0.3, 10)
            
            if score > high_score:
                high_score = score
                save_highscore(high_score)

            try:
                eat_sound.play()
            except:
                pass
            
        # Eat special fruit
        if special_fruit_active and x == special_x and y == special_y:
            score += 30
            length += 2
            special_fruit_active = False
            last_special_spawn = current_time
            try:
                golden_eat_sound.play()
            except:
                pass

    if score > high_score:
        high_score = score
        save_highscore(high_score)


    pygame.quit()
    quit()

game_loop()
