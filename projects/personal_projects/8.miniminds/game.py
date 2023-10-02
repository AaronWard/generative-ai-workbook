import time
import pygame
import config
import random
from player import Player
from game_state import GameState

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.objects = []
        self.game_state = GameState.NONE
        self.scheduled_events = []
        self.last_scheduled_event_time = pygame.time.get_ticks()
        self.map = []
        self.map_tile_image = {
            "G": pygame.transform.scale(pygame.image.load("imgs/grass1.png"), (config.SCALE, config.SCALE)),
            "W": pygame.transform.scale(pygame.image.load("imgs/water.png"), (config.SCALE, config.SCALE))
        }

    def set_up(self):
        player = Player(10, 10)
        self.player = player
        self.objects.append(player)
        self.game_state = GameState.RUNNING
        self.load_map()  # You can replace "01" with the actual name of your map file

    def update(self):
        self.screen.fill(config.BLACK)
        self.handle_events()
        self.render_map(self.screen)
        
        for object in self.objects:
            object.render(self.screen)

        current_time = pygame.time.get_ticks()
        while self.scheduled_events and self.scheduled_events[0][0] <= current_time:
            _, key = self.scheduled_events.pop(0)
            event = pygame.event.Event(pygame.KEYDOWN, key=key)
            pygame.event.post(event)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.ENDED
            # handle key events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = GameState.ENDED
                else:
                    x_change, y_change = 0, 0
                    if event.key == pygame.K_UP:  # up
                        y_change = -1
                    elif event.key == pygame.K_DOWN:  # down
                        y_change = 1
                    elif event.key == pygame.K_LEFT:  # left
                        x_change = -1
                    elif event.key == pygame.K_RIGHT:  # right
                        x_change = 1
                        
                    new_x, new_y = self.player.position[0] + x_change, self.player.position[1] + y_change
                    
                    if self.can_move_to_position(new_x, new_y):
                        self.player.update_position(x_change, y_change)

    def can_move_to_position(self, x, y):
        if x < 0 or x >= len(self.map[0]) or y < 0 or y >= len(self.map):
            return False  # Out of map bounds
        if self.map[y][x] == "W":
            return False  # Cannot move to water tile
        
        return True  # Can move to tile

    def simulate_key_events(self, keys):
        current_time = pygame.time.get_ticks()
        delay = 800  # 0.8 second delay
        for key in keys:
            scheduled_time = current_time + delay
            self.scheduled_events.append((scheduled_time, key))
            current_time += delay
            
    def generate_map(self):
        map_width = config.SCREEN_WIDTH // config.SCALE
        map_height = config.SCREEN_HEIGHT // config.SCALE
        
        # Define the possible tile types and their probabilities
        tile_types = ["G", "W"]
        tile_probabilities = [0.85, 0.15]  # % chance for grass, % chance for water
        
        # Initialize map
        generated_map = [[random.choices(tile_types, tile_probabilities)[0] for _ in range(map_width)] for _ in range(map_height)]
        
        # Cellular Automata Iterations
        iterations = 5
        for _ in range(iterations):
            new_map = [row[:] for row in generated_map]  # copy the map
            for y in range(map_height):
                for x in range(map_width):
                    water_neighbors = sum(1 for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                                        if 0 <= x + dx < map_width and 0 <= y + dy < map_height and generated_map[y + dy][x + dx] == "W")
                    
                    if generated_map[y][x] == "G" and water_neighbors >= 4:
                        new_map[y][x] = "W"  # Grass tile converts to water if it has 4 or more water neighbors
                    elif generated_map[y][x] == "W" and water_neighbors <= 2:
                        new_map[y][x] = "G"  # Water tile converts to grass if it has 2 or fewer water neighbors
            
            generated_map = new_map
        
        return generated_map

    def save_map_to_file(self, map, file_name): 
        with open(file_name, 'w') as f:
            for row in map:
                row_str = ' '.join(row)
                f.write(row_str + '\n')

    def load_map(self):
        self.map = self.generate_map()  # call generate_map to get a new map
        self.save_map_to_file(self.map, 'generated_map.txt')  # Save the generated map to a file
        print(self.map) 

    def render_map(self, screen):
        for y_pos, line in enumerate(self.map):
            for x_pos, tile in enumerate(line):
                image = self.map_tile_image.get(tile)
                if image:
                    rect = pygame.Rect(x_pos * config.SCALE, y_pos * config.SCALE, config.SCALE, config.SCALE)
                    screen.blit(image, rect)

