import pygame
import random
import os
import sys
import json  # For saving and loading data

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch the Stars")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# File paths for storing user data
if os.name == 'nt':  # Windows
    DATA_FILE = os.path.join(os.environ['APPDATA'], 'CatchTheStars', 'user_data.json')
else:  # Linux or macOS
    DATA_FILE = os.path.join(os.path.expanduser('~'), '.CatchTheStars', 'user_data.json')

# Ensure the directory exists
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

print(f"Saving data to: {DATA_FILE}")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # This is set when PyInstaller creates the .exe
    except Exception:
        base_path = os.path.abspath(".")  # If it's not an exe, fall back to the current directory
    final_path = os.path.join(base_path, relative_path)
    print(f"Loading resource from: {final_path}")
    return final_path

BOX_WIDTH, BOX_HEIGHT = 65, 45  # dimensions of the box image
STAR_WIDTH, STAR_HEIGHT = 50, 50  # dimensions of the star image

# Load Assets
raw_star_img = pygame.image.load(resource_path("assets/star.png"))
star_img = pygame.transform.scale(raw_star_img, (50, 50))

box_img = pygame.image.load(resource_path("assets/box.png"))
box_img = pygame.transform.scale(box_img, (65, 45))

background_img = pygame.image.load(resource_path("assets/background.png"))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

pygame.mixer.music.load(resource_path("assets/lofi.mp3"))
pygame.mixer.music.set_volume(0.5)

# Default Game State
stars = []
player = {"x": WIDTH // 2 - 40, "y": HEIGHT - 60, "speed": 10, "score": 0, "lives": 10}
username = f"Player{random.randint(1000, 9999)}"
highscore = 0
profile_pic = None
MAX_STARS = 3
fixed_speed = 11
volume_music = 0.5
last_spawn_time = pygame.time.get_ticks()
spawn_interval = 1200 # in ms

# Save user data to a JSON file
def save_user_data():
    data = {
        "username": username,
        "highscore": highscore
    }
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Load user data from a JSON file
def load_user_data():
    global username, highscore
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            username = data.get("username", f"Player{random.randint(1000, 9999)}")
            highscore = data.get("highscore", 0)

load_user_data()  # Load user data when the game starts

def draw_background():
    screen.blit(background_img, (0, 0))
  
def draw_player():
    screen.blit(box_img, (player["x"], player["y"]))

def draw_stars():
    for s in stars:
        screen.blit(star_img, (s["x"], s["y"]))

def update_stars():
    global player
    player_rect = pygame.Rect(player["x"], player["y"], BOX_WIDTH, BOX_HEIGHT)
    for s in stars[:]:  # Use a slice to iterate over a copy of the list
        s["y"] += fixed_speed
        star_rect = pygame.Rect(s["x"], s["y"], STAR_WIDTH, STAR_HEIGHT)

        if s["y"] > HEIGHT:  # Star goes off the bottom of the screen
            stars.remove(s)
            player["lives"] -= 1
        elif player_rect.colliderect(star_rect):  # Player collects the star
            stars.remove(s)
            player["score"] += 1

def draw_hud():
    score_text = font.render(f"Score: {player['score']}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {player['lives']}", True, (255, 100, 100))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))

def settings_menu():
    global volume_music
    running = True
    while running:
        screen.fill((30, 30, 50))
        txt = font.render("Settings - Use UP/DOWN to change volume. ESC to exit.", True, (255, 255, 255))
        screen.blit(txt, (50, 50))

        vol_mus = font.render(f"Music Volume: {int(volume_music*100)}%", True, (200, 200, 255))
        screen.blit(vol_mus, (50, 150))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_UP:
                    volume_music = min(volume_music + 0.1, 1)
                    pygame.mixer.music.set_volume(volume_music)
                elif e.key == pygame.K_DOWN:
                    volume_music = max(volume_music - 0.1, 0)
                    pygame.mixer.music.set_volume(volume_music)

