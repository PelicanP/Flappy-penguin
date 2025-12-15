import pygame
from sys import exit
import random
import asyncio

# Game variables
WIDTH, HEIGHT = 720, 640 # Screen dimensions

# Pygame setup
pygame.init() # Initialise pygame
pygame.mixer.init() # Initialize the mixer module for sound
window = pygame.display.set_mode((WIDTH, HEIGHT)) # Set up the game size dimensions
pygame.display.set_caption("Flappy Penguin") # Set the window title
clock = pygame.time.Clock() # Create a clock object to manage the frame rate

create_pipes_timer = pygame.USEREVENT + 0 # Custom event for creating pipes, 0 means it the first event
pygame.time.set_timer(create_pipes_timer, 1500) # set timer to trigger every 1.5 seconds

#bird class
bird_x = WIDTH/8 #x and y is the position of the bird
bird_y = HEIGHT/2
bird_width = 53 #resolution / 4
bird_height = 60 # size of the bird

# rect class is a rectangle containing all the parameters needed to draw an image (x,y,width,height)
class Bird(pygame.Rect): # Inherit from pygame's Rect class
    def __init__(self, img): 
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height) # Initialize the Rect with position and size
        self.img = img # Store the bird image

# Pipe class
pipe_x = WIDTH
pipe_y = 0
pipe_width = 74
pipe_height = 512

class Pipe(pygame.Rect): # Inherit from pygame's Rect class
    def __init__(self, img):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height) # Initialize the Rect with position and size
        self.img = img # Store the pipe image
        self.passed = False # Flag to check if the bird has passed the pipe

# Game images
background_image = pygame.image.load("background_snow.png") # Load background image
background_image = pygame.transform.scale(background_image, (919, HEIGHT)) # Scale background image
bird_image = pygame.image.load("penguin_sprite.png") # Load bird image 
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height)) # Scale bird image
top_pipe_image = pygame.image.load("icetop.png") # Load top pipe image
top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height)) # Scale top pipe image
bottom_pipe_image = pygame.image.load("icebottom.png") # Load bottom pipe image
bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height)) # Scale bottom pipe image

# Game sounds
game_over_sound = pygame.mixer.Sound("game_over.ogg") # Load game over sound effect
pass_pipe_sound = pygame.mixer.Sound("pass_pipe.ogg") # Load pass pipe sound effect
soundtrack_sound = pygame.mixer.Sound("Soundtrack_mezmer.ogg") # Load background music

# Game objects
bird = Bird(bird_image) # Create a Bird object
pipes = [] # List to hold Pipe objects
velocity_x = -2 # Speed at which pipes move left (2 pixels to the left)
acceleration_x = velocity_x # constant speed
velocity_y = 0 # Move birf up/down
gravity = 0.4 # Gravity affecting the bird
score = 0 # Player score
game_over = False # Game over flag
high_score = 0 # High score
soundtrack = False 

def draw(): # Function to draw the game elements
    window.blit(background_image, (0, 0)) # Draw the background image at the top-left corner
    window.blit(bird.img, bird) # Draw the bird image at its current position

    for pipe in pipes: # loop through all pipes
        window.blit(pipe.img, pipe) # Draw each pipe at its current position

    text_str = str(int(score)) # Convert score to string
    if game_over:
        text_str = "Game Over! Score: " + text_str # Update text if game is over

    text_font = pygame.font.SysFont("Calibri", 40) # Create a font object
    text_render = text_font.render(text_str, True, "Dark Blue") # Render the score text
    window.blit(text_render, (5,5)) # Draw the score text at the top-left corner
    # Update high score
    global high_score 
    if score > high_score:
        high_score = score
    high_score_str = "High Score: " + str(int(high_score)) # Create high score string
    high_score_render = text_font.render(high_score_str, True, "Dark Blue") # Render the high score text
    window.blit(high_score_render, (5, 45)) # Draw the high score text below the score  

