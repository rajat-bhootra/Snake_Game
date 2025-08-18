import pygame, time, random, json, os, sys

pygame.init()
pygame.mixer.init()

# Get display resolution (safer across platforms)
info = pygame.display.Info()
SCREEN_W, SCREEN_H = info.current_w, info.current_h

# Use explicit resolution for fullscreen (some platforms dislike (0,0))
flags = pygame.FULLSCREEN | pygame.SCALED
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
pygame.display.set_caption("Snake Game")

BASE_DIV = 30  # increase -> smaller cells; decrease -> larger cells
BLOCK = max(16, min(SCREEN_W, SCREEN_H) // BASE_DIV)

# head & tail sprites intentionally larger than block for the same style
HEAD_SIZE = int(BLOCK * 1.5)
TAIL_SIZE = int(BLOCK * 1.25)
HEART_SIZE = 40

# Fonts scaled
font = pygame.font.SysFont("consolas", max(24, BLOCK // 2), bold=True)
menu_font = pygame.font.SysFont("consolas", max(40, int(BLOCK * 0.9)), bold=True)
big_font = pygame.font.SysFont("consolas", max(24, int(BLOCK * 1.6)), bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
MENU_HIGHLIGHT = (220, 220, 220)

# Assets
IMG_DIR = os.path.join("assets", "image")
SND_DIR = os.path.join("assets", "sound")

ASSETS_IMAGES = {
    "icon": "logo.jpg",
    "apple": "apple.png",
    "golden": "golden_apple.png",
    "head_up": "snake_head_up.png",
    "head_down": "snake_head_down.png",
    "head_left": "snake_head_left.png",
    "head_right": "snake_head_right.png",
    "body": "snake_body.png",
    "body_h": "snake_body_horizontal.png",
    "tail_up": "snake_tail_up.png",
    "tail_down": "snake_tail_down.png",
    "tail_left": "snake_tail_left.png",
    "tail_right": "snake_tail_right.png",
    "start_bg": "background.png",
    "game_over_bg": "Game_over_bg.png",
    "heart": "heart.png",
}

ASSETS_SOUNDS = {
    "music": "background.mp3",
    "eat": "eat.mp3",
    "game_over": "game_over.mp3",
    "golden": "golden.mp3",
}

# Image & sound loaders
def safe_load_image(fname, scale=None, placeholder_color=(200, 0, 0)):
    path = os.path.join(IMG_DIR, fname)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"[image warning] couldn't load {path}: {e}")
        if scale:
            surf = pygame.Surface(scale, pygame.SRCALPHA)
            surf.fill(placeholder_color)
            return surf
        return None

def safe_load_sound(fname):
    path = os.path.join(SND_DIR, fname)
    try:
        snd = pygame.mixer.Sound(path)
        return snd
    except Exception as e:
        print(f"[sound warning] couldn't load {path}: {e}")
        return None

# load & scale images
icon = safe_load_image(ASSETS_IMAGES["icon"], scale=(HEAD_SIZE, HEAD_SIZE))
if icon:
    pygame.display.set_icon(icon)

apple_img = safe_load_image(ASSETS_IMAGES["apple"], scale=(BLOCK, BLOCK))
golden_img = safe_load_image(ASSETS_IMAGES["golden"], scale=(BLOCK, BLOCK))

head_up = safe_load_image(ASSETS_IMAGES["head_up"], scale=(HEAD_SIZE, HEAD_SIZE))
head_down = safe_load_image(ASSETS_IMAGES["head_down"], scale=(HEAD_SIZE, HEAD_SIZE))
head_left = safe_load_image(ASSETS_IMAGES["head_left"], scale=(HEAD_SIZE, HEAD_SIZE))
head_right = safe_load_image(ASSETS_IMAGES["head_right"], scale=(HEAD_SIZE, HEAD_SIZE))

body_img = safe_load_image(ASSETS_IMAGES["body"], scale=(BLOCK, BLOCK))
body_img_h = safe_load_image(ASSETS_IMAGES["body_h"], scale=(BLOCK, BLOCK))

tail_up = safe_load_image(ASSETS_IMAGES["tail_up"], scale=(TAIL_SIZE, TAIL_SIZE))
tail_down = safe_load_image(ASSETS_IMAGES["tail_down"], scale=(TAIL_SIZE, TAIL_SIZE))
tail_left = safe_load_image(ASSETS_IMAGES["tail_left"], scale=(TAIL_SIZE, TAIL_SIZE))
tail_right = safe_load_image(ASSETS_IMAGES["tail_right"], scale=(TAIL_SIZE, TAIL_SIZE))

start_bg = safe_load_image(ASSETS_IMAGES["start_bg"], scale=(SCREEN_W, SCREEN_H))
game_over_bg = safe_load_image(ASSETS_IMAGES["game_over_bg"], scale=(SCREEN_W, SCREEN_H))
heart_img = safe_load_image(ASSETS_IMAGES["heart"], scale=(HEART_SIZE, HEART_SIZE))

# sounds
music_path = os.path.join(SND_DIR, ASSETS_SOUNDS["music"])
if os.path.exists(music_path):
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.28)
    except Exception as e:
        print("[music warning]", e)
else:
    print("[music warning] background music file missing.")

eat_sound = safe_load_sound(ASSETS_SOUNDS["eat"])
game_over_sound = safe_load_sound(ASSETS_SOUNDS["game_over"])
golden_sound = safe_load_sound(ASSETS_SOUNDS["golden"])

clock = pygame.time.Clock()

# Highscores JSON
HIGHSCORE_FILE = "highscores.json"
TRACKED = ["Classic", "Timed", "Hardcore", "Survival"]

def ensure_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        data = {m: 0 for m in TRACKED}
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(data, f)
ensure_highscores()

def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("[hs warning]", e)
        return {m: 0 for m in TRACKED}

def save_highscore(mode, score):
    if mode not in TRACKED:
        return
    data = load_highscores()
    if score > data.get(mode, 0):
        data[mode] = score
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print("[hs warning] couldn't save:", e)

# Drawing helpers
def draw_grid():
    for x in range(0, SCREEN_W, BLOCK):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, BLOCK):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_W, y))