def show_leaderboard():
    global highscore
    if player["score"] > highscore:
        highscore = player["score"]
        save_user_data()  # Save highscore when it changes
    running = True
    while running:
        screen.fill((20, 20, 40))
        screen.blit(font.render("LEADERBOARD", True, (255, 255, 0)), (WIDTH//2 - 100, 60))
        screen.blit(font.render(f"{username} - High Score: {highscore}", True, (255, 255, 255)), (WIDTH//2 - 120, 120))
        screen.blit(font.render("Press ESC to return", True, (200, 200, 200)), (WIDTH//2 - 100, 300))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False

def profile_menu():
    global username
    running = True
    input_text = ""
    while running:
        screen.fill((10, 10, 30))
        screen.blit(font.render("Enter your name (ENTER to confirm):", True, (255, 255, 255)), (50, 100))
        screen.blit(font.render(input_text, True, (255, 255, 0)), (50, 150))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if input_text.strip() != "":
                        username = input_text
                        save_user_data()  # Save new username
                    running = False
                elif e.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += e.unicode

# Main game logic
def menu():
    pygame.mixer.music.play(-1)
    while True:
        screen.fill((25, 25, 35))
        draw_background()
        title = font.render("Catch the Stars ", True, (255, 255, 255))
        start_btn = font.render("[1] Start Game", True, (200, 255, 200))
        settings_btn = font.render("[2] Settings", True, (200, 200, 255))
        lb_btn = font.render("[3] Leaderboard", True, (255, 255, 200))
        prof_btn = font.render("[4] Profile", True, (255, 200, 255))

        screen.blit(title, (WIDTH//2 - 100, 100))
        screen.blit(start_btn, (WIDTH//2 - 100, 180))
        screen.blit(settings_btn, (WIDTH//2 - 100, 220))
        screen.blit(lb_btn, (WIDTH//2 - 100, 260))
        screen.blit(prof_btn, (WIDTH//2 - 100, 300))
        
        footer_text = font.render("Developed By s34g & Ghaymar | © 2025", True, (255, 255, 255))
        screen.blit(footer_text, (10, HEIGHT - 28))
        
        footer_text = font.render("v0.2", True, (255, 255, 255))
        screen.blit(footer_text, (750, HEIGHT - 28))
        
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return
                elif e.key == pygame.K_2:
                    settings_menu()
                elif e.key == pygame.K_3:
                    show_leaderboard()
                elif e.key == pygame.K_4:
                    profile_menu()

# Main Game loop, game over screen with highscore check
# Main Game loop, game over screen with highscore check
def game_over_screen():
    global player, highscore  # Access player and highscore
    screen.fill((0, 0, 0))  # Make background black for game over

    # Title - Game Over
    game_over_font = pygame.font.SysFont("arial", 50)  
    game_over_title = game_over_font.render("Game Over!", True, (255, 0, 0))
    screen.blit(game_over_title, (WIDTH // 2 - game_over_title.get_width() // 2, HEIGHT // 2 - 100))
    
    # Score Display
    score_text = font.render(f"Your Score: {player['score']}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 40))
    
    # Highscore Display
    highscore_text = font.render(f"High Score: {highscore}", True, (255, 255, 0))
    screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, HEIGHT // 2))

    # Instructions for next steps
    instructions_text = font.render("Press [M] to go to Main Menu or [ESC] to Exit", True, (255, 255, 255))
    screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT // 2 + 40))

    # Update highscore if player's score is higher
    if player["score"] > highscore:
        highscore = player["score"]
        save_user_data()  # Save highscore when it changes

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()  # Exit the game
                    return
                elif e.key == pygame.K_m:
                    player["score"] = 0
                    player["lives"] = 10
                    stars.clear()
                    menu()  # Go back to the main menu
                    return  # Stop the game over loop

menu()  # Display the main menu
run = True
while run:
    clock.tick(60)
    draw_background()
    
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= spawn_interval and len(stars) < MAX_STARS:
        stars.append({"x": random.randint(0, WIDTH - STAR_WIDTH), "y": 0, "speed": random.randint(3, 6)})
        last_spawn_time = current_time

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player["x"] -= player["speed"]
    if keys[pygame.K_RIGHT]:
        player["x"] += player["speed"]
    player["x"] = max(0, min(player["x"], WIDTH - 80))

    update_stars()
    draw_stars()
    draw_player()
    draw_hud()

    if player["lives"] <= 0:
        game_over_screen()

    pygame.display.flip()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                run = False

pygame.quit()
sys.exit()