def move(): # Function to move pipes
    global velocity_y, velocity_x, score, game_over, high_score # Access global variables
    velocity_y += gravity # Apply gravity to velocity_y 
    bird.y += velocity_y # Move bird by velocity_y
    bird.y = max(bird.y, 0) # Prevent bird from going above the screen
    bird.y = min(bird.y, HEIGHT - bird.height) # Prevent bird from going below the screen

    if bird.y >= HEIGHT - bird.height: # If the bird hits the ground
        velocity_y = 0 # Stop vertical movement
        game_over_sound.play() # Play game over sound
        game_over_sound.set_volume(0.5) # Set volume
        game_over = True # Set game over flag
        return

    for pipe in pipes: # Loop through all pipes
        pipe.x += velocity_x # Move pipe by velocity_x

        if not pipe.passed and bird.x > pipe.x + pipe.width: # If the bird has passed the pipe
            score += 0.5 # 0.5 because each pipe pair consists of a top and bottom pipe
            pass_pipe_sound.play() # Play pass pipe sound
            pass_pipe_sound.set_volume(0.5)
            pipe.passed = True # Mark the pipe as passed

        if bird.colliderect(pipe): # If the bird collides with a pipe
            game_over = True # Set game over flag
            game_over_sound.play()
            game_over_sound.set_volume(0.5)
            return

    while len(pipes) > 0 and pipes[0].x < -pipe_width: # While there are pipes and the first pipe is off-screen to the left
        pipes.pop(0) # Remove the first pipe from the list

    # increase speed as score increases
    velocity_x = acceleration_x - (score / 5) * 0.75 # Increase speed by 0.75 for every 5 points scored


def create_pipes(): # Function to create new pipes
    random_pipe_y = pipe_y - pipe_height/4 - random.random()*(pipe_height/2) # Randomize the vertical position of the top pipe. Range is 0-h/2
    opening_height = HEIGHT / 4 # Height of the opening between top and bottom pipes

    top_pipe = Pipe(top_pipe_image) # Create a top pipe
    top_pipe.y = random_pipe_y # shift the vertical position of the top pipe based on pipe height
    pipes.append(top_pipe) # Add the top pipe to the list

    bottom_pipe = Pipe(bottom_pipe_image) # Create a bottom pipe
    bottom_pipe.y = top_pipe.y + top_pipe.height + opening_height # Position the bottom pipe below the top pipe with an opening
    pipes.append(bottom_pipe) # Add the bottom pipe to the list

async def main():
    global game_over, soundtrack, velocity_y, velocity_x, score, high_score, bird # Access global variables
    running = True
    while running: # Game loop
        # registering events
        for event in pygame.event.get(): # Loop through all events

            if event.type == pygame.QUIT: # If the quit event is triggered
                running = False # Stop the game loop

            if not soundtrack and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): # If any key is pressed or mouse is clicked and soundtrack is not playing
                soundtrack_sound.play(-1) # Play the soundtrack on loop
                soundtrack_sound.set_volume(0.3) # Set volume
                soundtrack = True # Set soundtrack flag to true

            if event.type == create_pipes_timer and not game_over: # If the create pipes timer event is triggered
                create_pipes() # Create new pipes  
                next_pipe_time = random.randint(1500, 2700) # Randomize the time for the next pipe creation
                pygame.time.set_timer(create_pipes_timer, next_pipe_time) # set timer to trigger after the randomized time

            if event.type == pygame.MOUSEBUTTONDOWN:
                velocity_y = -5 # Move the bird up when mouse is clicked 
                                        # Restart the game if it's over
                if game_over: 
                    bird.y = bird_y # Reset bird position
                    pipes.clear() # Clear all existing pipes
                    score = 0 # Reset score
                    velocity_y = 0 # Reset vertical velocity
                    game_over = False # Reset game over flag
                    velocity_x = -2 # Reset pipe speed

            if event.type == pygame.KEYDOWN: # If a key is pressed once
                if event.key in (pygame.K_SPACE, pygame.K_UP): # If the spacebar is pressed
                        velocity_y = -5 # Move the bird up

                        # Restart the game if it's over
                        if game_over: 
                            bird.y = bird_y # Reset bird position
                            pipes.clear() # Clear all existing pipes
                            score = 0 # Reset score
                            velocity_y = 0 # Reset vertical velocity
                            game_over = False # Reset game over flag
                            velocity_x = -2 # Reset pipe speed
                        
        if not game_over:
            move() # Move the pipes
        draw() # Draw the background
        pygame.display.update()
        clock.tick(60) # Set the frame rate to 60 FPS
        await asyncio.sleep(0) # Yield control to the event loop

if __name__ == "__main__":
    asyncio.run(main()) # Run the main function
 