def draw_snake(snake_list, dx, dy):
    for i, (x, y) in enumerate(snake_list):
        px, py = x, y
        # head
        if i == len(snake_list) - 1:
            offset = (BLOCK - HEAD_SIZE) // 2
            if dx > 0:
                screen.blit(head_right, (px + offset, py + offset))
            elif dx < 0:
                screen.blit(head_left, (px + offset, py + offset))
            elif dy > 0:
                screen.blit(head_down, (px + offset, py + offset))
            elif dy < 0:
                screen.blit(head_up, (px + offset, py + offset))
        # tail
        elif i == 0 and len(snake_list) >= 2:
            offset = (BLOCK - TAIL_SIZE) // 2
            x2, y2 = snake_list[1]
            dx_tail = x2 - px
            dy_tail = y2 - py
            if dx_tail > 0:
                screen.blit(tail_left, (px, py + offset))
            elif dx_tail < 0:
                screen.blit(tail_right, (px + offset, py + offset))
            elif dy_tail > 0:
                screen.blit(tail_up, (px + offset, py + offset))
            elif dy_tail < 0:
                screen.blit(tail_down, (px + offset, py + offset))
        # body
        else:
            if len(snake_list) == 2:
                continue
            prev_x, prev_y = snake_list[i - 1]
            next_x, next_y = snake_list[i + 1]
            if prev_x == next_x:
                screen.blit(body_img, (px, py))
            elif prev_y == next_y:
                screen.blit(body_img_h, (px, py))
            else:
                screen.blit(body_img_h, (px, py))

def get_valid_food_position(snake):
    while True:
        x = random.randrange(0, SCREEN_W - BLOCK, BLOCK)
        y = random.randrange(0, SCREEN_H - BLOCK, BLOCK)
        if x < 200 and y < 80:
            continue
        if [x, y] in snake:
            continue
        return x, y

def show_score_and_high(mode, score):
    scores = load_highscores()
    high = scores.get(mode, 0)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    if mode in TRACKED:
        high_text = font.render(f"High Score: {high}", True, WHITE)
        screen.blit(high_text, (10, 10 + score_text.get_height() + 6))

# Game Modes (each is its own loop)

