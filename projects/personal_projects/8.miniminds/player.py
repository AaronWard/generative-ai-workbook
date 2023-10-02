import pygame
import config

class Player:
    def __init__(self, x_position, y_position):
        print("player created")
        self.position = [x_position, y_position]
        
        # Load and scale the player image
        self.image = pygame.image.load("imgs/player.png")
        self.image = pygame.transform.scale(self.image, (config.SCALE, config.SCALE))
        
        # Initialize the rectangle for positioning and collision detection
        self.rect = pygame.Rect(
            self.position[0] * config.SCALE,
            self.position[1] * config.SCALE,
            config.SCALE,
            config.SCALE
        )

    def update(self):
        print("player updated")

    def update_position(self, x_change, y_change):
        new_x = self.position[0] + x_change
        new_y = self.position[1] + y_change
        
        # Check boundaries and update position if within screen
        if 0 <= new_x < (config.SCREEN_WIDTH // config.SCALE) and 0 <= new_y < (config.SCREEN_HEIGHT // config.SCALE):
            self.position[0] = new_x
            self.position[1] = new_y
            
            # Update the rectangle position
            self.rect.topleft = (
                self.position[0] * config.SCALE,
                self.position[1] * config.SCALE
            )

    def render(self, screen):
        # Blit the image onto the screen at the rectangle's position
        screen.blit(self.image, self.rect)
