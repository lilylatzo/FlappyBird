import pygame
import pygame.locals
import random

# Initialize pygame
pygame.init()

# Set up the game clock and fps
clock = pygame.time.Clock()
fps = 60

# Set up the game screen dimensions
screen_width = 500
screen_height = 766

# Create the game screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# Load game images
bg = pygame.image.load("images/background.png")
ground = pygame.image.load("images/ground.png")
button = pygame.image.load("images/restart.png")

# Set up font for displaying score
font = pygame.font.SysFont("Bauds 93", 60)
white = (255, 255, 255)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


# Function to draw text on the screen
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# Function to reset the game state
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


# Bird class for the player-controlled character
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0

        # Character images for animation
        for num in range(1, 4):
            img = pygame.image.load(f"images/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.clicked = False

    # Update bird's position and animation
    def update(self, last_pipe=None):

        if flying is True:
            self.velocity += 0.5
            # Gravity
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom < 620:
                self.rect.y += int(self.velocity)

        # Jumping with click of mouse
        if game_over is False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                self.velocity = -10

            # Mouse released
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate bird animation
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


# Class for pipes that are obstacles
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/pipe.png")
        self.rect = self.image.get_rect()

        # Set top and bottom positions of pipes
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    # Randomizes the pipes' positions
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# Button class for the restart button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    # Draw the button on the screen and checks for interaction
    def draw(self):
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check if mouse is hovering over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Create instances of all objects and button
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height) / 2)
bird_group.add(flappy)
button = Button(int(screen_width / 2 - 50), int(screen_height / 2 - 50), button)

# Game loop
run = True
while run:
    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    # Updates the draw bird and draw pipes
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # Draw ground
    screen.blit(ground, (ground_scroll, 620))

    # Check score and display it
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe is False:
            pass_pipe = True
        if pass_pipe is True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Check for collisions and game over conditions
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # Check of bird has hit ground
    if flappy.rect.bottom > 620:
        game_over = True
        flying = False

    if game_over is False and flying is True:
        # Generate pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Move the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 300:
            ground_scroll = 0

        # Update pipes
        pipe_group.update()

    # Check for game over and restart
    if game_over is True:
        if button.draw() is True:
            game_over = False
            score = reset_game()

    # Handle user input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying is False and game_over is False:
            flying = True

    # Update the display
    pygame.display.update()

# Quit pygame when loop ends
pygame.quit()