# Classic - walls kill, self kill, tracked highscore
def game_loop_classic():
    mode = "Classic"
    high_before = load_highscores().get(mode, 0)

    # start centered on grid (multiples of BLOCK)
    x0 = (SCREEN_W // 2 // BLOCK) * BLOCK
    y0 = (SCREEN_H // 2 // BLOCK) * BLOCK
    x, y = x0, y0
    dx, dy = 0, 0
    snake = [[x - BLOCK, y], [x, y]]
    length = 2
    score = 0
    speed = 5

    special_active = False
    special_timer = 0
    special_duration = 5
    special_interval = 30
    last_special = time.time()
    special_x, special_y = 0, 0

    food_x, food_y = get_valid_food_position(snake)

    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    return
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        x += dx; y += dy

        # special spawn/despawn
        now = time.time()
        if not special_active and now - last_special > special_interval:
            special_x, special_y = get_valid_food_position(snake)
            special_active = True
            special_timer = now
        if special_active and now - special_timer > special_duration:
            special_active = False
            last_special = now

        # walls kill
        if x < 0 or x >= SCREEN_W or y < 0 or y >= SCREEN_H:
            try:
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
            except:
                pass
            running = False
            break

        screen.fill(BG_COLOR)
        draw_grid()
        if apple_img:
            screen.blit(apple_img, (food_x, food_y))
        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        # self collision
        if length >= 3 and [x, y] in snake[:-1]:
            try:
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
            except:
                pass
            running = False
            break

        draw_snake(snake, dx, dy)
        show_score_and_high(mode, score)
        if dx == 0 and dy == 0:
            press = font.render("Press Arrow Key to Start", True, WHITE)
            screen.blit(press, (SCREEN_W//2 - press.get_width()//2, SCREEN_H//2 + 220))
        if special_active and golden_img:
            screen.blit(golden_img, (special_x, special_y))

        pygame.display.update()
        clock.tick(speed)

        # Eat food
        if x == food_x and y == food_y:
            food_x, food_y = get_valid_food_position(snake)
            length += 1
            score += 10
            speed = min(speed + 0.3, 30)
            if score > high_before:
                save_highscore(mode, score)
            try:
                if eat_sound: eat_sound.play()
            except:
                pass

        # Eat special fruit
        if special_active and x == special_x and y == special_y:
            score += 30
            length += 2
            special_active = False
            last_special = now
            if score > high_before:
                save_highscore(mode, score)
            try:
                if golden_sound: golden_sound.play()
            except:
                pass

    if score > high_before:
        save_highscore(mode, score)
    try:
        pygame.mixer.music.stop()
        if game_over_sound: game_over_sound.play()
    except:
        pass

    game_over_screen(mode, score)

# Timed - 60s, wrap walls, self kills
def game_loop_timed():
    mode = "Timed"
    high_before = load_highscores().get(mode, 0)

    x0 = (SCREEN_W // 2 // BLOCK) * BLOCK
    y0 = (SCREEN_H // 2 // BLOCK) * BLOCK
    x, y = x0, y0
    dx, dy = 0, 0
    snake = [[x - BLOCK, y], [x, y]]
    length = 2
    score = 0
    speed = 5
    time_left = 60
    last_tick = time.time()

    special_active = False
    special_timer = 0
    special_duration = 5
    special_interval = 30
    last_special = time.time()
    special_x, special_y = 0, 0

    food_x, food_y = get_valid_food_position(snake)

    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        now = time.time()
        if now - last_tick >= 1:
            time_left -= 1
            last_tick = now
        if time_left <= 0:
            running = False
            break

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    return
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        x += dx; y += dy

        # special spawn/despawn
        if not special_active and now - last_special > special_interval:
            special_x, special_y = get_valid_food_position(snake)
            special_active = True
            special_timer = now
        if special_active and now - special_timer > special_duration:
            special_active = False
            last_special = now

        # wrap walls
        if x < 0: x = SCREEN_W - BLOCK
        elif x >= SCREEN_W: x = 0
        if y < 0: y = SCREEN_H - BLOCK
        elif y >= SCREEN_H: y = 0

        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        # self collision
        if length >= 3 and [x, y] in snake[:-1]:
            try:
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
            except:
                pass
            running = False
            break

        # eat
        if x == food_x and y == food_y:
            food_x, food_y = get_valid_food_position(snake)
            length += 1
            score += 10
            time_left += 2
            speed = min(speed + 0.3, 30)
            if score > high_before:
                save_highscore(mode, score)
            try:
                if eat_sound: eat_sound.play()
            except:
                pass

        if special_active and x == special_x and y == special_y:
            score += 30
            length += 2
            special_active = False
            last_special = now
            if score > high_before:
                save_highscore(mode, score)
            try:
                if golden_sound: golden_sound.play()
            except:
                pass

        # draw
        screen.fill(BG_COLOR)
        draw_grid()
        if apple_img:
            screen.blit(apple_img, (food_x, food_y))
        if special_active and golden_img:
            screen.blit(golden_img, (special_x, special_y))
        draw_snake(snake, dx, dy)
        show_score_and_high(mode, score)
        timer_text = font.render(f"Time: {time_left}s", True, WHITE)
        screen.blit(timer_text, (SCREEN_W - timer_text.get_width() - 20, 10))
        if dx == 0 and dy == 0:
            press = font.render("Press Arrow Key to Start", True, WHITE)
            screen.blit(press, (SCREEN_W//2 - press.get_width()//2, SCREEN_H//2 + 220))
        pygame.display.update()
        clock.tick(speed)

    if score > high_before:
        save_highscore(mode, score)
    try:
        pygame.mixer.music.stop()
        if game_over_sound: game_over_sound.play()
    except:
        pass
    game_over_screen(mode, score)

# Hardcore - double starting speed, walls kill & self kill
def game_loop_hardcore():
    mode = "Hardcore"
    high_before = load_highscores().get(mode, 0)

    x0 = (SCREEN_W // 2 // BLOCK) * BLOCK
    y0 = (SCREEN_H // 2 // BLOCK) * BLOCK
    x, y = x0, y0
    dx, dy = 0, 0
    snake = [[x - BLOCK, y], [x, y]]
    length = 2
    score = 0
    speed = min(40, 10)

    special_active = False
    special_timer = 0
    special_duration = 5
    special_interval = 30
    last_special = time.time()
    special_x, special_y = 0, 0

    food_x, food_y = get_valid_food_position(snake)

    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        now = time.time()
        if not special_active and now - last_special > special_interval:
            special_x, special_y = get_valid_food_position(snake)
            special_active = True
            special_timer = now
        if special_active and now - special_timer > special_duration:
            special_active = False
            last_special = now

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    return
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        x += dx; y += dy

        # walls kill
        if x < 0 or x >= SCREEN_W or y < 0 or y >= SCREEN_H:
            try:
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
            except:
                pass
            running = False
            break

        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        # self kills
        if length >= 3 and [x, y] in snake[:-1]:
            try:
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
            except:
                pass
            running = False
            break

        # eat
        if x == food_x and y == food_y:
            food_x, food_y = get_valid_food_position(snake)
            length += 1
            score += 10
            speed = min(60, speed + 1)
            if score > high_before:
                save_highscore(mode, score)
            try:
                if eat_sound: eat_sound.play()
            except:
                pass

        if special_active and x == special_x and y == special_y:
            score += 30
            length += 2
            special_active = False
            last_special = now
            if score > high_before:
                save_highscore(mode, score)
            try:
                if golden_sound: golden_sound.play()
            except:
                pass

        # draw
        screen.fill(BG_COLOR)
        draw_grid()
        if apple_img:
            screen.blit(apple_img, (food_x, food_y))
        if special_active and golden_img:
            screen.blit(golden_img, (special_x, special_y))
        draw_snake(snake, dx, dy)
        show_score_and_high(mode, score)
        if dx == 0 and dy == 0:
            press = font.render("Press Arrow Key to Start", True, WHITE)
            screen.blit(press, (SCREEN_W//2 - press.get_width()//2, SCREEN_H//2 + 220))
        pygame.display.update()
        clock.tick(speed)

    if score > high_before:
        save_highscore(mode, score)
    game_over_screen(mode, score)

# Survival - 3 lives, top-right xN display, respawn after collision until lives==0
def game_loop_survival():
    mode = "Survival"
    high_before = load_highscores().get(mode, 0)
    lives = 3

    x0 = (SCREEN_W // 2 // BLOCK) * BLOCK
    y0 = (SCREEN_H // 2 // BLOCK) * BLOCK
    x, y = x0, y0
    dx, dy = 0, 0
    snake = [[x - BLOCK, y], [x, y]]
    length = 2
    score = 0
    speed = 5

    special_active = False
    special_timer = 0
    special_duration = 5
    special_interval = 30
    last_special = time.time()
    special_x, special_y = 0, 0

    food_x, food_y = get_valid_food_position(snake)

    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        now = time.time()
        if not special_active and now - last_special > special_interval:
            special_x, special_y = get_valid_food_position(snake)
            special_active = True
            special_timer = now
        if special_active and now - special_timer > special_duration:
            special_active = False
            last_special = now

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    return
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        x += dx; y += dy

        # check collisions
        hit_wall = (x < 0 or x >= SCREEN_W or y < 0 or y >= SCREEN_H)
        snake.append([x, y])
        if len(snake) > length:
            del snake[0]
        hit_self = (length >= 3 and [x, y] in snake[:-1])

        if hit_wall or hit_self:
            lives -= 1
            if lives <= 0:
                try:
                    pygame.mixer.music.stop()
                    if game_over_sound: game_over_sound.play()
                except:
                    pass
                running = False
                break
            # respawn
            x = x0; y = y0
            dx = dy = 0
            speed = 5
            snake = [[x - BLOCK, y], [x, y]]
            length = 2
            time.sleep(0.4)
            continue

        # eat
        if x == food_x and y == food_y:
            food_x, food_y = get_valid_food_position(snake)
            length += 1
            score += 10
            speed = min(speed + 1, 30)
            if score > high_before:
                save_highscore(mode, score)
            try:
                if eat_sound: eat_sound.play()
            except:
                pass

        if special_active and x == special_x and y == special_y:
            score += 30
            length += 2
            special_active = False
            last_special = now
            if score > high_before:
                save_highscore(mode, score)
            try:
                if golden_sound: golden_sound.play()
            except:
                pass

        # draw
        screen.fill(BG_COLOR)
        draw_grid()
        if apple_img:
            screen.blit(apple_img, (food_x, food_y))
        if special_active and golden_img:
            screen.blit(golden_img, (special_x, special_y))
        draw_snake(snake, dx, dy)
        show_score_and_high(mode, score)

        # draw heart + number top-right (heart then 'xN' to its left)
        heart_x = SCREEN_W - 10 - HEART_SIZE
        heart_y = 10
        if heart_img:
            screen.blit(heart_img, (heart_x, heart_y))
        else:
            pygame.draw.rect(screen, (200, 20, 20), (heart_x, heart_y, HEART_SIZE, HEART_SIZE))
        lives_text = font.render(f"x{lives}", True, WHITE)
        screen.blit(lives_text, (heart_x - lives_text.get_width() - 8, heart_y + HEART_SIZE//2 - lives_text.get_height()//2))

        if dx == 0 and dy == 0:
            press = font.render("Press Arrow Key to Start", True, WHITE)
            screen.blit(press, (SCREEN_W//2 - press.get_width()//2, SCREEN_H//2 + 220))

        pygame.display.update()
        clock.tick(speed)

    if score > high_before:
        save_highscore(mode, score)
    game_over_screen(mode, score)

# Zen - wrap walls + no tracked highscore, ESC to exit to menu
def game_loop_zen():
    x0 = (SCREEN_W // 2 // BLOCK) * BLOCK
    y0 = (SCREEN_H // 2 // BLOCK) * BLOCK
    x, y = x0, y0
    dx, dy = 0, 0
    snake = [[x - BLOCK, y], [x, y]]
    length = 2
    score = 0
    speed = max(4, int(5))

    special_active = False
    special_timer = 0
    special_duration = 5
    special_interval = 30
    last_special = time.time()
    special_x, special_y = 0, 0

    food_x, food_y = get_valid_food_position(snake)

    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    return
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                elif e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                elif e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                elif e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        x += dx; y += dy

        now = time.time()
        if not special_active and now - last_special > special_interval:
            special_x, special_y = get_valid_food_position(snake)
            special_active = True
            special_timer = now
        if special_active and now - special_timer > special_duration:
            special_active = False
            last_special = now

        # wrap
        if x < 0: x = SCREEN_W - BLOCK
        elif x >= SCREEN_W: x = 0
        if y < 0: y = SCREEN_H - BLOCK
        elif y >= SCREEN_H: y = 0

        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        # gentle penalty on self-hit: reset length & position
        if length >= 3 and [x, y] in snake[:-1]:
            length = 2
            snake = [[x - BLOCK, y], [x, y]]

        # eat
        if x == food_x and y == food_y:
            food_x, food_y = get_valid_food_position(snake)
            length += 1
            score += 10
            try:
                if eat_sound: eat_sound.play()
            except:
                pass

        if special_active and x == special_x and y == special_y:
            score += 30
            length += 2
            special_active = False
            last_special = now
            try:
                if golden_sound: golden_sound.play()
            except:
                pass

        # draw
        screen.fill(BG_COLOR)
        draw_grid()
        if apple_img:
            screen.blit(apple_img, (food_x, food_y))
        if special_active and golden_img:
            screen.blit(golden_img, (special_x, special_y))
        draw_snake(snake, dx, dy)
        # Zen shows score but no highscore
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        if dx == 0 and dy == 0:
            press = font.render("Press Arrow Key to Start • ESC to exit", True, WHITE)
            screen.blit(press, (SCREEN_W//2 - press.get_width()//2, SCREEN_H//2 + 220))

        pygame.display.update()
        clock.tick(speed)


# UI screens
def game_over_screen(mode, score):
    if game_over_bg:
        screen.blit(game_over_bg, (0, 0))
    else:
        screen.fill(BLACK)
    sub = big_font.render(f"Mode: {mode}  |  Score: {score}", True, BLACK)
    screen.blit(sub, sub.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
    prompt = font.render("Press R to return to menu or Q to quit", True,BLACK)
    screen.blit(prompt, prompt.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 300)))
    pygame.display.update()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return
                if e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

# Start menu (text-based, arrow keys & Enter)
def start_menu():
    options = ["Classic", "Timed (60s)", "Hardcore", "Survival (3 lives)", "Zen", "Quit"]
    idx = 0
    while True:
        if start_bg:
            screen.blit(start_bg, (0, 0))
        else:
            screen.fill(BG_COLOR)

        hs = load_highscores()
        for i, opt in enumerate(options):
            y = SCREEN_H//2 + (i - 1) * (menu_font.get_height() + 12)
            if i == idx:
                text = menu_font.render(opt, True, BLACK)
                rect = text.get_rect(center=(SCREEN_W//2, y))
                pygame.draw.rect(screen, MENU_HIGHLIGHT, (rect.x - 18, rect.y - 6, rect.width + 36, rect.height + 12), border_radius=8)
                screen.blit(text, rect)
            else:
                text = menu_font.render(opt, True, BLACK)
                screen.blit(text, text.get_rect(center=(SCREEN_W//2, y)))

            # show highscore if tracked
            mode_name = opt.split()[0]
            if mode_name in hs:
                score_text = font.render(f"High Score: {hs[mode_name]}", True, BLACK)
                screen.blit(score_text, (SCREEN_W//2 + 260, y - score_text.get_height()//2))
            elif "Zen" in opt:
                note = font.render("(No Highscore)", True, BLACK)
                screen.blit(note, (SCREEN_W//2 + 250, y - note.get_height()//2))

        hint = font.render("Use ↑/↓ or W/S to move • Enter to select • Q to quit", True, BLACK)
        screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 80))
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(options)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(options)
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    sel = options[idx]
                    if "Classic" in sel:
                        game_loop_classic()
                    elif "Timed" in sel:
                        game_loop_timed()
                    elif "Hardcore" in sel:
                        game_loop_hardcore()
                    elif "Survival" in sel:
                        game_loop_survival()
                    elif "Zen" in sel:
                        game_loop_zen()
                    elif "Quit" in sel:
                        pygame.quit(); sys.exit()
                elif e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

# Start
if __name__ == "__main__":
    ensure_highscores()
    start_menu()
