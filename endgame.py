import pygame
import sys
import random 
import time
from moviepy.editor import VideoFileClip
import numpy as np

# Initialize pygame
pygame.init()

score = 0


# Display screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("dark tunnel")

# Set clock for frame rate
FPS = 60  # Game frame rate
clock = pygame.time.Clock()

#Colours
WHITE = (255,255,255)
BLACK = (0,0,0,)
RED = (255,0,0)
GREEN = (0,255,0)

def draw_text(text, font, color, surface, x, y):
    """utility function to draw text on screen """
    text_obj = font.render(text , True, color)
    text_rect =  text_obj.get_rect(center=(x,y))
    surface.blit(text_obj, text_rect)
    return text_rect #return rectangle for detecting clicks

def home_screen(screen, assets):
    """ Function to display the home screen with start and quit option"""
    font = assets['font']

    while True:
        screen.blit(assets['home_background'],(0,0))

        draw_text("RACE_In_SPACE", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//4)
        start_button = draw_text("START", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        quit_button= draw_text("QUIT", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 +80)

        #handle events
        for event in pygame.event.get():
            if event.type ==  pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # get mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()

                #check if start is clicked
                if start_button.collidepoint(mouse_x, mouse_y):
                    return #start the game
                # check if quit is clicked
                if quit_button.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(FPS)
                    
                    
def load_assets():
    assets = {}


    #load background image for home screen
    try:
        assets['home_background'] = pygame.image.load(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\homescreen\home_screen.png').convert()
    except pygame.error as e:
        print(f"Unable to load background image: {e}")
        sys.exit()
    
    #load custon font
    try:
        assets['font']= pygame.font.Font(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\font\font1.ttf',50) 
    except pygame.error as e:
        print(f"Unable to load font {e}")
        sys.exit()

    try:
        assets['score_font']= pygame.font.Font(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\font\font1.ttf',30) 
    except pygame.error as e:
        print(f"Unable to load font {e}")
        sys.exit()

    # Load background video
    try:
        video_clip = VideoFileClip(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\background\background.mp4')
    except Exception as e:
        print(f"Error loading background video: {e}")
        sys.exit()
    assets['background_video'] = video_clip
    assets['background_fps'] = video_clip.fps

    # Load character image
    try:
        assets['player'] = pygame.image.load(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\character\ship1.png').convert_alpha()
    except pygame.error as e:
        print(f"Unable to load player image: {e}")
        sys.exit()

    # Load obstacle image
    try:
        assets['obstacle'] = pygame.image.load(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\obstacle\fireball1.png').convert_alpha()
    except pygame.error as e:
        print(f"Unable to load obstacle image: {e}")
        sys.exit()

    # Load sounds
    try:
        pygame.mixer.music.load(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\sounds\background_music.mp3')
        assets['jump_sound'] = pygame.mixer.Sound(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\sounds\bladesound.wav')
        assets['game_over_sound'] = pygame.mixer.Sound(r'C:\Users\paree\AppData\Local\Programs\game\endless_runner\assets\sounds\gameover.wav')
    except pygame.error as e:
        print(f"Unable to load sounds: {e}")
        sys.exit()

    return assets

# Preprocess frames from video
def get_video_frames(video_clip):
    for frame in video_clip.iter_frames():
        frame_surface = pygame.surfarray.make_surface(np.rot90(frame))
        yield frame_surface

class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask from the player image
        self.speed = 5

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, initial_scale, speed):
        super().__init__()
        self.original_image = image  # Store the original image for scaling
        self.image = pygame.transform.scale(self.original_image, initial_scale)  # Scale it initially
        self.rect = self.image.get_rect(center=start_pos)
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask from the obstacle image
        self.speed = speed
        self.diverging = False
        self.diverging_direction = random.choice([-1, 0, 1])
        self.divergence_speed = 2
        self.divergence_point = SCREEN_HEIGHT // 3

    def update(self):
        if not self.diverging:
            # Move straight down toward the player
            self.rect.y += self.speed

            # Start diverging once the obstacle crosses the divergence point
            if self.rect.y > self.divergence_point:
                self.diverging = True
        else:
            # Continue moving down but also diverge left, right, or straight
            self.rect.y += self.speed
            self.rect.x += self.diverging_direction * self.divergence_speed

        # Scale the obstacle as it moves further down the screen to give a zoom-in effect
        new_width = int(self.image.get_width() * 1.02)
        new_height = int(self.image.get_height() * 1.02)
        if new_width>100:
            new_width = 100
        if new_height >100:
            new_height = 100
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.rect = self.image.get_rect(center=self.rect.center)

        # Remove obstacle if it goes off the screen
        if self.rect.top > SCREEN_HEIGHT or self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()

def show_game_over_screen(screen,assets):
    global high_score,score
    font = assets['font']
    score_font = assets['score_font']
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2-40))
    score_text = score_font.render(f"Score: {score}", True,(255,255, 0))
    high_score_text = score_font.render(f" High Score: {high_score}", True, (255,255,0))
    score_rect = score_text.get_rect(center= (200,50))
    high_score_rect = high_score_text.get_rect(center = (SCREEN_WIDTH-250, 50))

    screen.blit(text, text_rect)
    screen.blit(score_text, score_rect)
    screen.blit(high_score_text,high_score_rect)
    pygame.display.update()
    pygame.time.delay(3000)  # Display for 3 seconds


def save_high_score(high_score):
    with open('high_score.txt','w') as f:
        f.write(str(high_score))

def load_high_score():
    try:
        with open('high_score.txt','r') as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0


def show_game_over_panel(screen, assets):
    font = assets['score_font']
    retry_button_rect = draw_text("Retry?",font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)
    quit_button_rect = draw_text("Quit", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                #check if retry is clicked
                if retry_button_rect.collidepoint(mouse_x, mouse_y):
                    return True
                if quit_button_rect.collidepoint(mouse_x,mouse_y):
                    pygame.quit()
                    sys.exit()

def handle_game_over(screen, assets):
    """handle the game over scenario."""
    show_game_over_screen(screen, assets)
    return show_game_over_panel(screen, assets)

# Main loop
def main():
    global high_score, score
    running = True
    assets = load_assets()
    
    high_score = load_high_score()
    

    # Play background music
    pygame.mixer.music.play(-1)

    # Create player
    player = Player(assets['player'], (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    player_group = pygame.sprite.GroupSingle(player)

    # Initialize video frame generator
    frame_generator = get_video_frames(assets['background_video'])

    # Obstacle group
    obstacle_group = pygame.sprite.Group()

    # Timer for spawning obstacles
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer,800)  # Spawn every 0.8 seconds

    score_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(score_timer,1000)  # increase score every sec
    
    # Initialize clock for game loop
    game_clock = pygame.time.Clock()

    #start game from the home screen
    home_screen(screen, assets)

    # Set initial obstacle speed
    #obstacle_speed = 4
   # speed_increase_interval = 10000  # 10 seconds
    #last_speed_increase_time = pygame.time.get_ticks()

    # Background frame index
    bg_frame = None

    while running:
        score=0
         # Start the game session loop
        game_session_running = True
        obstacle_group.empty()  # Clear any previous obstacles

        # Set initial obstacle speed
        obstacle_speed = 4
        speed_increase_interval = 15000  # 15 seconds
        last_speed_increase_time = pygame.time.get_ticks()

        while game_session_running:
            clock.tick(FPS)

            current_time = pygame.time.get_ticks()

            if current_time - last_speed_increase_time >= speed_increase_interval:
                obstacle_speed += 1
                last_speed_increase_time = current_time

            try:
                bg_frame = next(frame_generator)
            except StopIteration:
                frame_generator = get_video_frames(assets['background_video'])
                bg_frame = next(frame_generator)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == obstacle_timer:
                    # Define tunnel area
                    tunnel_start_x = SCREEN_WIDTH // 3  # Starting x of the tunnel
                    tunnel_end_x = 2 * SCREEN_WIDTH // 3  # Ending x of the tunnel

                    # Spawn obstacles randomly within the tunnel area
                    start_x = random.randint(tunnel_start_x, tunnel_end_x)  # Start within tunnel width
                    start_y = 0  # Start at the top
                    obstacle = Obstacle(
                        assets['obstacle'],
                        (start_x, start_y),
                        initial_scale=(50,50),  # Smaller starting size to simulate distance
                        speed=obstacle_speed
                    )
                    obstacle_group.add(obstacle)

                if event.type == score_timer:
                    score +=1
                    


            # Get key inputs
            keys_pressed = pygame.key.get_pressed()

            # Update player position
            player_group.update(keys_pressed)

            # Draw the video frame as background
            screen.blit(bg_frame, (0, 0))

            # Update and draw player
            player_group.draw(screen)

            # Update and draw obstacles
            obstacle_group.update()
            obstacle_group.draw(screen)


            # Collision detection
            if pygame.sprite.spritecollide(player, obstacle_group, False, pygame.sprite.collide_mask):
                assets['game_over_sound'].play()
                if handle_game_over(screen, assets):
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    main()
                running = False

            #display score
            draw_text(f"Score: {score}", assets['score_font'], WHITE, screen, SCREEN_WIDTH//2, 50)
            save_high_score(high_score)

            pygame.display.flip()
        assets['background_video'].close()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
