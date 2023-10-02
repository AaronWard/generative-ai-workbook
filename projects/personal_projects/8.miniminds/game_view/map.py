import pygame
import config
import math
import random
import sys
import os

sys.path.append("../")

from person import Person

class Map:
    def __init__(self, screen):
        self.screen = screen
        self.map_array = []
        self.camera = [0, 0]
        self.map_tile_image = {
            config.MAP_TILE_GRASS: pygame.transform.scale(pygame.image.load("imgs/grass1.png"), (config.SCALE, config.SCALE)),
            config.MAP_TILE_WATER: pygame.transform.scale(pygame.image.load("imgs/water.png"), (config.SCALE, config.SCALE)),
            config.MAP_TILE_ROAD: pygame.transform.scale(pygame.image.load("imgs/road.png"), (config.SCALE, config.SCALE)),
        }

    def load(self, file_name):
        file_path = f"maps/{file_name}.txt"
        if not os.path.exists(file_path):  # Check if the file exists
            generated_map = self.generate_map()  # Generate the map
            self.save_map_to_file(generated_map, file_path)  # Save the generated map to a file
        
        with open(file_path) as map_file:
            for line in map_file:
                tiles = [tile for tile in line.strip().split()]
                self.map_array.append(tiles)

    def render(self, player, objects):
        self.determine_camera(player)
        for y_pos, line in enumerate(self.map_array):
            for x_pos, tile in enumerate(line):
                image = self.map_tile_image.get(tile)
                if image:
                    rect = pygame.Rect(x_pos * config.SCALE, y_pos * config.SCALE - (self.camera[1] * config.SCALE), config.SCALE, config.SCALE)
                    self.screen.blit(image, rect)
                

        for object in objects:
            # Check if object is an instance of Person
            if isinstance(object, Person):
                object.render(self.screen)  # Pass only the screen
            else:
                object.render(self.screen, self.camera)

    def determine_camera(self, player):
        max_y_position = len(self.map_array) - config.SCREEN_HEIGHT / config.SCALE
        y_position = player.position[1] - math.ceil(round(config.SCREEN_HEIGHT / config.SCALE / 2))

        if y_position <= max_y_position and y_position >= 0:
            self.camera[1] = y_position
        elif y_position < 0:
            self.camera[1] = 0
        else:
            self.camera[1] = max_y_position

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