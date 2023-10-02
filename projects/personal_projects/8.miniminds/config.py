import pygame

#main.py
FPS=50

# colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCALE = 30
SCREEN_WIDTH = (640 // SCALE) * SCALE  # This will ensure SCREEN_WIDTH is a multiple of SCALE
SCREEN_HEIGHT = (480 // SCALE) * SCALE  # This will ensure SCREEN_HEIGHT is a multiple of SCALE


MAP_TILE_GRASS = "G"
MAP_TILE_WATER = "W"
MAP_TILE_ROAD = "R"
MAP_TILE_PERSON = "P"

MOVEMENTS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}

NPC_CONFIGS = {
    "John": {
        "interests": "Cooking",
        "personality_type": "extroverted, friendly",
        "image_file": "imgs/player.png"
    },
    "Jane": {
        "interests": "Reading",
        "personality_type": "shy",
        "image_file": "imgs/player.png"
    }
}
