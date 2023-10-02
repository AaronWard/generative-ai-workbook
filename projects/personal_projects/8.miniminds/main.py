import pygame
import config
from game_state import GameState
from game import Game

pygame.init()
pygame.display.set_caption("Miniminds")
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
clock = pygame.time.Clock()
game = Game(screen)
game.set_up()

# character instruction TODO: Make specific to that player object
# game.simulate_key_events([pygame.K_RIGHT, pygame.K_RIGHT])

# Load the map before entering the game loop
game.load('generated_map')

while game.game_state == GameState.RUNNING:
    clock.tick(config.FPS)  # you might want to consider using a variable for the FPS
    game.update()
    pygame.display.flip()
