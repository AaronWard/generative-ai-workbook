import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
FPS = 10

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game variables
snake_pos = [100, 50]
food_pos = [400, 300]
direction = 'RIGHT'
score = 0

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                direction = 'UP'
            elif event.key == pygame.K_DOWN and direction != 'UP':
                direction = 'DOWN'
            elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                direction = 'RIGHT'

    # Move snake
    if direction == 'UP':
        snake_pos[1] -= BLOCK_SIZE
    elif direction == 'DOWN':
        snake_pos[1] += BLOCK_SIZE
    elif direction == 'LEFT':
        snake_pos[0] -= BLOCK_SIZE
    elif direction == 'RIGHT':
        snake_pos[0] += BLOCK_SIZE

    # Generate food
    if random.random() < 0.05:
        food_pos = [random.randint(0, WIDTH - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE,
                    random.randint(0, HEIGHT - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE]

    # Check for collisions
    if (snake_pos[0] <= 0 or snake_pos[0] >= WIDTH - BLOCK_SIZE or
        snake_pos[1] <= 0 or snake_pos[1] >= HEIGHT - BLOCK_SIZE or
        snake_pos in [food_pos]):
        print(f"Game over! Your score is {score}")
        pygame.quit()
        sys.exit()

    # Check for self collision
    if snake_pos == food_pos:
        score += 1
        food_pos = [random.randint(0, WIDTH - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE,
                    random.randint(0, HEIGHT - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE]

    # Draw everything
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREEN, (snake_pos[0], snake_pos[1], BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, RED, (food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, (10, 10, 10))
    screen.blit(text, (10, 10))

    # Update display
    pygame.display.flip()

    # Cap framerate
    clock.tick(FPS)