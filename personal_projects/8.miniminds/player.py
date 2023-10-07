"""
This script is for the player object that interacts with
the world. It 

TODO:
- Incorporate memory of past events and conversations with other people (agents).
- Implement summarization functionality to allow for 
    agents to recall generalities of past events.
- Implement personality initialization based on the big 5 personality trait model.
- Implement memory of other Persons in the world, use LLMs to formulate opinions
  based on interactions that would influence how they respond:
    eg. Jeff (self thought) -> Tim (other person) - "General opinion: Not fond of him"
- Incorporate the ability for the LLM to control using simulate_key_events()
"""
import pygame
import config
from person import Person 

class Player(Person):
    def __init__(self, x_position, y_position):
        super().__init__("Jeff", "player", "imgs/player.png")
        self.position = [x_position, y_position]
        self.rect.topleft = (
            self.position[0] * config.SCALE,
            self.position[1] * config.SCALE
        )
        
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